import json
import uuid
from dataclasses import asdict, dataclass, field
from functools import cached_property
from typing import Any, Dict, Optional, Union, cast

from langgraph.types import Interrupt, StateSnapshot
from uipath_sdk._cli._runtime._contracts import (
    ApiTriggerInfo,
    ErrorCategory,
    ExecutionResult,
    ResumeInfo,
    ResumeTrigger,
    RuntimeStatus,
)
from uipath_sdk._models.actions import Action

from ._context import LangGraphRuntimeContext
from ._escalation import Escalation
from ._exception import LangGraphRuntimeError


@dataclass
class InterruptInfo:
    """Contains all information about an interrupt."""

    value: Any

    @property
    def type(self) -> Optional[ResumeTrigger]:
        """Returns the type of the interrupt value."""
        if isinstance(self.value, Action):
            return ResumeTrigger.ACTION
        return None

    @property
    def identifier(self) -> Optional[str]:
        """Returns the identifier based on the type."""
        if isinstance(self.value, Action):
            return str(self.value.key)
        return None

    def serialize(self) -> str:
        """
        Converts the interrupt value to a JSON string if possible,
        falls back to string representation if not.
        """
        try:
            if hasattr(self.value, "dict"):
                data = self.value.dict()
            elif hasattr(self.value, "to_dict"):
                data = self.value.to_dict()
            elif hasattr(self.value, "__dataclass_fields__"):
                data = asdict(self.value)
            else:
                data = dict(self.value)

            return json.dumps(data, default=str)
        except (TypeError, ValueError, json.JSONDecodeError):
            return str(self.value)

    @cached_property
    def resume_trigger(self) -> ResumeInfo:
        """Creates the resume trigger based on interrupt type."""
        if self.type is None:
            return ResumeInfo(
                api_resume=ApiTriggerInfo(
                    inbox_id=str(uuid.uuid4()), request=self.serialize()
                )
            )
        else:
            return ResumeInfo(itemKey=self.identifier, triggerType=self.type)


@dataclass
class LangGraphOutputProcessor:
    """
    Contains and manages the complete output information from graph execution.
    Handles serialization, interrupt data, and file output.
    """

    context: LangGraphRuntimeContext

    _interrupt_info: Optional[InterruptInfo] = field(
        default=None, init=False, repr=False
    )
    _resume_trigger: Optional[ResumeInfo] = field(default=None, init=False, repr=False)

    def __post_init__(self):
        """Process and cache interrupt information after initialization."""
        state = cast(StateSnapshot, self.context.state)
        if not state or not hasattr(state, "next") or not state.next:
            return

        for task in state.tasks:
            if hasattr(task, "interrupts") and task.interrupts:
                for interrupt in task.interrupts:
                    if isinstance(interrupt, Interrupt):
                        self._interrupt_info = InterruptInfo(interrupt.value)
                        self._resume_trigger = self._interrupt_info.resume_trigger
                        return

    @property
    def status(self) -> RuntimeStatus:
        """Determines the execution status based on state."""
        return (
            RuntimeStatus.SUSPENDED
            if self._interrupt_info
            else RuntimeStatus.SUCCESSFUL
        )

    @property
    def interrupt_value(self) -> Union[Action, Any]:
        """Returns the actual value of the interrupt, with its specific type."""
        if self.interrupt_info is None:
            return None
        return self.interrupt_info.value

    @property
    def interrupt_info(self) -> Optional[InterruptInfo]:
        """Gets interrupt information if available."""
        return self._interrupt_info

    @property
    def resume_trigger(self) -> Optional[ResumeInfo]:
        """Gets resume trigger if interrupted."""
        return self._resume_trigger

    @cached_property
    def serialized_output(self) -> Dict[str, Any]:
        """Serializes the graph execution result."""
        try:
            if self.context.output is None:
                return {}
            if hasattr(self.context.output, "dict"):
                return self.context.output.dict()
            elif hasattr(self.context.output, "to_dict"):
                return self.context.output.to_dict()
            return dict(self.context.output)
        except Exception as e:
            raise LangGraphRuntimeError(
                "OUTPUT_SERIALIZATION_FAILED",
                "Failed to serialize graph output",
                f"Error serializing output data: {str(e)}",
                ErrorCategory.SYSTEM,
            ) from e

    async def process(self) -> ExecutionResult:
        """
        Process the output and prepare the final execution result.

        Returns:
            ExecutionResult: The processed execution result.

        Raises:
            LangGraphRuntimeError: If processing fails.
        """
        try:
            await self._save_resume_trigger()

            return ExecutionResult(
                output=self.serialized_output,
                status=self.status,
                resume=self.resume_trigger if self.resume_trigger else None,
            )

        except LangGraphRuntimeError:
            raise
        except Exception as e:
            raise LangGraphRuntimeError(
                "OUTPUT_PROCESSING_FAILED",
                "Failed to process execution output",
                f"Unexpected error during output processing: {str(e)}",
                ErrorCategory.SYSTEM,
            ) from e

    async def _save_resume_trigger(self) -> None:
        """
        Stores the resume trigger in the SQLite database if available.

        Raises:
            LangGraphRuntimeError: If database operations fail.
        """
        if not self.resume_trigger or not self.context.memory:
            return

        try:
            await self.context.memory.setup()
            async with (
                self.context.memory.lock,
                self.context.memory.conn.cursor() as cur,
            ):
                try:
                    await cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS {self.context.resume_triggers_table} (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            type TEXT NOT NULL,
                            key TEXT,
                            timestamp DATETIME DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'utc'))
                        )
                    """)
                except Exception as e:
                    raise LangGraphRuntimeError(
                        "DB_TABLE_CREATION_FAILED",
                        "Failed to create resume triggers table",
                        f"Database error while creating table: {str(e)}",
                        ErrorCategory.SYSTEM,
                    ) from e

                try:
                    default_escalation = Escalation()

                    if default_escalation.enabled:
                        action = await default_escalation.create(self.interrupt_value)
                        if action:
                            self._resume_trigger = ResumeInfo(
                                trigger_type=ResumeTrigger.ACTION, item_key=action.key
                            )

                except Exception as e:
                    raise LangGraphRuntimeError(
                        "ESCALATION_CREATION_FAILED",
                        "Failed to create escalation action",
                        f"Error while creating escalation action: {str(e)}",
                        ErrorCategory.SYSTEM,
                    ) from e

                if (
                    self.resume_trigger.trigger_type == ResumeTrigger.API
                    and self.resume_trigger.api_resume
                ):
                    trigger_key = self.resume_trigger.api_resume.inbox_id
                    trigger_type = str(self.resume_trigger.trigger_type)
                else:
                    trigger_key = self.resume_trigger.item_key
                    trigger_type = str(self.resume_trigger.trigger_type)

                try:
                    print(f"[ResumeTrigger]: Store DB {trigger_type} {trigger_key}")
                    await cur.execute(
                        f"INSERT INTO {self.context.resume_triggers_table} (type, key) VALUES (?, ?)",
                        (trigger_type, trigger_key),
                    )
                    await self.context.memory.conn.commit()
                except Exception as e:
                    raise LangGraphRuntimeError(
                        "DB_INSERT_FAILED",
                        "Failed to save resume trigger",
                        f"Database error while saving resume trigger: {str(e)}",
                        ErrorCategory.SYSTEM,
                    ) from e
        except LangGraphRuntimeError:
            raise
        except Exception as e:
            raise LangGraphRuntimeError(
                "RESUME_TRIGGER_SAVE_FAILED",
                "Failed to save resume trigger",
                f"Unexpected error while saving resume trigger: {str(e)}",
                ErrorCategory.SYSTEM,
            ) from e
