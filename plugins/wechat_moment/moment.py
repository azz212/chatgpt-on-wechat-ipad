import random

import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from channel.wechat.iPadWx import iPadWx


@plugins.register(name="moment",
                  desc="随机发朋友圈，图片和文字来源自于网上",
                  version="1.0",
                  author="Cool",
                  desire_priority=100)
class moment(Plugin):


    def __init__(self):
        super().__init__()

        try:
            self.config = super().load_config()
            if not self.config:
                self.config = self._load_config_template()
            self.base_url = self.config.get("base_url", {})
            self.token =  self.config.get("token", {})
            logger.info("[moment] inited")
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        except Exception as e:
            logger.error(f"[moment]初始化异常：{e}")
            raise "[moment] init failed, ignore "
        self.bot = iPadWx()
    def get_help_text(self, **kwargs):
        help_text = f"随机发朋友圈，图片和文字来源自于网上"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()

        if self.content.lower() == "发朋友圈":
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()
            url = self.base_url +"/randomimg"
            url1 = self.get_img(url)
            url2 = self.get_img(url)
            text = self.get_data(url = self.base_url +"/aword")
            urls =";".join([url1,url2])

            result = self.bot.moment_friends(text, urls)
            if result is not None:
                reply.type = ReplyType.TEXT
                reply.content = "朋友圈发送成功！"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "朋友圈发送失败！"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def get_img(self,url):
        #url = BASE_URL_DM
        params = {"type": "json"}
        headers = {'Content-Type': "application/json",

                   }
        data = {
                   "token": self.token,
                   "client": "android",
                   "mode": "json",
                   "type": random.choice(["ALL", "MN", "SG", "DM", "FJ", "MX", "WZRY"])
                   }
        try:
            response = requests.get(url=url, params=data, headers=headers, timeout=2, verify=False)
            if response.status_code == 200:
                json_data = response.json()
                logger.info(f"接口返回的数据：{json_data}")
                if json_data.get('code') == 200 and json_data.get('data'):
                    imageurl = json_data['data']['imageurl']
                    logger.info(f"主接口获取成功：{imageurl}")
                    return imageurl
                else:
                    logger.error(f"主接口返回值异常:{json_data}")
                    raise ValueError('not found')
            else:
                logger.error(f"主接口请求失败:{response.text}")
                raise Exception('request failed')
        except Exception as e:
            logger.error(f"接口异常：{e}")
        logger.error("所有接口都挂了,无法获取")
        return None

    def get_data(self,url):
        #url = BASE_URL_DM
        '''
        all(随机)、aword(一言)、aiqing(爱情)、badlanguage(口吐芬芳)、enandch(英汉)、gushi(故事)、mingyan(名言警句)、qinghua(情话)、shanggan(伤感)、tiangou(舔狗日记)、xiaohua(笑话)、yulu(语录)、zheli(哲理)
        '''
        headers = {'Content-Type': "application/json",

                   }
        params = {
                   "token":self.token,
                   "mode":"json",
                   "type":"all"
                   }
        try:
            response = requests.get(url=url, params=params, headers=headers, timeout=2, verify=False)
            if response.status_code == 200:
                json_data = response.json()
                logger.info(f"接口返回的数据：{json_data}")
                if json_data.get('code') == 200 and json_data.get('data'):
                    msg = json_data['data']['content']
                    logger.info(f"主接口获取成功：{msg}")
                    return msg
                else:
                    logger.error(f"主接口返回值异常:{json_data}")
                    raise ValueError('not found')
            else:
                logger.error(f"主接口请求失败:{response.text}")
                raise Exception('request failed')
        except Exception as e:
            logger.error(f"接口异常：{e}")
        logger.error("所有接口都挂了,无法获取")
        return None

if __name__ == "__main__":
    kfc_wenan_plugin = moment()
    result = kfc_wenan_plugin.KFCwenan()
    if result:
        print("获取到的文案内容：", result)
    else:
        print("获取失败")
