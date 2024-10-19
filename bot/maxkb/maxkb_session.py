from common.expired_dict import ExpiredDict
from config import conf

class MaxKBSession(object):
    def __init__(self, session_id: str, user: str, conversation_id: str = '', chat_id=None):
        """
        MaxKB 机器人会话对象，包含会话ID、用户信息和会话中的相关数据。
        """
        self.__session_id = session_id
        self.__user = user
        self.__conversation_id = conversation_id
        self.__user_message_counter = 0  # 记录用户发送的消息计数
        self.chat_id = chat_id  # Initialize chat_id
    def set_chat_id(self, chat_id):
        """Sets the chat_id for the session."""
        self.chat_id = chat_id

    def get_chat_id(self):
        """Returns the chat_id for the session."""
        return self.chat_id
    def get_session_id(self):
        return self.__session_id

    def get_user(self):
        return self.__user

    def get_conversation_id(self):
        return self.__conversation_id

    def set_conversation_id(self, conversation_id):
        self.__conversation_id = conversation_id

    def count_user_message(self):
        """
        统计用户消息数量，如果超过预设的最大值，则重置会话。
        """
        max_messages = conf().get("expires_in_seconds", 5)
        if self.__user_message_counter >= max_messages:
            self.__user_message_counter = 0
            # 达到最大消息数，清空会话ID来重置会话
            self.__conversation_id = ''
        self.__user_message_counter += 1

    def reset_message_counter(self):
        """手动重置消息计数器"""
        self.__user_message_counter = 0


class MaxKBSessionManager(object):
    def __init__(self, sessioncls, **session_kwargs):
        """
        MaxKB 机器人会话管理类，用于管理多个用户的会话。
        如果设置了过期时间，则会自动过期清除会话。
        """
        expires_in_seconds = conf().get("expires_in_seconds", 3600)
        self.sessions = ExpiredDict(expires_in_seconds) if expires_in_seconds else dict()
        self.sessioncls = sessioncls
        self.session_kwargs = session_kwargs

    def _build_session(self, session_id: str, user: str):
        """
        如果 session_id 不存在，则创建一个新的 session 并添加到 sessions 中。
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = self.sessioncls(session_id, user)
        return self.sessions[session_id]

    def get_session(self, session_id: str, user: str):
        """
        根据 session_id 获取会话，如果不存在则创建新的会话。
        """
        return self._build_session(session_id, user)

    def clear_session(self, session_id: str):
        """
        清除指定的 session。
        """
        if session_id in self.sessions:
            del self.sessions[session_id]

    def clear_all_sessions(self):
        """
        清除所有的 session。
        """
        self.sessions.clear()

    def count_message_for_session(self, session_id: str, user: str):
        """
        为指定的 session 计数用户发送的消息。
        """
        session = self.get_session(session_id, user)
        session.count_user_message()

    def reset_message_counter_for_session(self, session_id: str):
        """
        重置指定会话的消息计数器。
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.reset_message_counter()
