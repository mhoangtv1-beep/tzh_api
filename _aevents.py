from ._core import Enum

class EventType(Enum):
    MESSAGE = "message"
    REACTION = "reaction"
    COMMENT = "comment"
    FOLLOW = "follow"
    LIVE_MESSAGE = "live_message"
    LIVE_GIFT = "live_gift"

class GroupEventType(Enum):
    JOIN = "group_join"
    LEAVE = "group_leave"
    UPDATE_NAME = "update_group_name"
    UPDATE_AVATAR = "update_group_avatar"
