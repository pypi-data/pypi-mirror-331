from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncGenerator

from nanows.domain.models.message import BaseMessage
from nanows.domain.models.subscription import Subscription


class WebSocketClientInterface(ABC):
    """Interface for WebSocket client implementations"""

    @abstractmethod
    async def connect(self) -> None:
        """Connect to the WebSocket server"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server"""
        pass

    @abstractmethod
    async def send_message(
        self, message: Dict[str, Any], ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """Send a message to the WebSocket server"""
        pass

    @abstractmethod
    async def subscribe(self, subscription: Subscription) -> None:
        """Subscribe to a topic"""
        pass

    @abstractmethod
    async def unsubscribe(
        self, topic: str, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """Unsubscribe from a topic"""
        pass

    @abstractmethod
    async def update_subscription(
        self,
        topic: str,
        accounts_add: Optional[List[str]] = None,
        accounts_del: Optional[List[str]] = None,
    ) -> None:
        """Update a subscription"""
        pass

    @abstractmethod
    async def ping(self, ack: bool = False, ws_id: Optional[str] = None) -> None:
        """Send a ping message"""
        pass

    @abstractmethod
    async def receive_messages(
        self, topic_filter: Optional[str] = None
    ) -> AsyncGenerator[BaseMessage, None]:
        """Receive messages from the WebSocket server"""
        pass
