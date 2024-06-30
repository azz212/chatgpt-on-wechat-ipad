import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger


@plugins.register(name="jdjcj",
                  desc="发送【积存金】获取当前京东积存金价格",
                  version="1.0",
                  author="jasper",
                  desire_priority=100)
class jdjcj(Plugin):

    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")

    def get_help_text(self, **kwargs):
        help_text = f"发送【积存金】获取当前京东积存金价格"
        return help_text

    def on_handle_context(self, e_context: EventContext):
        if e_context['context'].type != ContextType.TEXT:
            return
        self.content = e_context["context"].content.strip()

        if self.content.lower() == "积存金":
            logger.info(f"[{__class__.__name__}] 收到消息: {self.content}")
            reply = Reply()

            result = self.jdjr_jcj()
            if result is not None:
                reply.type = ReplyType.TEXT
                reply.content = f"当前价格：{result}"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS
            else:
                reply.type = ReplyType.ERROR
                reply.content = "获取失败,等待修复⌛️"
                e_context["reply"] = reply
                e_context.action = EventAction.BREAK_PASS

    def jdjr_jcj(self):
        s = requests.session()
        # client_id 为官网获取的AK， client_secret 为官网获取的SK
        url = 'https://api.jdjygold.com/gw/generic/hj/h5/m/latestPrice'
        header = {
            "Host": "api.jdjygold.com",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; ELS-AN00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.18 Mobile Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://m.jdjygold.com",
            "Referer": "https://m.jdjygold.com/finance-gold/newgold/index/?jrcontainer=h5",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            # "Cookie": "qd_uid=KM24GD8A-UZDK27G1GDEYYUG8V0Y7;  ",
        }
        data = {}
        ret_json = self.basic_jd_req(s, url, data)
        if ret_json != None:
            try:
                if ret_json['resultCode'] == 0:
                    price = ret_json['resultData']['datas']['price']
                    yesterdayPrice = ret_json['resultData']['datas']['yesterdayPrice']
                    # logger.info('当前价格{0}'.format(price))
                    return price
                else:
                    logger.info('获取价格失败2!')
                    return 0
            except Exception as e:
                logger.info('获取价格失败!')
                logger.info(e)
                return 0
        return 0

    def basic_jd_req(self,s, url, data):
        # data = {'reqData': '{"productSku":"21001001000001"}'}

        header = {
            "Host": "api.jdjygold.com",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; ELS-AN00) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.18 Mobile Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "Origin": "https://m.jdjygold.com",
            "Referer": "https://m.jdjygold.com/finance-gold/newgold/index/?jrcontainer=h5",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7",
            # "Cookie": "qd_uid=KM24GD8A-UZDK27G1GDEYYUG8V0Y7;  ",
        }

        try:
            response = s.post(url, headers=header, data=data, proxies=None, verify=False, timeout=3)
        except Exception as e:
            print(e)
            print('发生错误')
            return None
        ret_json = None
        if response:
            try:
                ret_json = response.json()
            except Exception as e:
                print('请求失败')
                print(e)
        return ret_json


if __name__ == "__main__":
    jd = jcj()
    result = jd.jdjr_jcj()
    if result:
        print("获取到的文案内容：", result)
    else:
        print("获取失败")
