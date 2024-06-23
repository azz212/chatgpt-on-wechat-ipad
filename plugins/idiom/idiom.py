# encoding:utf-8
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
from threading import Thread

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
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            self.handlers[Event.ON_RECEIVE_MESSAGE] = self.on_receive_message

        except Exception as e:
            logger.error(f"[idiom]初始化异常：{e}")
            raise "[idiom] init failed, ignore "
        # 游戏模式
        self.game_mode_rooms = {}
        self.game_point = {}
        self.game_answer = {}
        self.game_success = {}
        self.idiom_pic = {}
    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT,
        ]:
            return
        msg: ChatMessage = e_context["context"]["msg"]

        group_name = msg.from_user_nickname

        content = e_context["context"].content
        logger.debug("[idiom] on_handle_context. content: %s" % content)
        if  "看图猜成语" == content :
            Thread(target=self.start_guess_idiom_image, name="看图猜成语", args=(e_context,)).start()

    def on_receive_message(self, e_context: EventContext):
        if e_context['context']['msg'].ctype!=ContextType.TEXT:
            return
        context = e_context['context']
        cmsg : ChatMessage = e_context['context']['msg']
        content = e_context["context"].content
        if "看图猜成语" == content:
            username = None
            room_id=cmsg.other_user_id
            session_id = cmsg.from_user_id
            user_id =cmsg.from_user_id
            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = (
                f'看图猜成语游戏开始，总共五轮！\n'
                f'如果要提前中止游戏，\n'
                f'请回复“退出游戏”。\n'
                f'如果未成功收到图片，\n'
                f'请回复“重发”。'
            )
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def start_guess_idiom_image(self, e_context: EventContext):
        msg: ChatMessage = e_context["context"]["msg"]
        reply = Reply()
        reply.type = ReplyType.TEXT

        reply.content = (
            f'看图猜成语游戏开始，总共五轮！\n'
            f'如果要提前中止游戏，\n'
            f'请回复“退出游戏”。\n'
            f'如果未成功收到图片，\n'
            f'请回复“重发”。'
        )
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

        self.game_mode_rooms[msg.other_user_id] = True
        for i in range(5):
            if not self.game_mode_rooms.get(msg.other_user_id):
                break
            save_path, idiom_data = self.get_idiom()
            self.idiom_pic[msg.other_user_id] = save_path
            self.game_answer[msg.other_user_id] = idiom_data
            self.wcf.send_image(path=save_path, receiver=msg.other_user_id)
            self.wcf.send_text(msg=f'第{i + 1}轮题目：', receiver=msg.other_user_id)
            self.wcf.send_text(msg='请在六十秒内回答，否则将跳过此题', receiver=msg.other_user_id)
            cur_time = time.time()
            while time.time() - cur_time < 63:
                if not self.game_mode_rooms.get(msg.other_user_id, False):
                    return
                if self.game_success.get(msg.other_user_id, False):
                    break
                time.sleep(1)
            if not self.game_mode_rooms.get(msg.other_user_id, False):
                return
            if self.game_success.get(msg.other_user_id, False):
                self.game_success[msg.other_user_id] = False
                self.wcf.send_text(msg='回答正确！', receiver=msg.other_user_id)
            else:
                self.wcf.send_text(msg='没有人回答正确！', receiver=msg.other_user_id)
            answer = f"答案: {idiom_data['答案']}\n" \
                     f"拼音: {idiom_data['拼音']}\n" \
                     f"解释: {idiom_data['解释']}\n" \
                     f"出处: {idiom_data['出处']}\n" \
                     f"例句: {idiom_data['例句']}"
            self.wcf.send_text(msg=answer, receiver=msg.other_user_id)
            time.sleep(0.5)
        msg_over = ["游戏结束！"]
        for wx_name, point in self.game_point[msg.other_user_id].items():
            msg_over.append(f"{wx_name}：{point} 分")
        self.wcf.send_text(msg='\n'.join(msg_over), receiver=msg.other_user_id)

        # 清空游戏数据
        self.game_mode_rooms[msg.other_user_id] = False
        self.game_point[msg.other_user_id] = {}
        self.game_answer[msg.other_user_id] = None
        self.idiom_pic[msg.other_user_id] = None
        self.game_success[msg.other_user_id] = False


    def get_idiom_data(self):
        url = "https://api.andeer.top/API/guess_idiom_img.php"
        try:
            json_data = requests.get(url=url, headers=self.headers, timeout=30, verify=False).json()
            if json_data['code'] != 200:
                return None
            data = json_data['data']
            return data
        except Exception as e:
            return None

    # 看图猜成语
    def get_idiom(self):
        logger.info('[*]: 正在调用看图猜成语API接口... ...')
        idiom_data = self.get_idiom_data()
        save_path = self.Cache_path + '/pic/' + str(int(time.time() * 1000)) + '.jpg'
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
        return save_path, idiom_data

    def get_help_text(self, **kwargs):
        help_text = "输入idiom，我会回复你的名字\n输入End，我会回复你世界的图片\n"
        return help_text

    def _load_config_template(self):
        logger.debug("No idiom plugin zhao_config.json, use plugins/idiom/zhao_config.json.template")
        try:
            plugin_config_path = os.path.join(self.path, "config.json.template")
            if os.path.exists(plugin_config_path):
                with open(plugin_config_path, "r", encoding="utf-8") as f:
                    plugin_conf = json.load(f)
                    return plugin_conf
        except Exception as e:
            logger.exception(e)