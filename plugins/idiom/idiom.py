import xml.etree.ElementTree as ET

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from config import conf
import time
import requests
import json
import os
import re
from urllib.parse import quote,urlsplit,urlunsplit
from threading import Thread
#from .IdiomGame import IdiomGame
import threading

@plugins.register(
    name="idiom",
    desire_priority=-1,
    hidden=True,
    desc="猜成语",
    version="0.1",
    author="zhao",
)
class idiom(Plugin):
    def __init__(self):
        super().__init__()
        try:
            self.config = super().load_config()
            if not self.config:
                self.config = self._load_config_template()

            logger.info("[idiom] inited")
            self.current_plugin_path = None
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            self.handlers[Event.ON_RECEIVE_MESSAGE] = self.on_receive_message
        except Exception as e:
            logger.error(f"[idiom]初始化异常：{e}")
            raise "[idiom] init failed, ignore "

        # Initialize game-related attributes
        self.game_mode_rooms = {}
        self.game_point = {}
        self.game_answer = {}
        self.game_success = {}
        self.idiom_pic = {}
        self.current_round = {}
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            # 'Connection':'keep-alive' ,#默认时链接一次，多次爬取之后不能产生新的链接就会产生报错Max retries exceeded with url
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "Connection": "close",  # 解决Max retries exceeded with url报错
        }
        # 创建一个线程锁
        self.counter_lock = threading.Lock()

    def on_receive_message(self, e_context: EventContext):
        if e_context['context']['msg'].ctype != ContextType.TEXT:
            return

        context = e_context['context']
        msg: ChatMessage = e_context['context']['msg']
        content = e_context["context"].content
        room_id = msg.other_user_id

        if content == "看图猜成语":
            reply = Reply()
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

        if room_id in self.game_mode_rooms and self.game_mode_rooms[room_id]:
            # Process game-related commands
            if content in ["退出游戏","重发"] or len(content)==4:
                reply = Reply()
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                pass
                #e_context.action = EventAction.BREAK_PASS
    def _load_config_template(self):
        logger.debug("No Hello plugin config.json, use plugins/hello/config.json.template")
        try:
            plugin_config_path = os.path.join(self.path, "config.json.template")
            if os.path.exists(plugin_config_path):
                with open(plugin_config_path, "r", encoding="utf-8") as f:
                    plugin_conf = json.load(f)
                    return plugin_conf
        except Exception as e:
            logger.exception(e)



    def send_text_reply(self, e_context: EventContext, message: str, receiver: str = None):
        reply=Reply()
        reply.content  = message
        reply.type = ReplyType.TEXT
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS

    def send_image_reply(self, e_context: EventContext, image_path: str, receiver: str = None):
        reply = Reply()
        reply.content = image_path
        reply.type = ReplyType.IMAGE_URL
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return

        msg: ChatMessage = e_context["context"]["msg"]
        content = e_context["context"].content
        room_id = msg.other_user_id

        logger.debug("[idiom] on_handle_context. content: %s" % content)
        if content == "看图猜成语":
            Thread(target=self.start_guess_idiom_image, name="看图猜成语", args=(e_context,)).start()
            reply = Reply()
            reply.type = ReplyType.TEXT
            #reply.content = f"看图猜成语开始"
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑
        elif content == "退出游戏":
            self.game_mode_rooms[room_id] = False
            self.send_text_reply(e_context,f'游戏已中止！')
        elif content == "重发":
            if  self.game_mode_rooms.get(room_id, False):
                self.send_image_reply(e_context,self.idiom_pic[room_id])
        elif self.game_mode_rooms.get(room_id, False):
            self.gaming_function(e_context)



    def start_guess_idiom_image(self, e_context: EventContext):
        msg: ChatMessage = e_context["context"]["msg"]
        content = e_context["context"].content
        room_id = msg.other_user_id
        nick_name = msg.from_user_nickname
        message = (
            "🎉 **看图猜成语游戏开始** 🎉\n"
            "游戏规则如下：\n"
            "1. 总共进行五轮成语猜测。\n"
            "2. 如果要提前中止游戏，请回复 “退出游戏”。\n"
            "3. 如果未成功收到图片，请回复 “重发”。\n"
            "祝您玩得愉快！😊"
        )
        _send_info(e_context,message)
        time.sleep(0.2)
        self.game_mode_rooms[room_id] = True
        for i in range(5):
            if not self.game_mode_rooms.get(room_id):
                break
            save_path, idiom_data,url = self.get_idiom()
            self.idiom_pic[room_id] = url
            self.game_answer[room_id] = idiom_data
            #url_parts = list(urlsplit(url))
            #url_parts[2] =quote(url_parts[2])
            #encode_url = urlunsplit(url_parts)
            _send_info(e_context,url,ReplyType.IMAGE_URL)
            _send_info(e_context,f'第{i + 1}轮题目：请在六十秒内回答，否则将跳过此题')
            cur_time = time.time()
            while time.time() - cur_time < 63:
                if not self.game_mode_rooms.get(room_id, False):
                    return
                if self.game_success.get(room_id, False):
                    break
                time.sleep(1)
            if not self.game_mode_rooms.get(room_id, False):
                return
            if self.game_success.get(room_id, False):
                self.game_success[room_id] = False
                _send_info(e_context,content='回答正确！')
            else:
                _send_info(e_context,content='没有人回答正确！')
            answer = f"答案: {idiom_data['答案']}\n" \
                     f"拼音: {idiom_data['拼音']}\n" \
                     f"解释: {idiom_data['解释']}\n" \
                     f"出处: {idiom_data['出处']}\n" \
                     f"例句: {idiom_data['例句']}"
            _send_info(e_context,content=answer)
            time.sleep(0.5)
        msg_over = ["游戏结束！"]
        if room_id in self.game_point:
            for nick_name, point in self.game_point[room_id].items():
                msg_over.append(f"{nick_name}：{point} 分")
        _send_info(e_context,content='\n'.join(msg_over))

        # 清空游戏数据
        self.game_mode_rooms[room_id] = False
        self.game_point[room_id] = {}
        self.game_answer[room_id] = None
        self.idiom_pic[room_id] = None
        self.game_success[room_id] = False
    def gaming_function(self,  e_context: EventContext):
        msg: ChatMessage = e_context["context"]["msg"]
        content = e_context["context"].content
        room_id = msg.other_user_id
        nick_name= msg.from_user_nickname
        try:
            with self.counter_lock:
                if self.game_success.get(room_id, False):
                    return
                if content == self.game_answer[room_id].get('答案', ''):
                    self.game_success[room_id] = True
                    self.game_answer[room_id] = None

                    self.send_text_reply(e_context,f'恭喜答对了！')
                    if room_id in self.game_point.keys():
                        if nick_name in self.game_point[room_id].keys():
                            self.game_point[room_id][nick_name] += 1
                        else:
                            self.game_point[room_id][nick_name] = 1
                    else:
                        self.game_point[room_id] = {nick_name: 1}
                else:
                    e_context.action=EventAction.BREAK_PASS
        except Exception as e:
            print(e)
    def get_idiom(self):
        logger.info('[*]: 正在调用看图猜成语API接口... ...')
        idiom_data = self.get_idiom_data()
        curdir = os.path.dirname(__file__)
        save_path = os.path.join(curdir, 'Pic_Cache', str(int(time.time() * 1000)) + '.jpg')
        try:
            url = idiom_data['图片链接']
            pic_data = requests.get(url=url, headers=self.headers, timeout=30, verify=False).content
            with open(file=save_path, mode='wb') as pd:
                pd.write(pic_data)
        except Exception as e:
            msg = f'[-]: 看图猜成语接口出现错误，错误信息：{e}，回调中... ...'
            logger.info(msg)
            time.sleep(0.2)
            return self.get_idiom()
        logger.info(f'[+]: 看图猜成语接口调用成功！！！')
        print(idiom_data)
        return save_path, idiom_data,url
    def get_idiom_data(self):
        url = "https://api.andeer.top/API/guess_idiom_img.php"
        try:
            json_data = requests.get(url=url, headers=self.headers, timeout=30, verify=False).json()
            if json_data['code'] != 200:
                return None
            data = json_data['data']
            return data
        except Exception as e:
            logger.info(e)
            return None

def _send_info(e_context: EventContext, content: str,type:ReplyType=ReplyType.TEXT):
    reply = Reply(type, content)
    channel = e_context["channel"]
    channel.send(reply, e_context["context"])
