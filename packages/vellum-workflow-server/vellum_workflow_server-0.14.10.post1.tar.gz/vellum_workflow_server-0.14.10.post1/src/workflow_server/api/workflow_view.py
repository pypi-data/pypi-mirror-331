from asyncio import Future
from datetime import datetime
import json
import logging
from multiprocessing import Queue, set_start_method
from queue import Empty
import time
import traceback
from uuid import uuid4
from typing import Generator, Iterator, Optional

from flask import Blueprint, Response, current_app as app, request, stream_with_context
from pydantic import ValidationError

from workflow_server.core.executor import (
    CHUNK_END,
    CHUNK_END_JSON_LOAD,
    execute_workflow_pebble_timeout,
    execute_workflow_process_timeout,
    stream_node_pebble_timeout,
    stream_workflow_pebble_timeout,
    stream_workflow_process_timeout,
)
from workflow_server.core.workflow_executor_context import (
    DEFAULT_TIMEOUT_SECONDS,
    NodeExecutorContext,
    WorkflowExecutorContext,
)
from workflow_server.utils.utils import (
    VEMBDA_EXECUTION_FULFILLED_EVENT_NAME,
    VembdaExecutionFulfilledBody,
    VembdaExecutionFulfilledEvent,
    VembdaExecutionInitiatedBody,
    VembdaExecutionInitiatedEvent,
    convert_json_inputs_to_vellum,
    get_version,
)

bp = Blueprint("exec", __name__)

set_start_method("fork", force=True)

logger = logging.getLogger(__name__)


@bp.route("/execute", methods=["POST"])
def exec_route() -> tuple[dict, int]:
    data = request.get_json()
    context = get_workflow_request_context(data)

    app.logger.debug(f"Request received {data.get('execution_id')}")

    try:
        # Pebble uses some sort of managed process pool with timeouts and is like 80ms faster [on live not local]
        # than doing a process yourself. Pebble didn't like it when I used their timeout helper a bunch of times in a
        # big loop and when I used their process pool manually it did other stuff wrong so only used when timeout
        # is the default one
        if context.timeout != DEFAULT_TIMEOUT_SECONDS:
            output = execute_workflow_process_timeout(context)
        else:
            output = execute_workflow_pebble_timeout(context).result()

        resp = {
            "log": output["log"],
            "result": output["result"],
            "stderr": output["stderr"],
            "exit_code": output["exit_code"],
            "timed_out": False,
        }

        app.logger.debug(f"Request complete {data.get('execution_id')}")
        return resp, 200

    except TimeoutError:
        resp = {
            "log": "",
            "result": "",
            "stderr": "",
            "exit_code": -1,
            "timed_out": True,
        }
        return resp, 200
    except Exception as e:
        app.logger.exception(e)

        return {
            "result": "",
            "stderr": traceback.format_exc(),
            "exit_code": -1,
            "timed_out": False,
        }, 200


@bp.route("/stream", methods=["POST"])
def stream_workflow_route() -> Response:
    data = request.get_json()

    try:
        context = get_workflow_request_context(data)
    except ValidationError as e:
        error_message = e.errors()[0]["msg"]
        error_location = e.errors()[0]["loc"]

        return Response(
            json.dumps({"detail": f"Invalid context: {error_message} at {error_location}"}),
            status=400,
            content_type="application/json",
        )

    # Create this event up here so timestamps are fully from the start to account for any unknown overhead
    vembda_initiated_event = VembdaExecutionInitiatedEvent(
        id=uuid4(),
        timestamp=datetime.now(),
        trace_id=context.trace_id,
        span_id=context.execution_id,
        body=VembdaExecutionInitiatedBody(
            sdk_version=get_version().get("sdk_version"),
            server_version=get_version().get("server_version"),
        ),
        parent=None,
    )

    app.logger.debug(f"Stream received {context.execution_id}")

    def process_events(queue: Queue, pebble_future: Optional[Future] = None) -> Iterator[dict]:
        chunked_event: str = ""

        while True:
            try:
                item = queue.get(timeout=context.timeout)

                if isinstance(item, dict):
                    event = item
                elif item == CHUNK_END_JSON_LOAD:
                    # This case is for if Vembda fulfilled is chunked we need to load the json so we can
                    # check it's name. It's important to avoid calling a json.loads() on a big object so
                    # we only load it for this case
                    event = json.loads(chunked_event)
                    chunked_event = ""
                elif item == CHUNK_END:
                    # how did mypy what even, even with an isinstance str check below this doesn't work
                    event = chunked_event  # type: ignore
                    chunked_event = ""
                else:
                    chunked_event += item
                    continue

            except Empty:
                try:
                    if pebble_future and pebble_future.exception(timeout=0.001) is not None:  # type: ignore
                        # This happens when theres a problem with the stream function call
                        # itself not the workflow runner
                        vembda_fulfilled_event = VembdaExecutionFulfilledEvent(
                            id=uuid4(),
                            timestamp=datetime.now(),
                            trace_id=context.trace_id,
                            span_id=context.execution_id,
                            body=VembdaExecutionFulfilledBody(
                                exit_code=-1,
                                stderr="Internal Server Error",
                                container_overhead_latency=context.container_overhead_latency,
                            ),
                            parent=None,
                        )
                        yield vembda_fulfilled_event.model_dump(mode="json")
                        app.logger.exception(stream_future.exception(timeout=0.01))
                        break
                    else:
                        continue
                except TimeoutError:
                    continue
                except Exception as e:
                    logger.exception(e)
                    continue
            except Exception as e:
                logger.exception(e)
                continue

            yield event
            if isinstance(event, dict) and event.get("name") == VEMBDA_EXECUTION_FULFILLED_EVENT_NAME:
                break

    # We have an if check here because pebble is a bit faster since it uses a process tool, but when I set it up
    # I was unable to get the process pool to work directly without the decorator wrapper and you can't create
    # the decorated function with a timeout on the fly so here we are.
    if context.timeout != DEFAULT_TIMEOUT_SECONDS:
        process_queue: Queue[dict] = Queue()

        stream_workflow_process_timeout(
            executor_context=context,
            queue=process_queue,
        )

        workflow_events = process_events(process_queue)

    else:
        pebble_queue: Queue[dict] = Queue()
        # noinspection PyNoneFunctionAssignment
        stream_future = stream_workflow_pebble_timeout(
            executor_context=context,
            queue=pebble_queue,
        )

        workflow_events = process_events(pebble_queue, stream_future)

    def generator() -> Generator[str, None, None]:
        yield "\n"
        yield vembda_initiated_event.model_dump_json()
        yield "\n"
        for index, row in enumerate(workflow_events):
            yield "\n"
            if isinstance(row, dict):
                yield json.dumps(row)
            else:
                yield row
            yield "\n"

    resp = Response(stream_with_context(generator()), status=200, content_type='application/x-ndjson"')
    return resp


@bp.route("/stream-node", methods=["POST"])
def stream_node_route() -> Response:
    data = request.get_json()

    try:
        context = get_node_request_context(data)
    except ValidationError as e:
        error_message = e.errors()[0]["msg"]
        error_location = e.errors()[0]["loc"]
        return Response(
            json.dumps({"detail": f"Invalid context: {error_message} at {error_location}"}),
            status=400,
            content_type="application/json",
        )

    # Create this event up here so timestamps are fully from the start to account for any unknown overhead
    vembda_initiated_event = VembdaExecutionInitiatedEvent(
        id=uuid4(),
        timestamp=datetime.now(),
        trace_id=context.trace_id,
        span_id=context.execution_id,
        body=VembdaExecutionInitiatedBody(
            sdk_version=get_version().get("sdk_version"),
            server_version=get_version().get("server_version"),
        ),
        parent=None,
    )

    app.logger.debug(f"Node stream received {data.get('execution_id')}")

    pebble_queue: Queue[dict] = Queue()
    stream_future = stream_node_pebble_timeout(
        executor_context=context,
        queue=pebble_queue,
    )

    def node_events() -> Iterator[dict]:
        while True:
            try:
                event = pebble_queue.get(timeout=context.timeout)
            except Empty:
                if stream_future.exception() is not None:
                    # This happens when theres a problem with the stream function call
                    # itself not the workflow runner
                    vembda_fulfilled_event = VembdaExecutionFulfilledEvent(
                        id=uuid4(),
                        timestamp=datetime.now(),
                        trace_id=context.trace_id,
                        span_id=context.execution_id,
                        body=VembdaExecutionFulfilledBody(
                            exit_code=-1,
                            stderr="Internal Server Error",
                            container_overhead_latency=context.container_overhead_latency,
                        ),
                        parent=None,
                    )
                    yield vembda_fulfilled_event.model_dump(mode="json")
                    app.logger.exception(stream_future.exception())
                    break
                else:
                    continue

            yield event
            if event.get("name") == VEMBDA_EXECUTION_FULFILLED_EVENT_NAME:
                break

    def generator() -> Generator[str, None, None]:
        yield json.dumps(vembda_initiated_event.model_dump(mode="json"))

        for index, row in enumerate(node_events()):
            yield "\n"
            yield json.dumps(row)

    resp = Response(stream_with_context(generator()), status=200, content_type='application/x-ndjson"')
    return resp


@bp.route("/version", methods=["GET"])
def get_version_route() -> tuple[dict, int]:
    resp = get_version()

    return resp, 200


def get_workflow_request_context(data: dict) -> WorkflowExecutorContext:
    # not sure if this is the filter we want to pass forward?
    context_data = {
        **data,
        "inputs": convert_json_inputs_to_vellum(data["inputs"]),
        "trace_id": uuid4(),
        "request_start_time": time.time_ns(),
    }

    return WorkflowExecutorContext.model_validate(context_data)


def get_node_request_context(data: dict) -> NodeExecutorContext:
    context_data = {
        **data,
        "inputs": convert_json_inputs_to_vellum(data["inputs"]),
        "trace_id": uuid4(),
        "request_start_time": time.time_ns(),
    }

    return NodeExecutorContext.model_validate(context_data)
