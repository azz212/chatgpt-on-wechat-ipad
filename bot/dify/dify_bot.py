# encoding:utf-8
import json
import threading

import requests

from bot.bot1 import Bot
from bot.dify.dify_session import DifySession, DifySessionManager
from bridge.context import ContextType, Context
from bridge.reply import Reply, ReplyType
from common.log import logger
from common import const
from config import conf

class DifyBot(Bot):
    def __init__(self):
        super().__init__()
        self.api_key = conf().get("open_ai_api_key")
        if conf().get("open_ai_api_base"):
            self.api_base = conf().get("open_ai_api_base")
        proxy = conf().get("proxy")
        if proxy:
            self.proxy = proxy
        self.sessions = DifySessionManager(DifySession, model=conf().get("model", const.DIFY))

    def reply(self, query, context: Context=None):
        if context.type == ContextType.TEXT or context.type == ContextType.IMAGE_CREATE:
            if context.type == ContextType.IMAGE_CREATE:
                query = conf().get('image_create_prefix', ['画'])[0] + query
            logger.info("[DIFY] query={}".format(query))
            session_id = context["session_id"]
            channel_type = conf().get("channel_type")
            user = None
            if channel_type == "wx":
                user = context["msg"].other_user_nickname if context.get("msg") else "default"
            elif channel_type in ["wechatcom_app", "wechatmp", "wechatmp_service", "wechatcom_service", "wework",
                                  "dingtalk"]:
                user = context["msg"].other_user_id if context.get("msg") else "default"
            else:
                return Reply(ReplyType.ERROR,
                             f"unsupported channel type: {channel_type}, now dify only support wx, wechatcom_app, wechatmp, wechatmp_service, dingtalk channel")
            logger.debug(f"[DIFY] dify_user={user}")
            user = user if user else "default" # 防止用户名为None，当被邀请进的群未设置群名称时用户名为None
            session = self.sessions.get_session(session_id, user)
            logger.debug(f"[DIFY] session={session} query={query}")

            reply, err = self._reply(query, session, context)
            if err != None:
                reply = Reply(ReplyType.TEXT, "我暂时遇到了一些问题，请您稍后重试~")
            return reply
        else:
            reply = Reply(ReplyType.ERROR, "Bot不支持处理{}类型的消息".format(context.type))
            return reply

    def _get_api_base_url(self):
        return self.api_base

    def _get_headers(self):
        return {
            'Authorization': f"Bearer {self.api_key}"
        }

    def _get_payload(self, query, session: DifySession, response_mode):
        return {
            'inputs': {},
            "query": query,
            "response_mode": response_mode,
            "conversation_id": session.get_conversation_id(),
            "user": session.get_user()
        }

    def _reply(self, query: str, session: DifySession, context: Context):
        try:
            session.count_user_message() # 限制一个conversation中消息数，防止conversation过长
            dify_app_type = conf().get('dify_app_type', 'chatbot')
            if dify_app_type == 'chatbot':
                return self._handle_chatbot(query, session)
            elif dify_app_type == 'agent':
                return self._handle_agent(query, session, context)
            elif dify_app_type == 'workflow':
                return self._handle_workflow(query, session)
            else:
                return None, "dify_app_type must be agent, chatbot or workflow"

        except Exception as e:
            error_info = f"[DIFY] Exception: {e}"
            logger.exception(error_info)
            return None, error_info

    def _handle_chatbot(self, query: str, session: DifySession):
        # TODO: 获取response部分抽取为公共函数
        base_url = self._get_api_base_url()
        chat_url = f'{base_url}/chat-messages'
        headers = self._get_headers()
        response_mode = 'blocking'
        payload = self._get_payload(query, session, response_mode)
        response = requests.post(chat_url, headers=headers, json=payload)
        if response.status_code != 200:
            error_info = f"[DIFY] response text={response.text} status_code={response.status_code}"
            logger.warn(error_info)
            return None, error_info
        rsp_data = response.json()
        logger.debug("[DIFY] usage {}".format(rsp_data.get('metadata', {}).get('usage', 0)))
        # TODO: 处理返回的图片文件
        reply = Reply(ReplyType.TEXT, rsp_data['answer'])
        # 设置dify conversation_id, 依靠dify管理上下文
        if session.get_conversation_id() == '':
            session.set_conversation_id(rsp_data['conversation_id'])
        return reply, None

    def _handle_agent(self, query: str, session: DifySession, context: Context):
        # TODO: 获取response抽取为公共函数
        base_url = self._get_api_base_url()
        chat_url = f'{base_url}/chat-messages'
        headers = self._get_headers()
        response_mode = 'streaming'
        payload = self._get_payload(query, session, response_mode)
        response = requests.post(chat_url, headers=headers, json=payload)
        if response.status_code != 200:
            error_info = f"[DIFY] response text={response.text} status_code={response.status_code}"
            logger.warn(error_info)
            return None, error_info
        msgs, conversation_id = self._handle_sse_response(response)
        channel = context.get("channel")
        # TODO: 适配除微信以外的其他channel
        is_group = context.get("isgroup", False)
        for msg in msgs[:-1]:
            if msg['type'] == 'agent_message':
                if is_group:
                    at_prefix = "@" + context["msg"].actual_user_nickname + "\n"
                    msg['content'] = at_prefix + msg['content']
                reply = Reply(ReplyType.TEXT, msg['content'])
                channel.send(reply, context)
            elif msg['type'] == 'message_file':
                url = self._fill_file_base_url(msg['content']['url'])
                reply = Reply(ReplyType.IMAGE_URL, url)
                thread = threading.Thread(target=channel.send, args=(reply, context))
                thread.start()
        final_msg = msgs[-1]
        reply = None
        if final_msg['type'] == 'agent_message':
            reply = Reply(ReplyType.TEXT, final_msg['content'])
        elif final_msg['type'] == 'message_file':
            url = self._fill_file_base_url(final_msg['content']['url'])
            reply = Reply(ReplyType.IMAGE_URL, url)
        # 设置dify conversation_id, 依靠dify管理上下文
        if session.get_conversation_id() == '':
            session.set_conversation_id(conversation_id)
        return reply, None

    def _handle_workflow(self, query: str, session: DifySession):
        base_url = self._get_api_base_url()
        workflow_url = f'{base_url}/workflows/run'
        headers = self._get_headers()
        payload = self._get_workflow_payload(query, session)
        response = requests.post(workflow_url, headers=headers, json=payload)
        if response.status_code != 200:
            error_info = f"[DIFY] response text={response.text} status_code={response.status_code}"
            logger.warn(error_info)
            return None, error_info
        rsp_data = response.json()
        reply = Reply(ReplyType.TEXT, rsp_data['data']['outputs']['text'])
        return reply, None

    def _fill_file_base_url(self, url: str):
        if url.startswith("https://") or url.startswith("http://"):
            return url
        # 补全文件base url, 默认使用去掉"/v1"的dify api base url
        return self._get_file_base_url() + url

    def _get_file_base_url(self) -> str:
        return self._get_api_base_url().replace("/v1", "")

    def _get_workflow_payload(self, query, session: DifySession):
        return {
            'inputs': {
                "query": query
            },
            "response_mode": "blocking",
            "user": session.get_user()
        }

    def _parse_sse_event(self, event_str):
        """
        Parses a single SSE event string and returns a dictionary of its data.
        """
        event_prefix = "data: "
        if not event_str.startswith(event_prefix):
            return None
        trimmed_event_str = event_str[len(event_prefix):]

        # Check if trimmed_event_str is not empty and is a valid JSON string
        if trimmed_event_str:
            try:
                event = json.loads(trimmed_event_str)
                return event
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from SSE event: {trimmed_event_str}")
                return None
        else:
            logger.warn("Received an empty SSE event.")
            return None

    # TODO: 异步返回events
    def _handle_sse_response(self, response: requests.Response):
        events = []
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                event = self._parse_sse_event(decoded_line)
                if event:
                    events.append(event)

        merged_message = []
        accumulated_agent_message = ''
        conversation_id = None
        for event in events:
            event_name = event['event']
            if event_name == 'agent_message' or event_name == 'message':
                accumulated_agent_message += event['answer']
                logger.debug("[DIFY] accumulated_agent_message: {}".format(accumulated_agent_message))
                # 保存conversation_id
                if not conversation_id:
                    conversation_id = event['conversation_id']
            elif event_name == 'agent_thought':
                self._append_agent_message(accumulated_agent_message, merged_message)
                accumulated_agent_message = ''
                logger.debug("[DIFY] agent_thought: {}".format(event))
            elif event_name == 'message_file':
                self._append_agent_message(accumulated_agent_message, merged_message)
                accumulated_agent_message = ''
                self._append_message_file(event, merged_message)
            elif event_name == 'message_replace':
                # TODO: handle message_replace
                pass
            elif event_name == 'error':
                logger.error("[DIFY] error: {}".format(event))
                raise Exception(event)
            elif event_name == 'message_end':
                self._append_agent_message(accumulated_agent_message, merged_message)
                logger.debug("[DIFY] message_end usage: {}".format(event['metadata']['usage']))
                break
            else:
                logger.warn("[DIFY] unknown event: {}".format(event))

        if not conversation_id:
            raise Exception("conversation_id not found")

        return merged_message, conversation_id

    def _append_agent_message(self, accumulated_agent_message,  merged_message):
        if accumulated_agent_message:
            merged_message.append({
                'type': 'agent_message',
                'content': accumulated_agent_message,
            })

    def _append_message_file(self, event: dict, merged_message: list):
        if event.get('type') != 'image':
            logger.warn("[DIFY] unsupported message file type: {}".format(event))
        merged_message.append({
            'type': 'message_file',
            'content': event,
        })