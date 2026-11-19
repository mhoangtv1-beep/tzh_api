class User(object):
    def __init__(self, uid=None, sec_uid=None, unique_id=None, nickname=None, avatar=None, follower_count=0, following_count=0):
        self.uid = uid
        self.sec_uid = sec_uid
        self.unique_id = unique_id
        self.nickname = nickname
        self.avatar = avatar
        self.follower_count = follower_count
        self.following_count = following_count

    def __repr__(self):
        return f"<User unique_id={self.unique_id!r} uid={self.uid!r}>"

class Group(object):
    def __init__(self, conversation_id=None, name=None, member_count=0, members=None):
        self.conversation_id = conversation_id
        self.name = name
        self.member_count = member_count
        self.members = members or []

    def __repr__(self):
        return f"<Group id={self.conversation_id!r} name={self.name!r}>"

class MessageObject(object):
    def __init__(self, msg_id=None, thread_id=None, thread_type=None, sender_id=None, content=None, timestamp=None):
        self.msg_id = msg_id
        self.thread_id = thread_id
        self.thread_type = thread_type
        self.sender_id = sender_id
        self.content = content
        self.timestamp = timestamp

    def __repr__(self):
        return f"<MessageObject id={self.msg_id!r} thread={self.thread_id!r}>"

class EventObject(object):
    def __init__(self, event_type=None, data=None):
        self.type = event_type
        self.data = data
