# encoding:utf-8

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
from plugins import *
from channel.chat_message import ChatMessage


@plugins.register(
    name="Finish",
    desire_priority=-999,
    hidden=True,
    desc="A plugin that check unknown command",
    version="1.0",
    author="js00000",
)
class Finish(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[Finish] inited")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return

        content = e_context["context"].content
        logger.debug("[Finish] on_handle_context. content: %s" % content)
        trigger_prefix = conf().get("plugin_trigger_prefix", "$")
        #处理at其他人，没有at自己，但是没有插件处理的得情况。这种不用ai回答
        cmsg: ChatMessage = e_context['context']['msg']
        at_list = cmsg.at_list
        content = e_context["context"].content
        if cmsg.is_at:
            if cmsg.to_user_id not in at_list and cmsg.is_group :
                #return
                reply = Reply()
                reply.type = ReplyType.TEXT
                reply.content = None
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
                logger.debug("[finish] at无插件处理. content: %s" % content)

        if content.startswith(trigger_prefix) and trigger_prefix!="": #如果插件触发为“”则不检查是否处理
            reply = Reply()
            reply.type = ReplyType.ERROR
            reply.content = "未知插件命令\n查看插件命令列表请输入#help 插件名\n"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def get_help_text(self, **kwargs):
        return ""
