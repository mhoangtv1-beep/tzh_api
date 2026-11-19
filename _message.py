from ._core import Enum

class MessageReaction(Enum):
    LIKE = "like"
    LOVE = "love"
    HAHA = "haha"
    WOW = "wow"
    SAD = "sad"
    ANGRY = "angry"

class Message(object):
    def __init__(self, text="", mention=None, quote=None):
        self.text = text
        self.mention = mention
        self.quote = quote

    def __repr__(self):
        return f"<Message text={self.text!r}>"

class Mention(object):
    def __init__(self, uid, offset=0, length=0):
        self.uid = uid
        self.offset = offset
        self.length = length
