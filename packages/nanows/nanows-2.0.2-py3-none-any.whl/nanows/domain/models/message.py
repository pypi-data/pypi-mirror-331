from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum


class ConfirmationType(str, Enum):
    """Enum for confirmation types"""

    ACTIVE_QUORUM = "active_quorum"
    ACTIVE_CONFIRMATION_HEIGHT = "active_confirmation_height"
    INACTIVE = "inactive"
    ALL = "all"
    ACTIVE = "active"


class VoteType(str, Enum):
    """Enum for vote types"""

    VOTE = "vote"
    REPLAY = "replay"
    INDETERMINATE = "indeterminate"


class BlockType(str, Enum):
    """Enum for block types"""

    STATE = "state"
    SEND = "send"
    RECEIVE = "receive"
    OPEN = "open"
    CHANGE = "change"


class BlockSubType(str, Enum):
    """Enum for state block subtypes"""

    SEND = "send"
    RECEIVE = "receive"
    OPEN = "open"
    CHANGE = "change"
    EPOCH = "epoch"


@dataclass
class BaseMessage:
    """Base class for all WebSocket messages"""

    topic: str
    time: str  # Milliseconds since epoch
    raw_message: Dict[str, Any]  # Original message


@dataclass
class Block:
    """Represents a block in a confirmation message"""

    type: BlockType
    account: str
    previous: str
    representative: str
    balance: str
    link: str
    signature: str
    work: str
    subtype: Optional[BlockSubType] = None
    link_as_account: Optional[str] = None
    linked_account: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Block":
        """Create a Block from a dictionary"""
        return cls(
            type=BlockType(data.get("type", "state")),
            account=data.get("account", ""),
            previous=data.get("previous", ""),
            representative=data.get("representative", ""),
            balance=data.get("balance", ""),
            link=data.get("link", ""),
            signature=data.get("signature", ""),
            work=data.get("work", ""),
            subtype=BlockSubType(data.get("subtype")) if data.get("subtype") else None,
            link_as_account=data.get("link_as_account"),
            linked_account=data.get("linked_account"),
        )


@dataclass
class ElectionInfo:
    """Represents election information in a confirmation message"""

    duration: str  # milliseconds
    time: str  # milliseconds since epoch
    tally: str  # raw unit
    request_count: Optional[str] = None
    blocks: Optional[str] = None
    voters: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ElectionInfo":
        """Create an ElectionInfo from a dictionary"""
        return cls(
            duration=data.get("duration", ""),
            time=data.get("time", ""),
            tally=data.get("tally", ""),
            request_count=data.get("request_count"),
            blocks=data.get("blocks"),
            voters=data.get("voters"),
        )


@dataclass
class SidebandInfo:
    """Represents sideband information in a confirmation message"""

    height: str
    local_timestamp: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SidebandInfo":
        """Create a SidebandInfo from a dictionary"""
        return cls(
            height=data.get("height", ""),
            local_timestamp=data.get("local_timestamp", ""),
        )


@dataclass
class ConfirmationMessage(BaseMessage):
    """Represents a confirmation message"""

    account: str
    amount: str
    hash: str
    confirmation_type: ConfirmationType
    block: Optional[Block] = None
    election_info: Optional[ElectionInfo] = None
    sideband_info: Optional[SidebandInfo] = None

    @classmethod
    def from_raw(cls, raw_message: Dict[str, Any]) -> "ConfirmationMessage":
        """Create a ConfirmationMessage from a raw WebSocket message"""
        message = raw_message.get("message", {})

        # Process block if present
        block_data = message.get("block")
        block = Block.from_dict(block_data) if block_data else None

        # Process election info if present
        election_info_data = message.get("election_info")
        election_info = (
            ElectionInfo.from_dict(election_info_data) if election_info_data else None
        )

        # Process sideband info if present
        sideband_info_data = message.get("sideband_info")
        sideband_info = (
            SidebandInfo.from_dict(sideband_info_data) if sideband_info_data else None
        )

        return cls(
            topic="confirmation",
            time=raw_message.get("time", ""),
            raw_message=raw_message,
            account=message.get("account", ""),
            amount=message.get("amount", ""),
            hash=message.get("hash", ""),
            confirmation_type=ConfirmationType(
                message.get("confirmation_type", "active_quorum")
            ),
            block=block,
            election_info=election_info,
            sideband_info=sideband_info,
        )


@dataclass
class VoteMessage(BaseMessage):
    """Represents a vote message"""

    account: str
    signature: str
    sequence: str
    blocks: List[str]
    vote_type: VoteType
    timestamp: Optional[str] = None

    @classmethod
    def from_raw(cls, raw_message: Dict[str, Any]) -> "VoteMessage":
        """Create a VoteMessage from a raw WebSocket message"""
        message = raw_message.get("message", {})
        return cls(
            topic="vote",
            time=raw_message.get("time", ""),
            raw_message=raw_message,
            account=message.get("account", ""),
            signature=message.get("signature", ""),
            sequence=message.get("sequence", ""),
            blocks=message.get("blocks", []),
            vote_type=VoteType(message.get("type", "vote")),
            timestamp=message.get("timestamp"),
        )


@dataclass
class TelemetryMessage(BaseMessage):
    """Represents a telemetry message"""

    block_count: str
    cemented_count: str
    unchecked_count: str
    account_count: str
    bandwidth_cap: str
    peer_count: str
    protocol_version: str
    uptime: str
    major_version: str
    minor_version: str
    patch_version: Optional[str] = None
    pre_release_version: Optional[str] = None
    maker: Optional[str] = None
    timestamp: Optional[str] = None
    active_difficulty: Optional[str] = None
    node_id: Optional[str] = None
    signature: Optional[str] = None
    address: Optional[str] = None
    port: Optional[str] = None

    @classmethod
    def from_raw(cls, raw_message: Dict[str, Any]) -> "TelemetryMessage":
        """Create a TelemetryMessage from a raw WebSocket message"""
        message = raw_message.get("message", {})
        return cls(
            topic="telemetry",
            time=raw_message.get("time", ""),
            raw_message=raw_message,
            block_count=message.get("block_count", ""),
            cemented_count=message.get("cemented_count", ""),
            unchecked_count=message.get("unchecked_count", ""),
            account_count=message.get("account_count", ""),
            bandwidth_cap=message.get("bandwidth_cap", ""),
            peer_count=message.get("peer_count", ""),
            protocol_version=message.get("protocol_version", ""),
            uptime=message.get("uptime", ""),
            major_version=message.get("major_version", ""),
            minor_version=message.get("minor_version", ""),
            patch_version=message.get("patch_version"),
            pre_release_version=message.get("pre_release_version"),
            maker=message.get("maker"),
            timestamp=message.get("timestamp"),
            active_difficulty=message.get("active_difficulty"),
            node_id=message.get("node_id"),
            signature=message.get("signature"),
            address=message.get("address"),
            port=message.get("port"),
        )


@dataclass
class ElectionMessage(BaseMessage):
    """Represents an election message (started or stopped)"""

    hash: str

    @classmethod
    def from_raw(cls, raw_message: Dict[str, Any]) -> "ElectionMessage":
        """Create an ElectionMessage from a raw WebSocket message"""
        message = raw_message.get("message", {})
        return cls(
            topic=raw_message.get("topic", ""),
            time=raw_message.get("time", ""),
            raw_message=raw_message,
            hash=message.get("hash", ""),
        )


@dataclass
class ActiveDifficultyMessage(BaseMessage):
    """Represents an active difficulty message"""

    multiplier: str
    network_current: str
    network_minimum: str
    network_receive_current: Optional[str] = None
    network_receive_minimum: Optional[str] = None

    @classmethod
    def from_raw(cls, raw_message: Dict[str, Any]) -> "ActiveDifficultyMessage":
        """Create an ActiveDifficultyMessage from a raw WebSocket message"""
        message = raw_message.get("message", {})
        return cls(
            topic="active_difficulty",
            time=raw_message.get("time", ""),
            raw_message=raw_message,
            multiplier=message.get("multiplier", ""),
            network_current=message.get("network_current", ""),
            network_minimum=message.get("network_minimum", ""),
            network_receive_current=message.get("network_receive_current"),
            network_receive_minimum=message.get("network_receive_minimum"),
        )


@dataclass
class WorkMessage(BaseMessage):
    """Represents a work message"""

    success: bool
    reason: str
    duration: str
    request: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    bad_peers: Optional[List[str]] = None

    @classmethod
    def from_raw(cls, raw_message: Dict[str, Any]) -> "WorkMessage":
        """Create a WorkMessage from a raw WebSocket message"""
        message = raw_message.get("message", {})
        success = message.get("success", "false").lower() == "true"
        bad_peers = message.get("bad_peers", [])
        if isinstance(bad_peers, str) and not bad_peers:
            bad_peers = []

        return cls(
            topic="work",
            time=raw_message.get("time", ""),
            raw_message=raw_message,
            success=success,
            reason=message.get("reason", ""),
            duration=message.get("duration", ""),
            request=message.get("request", {}),
            result=message.get("result"),
            bad_peers=bad_peers,
        )


@dataclass
class BootstrapMessage(BaseMessage):
    """Represents a bootstrap message"""

    reason: str
    id: str
    mode: str
    total_blocks: Optional[str] = None
    duration: Optional[str] = None

    @classmethod
    def from_raw(cls, raw_message: Dict[str, Any]) -> "BootstrapMessage":
        """Create a BootstrapMessage from a raw WebSocket message"""
        message = raw_message.get("message", {})
        return cls(
            topic="bootstrap",
            time=raw_message.get("time", ""),
            raw_message=raw_message,
            reason=message.get("reason", ""),
            id=message.get("id", ""),
            mode=message.get("mode", ""),
            total_blocks=message.get("total_blocks"),
            duration=message.get("duration"),
        )


@dataclass
class UnconfirmedBlockMessage(BaseMessage):
    """Represents a new unconfirmed block message"""

    block: Block

    @classmethod
    def from_raw(cls, raw_message: Dict[str, Any]) -> "UnconfirmedBlockMessage":
        """Create an UnconfirmedBlockMessage from a raw WebSocket message"""
        message = raw_message.get("message", {})
        block = Block.from_dict(message)

        return cls(
            topic="new_unconfirmed_block",
            time=raw_message.get("time", ""),
            raw_message=raw_message,
            block=block,
        )
