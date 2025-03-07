import logging
import warnings
from typing import Any, AsyncIterator, Dict, Iterator, Optional

from .._api import BaseAPI, BaseAsyncAPI
from .types import (
    TaskCall,
    TaskCallResponse,
    TaskRoster,
    TaskStreamData,
    TaskStreamExecutionMetadata,
    TaskStreamQuotaMetaData,
    TaskStreamText,
)

logger = logging.getLogger(__name__)


class TasksAPI(BaseAPI):
    """TaskAPI client."""

    def execute_stream(self, call: TaskCall) -> Iterator[TaskStreamData]:
        """Executes supplied task call in TaskAPI.

        Args:
            call: task call to execute
        Returns:
            Stream of `TaskStreamData` objects in a form of iterator.
        """
        call_body = call.serialize()
        logger.debug("Executing request to TaskAPI with body: %r", call_body)
        for sse_event in self.client.stream(
            method="POST",
            path="task/stream/v2",
            json=call_body,
        ):
            if event := _convert_sse_event(sse_event):
                yield event

    def execute(self, call: TaskCall) -> TaskCallResponse:
        """Executes supplied task call in TaskAPI.

        Args:
            call: task call to execute
        Returns:
            `TaskCallResponse` object that aggregates the streamed response from TaskAPI.
        """
        content = []
        quota_metadata = None
        execution_metadata = []

        for task_stream_data in self.execute_stream(call):
            if isinstance(task_stream_data, TaskStreamText):
                content.append(task_stream_data.content)
            elif isinstance(task_stream_data, TaskStreamQuotaMetaData):
                quota_metadata = task_stream_data
            elif isinstance(task_stream_data, TaskStreamExecutionMetadata):
                execution_metadata.append(task_stream_data)

        return TaskCallResponse(
            content="".join(content),
            quota_metadata=quota_metadata,
            execution_metadata=execution_metadata,
        )

    def roster(self) -> TaskRoster:
        """Returns all available task ids."""
        resp = self.client.request(
            method="GET",
            path="task/roster",
        )
        return TaskRoster.parse_raw(resp.read())


class AsyncTasksAPI(BaseAsyncAPI):
    """TaskAPI async client."""

    async def execute_stream(self, call: TaskCall) -> AsyncIterator[TaskStreamData]:
        """Executes supplied task call in TaskAPI.

        Args:
            call: task call to execute
        Returns:
            Stream of `TaskStreamData` objects in a form of async iterator.
        """
        call_body = call.serialize()
        logger.debug("Executing request to TaskAPI with body: %r", call_body)
        async for sse_event in self.client.stream(
            method="POST",
            path="task/stream/v2",
            json=call_body,
        ):
            if event := _convert_sse_event(sse_event):
                yield event

    async def execute(self, call: TaskCall) -> TaskCallResponse:
        """Executes supplied task call in TaskAPI.

        Args:
            call: task call to execute
        Returns:
            `TaskCallResponse` object that aggregates the streamed response from TaskAPI.
        """
        content = []
        quota_metadata = None
        execution_metadata = []

        async for task_stream_data in self.execute_stream(call):
            if isinstance(task_stream_data, TaskStreamText):
                content.append(task_stream_data.content)
            elif isinstance(task_stream_data, TaskStreamQuotaMetaData):
                quota_metadata = task_stream_data
            elif isinstance(task_stream_data, TaskStreamExecutionMetadata):
                execution_metadata.append(task_stream_data)

        return TaskCallResponse(
            content="".join(content),
            quota_metadata=quota_metadata,
            execution_metadata=execution_metadata,
        )

    async def roster(self) -> TaskRoster:
        """Returns all available task ids."""
        resp = await self.client.request(
            method="GET",
            path="task/roster",
        )
        return TaskRoster.parse_raw(await resp.aread())


def _convert_sse_event(sse_event: Dict[str, Any]) -> Optional[TaskStreamData]:
    logger.debug("Received SSE from TaskAPI: %r", sse_event)

    event_type = sse_event.pop("type")

    if event_type == "Content":
        return TaskStreamText.parse_obj(sse_event)
    elif event_type == "QuotaMetadata":
        return TaskStreamQuotaMetaData.parse_obj(sse_event)
    elif event_type == "ExecutionMetadata":
        return TaskStreamExecutionMetadata.parse_obj(sse_event)

    warnings.warn(f"Can't convert unknown task stream event type {event_type!r}")
    return None
