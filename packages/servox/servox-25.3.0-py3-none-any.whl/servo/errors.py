# Copyright 2022 Cisco Systems, Inc. and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import datetime
from typing import Optional

import servo

__all__ = (
    "AdjustmentFailedError",
    "AdjustmentRejectedError",
    "BaseError",
    "ConnectorError",
    "ConnectorNotFoundError",
    "EventAbortedError",
    "EventCancelledError",
    "EventHandlersNotFoundError",
    "EventError",
    "MeasurementFailedError",
    "ServoError",
    "UnexpectedEventError",
)


class BaseError(RuntimeError):
    """The base class for all errors in the servo package."""

    def __init__(
        self,
        message: str = "",
        reason: Optional[str] = None,
        *args,
        assembly: Optional[servo.Assembly] = None,
        servo_: Optional[servo.Servo] = None,
        connector: Optional[servo.Connector] = None,
        event: Optional[servo.Event] = None,
        additional_errors: Optional[list[Exception]] = None,
    ) -> None:
        super().__init__(message, *args)

        # Use the context vars to infer the assembly, servo, connector, and event
        import servo

        self._reason = reason
        self._assembly = assembly or servo.current_assembly()
        self._servo = servo_ or servo.current_servo()
        self._connector = connector or getattr(self._servo, "connector", None)
        self._event = event or getattr(self._servo, "event", None)
        self._created_at = datetime.datetime.now()
        self._additional_errors = additional_errors

    @property
    def reason(self) -> Optional[str]:
        """A supplemental reason explaining why the error occurred."""
        return self._reason

    @reason.setter
    def reason(self, value: Optional[str]) -> None:
        self._reason = value

    @property
    def created_at(self) -> datetime.datetime:
        """The date and time when the error occurred."""
        return self._created_at

    @property
    def assembly(self) -> servo.Assembly:
        """The assembly in which the error occurred."""
        return self._assembly

    @property
    def servo(self) -> Optional[servo.Servo]:
        """The servo that was active when the error occurred."""
        return self._servo

    @property
    def connector(self) -> Optional[servo.Connector]:
        """The connector that was active when the error occurred."""
        return self._connector

    @property
    def event(self) -> Optional[servo.Event]:
        """The event that was executing when the error occurred."""
        return self._event


class ServoError(BaseError):
    """An error occurred within a servo."""

    @property
    def servo(self) -> servo.Servo:
        return self._servo

    def __lt__(self, other: ServoError) -> bool:
        cur_pri = _ERROR_PRIORITIES.get(self.__class__, 0)
        o_pri = _ERROR_PRIORITIES.get(other.__class__, 0)
        return cur_pri < o_pri

    @classmethod
    def servo_error_from_group(
        cls, exception_group: ExceptionGroup, default_error: type[BaseError] = None
    ) -> ServoError:
        """
        Walk the ExceptionGroup and return the highest priority error to be communicated to the API. Implementation
        is temporary as we will eventually need to support error groups on the backend
        """
        if default_error is None:
            default_error = cls
        top_error = None
        exc_list = []

        # traverse tree of exceptions depth first. Evaluate priority and raise as the "main" exception with others included as property additional exceptions
        visit_list = list(exception_group.exceptions)
        while visit_list:
            exc = visit_list.pop(0)
            if isinstance(exc, ExceptionGroup):
                visit_list = list(exc.exceptions) + visit_list
            elif isinstance(exc, servo.BaseError):
                exc_list.append(exc)
                if top_error is None or top_error < exc:
                    top_error = exc
            else:
                exc_list.append(exc)

        if top_error is None:
            try:
                # raise from to capture full trace
                raise default_error(
                    message=str(exc_list[0]), additional_errors=exc_list
                ) from exc_list[0]
            except Exception as e:
                return e
        else:
            top_error._additional_errors = exc_list
            return top_error


class ConnectorNotFoundError(ServoError):
    """A mission critical attempt to locate a connector by name or ID has failed"""


class ConnectorError(ServoError):
    """An error occurred within a connector."""

    @property
    def connector(self) -> servo.connector.BaseConnector:
        return self._connector


class EventHandlersNotFoundError(ConnectorError):
    """None of the currently assembled connectors implement handlers for the Event being checked"""


class EventError(ConnectorError):
    """An error occurred during the processing of an event by a connector."""

    @property
    def event(self) -> servo.Event:
        return self._event


class UnexpectedEventError(EventError):
    """The optimizer reported that an unexpected event was submitted."""


class UnexpectedCommandIdError(EventError):
    """The optimizer reported that an unexpected command ID was submitted."""


class EventCancelledError(EventError):
    """The event was cancelled and processing was halted."""


class MeasurementFailedError(EventError):
    """A failure occurred while attempting to perform a measurement.

    Measurement failures are potentially recoverable errors in which the
    measurement was not fully collected due to a transient failure, lost
    connection, interruption, etc. and be retried by the optimizer.
    """


class AdjustmentFailedError(EventError):
    """A failure occurred while attempting to perform an adjustment.

    Adjustment failures are potentially recoverable errors in which the
    adjustment was not fully applied due to a transient failure, lost
    connection, interruption, etc. and be retried by the optimizer.
    """


class AdjustmentRejectedError(AdjustmentFailedError):
    """The adjustment was irrecoverably rejected when applied.

    Rejections occur in circumstances where the target application fails
    to start, becomes unstable, the orchestrator refuses to apply it, or
    other such definitive error condition is encountered that excludes the
    applied configuration from further consideration by the optimizer.
    """


class EventAbortedError(EventError):
    """Abort the currently running event

    During long-running measurements (and, optionally, adjustments) it is often
    necessary to complete the operation early e.g. if there are sustained SLO violations.
    """


# Higher numbers indicate a higher prioerity for the error. 0 is reserved for unrecognized exceptions
_ERROR_PRIORITIES = {
    MeasurementFailedError: 1,
    AdjustmentFailedError: 2,
    AdjustmentRejectedError: 3,
    EventAbortedError: 4,
}
