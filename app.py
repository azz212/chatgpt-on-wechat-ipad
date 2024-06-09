# encoding:utf-8

import os
import signal
import sys
import time

from channel import channel_factory
from common import const
from config import load_config
from plugins import *
import threading
from quart import Quart, request, jsonify,render_template,send_file

quart_app = Quart(__name__)


def sigterm_handler_wrap(_signo):
    old_handler = signal.getsignal(_signo)

    def func(_signo, _stack_frame):
        logger.info("signal {} received, exiting...".format(_signo))
        conf().save_user_datas()
        if callable(old_handler):  #  check old_handler
            return old_handler(_signo, _stack_frame)
        sys.exit(0)

    signal.signal(_signo, func)


def start_channel(channel_name: str):
    channel = channel_factory.create_channel(channel_name)
    if channel_name in ["wx", "wxy", "terminal", "wechatmp", "wechatmp_service", "wechatcom_app", "wework",
                        const.FEISHU, const.DINGTALK]:
        PluginManager().load_plugins()

    if conf().get("use_linkai"):
        try:
            from common import linkai_client
            threading.Thread(target=linkai_client.start, args=(channel,)).start()
        except Exception as e:
            pass
    channel.startup()


def run():
    try:
        # load config
        load_config()
        # ctrl + c
        sigterm_handler_wrap(signal.SIGINT)
        # kill signal
        sigterm_handler_wrap(signal.SIGTERM)

        # create channel
        channel_name = conf().get("channel_type", "wx")

        if "--cmd" in sys.argv:
            channel_name = "terminal"

        if channel_name == "wxy":
            os.environ["WECHATY_LOG"] = "warn"

        start_channel(channel_name)

        while True:
            time.sleep(1)
    except Exception as e:
        logger.error("App startup failed!")
        logger.exception(e)


if __name__ == "__main__":
    '''
    todo 1 将web框架修改为flask 或者Quart OK
    todo 2 接收图片时判断是否为空，如果为空，则发送提醒 OK
    todo 3 发送超过1024时，要分段发送
    todo 4 画图时，结果可以at 并显示提示词。yes
    todo 5 画图时，先发送一个等待消息，提示正在处理中 NA
    todo 6 help和菜单功能
    todo 7 多个API接入点，如何切换和检查错误，主动屏蔽经常不可用服务器 。 功能和模型对应
    todo 8 部署到香港服务器
    
    '''
    run()
