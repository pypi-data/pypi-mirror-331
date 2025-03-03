import json
import asyncio
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
import websockets
from websockets.exceptions import ConnectionClosed

from nanows.domain.interfaces.websocket_client import WebSocketClientInterface
from nanows.domain.models.message import BaseMessage
from nanows.domain.models.subscription import Subscription
from nanows.domain.exceptions.websocket_exceptions import (
    ConnectionError,
    SubscriptionError,
    MessageError,
)
from nanows.infrastructure.serialization.message_factory import MessageFactory


logger = logging.getLogger(__name__)


class WebSocketClient(WebSocketClientInterface):
    """Implementation of the WebSocket client interface"""

    def __init__(
        self,
        url: str = "ws://localhost:7078",
        reconnect_attempts: int = 5,
        reconnect_delay: float = 1.0,
        reconnect_backoff: float = 1.5,
        keepalive_interval: int = 120,
    ):
        """
        Initialize the WebSocket client.

        Args:
            url: The WebSocket server URL
            reconnect_attempts: Maximum number of reconnection attempts
            reconnect_delay: Initial delay between reconnection attempts (seconds)
            reconnect_backoff: Backoff factor for reconnection delay
            keepalive_interval: Interval between keepalive messages (seconds)
        """
        self.url = url
        self.reconnect_attempts = reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self.reconnect_backoff = reconnect_backoff
        self.keepalive_interval = keepalive_interval

        self.websocket = None
        self.active_subscriptions: Dict[str, Subscription] = {}
        self.keepalive_task = None
        self.connected = False
        self.message_factory = MessageFactory()

    async def connect(self) -> None:
        """Connect to the WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.url)
            self.connected = True
            logger.info(f"Connected to WebSocket server at {self.url}")

            # Start keepalive task
            if self.keepalive_task is None or self.keepalive_task.done():
                self.keepalive_task = asyncio.create_task(self._keepalive_loop())

            # Restore subscriptions if any
            await self._restore_subscriptions()

        except Exception as e:
            self.connected = False
            logger.error(f"Failed to connect to WebSocket server: {e}")
            raise ConnectionError(f"Failed to connect to WebSocket server: {e}")

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket server"""
        if self.keepalive_task and not self.keepalive_task.done():
            self.keepalive_task.cancel()
            try:
                await self.keepalive_task
            except asyncio.CancelledError:
                logger.debug("Keepalive task cancelled")

        if self.websocket:
            try:
                await self.websocket.close()
                logger.info("Disconnected from WebSocket server")
            except Exception as e:
                logger.error(f"Error disconnecting from WebSocket server: {e}")
            finally:
                self.websocket = None
                self.connected = False

    async def _keepalive_loop(self) -> None:
        """Send periodic ping messages to keep the connection alive"""
        while True:
            try:
                # Check if the websocket is connected
                if self.websocket and self.connected:
                    try:
                        await self.ping()
                        logger.debug("Sent keepalive ping")
                    except Exception as e:
                        logger.error(f"Failed to send ping message: {e}")
                        # Update connection status
                        self.connected = False
                        self.websocket = None

                # Wait for the specified interval
                await asyncio.sleep(self.keepalive_interval)
            except Exception as e:
                logger.error(f"Error in keepalive loop: {e}")
                # Update connection status on error
                self.connected = False
                self.websocket = None

    async def ping(self, ack: bool = False, ws_id: Optional[str] = None) -> None:
        """Send a ping message to the server"""
        message = {"action": "ping"}

        if ack:
            message["ack"] = True

        if ws_id:
            message["id"] = ws_id

        try:
            if self.websocket and self.connected:
                await self.websocket.send(json.dumps(message))
                logger.debug("Sent ping message")
        except ConnectionClosed as e:
            logger.error(f"Failed to send ping message: {e}")
            self.connected = False
            self.websocket = None
        except Exception as e:
            logger.error(f"Failed to send ping message: {e}")
            # Don't raise an exception here to avoid breaking the keepalive loop

    async def send_message(
        self, message: Dict[str, Any], ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """Send a message to the WebSocket server"""
        if not self.websocket:
            await self.connect()

        if ack:
            message["ack"] = True

        if ws_id:
            message["id"] = ws_id

        try:
            await self.websocket.send(json.dumps(message))
            logger.debug(f"Sent message: {message}")
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise MessageError(f"Failed to send message: {e}")

    async def subscribe(self, subscription: Subscription) -> None:
        """Subscribe to a topic"""
        if not self.websocket:
            await self.connect()

        message = subscription.to_dict()

        try:
            await self.websocket.send(json.dumps(message))
            logger.info(f"Subscribed to topic: {subscription.topic}")

            # Store the subscription for reconnection
            self.active_subscriptions[subscription.topic] = subscription

        except Exception as e:
            logger.error(f"Failed to subscribe to topic {subscription.topic}: {e}")
            raise SubscriptionError(
                f"Failed to subscribe to topic {subscription.topic}: {e}"
            )

    async def unsubscribe(
        self, topic: str, ack: bool = False, ws_id: Optional[str] = None
    ) -> None:
        """Unsubscribe from a topic"""
        if not self.websocket:
            await self.connect()

        message = {"action": "unsubscribe", "topic": topic}

        if ack:
            message["ack"] = True

        if ws_id:
            message["id"] = ws_id

        try:
            await self.websocket.send(json.dumps(message))
            logger.info(f"Unsubscribed from topic: {topic}")

            # Remove the subscription
            if topic in self.active_subscriptions:
                del self.active_subscriptions[topic]

        except Exception as e:
            logger.error(f"Failed to unsubscribe from topic {topic}: {e}")
            raise SubscriptionError(f"Failed to unsubscribe from topic {topic}: {e}")

    async def update_subscription(
        self,
        topic: str,
        accounts_add: Optional[List[str]] = None,
        accounts_del: Optional[List[str]] = None,
    ) -> None:
        """Update a subscription"""
        if not self.websocket:
            await self.connect()

        # Validate that accounts aren't in both lists
        if accounts_add and accounts_del:
            shared_accounts = set(accounts_add).intersection(accounts_del)
            if shared_accounts:
                raise SubscriptionError(
                    f"Accounts cannot be in both add and delete lists: {shared_accounts}"
                )

        options = {}
        if accounts_add:
            options["accounts_add"] = accounts_add
        if accounts_del:
            options["accounts_del"] = accounts_del

        message = {"action": "update", "topic": topic, "options": options}

        try:
            await self.websocket.send(json.dumps(message))
            logger.info(f"Updated subscription for topic: {topic}")

            # Update the stored subscription
            if topic in self.active_subscriptions:
                subscription = self.active_subscriptions[topic]

                # Update the accounts in the subscription options
                if "accounts" in subscription.options:
                    current_accounts = set(subscription.options["accounts"])

                    if accounts_add:
                        current_accounts.update(accounts_add)

                    if accounts_del:
                        current_accounts = current_accounts - set(accounts_del)

                    subscription.options["accounts"] = list(current_accounts)

        except Exception as e:
            logger.error(f"Failed to update subscription for topic {topic}: {e}")
            raise SubscriptionError(
                f"Failed to update subscription for topic {topic}: {e}"
            )

    async def _restore_subscriptions(self) -> None:
        """Restore all active subscriptions after reconnection"""
        if not self.active_subscriptions:
            return

        logger.info(f"Restoring {len(self.active_subscriptions)} subscriptions")

        for topic, subscription in self.active_subscriptions.items():
            try:
                await self.subscribe(subscription)
                logger.info(f"Restored subscription to topic: {topic}")
            except Exception as e:
                logger.error(f"Failed to restore subscription to topic {topic}: {e}")
                # Continue with other subscriptions even if one fails

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
        reconnect_attempts = 0
        current_delay = self.reconnect_delay

        while True:
            try:
                if not self.websocket or not self.connected:
                    await self.connect()
                    reconnect_attempts = 0
                    current_delay = self.reconnect_delay

                # Receive message
                message = await self.websocket.recv()
                logger.debug(f"Received message: {message}")

                try:
                    # Parse the message
                    parsed_message = json.loads(message)

                    # Check if it's a topic message
                    if "topic" in parsed_message:
                        # Filter by topic if specified
                        if (
                            topic_filter is None
                            or parsed_message.get("topic") == topic_filter
                        ):
                            # Create a message object using the factory
                            factory = MessageFactory()
                            message_obj = factory.create_message(parsed_message)
                            yield message_obj
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")

            except (websockets.exceptions.ConnectionClosed, ConnectionError) as e:
                logger.warning(f"WebSocket connection closed: {e}")
                await self._handle_reconnection(reconnect_attempts, current_delay)
                reconnect_attempts += 1
                current_delay *= self.reconnect_backoff
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                await asyncio.sleep(1)  # Brief pause before retrying

    async def _handle_reconnection(
        self, reconnect_attempts: int, current_delay: float
    ) -> None:
        """Handle reconnection logic"""
        if reconnect_attempts < self.reconnect_attempts:
            logger.info(f"Attempting to reconnect in {current_delay:.2f} seconds...")
            await asyncio.sleep(current_delay)
            try:
                await self.connect()
                logger.info("Reconnected successfully")
            except Exception as e:
                logger.error(f"Failed to reconnect: {e}")
        else:
            logger.error(
                f"Max reconnection attempts ({self.reconnect_attempts}) reached"
            )
            raise ConnectionError("Failed to reconnect after maximum attempts")
