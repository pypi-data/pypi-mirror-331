from typing import Dict, List, Optional, Union, Any, AsyncGenerator
import logging

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
from nanows.infrastructure.websocket.websocket_client import WebSocketClient
from nanows.application.nano_websocket_service import NanoWebSocketService


logger = logging.getLogger(__name__)


class NanoWebSocketClient:
    """
    Client for interacting with a Nano node via WebSockets.

    This client provides methods for subscribing to various topics and
    receiving messages from the WebSocket server.
    """

    def __init__(
        self,
        url: str = "ws://localhost:7078",
        reconnect_attempts: int = 5,
        reconnect_delay: float = 1.0,
        reconnect_backoff: float = 1.5,
        keepalive_interval: int = 120,
    ):
        """
        Initialize the NanoWebSocketClient.

        Args:
            url: The WebSocket server URL
            reconnect_attempts: Maximum number of reconnection attempts
            reconnect_delay: Initial delay between reconnection attempts (seconds)
            reconnect_backoff: Backoff factor for reconnection delay
            keepalive_interval: Interval between keepalive messages (seconds)
        """
        self.websocket_client = WebSocketClient(
            url=url,
            reconnect_attempts=reconnect_attempts,
            reconnect_delay=reconnect_delay,
            reconnect_backoff=reconnect_backoff,
            keepalive_interval=keepalive_interval,
        )
        self.service = NanoWebSocketService(self.websocket_client)

    async def connect(self) -> None:
        """Connect to the WebSocket server"""
        await self.service.connect()

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server"""
        await self.service.disconnect()

    async def receive_messages(
        self, topic_filter: Optional[str] = None
    ) -> AsyncGenerator[BaseMessage, None]:
        """
        Receive messages from the WebSocket server.

        Args:
            topic_filter: Optional topic to filter messages by

        Yields:
            Parsed messages from the WebSocket server
        """
        async for message in self.service.receive_messages(topic_filter):
            yield message

    async def subscribe_confirmation(
        self,
        accounts: Optional[List[str]] = None,
        include_block: bool = True,
        include_election_info: bool = False,
        include_linked_account: bool = False,
        include_sideband_info: bool = False,
        confirmation_type: Optional[str] = None,
        ack: bool = False,
        ws_id: Optional[str] = None,
    ) -> None:
        """
        Subscribe to confirmation messages.

        Args:
            accounts: List of accounts to filter by
            include_block: Whether to include block info in the response
            include_election_info: Whether to include election info in the response
            include_linked_account: Whether to include linked account info in the response
            include_sideband_info: Whether to include sideband info in the response
            confirmation_type: Type of confirmation to filter by (all, active, or inactive)
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        await self.service.subscribe_confirmation(
            accounts=accounts,
            include_block=include_block,
            include_election_info=include_election_info,
            include_linked_account=include_linked_account,
            include_sideband_info=include_sideband_info,
            confirmation_type=confirmation_type or "all",
            ack=ack,
            ws_id=ws_id,
        )

    async def subscribe_vote(
        self,
        representatives: Optional[List[str]] = None,
        include_replays: bool = False,
        include_indeterminate: bool = False,
        ack: bool = False,
        ws_id: Optional[str] = None,
    ) -> None:
        """
        Subscribe to vote messages.

        Args:
            representatives: List of representatives to subscribe to
            include_replays: Whether to include replay votes
            include_indeterminate: Whether to include indeterminate votes
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.subscribe_vote(
            representatives=representatives,
            include_replays=include_replays,
            include_indeterminate=include_indeterminate,
            ack=ack,
            ws_id=ws_id,
        )

    async def subscribe_telemetry(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to telemetry messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.subscribe_telemetry(ack=ack, ws_id=ws_id)

    async def subscribe_started_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to started election messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.subscribe_started_election(ack=ack, ws_id=ws_id)

    async def subscribe_stopped_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to stopped election messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.subscribe_stopped_election(ack=ack, ws_id=ws_id)

    async def subscribe_new_unconfirmed_block(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to new unconfirmed block messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.subscribe_new_unconfirmed_block(ack=ack, ws_id=ws_id)

    async def subscribe_bootstrap(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to bootstrap messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.subscribe_bootstrap(ack=ack, ws_id=ws_id)

    async def subscribe_active_difficulty(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to active difficulty messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.subscribe_active_difficulty(ack=ack, ws_id=ws_id)

    async def subscribe_work(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to work messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.subscribe_work(ack=ack, ws_id=ws_id)

    async def unsubscribe_confirmation(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from confirmation messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.unsubscribe_confirmation(ack=ack, ws_id=ws_id)

    async def unsubscribe_vote(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from vote messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.unsubscribe_vote(ack=ack, ws_id=ws_id)

    async def unsubscribe_telemetry(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from telemetry messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.unsubscribe_telemetry(ack=ack, ws_id=ws_id)

    async def unsubscribe_started_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from started election messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.unsubscribe_started_election(ack=ack, ws_id=ws_id)

    async def unsubscribe_stopped_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from stopped election messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.unsubscribe_stopped_election(ack=ack, ws_id=ws_id)

    async def unsubscribe_new_unconfirmed_block(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from new unconfirmed block messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.unsubscribe_new_unconfirmed_block(ack=ack, ws_id=ws_id)

    async def unsubscribe_bootstrap(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from bootstrap messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.unsubscribe_bootstrap(ack=ack, ws_id=ws_id)

    async def unsubscribe_active_difficulty(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from active difficulty messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.unsubscribe_active_difficulty(ack=ack, ws_id=ws_id)

    async def unsubscribe_work(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from work messages.

        Args:
            ack: Whether to request acknowledgement
            ws_id: Optional WebSocket ID
        """
        await self.service.unsubscribe_work(ack=ack, ws_id=ws_id)

    async def update_confirmation_subscription(
        self,
        accounts_add: Optional[List[str]] = None,
        accounts_del: Optional[List[str]] = None,
    ) -> None:
        """
        Update a confirmation subscription.

        Args:
            accounts_add: Accounts to add to the subscription
            accounts_del: Accounts to remove from the subscription
        """
        await self.service.update_confirmation_subscription(
            accounts_add=accounts_add, accounts_del=accounts_del
        )

    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
