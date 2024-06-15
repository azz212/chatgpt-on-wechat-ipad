# encoding:utf-8

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from config import conf
from .downloadvideo import download_163news,upload_aliyun

@plugins.register(
    name="neteasy",
    desire_priority=-1,
    hidden=True,
    desc="发送链接下载网易视频",
    version="0.1",
    author="lanvent",
)


class neteasy(Plugin):

    group_welc_prompt = "请你随机使用一种风格说一句问候语来欢迎新用户\"{nickname}\"加入群聊。"
    group_exit_prompt = "请你随机使用一种风格介绍你自己，并告诉用户输入#help可以查看帮助信息。"
    patpat_prompt = "请你随机使用一种风格跟其他群用户说他违反规则\"{nickname}\"退出群聊。"

    def __init__(self):
        super().__init__()
        try:
            self.config = super().load_config()
            if not self.config:
                self.config = self._load_config_template()

            logger.info("[neteasy] inited")
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        except Exception as e:
            logger.error(f"[neteasy]初始化异常：{e}")
            raise "[neteasy] init failed, ignore "

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.XML,
        ]:
            return
        msg: ChatMessage = e_context["context"]["msg"]

        group_name = msg.from_user_nickname

        content = e_context["context"].content
        logger.debug("[neteasy] on_handle_context. content: %s" % content)
        if  "wx7be3c1bb46c68c63" in content :
            retcode, filename, filepath = download_163news(content)
            ret = upload_aliyun(filepath, '网易视频')

            reply = Reply()
            reply.type = ReplyType.TEXT
            if ret:
                reply.content = f"neteasy,视频上传完成: {filename} "
            else:
                reply.content = f"neteasy,视频上传失败:, {filename}"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑




    def get_help_text(self, **kwargs):
        help_text = "输入neteasy，我会回复你的名字\n输入End，我会回复你世界的图片\n"
        return help_text

    def _load_config_template(self):
        logger.debug("No neteasy plugin zhao_config.json, use plugins/neteasy/zhao_config.json.template")
        try:
            plugin_config_path = os.path.join(self.path, "config.json.template")
            if os.path.exists(plugin_config_path):
                with open(plugin_config_path, "r", encoding="utf-8") as f:
                    plugin_conf = json.load(f)
                    return plugin_conf
        except Exception as e:
            logger.exception(e)



