from typing import Dict, Any

from nanows.domain.models.message import (
    BaseMessage,
    ConfirmationMessage,
    VoteMessage,
    TelemetryMessage,
    ElectionMessage,
    ActiveDifficultyMessage,
    WorkMessage,
    BootstrapMessage,
    UnconfirmedBlockMessage,
)


class MessageFactory:
    """Factory for creating typed message objects from raw WebSocket messages"""

    @staticmethod
    def create_message(raw_message: Dict[str, Any]) -> BaseMessage:
        """
        Create a typed message object from a raw WebSocket message.

        Args:
            raw_message: The raw WebSocket message

        Returns:
            A typed message object
        """
        topic = raw_message.get("topic")

        if topic == "confirmation":
            return ConfirmationMessage.from_raw(raw_message)

        elif topic == "vote":
            return VoteMessage.from_raw(raw_message)

        elif topic == "telemetry":
            return TelemetryMessage.from_raw(raw_message)

        elif topic in ["started_election", "stopped_election"]:
            return ElectionMessage.from_raw(raw_message)

        elif topic == "active_difficulty":
            return ActiveDifficultyMessage.from_raw(raw_message)

        elif topic == "work":
            return WorkMessage.from_raw(raw_message)

        elif topic == "bootstrap":
            return BootstrapMessage.from_raw(raw_message)

        elif topic == "new_unconfirmed_block":
            return UnconfirmedBlockMessage.from_raw(raw_message)

        # Default case - return a BaseMessage
        return BaseMessage(
            topic=topic or "", time=raw_message.get("time", ""), raw_message=raw_message
        )
