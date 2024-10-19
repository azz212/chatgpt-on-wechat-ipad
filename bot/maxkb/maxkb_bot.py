import json
import requests
from bot.bot1 import Bot
from bot.maxkb.maxkb_session import MaxKBSession, MaxKBSessionManager
from bridge.context import ContextType, Context
from bridge.reply import Reply, ReplyType
from common.log import logger
from common import const
from config import conf


class MaxKBBot(Bot):
    def __init__(self):
        super().__init__()
        self.api_key = conf().get("open_ai_api_key")
        self.api_base = conf().get("open_ai_api_base")
        proxy = conf().get("proxy")
        if proxy:
            self.proxy = proxy
        self.sessions = MaxKBSessionManager(MaxKBSession, model=conf().get("model", const.MAXKB))

    def reply(self, query, context: Context = None):
        if context.type == ContextType.TEXT or context.type == ContextType.IMAGE_CREATE:
            if context.type == ContextType.IMAGE_CREATE:
                query = conf().get('image_create_prefix', ['画'])[0] + query
            logger.info("[MaxKB] query={}".format(query))

            session_id = context["session_id"]
            channel_type = conf().get("channel_type")
            user = None
            if channel_type == "wx":
                user = context["msg"].other_user_nickname if context.get("msg") else "default"
            elif channel_type == "wx-beta":
                user = context["msg"].other_user_nickname if context.get("msg") else "default"
            elif channel_type in ["wechatcom_app", "wechatmp", "wechatmp_service", "wechatcom_service", "wework", "dingtalk"]:
                user = context["msg"].other_user_id if context.get("msg") else "default"
            else:
                return Reply(ReplyType.ERROR, f"Unsupported channel type: {channel_type}, MaxKB only supports wx and dingtalk channels")
            logger.debug(f"[MaxKB] maxkb_user={user}")

            user = user if user else "default"
            session = self.sessions.get_session(session_id, user)
            logger.debug(f"[MaxKB] session={session} query={query}")

            # New flow: Fetch profile_id, chat_id, and send message
            reply, err = self._reply_with_session_management(query, session, context)
            if err:
                reply = Reply(ReplyType.TEXT, "I encountered an issue. Please try again later.")
            return reply
        else:
            return Reply(ReplyType.ERROR, f"Bot does not support handling {context.type} message types")

    def _get_headers(self):
        return {
            'Authorization': f"{self.api_key}",
            'Content-Type': 'application/json',
            'accept': 'application/json'
        }

    def _reply_with_session_management(self, query: str, session: MaxKBSession, context: Context):
        try:
            session.count_user_message()  # Message limit

            # Check if the session already has a valid chat_id
            chat_id = session.get_chat_id()

            if not chat_id:  # If no chat_id is found, fetch profile_id and create a new chat_id
                profile_id = self._get_profile_id()
                if not profile_id:
                    return None, "Failed to get profile_id"

                chat_id = self._get_chat_id(profile_id)
                if not chat_id:
                    return None, "Failed to get chat_id"

                # Store the new chat_id in the session for future messages
                session.set_chat_id(chat_id)

            # Prepare payload and send message
            response = self._send_chat_message(chat_id, query)
            if response:
                return Reply(ReplyType.TEXT, response['data']['content']), None
            else:
                return None, "Failed to send chat message"
        except Exception as e:
            logger.exception(f"[MaxKB] Exception: {e}")
            return None, str(e)

    def _get_profile_id(self):
        endpoint = 'api/application/profile'
        profile_url = f"{self.api_base}{endpoint}"
        response = requests.get(profile_url, headers=self._get_headers())
        if response.status_code == 200:
            profile_id = response.json()['data']['id']
            return profile_id
        else:
            logger.error(f"Failed to get profile_id, status code: {response.status_code}")
            return None

    def _get_chat_id(self, profile_id):

        chat_open_url = f"{self.api_base}api/application/{profile_id}/chat/open"
        response = requests.get(chat_open_url, headers=self._get_headers())
        if response.status_code == 200:
            return response.json()['data']
        else:
            logger.error(f"Failed to get chat_id, status code: {response.status_code}")
            return None


    def _send_chat_message(self, chat_id, message):
        chat_message_url = f"{self.api_base}api/application/chat_message/{chat_id}"
        payload = {
            "message": message,
            "re_chat": False,
            "stream": False
        }
        response = requests.post(chat_message_url, headers=self._get_headers(), json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to send message, status code: {response.status_code}, content: {response.text}")
            return None
