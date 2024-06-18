# encoding:utf-8

import time

import openai
import openai.error

from bot.bot import Bot
from bot.openai.open_ai_image import OpenAIImage
from bot.openai.open_ai_session import OpenAISession
from bot.session_manager import SessionManager
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
import re
import asyncio
import aiohttp
import os
from urllib.parse import urlparse
user_session = dict()


# OpenAI对话模型API (可用)
class OpenAIBot(Bot, OpenAIImage):
    def __init__(self):
        super().__init__()
        openai.api_key = conf().get("open_ai_api_key")
        if conf().get("open_ai_api_base"):
            openai.api_base = conf().get("open_ai_api_base")
        proxy = conf().get("proxy")
        if proxy:
            openai.proxy = proxy

        self.sessions = SessionManager(OpenAISession, model=conf().get("model") or "text-davinci-003")
        self.args = {
            "model": conf().get("model") or "text-davinci-003",  # 对话模型的名称
            "temperature": conf().get("temperature", 0.9),  # 值在[0,1]之间，越大表示回复越具有不确定性
            "max_tokens": 1200,  # 回复最大的字符数
            "top_p": 1,
            "frequency_penalty": conf().get("frequency_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "presence_penalty": conf().get("presence_penalty", 0.0),  # [-2,2]之间，该值越大则更倾向于产生不同的内容
            "request_timeout": conf().get("request_timeout", None),  # 请求超时时间，openai接口默认设置为600，对于难问题一般需要较长时间
            "timeout": conf().get("request_timeout", None),  # 重试超时时间，在这个时间内，将会自动重试
            "stop": ["\n\n\n"],
        }

    def reply(self, query, context=None):
        # acquire reply content
        if context and context.type:
            if context.type == ContextType.TEXT:
                logger.info("[OPEN_AI] query={}".format(query))
                session_id = context["session_id"]
                reply = None
                if query == "#清除记忆":
                    self.sessions.clear_session(session_id)
                    reply = Reply(ReplyType.INFO, "记忆已清除")
                elif query == "#清除所有":
                    self.sessions.clear_all_session()
                    reply = Reply(ReplyType.INFO, "所有人记忆已清除")
                else:
                    session = self.sessions.session_query(query, session_id)
                    result = self.reply_text(session)
                    total_tokens, completion_tokens, reply_content = (
                        result["total_tokens"],
                        result["completion_tokens"],
                        result["content"],
                    )
                    logger.debug(
                        "[OPEN_AI] new_query={}, session_id={}, reply_cont={}, completion_tokens={}".format(str(session), session_id, reply_content, completion_tokens)
                    )

                    if total_tokens == 0:
                        reply = Reply(ReplyType.ERROR, reply_content)
                    else:
                        self.sessions.session_reply(reply_content, session_id, total_tokens)
                        reply = Reply(ReplyType.TEXT, reply_content)
                return reply
            elif context.type == ContextType.IMAGE_CREATE:
                ok, retstring,prompt = self.create_img(query, 0)


                if ok:
                    #如果是 'p19-flow-sign-sg' 则下载到本地 todo 为什么这个要下载
                    if 'p19-flow-sign-sg' in retstring:
                        file_name = asyncio.run(self.download_first(retstring))
                        parsed_url = urlparse(conf().get("http_hook"))

                        domain = parsed_url.netloc.split(':')[0]
                        port = parsed_url.port
                        scheme = parsed_url.scheme
                        retstring = "{}://{}:{}/pic/{}".format(scheme, domain, port,file_name)


                    reply = Reply(ReplyType.IMAGE_URL, prompt)
                else:
                    reply = Reply(ReplyType.ERROR, retstring)
                return reply

    def reply_text(self, session: OpenAISession, retry_count=0):
        try:
            response = openai.Completion.create(prompt=str(session), **self.args)
            res_content = response.choices[0]["text"].strip().replace("<|endoftext|>", "")
            total_tokens = response["usage"]["total_tokens"]
            completion_tokens = response["usage"]["completion_tokens"]
            logger.info("[OPEN_AI] reply={}".format(res_content))
            return {
                "total_tokens": total_tokens,
                "completion_tokens": completion_tokens,
                "content": res_content,
            }
        except Exception as e:
            need_retry = retry_count < 2
            result = {"completion_tokens": 0, "content": "我现在有点累了，等会再来吧"}
            if isinstance(e, openai.error.RateLimitError):
                logger.warn("[OPEN_AI] RateLimitError: {}".format(e))
                result["content"] = "提问太快啦，请休息一下再问我吧"
                if need_retry:
                    time.sleep(20)
            elif isinstance(e, openai.error.Timeout):
                logger.warn("[OPEN_AI] Timeout: {}".format(e))
                result["content"] = "我没有收到你的消息"
                if need_retry:
                    time.sleep(5)
            elif isinstance(e, openai.error.APIConnectionError):
                logger.warn("[OPEN_AI] APIConnectionError: {}".format(e))
                need_retry = False
                result["content"] = "我连接不到你的网络"
            else:
                logger.warn("[OPEN_AI] Exception: {}".format(e))
                need_retry = False
                self.sessions.clear_session(session.session_id)

            if need_retry:
                logger.warn("[OPEN_AI] 第{}次重试".format(retry_count + 1))
                return self.reply_text(session, retry_count + 1)
            else:
                return result

    async def download_first(self,image_url):
        # 替换为你要下载的图片的 URL
        res = await self.download_image(image_url,"pic", callback=self.on_download_complete)
        index = image_url.find(".png")
        image_name = image_url[:index + 4]
        match = re.search(r'([^/]+.png)', image_name)
        if match:
            image_name = match.group(1)
            print(image_name)

        return image_name
    def on_download_complete(self,result):
        if result:
            return result
        else:
            return result

    async def download_image(self, url, folder, callback):
        if not os.path.exists(folder):
            os.makedirs(folder)

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:

                    # image_url = "https://p16-flow-sign-sg.ciciai.com/ocean-cloud-tos-sg/917708ae0d43462db893e675a03c5de0.png~tplv-0es2k971ck-image.png?rk3s=18ea6f23&x-expires=1749268779&x-signature=QArhLoUB%2BiCAmJlXSc2xVlk2YYQ%3D"
                    index = url.find(".png")
                    image_name = url[:index + 4]
                    match = re.search(r'([^/]+.png)', image_name)
                    if match:
                        image_name = match.group(1)
                        print(image_name)
                    filename = os.path.join(folder, image_name)

                    with open(filename, 'wb') as f:
                        while True:
                            chunk = await response.content.read(1024)
                            if not chunk:
                                break
                            f.write(chunk)
                    print(f"下载成功: {filename}")
                    callback(filename)  # 调用回调函数表示下载完成
                else:
                    print(f"下载失败，状态码: {response.status}")
                    callback("")  # 调用回调函数表示下载失败