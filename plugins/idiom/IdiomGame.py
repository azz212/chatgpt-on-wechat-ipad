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


class IdiomGame:
    def __init__(self):
        self.game_running = False
        self.current_round = 0
        self.total_rounds = 5
        self.players_scores = {}

    def is_game_running(self):
        return self.game_running

    def start_game(self, group_name):
        self.game_running = True
        self.current_round = 1
        self.players_scores = {}
        # 初始化游戏，发送第一轮图片和问题

    def process_answer(self, msg, answer):
        # 检查答案是否正确，并更新分数
        score = 0
        if answer == self.get_current_answer():  # 假设这是获取当前正确答案的方法
            score = 10  # 假设每题10分
        self.players_scores[msg.from_user_nickname] = self.players_scores.get(msg.from_user_nickname, 0) + score
        return score

    def get_current_answer(self):
        # 返回当前题目的正确答案
        pass

    def send_reply(self, e_context, reply_content):
        reply = Reply()
        reply.type = ReplyType.TEXT
        #reply.content = reply_content
        reply.content = (
            f'看图猜成语游戏开始，总共五轮！\n'
            f'如果要提前中止游戏，\n'
            f'请回复“退出游戏”。\n'
            f'如果未成功收到图片，\n'
            f'请回复“重发”。'
        )
        e_context["reply"] = reply
        e_context.action = EventAction.BREAK_PASS  # 事件结束，并跳过处理context的默认逻辑

    def end_game(self):
        self.game_running = False
        # 发送游戏结束消息和最终得分

    def is_time_for_new_round(self):
        # 检查是否到了开始新轮的时间
        pass
