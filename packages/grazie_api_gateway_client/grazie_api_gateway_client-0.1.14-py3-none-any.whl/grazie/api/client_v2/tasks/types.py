import json
import time
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from ..types import Credit, Quota

TASK_TYPE_MAP = {
    str: "text",
    bool: "bool",
    int: "int",
    float: "double",
    bytes: "bytes",
    dict: "json",
}


class Key(BaseModel):
    fqdn: str
    type: str


class Value(BaseModel):
    type: str
    value: Any
    modified: Optional[int] = None


class Attributes(BaseModel):
    data: List[Union[Key, Value]]


class TaskCall(BaseModel):
    id: str
    parameters: Union[Dict[str, Any], BaseModel] = {}

    @classmethod
    def from_obj(cls, obj: Union[Dict[str, Any], "TaskCall"]) -> "TaskCall":
        if isinstance(obj, TaskCall):
            return obj
        return cls(**obj)

    def serialize(self) -> Dict[str, Any]:
        data: List[Union[Key, Value]] = []
        now = int(time.time() * 1000)

        parameters = self.parameters
        if isinstance(parameters, BaseModel):
            parameters = parameters.dict()

        for key, value in parameters.items():
            if value is None:
                continue

            parame_type = TASK_TYPE_MAP.get(type(value))
            if parame_type is None:
                raise ValueError(f"Unsupported task parameter type {parame_type!r}")

            data.append(Key(fqdn=key, type=parame_type))
            if parame_type == "json":
                value = json.dumps(value)
            data.append(Value(modified=now, type=parame_type, value=value))

        return {
            "task": self.id,
            "parameters": Attributes(data=data).dict(),
        }


class TaskStreamText(BaseModel):
    content: str


class TaskStreamQuotaMetaData(BaseModel):
    updated: Quota
    spent: Credit


class TaskStreamExecutionMetadata(BaseModel):
    attributes: Attributes


TaskStreamData = Union[TaskStreamText, TaskStreamQuotaMetaData, TaskStreamExecutionMetadata]


class TaskCallResponse(BaseModel):
    content: str
    quota_metadata: Optional[TaskStreamQuotaMetaData] = None
    execution_metadata: List[TaskStreamExecutionMetadata] = []


class TaskRoster(BaseModel):
    ids: List[str]
