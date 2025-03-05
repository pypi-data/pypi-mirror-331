#  This Source Code Form is subject to the terms of the Mozilla Public
#   License, v. 2.0. If a copy of the MPL was not distributed with this
#   file, You can obtain one at https://mozilla.org/MPL/2.0/.
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Protocol, Callable, Awaitable, TypeVar, Dict, Any, List, Generic

from pydantic import BaseModel, Field

from .constants import DEFAULT_SERVICE_KEY_PATH
from .exceptions import OrraError

T_Input = TypeVar('T_Input', bound=BaseModel)
T_Output = TypeVar('T_Output', bound=BaseModel)

# Type alias for handler functions
ServiceHandler = Callable[[T_Input], Awaitable[T_Output]]


class PersistenceMethod(str, Enum):
    FILE = "file"
    CUSTOM = "custom"


class CustomPersistence(Protocol):
    async def save(self, service_id: str) -> None: ...

    async def load(self) -> Optional[str]: ...


class PersistenceConfig(BaseModel):
    method: PersistenceMethod = Field(
        default=PersistenceMethod.FILE,
        description="Method for persisting service identity"
    )
    file_path: Path = Field(
        default=DEFAULT_SERVICE_KEY_PATH,
        description="Path to service key file when using file persistence"
    )
    custom_save: Optional[Callable[[str], Awaitable[None]]] = Field(
        default=None,
        description="Custom save function for service ID persistence"
    )
    custom_load: Optional[Callable[[], Awaitable[Optional[str]]]] = Field(
        default=None,
        description="Custom load function for service ID persistence"
    )

    def model_post_init(self, __context) -> None:
        if self.method == PersistenceMethod.CUSTOM:
            if not (self.custom_save and self.custom_load):
                raise ValueError(
                    "Custom persistence requires both custom_save and custom_load functions"
                )


class CompensationStatus(str, Enum):
    """Status of a compensation operation."""
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"
    EXPIRED = "expired"


class CompensationData(BaseModel):
    """Data required for compensation operations."""
    data: Dict[str, Any] = Field(
        description="Original task and result data needed for compensation"
    )
    ttl_ms: int = Field(
        default=24 * 60 * 60 * 1000,  # 24 hours in milliseconds
        description="Time-to-live for compensation data in milliseconds",
        alias="ttl"
    )


class PartialCompensation(BaseModel):
    """Represents partial compensation state for complex operations."""
    completed: List[str] = Field(
        default=list,
        description="List of completed compensation steps"
    )
    remaining: List[str] = Field(
        default=list,
        description="List of remaining compensation steps"
    )
    model_config = {
        "validate_assignment": True,
        "extra": "forbid"
    }


class CompensationResult(BaseModel):
    """Result of a compensation operation."""
    status: CompensationStatus = Field(
        description="Status of the compensation operation"
    )
    partial: Optional[PartialCompensation] = Field(
        default=None,
        description="Partial compensation details if status is PARTIAL"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if compensation failed"
    )


class TaskResultPayload(BaseModel):
    """Complete task result including compensation data if applicable."""
    task: Dict[str, Any] = Field(
        description="The actual task result"
    )
    compensation: Optional[CompensationData] = Field(
        default=None,
        description="Compensation data if the service is revertible"
    )


class Task(Generic[T_Input]):
    """
    A task received from the plan engine.

    Attributes:
        input: The task input data
        push_update: A method to send interim results back to the plan engine
    """

    def __init__(self, input: T_Input, _sdk=None, _task_id=None, _execution_id=None, _idempotency_key=None):
        self.input = input
        self._sdk = _sdk
        self._task_id = _task_id
        self._execution_id = _execution_id
        self._idempotency_key = _idempotency_key

    async def push_update(self, update_data: dict) -> None:
        """
        Push an interim result update back to the orchestration engine.

        Args:
            update_data: The interim task result data

        Raises:
            OrraError: If the SDK is not properly initialized
        """
        if not self._sdk or not self._task_id or not self._execution_id or not self._idempotency_key:
            raise OrraError("Task not properly initialized for pushing updates")

        await self._sdk.push_update(self._task_id, self._execution_id, self._idempotency_key, update_data)


@dataclass
class RevertSource(Generic[T_Input, T_Output]):
    """
    Wrapper for revert handler inputs that provides access to both
    the original task and its result.

    Type Parameters:
        T_Input: Type of the original task's input model
        T_Output: Type of the original task's output model
    """
    input: T_Input
    output: T_Output
