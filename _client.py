import time
import threading
from .models import *
from . import _util, _state
from .logging import Logging

logger = Logging()

class TzhAPI(object):
    def __init__(self, session_cookies=None, user_agent=None, auto_login=True):
        self._state = _state.State(user_agent=user_agent)
        self._condition = threading.Event()
        self._listening = False
        self.key = _util.generate_p256_key()
        self._uid = None
        self._sec_uid = None

        if session_cookies:
            self.setSession(session_cookies)
            if auto_login and not self.isLoggedIn():
                logger.warning("Session cookies might be invalid or expired")

    @property
    def uid(self):
        return self._uid

    @property
    def sec_uid(self):
        return self._sec_uid

    def _get(self, *args, **kwargs):
        return self._state._get(*args, **kwargs)

    def _post(self, *args, **kwargs):
        return self._state._post(*args, **kwargs)

    def setSession(self, session_cookies):
        self._state.setCookies(session_cookies)
        cookies = self._state.getCookies()
        self._uid = cookies.get("uid") or cookies.get("my_user_id") or cookies.get("passport_csrf_token_default")
        return True

    def getSession(self):
        return self._state.getCookies()

    def isLoggedIn(self):
        res = self.fetchAccountInfo()
        if isinstance(res, dict) and (res.get("data", {}).get("user_id") or res.get("userInfo")):
            user_data = res.get("data") or res.get("userInfo")
            self._uid = user_data.get("user_id") or user_data.get("user", {}).get("id")
            self._sec_uid = user_data.get("sec_uid") or user_data.get("user", {}).get("secUid")
            return True
        return False

    def fetchAccountInfo(self):
        url = "https://passport.tiktok.com/passport/web/account/info/"
        res = self._get(url, params={"aid": 1988})
        if isinstance(res, dict) and res.get("data", {}).get("user_id"):
            return res
        return self.fetchUserInfo()

    def fetchUserInfo(self, unique_id="", sec_uid=""):
        url = "https://www.tiktok.com/api/user/detail/"
        params = {"aid": 1988}
        if unique_id:
            params["uniqueId"] = unique_id
        if sec_uid:
            params["secUid"] = sec_uid
        return self._get(url, params=params)

    def fetchAllConversations(self, cursor=0, count=20):
        url = "https://im-api-sg.tiktok.com/v2/message/get_by_user_init"
        params = {"aid": 1988, "cursor": cursor, "count": count}
        return self._get(url, params=params)

    def fetchConversationHistory(self, thread_id, cursor=0, count=20):
        url = "https://im-api-sg.tiktok.com/v1/message/get_by_conversation"
        params = {
            "aid": 1988,
            "conversation_id": thread_id,
            "cursor": cursor,
            "count": count
        }
        return self._get(url, params=params)

    def sendMessage(self, message, thread_id, thread_type=ThreadType.GROUP, anti_detection=True):
        text = message.text if isinstance(message, Message) else str(message)
        if anti_detection:
            text = _util.mask_text(text)

        payload_bytes = _util.build_im_message_payload(str(thread_id), text, self._uid or 0)
        url = "https://im-api-sg.tiktok.com/v1/message/send"
        dpop_token = _util.build_dpop_token(self.key, "POST", url)
        headers = {
            "Content-Type": "application/x-protobuf",
            "DPoP": dpop_token,
            "Referer": "https://www.tiktok.com/messages"
        }
        return self._post(url, params={"aid": 1988}, data=payload_bytes, headers=headers)

    def deleteMessage(self, thread_id, msg_id):
        url = "https://im-api-sg.tiktok.com/v1/message/recall"
        params = {"aid": 1988}
        data = {"conversation_id": thread_id, "server_message_id": msg_id}
        return self._post(url, params=params, data=data)

    def markConversationRead(self, thread_id, last_msg_index):
        url = "https://im-api-sg.tiktok.com/v1/conversation/mark_read"
        params = {"aid": 1988}
        data = {"conversation_id": thread_id, "read_index": last_msg_index}
        return self._post(url, params=params, data=data)

    def fetchGroupInfo(self, group_id):
        url = "https://im-api-sg.tiktok.com/v1/conversation/get"
        params = {"aid": 1988, "conversation_id": group_id}
        return self._get(url, params=params)

    def createGroup(self, user_ids, name=""):
        url = "https://im-api-sg.tiktok.com/v1/conversation/create"
        params = {"aid": 1988}
        data = {"participants": user_ids, "name": name}
        return self._post(url, params=params, data=data)

    def changeGroupName(self, group_id, name):
        url = "https://im-api-sg.tiktok.com/v1/conversation/modify"
        params = {"aid": 1988}
        data = {"conversation_id": group_id, "name": name}
        return self._post(url, params=params, data=data)

    def addUsersToGroup(self, group_id, user_ids):
        url = "https://im-api-sg.tiktok.com/v1/conversation/participants/add"
        params = {"aid": 1988}
        data = {"conversation_id": group_id, "participants": user_ids}
        return self._post(url, params=params, data=data)

    def removeUserFromGroup(self, group_id, user_ids):
        url = "https://im-api-sg.tiktok.com/v1/conversation/participants/remove"
        params = {"aid": 1988}
        data = {"conversation_id": group_id, "participants": user_ids}
        return self._post(url, params=params, data=data)

    def leaveGroup(self, group_id):
        url = "https://im-api-sg.tiktok.com/v1/conversation/leave"
        params = {"aid": 1988}
        data = {"conversation_id": group_id}
        return self._post(url, params=params, data=data)

    def fetchFeed(self, count=30, refresh_index=1):
        url = "https://www.tiktok.com/api/recommend/item_list/"
        params = {"aid": 1988, "count": count, "refresh_index": refresh_index, "clientCount": 0}
        return self._get(url, params=params)

    def fetchFollowingFeed(self, count=30, cursor=0):
        url = "https://www.tiktok.com/api/feed/follow/list/"
        params = {"aid": 1988, "count": count, "cursor": cursor}
        return self._get(url, params=params)

    def fetchFriendsFeed(self, count=30, cursor=0):
        url = "https://www.tiktok.com/api/friend/feed/list/"
        params = {"aid": 1988, "count": count, "cursor": cursor}
        return self._get(url, params=params)

    def fetchUserPosts(self, sec_uid, count=30, cursor=0):
        url = "https://www.tiktok.com/api/post/item_list/"
        params = {"aid": 1988, "secUid": sec_uid, "count": count, "cursor": cursor}
        return self._get(url, params=params)

    def fetchUserLikedPosts(self, sec_uid, count=30, cursor=0):
        url = "https://www.tiktok.com/api/favorite/item_list/"
        params = {"aid": 1988, "secUid": sec_uid, "count": count, "cursor": cursor}
        return self._get(url, params=params)

    def fetchVideoDetail(self, item_id):
        url = "https://www.tiktok.com/api/item/detail/"
        params = {"aid": 1988, "itemId": item_id}
        return self._get(url, params=params)

    def likeVideo(self, item_id):
        url = "https://www.tiktok.com/api/commit/item/digg/"
        params = {"aid": 1988, "aweme_id": item_id, "type": 1}
        return self._post(url, params=params)

    def unlikeVideo(self, item_id):
        url = "https://www.tiktok.com/api/commit/item/digg/"
        params = {"aid": 1988, "aweme_id": item_id, "type": 0}
        return self._post(url, params=params)

    def collectVideo(self, item_id):
        url = "https://www.tiktok.com/api/item/collect/"
        params = {"aid": 1988, "item_id": item_id, "action": 1}
        return self._post(url, params=params)

    def uncollectVideo(self, item_id):
        url = "https://www.tiktok.com/api/item/collect/"
        params = {"aid": 1988, "item_id": item_id, "action": 0}
        return self._post(url, params=params)

    def followUser(self, user_id):
        url = "https://www.tiktok.com/api/commit/follow/user/"
        params = {"aid": 1988, "user_id": user_id, "type": 1}
        return self._post(url, params=params)

    def unfollowUser(self, user_id):
        url = "https://www.tiktok.com/api/commit/follow/user/"
        params = {"aid": 1988, "user_id": user_id, "type": 0}
        return self._post(url, params=params)

    def fetchFollowers(self, sec_uid, count=30, cursor=0):
        url = "https://www.tiktok.com/api/user/list/"
        params = {"aid": 1988, "secUid": sec_uid, "count": count, "minCursor": cursor, "scene": 67}
        return self._get(url, params=params)

    def fetchFollowing(self, sec_uid, count=30, cursor=0):
        url = "https://www.tiktok.com/api/user/list/"
        params = {"aid": 1988, "secUid": sec_uid, "count": count, "minCursor": cursor, "scene": 21}
        return self._get(url, params=params)

    def fetchFriends(self, sec_uid, count=30, cursor=0):
        url = "https://www.tiktok.com/api/user/list/"
        params = {"aid": 1988, "secUid": sec_uid, "count": count, "minCursor": cursor, "scene": 68}
        return self._get(url, params=params)

    def fetchComments(self, item_id, cursor=0, count=20):
        url = "https://www.tiktok.com/api/comment/list/"
        params = {"aid": 1988, "aweme_id": item_id, "cursor": cursor, "count": count}
        return self._get(url, params=params)

    def fetchCommentReplies(self, item_id, comment_id, cursor=0, count=20):
        url = "https://www.tiktok.com/api/comment/list/reply/"
        params = {"aid": 1988, "item_id": item_id, "comment_id": comment_id, "cursor": cursor, "count": count}
        return self._get(url, params=params)

    def sendComment(self, text, item_id):
        url = "https://www.tiktok.com/api/comment/publish/"
        params = {"aid": 1988, "aweme_id": item_id, "text": text}
        return self._post(url, params=params)

    def replyComment(self, text, item_id, reply_id):
        url = "https://www.tiktok.com/api/comment/publish/"
        params = {"aid": 1988, "aweme_id": item_id, "text": text, "reply_id": reply_id}
        return self._post(url, params=params)

    def deleteComment(self, cid):
        url = "https://www.tiktok.com/api/comment/delete/"
        params = {"aid": 1988, "cid": cid}
        return self._post(url, params=params)

    def likeComment(self, cid):
        url = "https://www.tiktok.com/api/comment/digg/"
        params = {"aid": 1988, "cid": cid, "type": 1}
        return self._post(url, params=params)

    def unlikeComment(self, cid):
        url = "https://www.tiktok.com/api/comment/digg/"
        params = {"aid": 1988, "cid": cid, "type": 0}
        return self._post(url, params=params)

    def searchGeneral(self, keyword, offset=0, count=10):
        url = "https://www.tiktok.com/api/search/general/full/"
        params = {"aid": 1988, "keyword": keyword, "offset": offset, "count": count}
        return self._get(url, params=params)

    def searchUsers(self, keyword, cursor=0, count=10):
        url = "https://www.tiktok.com/api/search/user/full/"
        params = {"aid": 1988, "keyword": keyword, "cursor": cursor, "count": count}
        return self._get(url, params=params)

    def searchVideos(self, keyword, cursor=0, count=10):
        url = "https://www.tiktok.com/api/search/item/full/"
        params = {"aid": 1988, "keyword": keyword, "cursor": cursor, "count": count}
        return self._get(url, params=params)

    def searchLive(self, keyword, offset=0, count=10):
        url = "https://www.tiktok.com/api/search/live/full/"
        params = {"aid": 1988, "keyword": keyword, "offset": offset, "count": count}
        return self._get(url, params=params)

    def fetchNotifications(self, count=20, max_time=0):
        url = "https://www.tiktok.com/api/notice/multi/"
        params = {"aid": 1988, "count": count, "max_time": max_time}
        return self._get(url, params=params)

    def fetchLiveRoomInfo(self, room_id):
        url = "https://webcast.tiktok.com/webcast/room/info/"
        params = {"aid": 1988, "room_id": room_id}
        return self._get(url, params=params)

    def checkUserLive(self, room_ids):
        url = "https://webcast.tiktok.com/webcast/room/check_alive/"
        params = {"aid": 1988, "room_ids": room_ids}
        return self._get(url, params=params)

    def fetchLiveMessages(self, room_id, cursor=""):
        url = "https://webcast.tiktok.com/webcast/im/fetch/"
        params = {"aid": 1988, "room_id": room_id, "cursor": cursor}
        return self._get(url, params=params)

    def fetchLiveGiftList(self, room_id):
        url = "https://webcast.tiktok.com/webcast/gift/list/"
        params = {"aid": 1988, "room_id": room_id}
        return self._get(url, params=params)

    def listen(self, delay=3):
        self._listening = True
        logger.info("TzhAPI listening started...")
        last_cursor = 0
        while self._listening:
            try:
                conversations = self.fetchAllConversations(cursor=last_cursor, count=10)
                if isinstance(conversations, dict) and "data" in conversations:
                    pass
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Error in listen loop: {e}")
                time.sleep(delay)

    def stopListening(self):
        self._listening = False
        logger.info("TzhAPI listening stopped.")
