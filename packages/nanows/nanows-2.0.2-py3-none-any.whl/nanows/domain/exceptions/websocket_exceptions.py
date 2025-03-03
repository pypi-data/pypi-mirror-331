class NanoWebSocketError(Exception):
    """Base exception for all NanoWebSocket errors"""

    pass


class ConnectionError(NanoWebSocketError):
    """Exception raised when a connection error occurs"""

    pass


class SubscriptionError(NanoWebSocketError):
    """Exception raised when a subscription error occurs"""

    pass


class MessageError(NanoWebSocketError):
    """Exception raised when a message error occurs"""

    pass


class ReconnectionError(NanoWebSocketError):
    """Exception raised when a reconnection error occurs"""

    pass


class InvalidTopicError(NanoWebSocketError):
    """Exception raised when an invalid topic is specified"""

    pass


class InvalidOptionsError(NanoWebSocketError):
    """Exception raised when invalid options are specified"""

    pass
