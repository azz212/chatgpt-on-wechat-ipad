# encoding:utf-8
import xml.etree.ElementTree as ET

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
    author="zhao",
)


class neteasy(Plugin):


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

        elif '' in content:

            url =self.get_xml_element(content,'url')
            #修改接收到的消息，将url提取后，继续让gpt处理
            if 'http://mp.weixin.qq.com/' in url:
                e_context["context"].content="请提取URl的内容，总结这篇文章，URL是{}".format(url)

                e_context.action = EventAction.CONTINUE  # 事件继续


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

    def get_xml_element(self,xml_data,tag):
        value = ""
        # 解析XML数据
        root = ET.fromstring(xml_data)

        # 获取<title>标签的文本内容
        #title = root.find('.//title').text

        # 获取<url>标签的文本内容
        value = root.find('.//'+tag).text

        return value



