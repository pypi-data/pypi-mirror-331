from typing import AsyncGenerator, Dict, List, Optional, Any

from nanows.domain.interfaces.websocket_client import WebSocketClientInterface
from nanows.domain.models.message import BaseMessage
from nanows.domain.models.subscription import Subscription


class NanoWebSocketService:
    """Service for interacting with the Nano WebSocket API"""

    def __init__(self, websocket_client: WebSocketClientInterface):
        """
        Initialize the service with a WebSocket client.

        Args:
            websocket_client: The WebSocket client to use for communication
        """
        self.websocket_client = websocket_client

    async def connect(self) -> None:
        """Connect to the WebSocket server"""
        await self.websocket_client.connect()

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server"""
        await self.websocket_client.disconnect()

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
        async for message in self.websocket_client.receive_messages(topic_filter):
            yield message

    async def subscribe_confirmation(
        self,
        accounts: Optional[List[str]] = None,
        all_local_accounts: bool = False,
        include_election_info: bool = False,
        include_block: bool = True,
        include_sideband_info: bool = False,
        include_linked_account: bool = False,
        confirmation_type: str = "all",
        ack: bool = False,
        ws_id: Optional[str] = None,
    ) -> None:
        """
        Subscribe to confirmation messages.

        Args:
            accounts: List of accounts to filter by
            all_local_accounts: Whether to subscribe to all local accounts
            include_election_info: Whether to include election info in the response
            include_block: Whether to include block info in the response
            include_sideband_info: Whether to include sideband info in the response
            include_linked_account: Whether to include linked account info in the response
            confirmation_type: Type of confirmation to filter by (all, active, or inactive)
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        options = {}
        if accounts:
            options["accounts"] = accounts
        if all_local_accounts:
            options["all_local_accounts"] = all_local_accounts
        if include_election_info:
            options["include_election_info"] = include_election_info
        if not include_block:
            options["include_block"] = include_block
        if include_sideband_info:
            options["include_sideband_info"] = include_sideband_info
        if include_linked_account:
            options["include_linked_account"] = include_linked_account
        if confirmation_type:
            options["confirmation_type"] = confirmation_type

        subscription = Subscription(
            topic="confirmation", options=options, ack=ack, ws_id=ws_id
        )
        await self.websocket_client.subscribe(subscription)

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
            representatives: List of representatives to filter by
            include_replays: Whether to include replay votes
            include_indeterminate: Whether to include indeterminate votes
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        options = {}
        if representatives:
            options["representatives"] = representatives
        if include_replays:
            options["include_replays"] = include_replays
        if include_indeterminate:
            options["include_indeterminate"] = include_indeterminate

        subscription = Subscription(topic="vote", options=options, ack=ack, ws_id=ws_id)
        await self.websocket_client.subscribe(subscription)

    async def subscribe_telemetry(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to telemetry messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        subscription = Subscription(topic="telemetry", ack=ack, ws_id=ws_id)
        await self.websocket_client.subscribe(subscription)

    async def subscribe_started_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to started election messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        subscription = Subscription(topic="started_election", ack=ack, ws_id=ws_id)
        await self.websocket_client.subscribe(subscription)

    async def subscribe_stopped_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to stopped election messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        subscription = Subscription(topic="stopped_election", ack=ack, ws_id=ws_id)
        await self.websocket_client.subscribe(subscription)

    async def subscribe_new_unconfirmed_block(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to new unconfirmed block messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        subscription = Subscription(topic="new_unconfirmed_block", ack=ack, ws_id=ws_id)
        await self.websocket_client.subscribe(subscription)

    async def subscribe_bootstrap(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to bootstrap messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        subscription = Subscription(topic="bootstrap", ack=ack, ws_id=ws_id)
        await self.websocket_client.subscribe(subscription)

    async def subscribe_active_difficulty(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to active difficulty messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        subscription = Subscription(topic="active_difficulty", ack=ack, ws_id=ws_id)
        await self.websocket_client.subscribe(subscription)

    async def subscribe_work(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Subscribe to work messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        subscription = Subscription(topic="work", ack=ack, ws_id=ws_id)
        await self.websocket_client.subscribe(subscription)

    async def unsubscribe_confirmation(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from confirmation messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        await self.websocket_client.unsubscribe(
            topic="confirmation", ack=ack, ws_id=ws_id
        )

    async def unsubscribe_vote(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from vote messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        await self.websocket_client.unsubscribe(topic="vote", ack=ack, ws_id=ws_id)

    async def unsubscribe_telemetry(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from telemetry messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        await self.websocket_client.unsubscribe(topic="telemetry", ack=ack, ws_id=ws_id)

    async def unsubscribe_started_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from started election messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        await self.websocket_client.unsubscribe(
            topic="started_election", ack=ack, ws_id=ws_id
        )

    async def unsubscribe_stopped_election(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from stopped election messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        await self.websocket_client.unsubscribe(
            topic="stopped_election", ack=ack, ws_id=ws_id
        )

    async def unsubscribe_new_unconfirmed_block(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from new unconfirmed block messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        await self.websocket_client.unsubscribe(
            topic="new_unconfirmed_block", ack=ack, ws_id=ws_id
        )

    async def unsubscribe_bootstrap(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from bootstrap messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        await self.websocket_client.unsubscribe(topic="bootstrap", ack=ack, ws_id=ws_id)

    async def unsubscribe_active_difficulty(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from active difficulty messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        await self.websocket_client.unsubscribe(
            topic="active_difficulty", ack=ack, ws_id=ws_id
        )

    async def unsubscribe_work(
        self, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """
        Unsubscribe from work messages.

        Args:
            ack: Whether to request an acknowledgement
            ws_id: Optional WebSocket ID for the subscription
        """
        await self.websocket_client.unsubscribe(topic="work", ack=ack, ws_id=ws_id)

    async def update_confirmation_subscription(
        self,
        accounts_add: Optional[List[str]] = None,
        accounts_del: Optional[List[str]] = None,
    ) -> None:
        """
        Update a confirmation subscription.

        Args:
            accounts_add: List of accounts to add to the subscription
            accounts_del: List of accounts to remove from the subscription
        """
        await self.websocket_client.update_subscription(
            topic="confirmation", accounts_add=accounts_add, accounts_del=accounts_del
        )

    async def update_vote_subscription(
        self,
        representatives_add: Optional[List[str]] = None,
        representatives_del: Optional[List[str]] = None,
    ) -> None:
        """
        Update a vote subscription.

        Args:
            representatives_add: List of representatives to add to the subscription
            representatives_del: List of representatives to remove from the subscription
        """
        await self.websocket_client.update_subscription(
            topic="vote",
            accounts_add=representatives_add,
            accounts_del=representatives_del,
        )
