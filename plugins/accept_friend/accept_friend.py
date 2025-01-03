# encoding:utf-8
import time

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from config import conf
from config import load_config,save_config
from plugins import *
import xml.etree.ElementTree as ET
from channel.wechat.iPadWx import iPadWx
import random
from bridge.context import ContextType,  Context
from channel.chat_message import ChatMessage

config = conf()
channel_name = conf().get("channel_type", "wx")
if channel_name == "wx":
    from channel.wechat.iPadWx import iPadWx
elif channel_name=='wx-beta':
    from channel.wechat.iPadWx_Beta import iPadWx
@plugins.register(
    name="accept_friend",
    desire_priority=100,
    hidden=True,
    desc="自动通过好友，并打招呼！",
    version="1.0",
    author="js00000",
)
class Accept_Friend(Plugin):
    def __init__(self):
        super().__init__()
        try:
            # 首先设置插件路径
            self.path = os.path.dirname(os.path.abspath(__file__))
            self.curdir = self.path  # 同时更新 curdir

            self.conf = self.load_config()
            # 加载关键词
            self.auto_reply = self.conf['是否发送消息']['value']
            self.auto_reply_active = self.conf['主动发送消息']['value']
            self.curdir = os.path.dirname(__file__)
            self.reply_content = self.conf['回复文字']['value']
            self.agree_delay = int(self.conf['同意好友延迟时间']['value'])
            self.save_whitelist=False
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            self.handlers[Event.ON_CONFIG_CHANGED] = self.on_config_change
            logger.info("[Accept_Friend] inited.")
        except Exception as e:
            logger.warn(
                "[Accept_Friend] init failed, ignore or see https://github.com/zhayujie/chatgpt-on-wechat/tree/master/plugins/Accept_Friend .")
            raise e

        self.bot = iPadWx()

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.ADD_FRIEND and e_context["context"].type != ContextType.TEXT :
            return

        context = e_context["context"]
        if context.type == ContextType.ADD_FRIEND:
            self.handle_add_friend(context, e_context)
        #处理主动加好友，通过时第一时间发消息给对方
        content = context.content
        cmsg: ChatMessage = context['msg']
        fromusername = cmsg.from_user_id
        if context.type == ContextType.TEXT and content=="我通过了你的朋友验证请求，现在我们可以开始聊天了" \
                and not cmsg.is_group and not cmsg.my_msg:
            if self.auto_reply_active:
                # 再随机延时5-10秒发送打招呼语
                delay = random.randint(5, 10)
                time.sleep(delay)

                # 发送打招呼语，包括文字、图片��视频和小程序
                self.send_greeting_message(fromusername, cmsg.to_user_id,e_context)
                e_context.action = EventAction.BREAK_PASS  # 不再处理该事件

    def handle_add_friend(self, context: Context, e_context: EventContext):
        content = context.content
        cmsg: ChatMessage = context['msg']
        logger.debug("[自动加好友客服] Handling friend request. Content: %s" % content)
        # 解析 XML
        xml_data = content
        root = ET.fromstring(xml_data)

        # 获取 scene 和 ticket
        scene = root.get('scene')
        ticket = root.get('ticket')
        v3 = root.get('encryptusername')
        fromnickname = root.get('fromnickname')
        fromusername = root.get('fromusername')
        friend_content  = root.get('content')
        alias = root.get('alias')
        sex = root.get('sex')
        bigheadimgurl = root.get('bigheadimgurl')
        smallheadimgurl = root.get('smallheadimgurl')
        logger.info(f"scene: {scene}, ticket: {ticket}, fromusername: {fromusername}")
        #将好友保存到联系人中
        if  channel_name =='wx':
            if fromusername not in iPadWx.shared_wx_contact_list:
                iPadWx.shared_wx_contact_list[fromusername] = {
                    'nickName': fromnickname,
                    'userName': fromusername,
                    'weixin': alias,
                    'sex': sex,
                    'bigHead': bigheadimgurl,
                    'smallHead': smallheadimgurl,
                    "remark": ""

                }
            else:
                logger.info(f"用户{fromusername}已存在")
        elif channel_name == 'wx-beta':
            if fromusername not in iPadWx.shared_wx_contact_list:
                iPadWx.shared_wx_contact_list[fromusername] = {
                    'nickName': fromnickname,
                    'userName': fromusername,
                    'alias': alias,
                    'sex': sex,
                    'bigHeadImgUrl': bigheadimgurl,
                    'smallHeadImgUrl': smallheadimgurl,
                    "remark":""

                }
        self.bot.save_contact()
        if self.save_whitelist:
            self.save_default_whitelist(fromusername,fromnickname)


        # 随机延时5-15秒再同意
        delay = random.randint(self.agree_delay, self.agree_delay+10)

        logger.info(f"[自动加好友客服] Delaying friend acceptance by {delay} seconds.")
        time.sleep(delay)
        if channel_name=='wx':
            self.bot.agree_friend(scene, ticket, fromusername)
        else:
            option=3
            self.bot.agree_friend( scene, option, v3, ticket, friend_content)

        logger.info(f"[自动加好友客服] Accepted friend request from {fromusername}.")
        if  self.auto_reply:
            # 再随机延时5-10秒发送打招呼语
            delay = random.randint(5, 10)
            time.sleep(delay)

            # 发送打招呼语，包括文字、图片、视频和小程序
            e_context["context"]["receiver"]= fromusername
            self.send_greeting_message(fromusername,cmsg.to_user_id,e_context)

        e_context.action = EventAction.BREAK_PASS  # 不再处理该事件
    def send_greeting_message(self, to_user,sender_id,e_context):



        # 发送文字地址
        if  self.reply_content:
            self.bot.send_txt_msg(to_user, self.reply_content)
            logger.info(f"[自动加好友客服] Sent address text to {to_user}.")
            time.sleep(2)

        # 发送图片
        image_paths = self.conf.get('回复图片')['value']
        if isinstance(image_paths,str):
            image_path=image_paths
            if image_path.endswith(".xml"):
                image_content = open(os.path.join(self.curdir ,image_path),'r', encoding='utf-8').read()
                self.bot.forward_img(to_user, image_content)
                logger.info(f"[自动加好友客服] Sent image to {to_user}.")
            elif image_path.endswith(".png") or image_path.endswith(".jpg"):
                #image_url = self.bot.upload_pic(image_path, "")['url']
                #self.bot.send_image_url(to_user, image_url)
                logger.info(f"[自动加好友客服] Sent image to {to_user}.")
                reply_text = get_image_url(image_path)
                # reply = Reply()
                _send_info(e_context, reply_text, ReplyType.IMAGE_URL)
            else:
                logger.info(f"[自动加好友客服] image not exist.")

            time.sleep(2)
        else:
            if isinstance(image_paths,list):
                for image_path in image_paths:
                    if image_path.endswith(".xml"):
                        image_content = open(os.path.join(self.curdir, image_path), 'r', encoding='utf-8').read()
                        self.bot.forward_img(to_user, image_content)
                        logger.info(f"[自动加好友客服] Sent image to {to_user}.")
                    elif image_path.endswith(".png") or image_path.endswith(".jpg"):
                        #image_url = self.bot.upload_pic(image_path, "")['url']
                        #self.bot.send_image_url(to_user, image_url)
                        logger.info(f"[自动加好友客服] Sent image to {to_user}.")
                        reply_text = get_image_url(image_path)
                        # reply = Reply()
                        _send_info(e_context, reply_text, ReplyType.IMAGE_URL)
                    else:
                        logger.info(f"[自动加好友客服] image not exist.")

                    time.sleep(2)


        # 发送导航视频
        video_path = self.conf.get('回复视频')['value']
        if video_path.endswith(".xml"):
            video_content = open(os.path.join(self.curdir ,video_path), 'r', encoding='utf-8').read()
            self.bot.forward_video(to_user, video_content)
            logger.info(f"[自动加好友客服] Sent video to {to_user}.")
        else:
            logger.info(f"[自动加好友客服] video not support {to_user}.")

        time.sleep(2)

        # 发送位置链接
        link_data = self.conf.get('回复链接')['value']
        url = "https://ditu.amap.com/search?id=B0IAJMRL30&amp;city=440114&amp;geoobj=104.045896%7C30.644358%7C104.050948%7C30.646878&amp;query_type=IDQ&amp;query=%E5%87%A4%E5%87%B0%E5%9B%BD%E9%99%85%E5%95%86%E5%8A%A1%E4%B8%AD%E5%BF%83&amp;zoom=17.5"
        pic_url = "https://www.suban88.com/uploads/allimg/20220612/1-220612140450G4.jpg"
        # pic_url=""
        title = "搜索 - 高德地图"
        desc = "https://ditu.amap.com/search?id=B0IAJMRL30&amp;city=440114&amp;geoobj=104.045896%7C30.644358%7C104.050948%7C30.646878&amp;query_type=IDQ&amp;query=%E5%87%A4%E5%87%B0%E5%9B%BD%E9%99%85%E5%95%86%E5%8A%A1%E4%B8%AD%E5%BF%83&amp;zoom=17.5"
        # self.bot.send_card(to_user,title,url,desc,pic_url)
        if link_data.endswith(".xml"):
            link_content = open(os.path.join(self.curdir, link_data), 'r', encoding='utf-8').read()
            # mini_program_content = self.replace_mini_program(mini_program_content, sender_id)
            self.bot.send_mini_program(to_user, link_content)
            logger.info(f"[自动加好友客服] Sent 位置信息 to {to_user}.")
        else:
            logger.info(f"[自动加好友客服] 位置信息  not support {to_user}.")


        time.sleep(2)
        # 发送小程序
        mini_program_data = self.conf.get('回复小程序')['value']
        if mini_program_data.endswith(".xml"):
            mini_program_content = open(os.path.join(self.curdir, mini_program_data), 'r', encoding='utf-8').read()
            # mini_program_content = self.replace_mini_program(mini_program_content, sender_id)
            self.bot.send_mini_program(to_user, mini_program_content)
            logger.info(f"[自动加好友客服] Sent mini program to {to_user}.")

    def save_default_whitelist(self,wxid, nickname):
        # 保存默认白名单
        private_ids=config.get("private_id_white_list")
        private_names = config.get("private_name_white_list")
        if wxid not in private_ids:
            private_ids.append(wxid)
        if nickname not in private_names:
            private_names.append(nickname)
        config.__setitem__("private_id_white_list", private_ids)
        config.__setitem__("private_name_white_list", private_names)
        save_config()

    def on_config_change(self, e_context: EventContext):
        """处理配置变更事件"""
        if e_context["plugin_name"] == "accept_friend":
            # 重新加载配置
            # 首先设置插件路径
            self.path = os.path.dirname(os.path.abspath(__file__))
            self.curdir = self.path  # 同时更新 curdir
            self.conf = super().load_config()
            # 更新相关配置项
            self.auto_reply = self.conf['是否发送消息']['value']
            self.auto_reply_active = self.conf['主动发送消息']['value']
            self.reply_content = self.conf['回复文字']['value']
            self.agree_delay = int(self.conf['同意好友延迟时间']['value'])
            logger.info("[Accept_Friend] config updated.")

    def get_help_text(self, **kwargs):
        return "自动通过好友，并且自动打招呼"
def _send_info(e_context: EventContext, content: str,type:ReplyType=ReplyType.TEXT):
    reply = Reply(type, content)
    channel = e_context["channel"]
    channel.send(reply, e_context["context"])
def get_image_url1(image_name):
    http_addr = conf().get("http_hook")

    parts = http_addr.split("/")
    result = "/".join(parts[:-1])

    result = f"{result}/pic//{image_name}"
    logger.info(f"要发送的图片 {result}")
    return result
def get_image_url(image_name):
    if channel_name == "wx":
        http_addr = conf().get("http_hook")
    elif channel_name == 'wx-beta':
        http_addr = conf().get("http_hook_ipad")
    else:
        http_addr = conf().get("http_hook")
    parts = http_addr.split("/")
    result = "/".join(parts[:-1])

    result = f"{result}/pic/{image_name}"
    logger.info(f"要发送的图片 {result}")
    return result