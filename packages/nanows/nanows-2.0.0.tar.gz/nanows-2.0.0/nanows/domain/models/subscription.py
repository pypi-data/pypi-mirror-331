from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any


@dataclass
class Subscription:
    """
    Represents a WebSocket subscription to a specific topic with optional filters.
    """

    topic: str
    options: Dict[str, Any] = field(default_factory=dict)
    ack: bool = False
    ws_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the subscription to a dictionary format for WebSocket messages.
        """
        message = {"action": "subscribe", "topic": self.topic}

        if self.options:
            message["options"] = self.options

        if self.ack:
            message["ack"] = self.ack

        if self.ws_id:
            message["id"] = self.ws_id

        return message
