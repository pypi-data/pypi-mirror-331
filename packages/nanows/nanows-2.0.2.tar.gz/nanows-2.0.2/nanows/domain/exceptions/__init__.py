"""Exceptions for the nanows package."""

from nanows.domain.exceptions.websocket_exceptions import (
    NanoWebSocketError,
    ConnectionError,
    SubscriptionError,
    MessageError,
    ReconnectionError,
    InvalidTopicError,
    InvalidOptionsError,
)

__all__ = [
    "NanoWebSocketError",
    "ConnectionError",
    "SubscriptionError",
    "MessageError",
    "ReconnectionError",
    "InvalidTopicError",
    "InvalidOptionsError",
]
