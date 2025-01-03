'''
Author: sineom h.sineom@gmail.com
Date: 2024-11-11 14:17:56
LastEditors: sineom h.sineom@gmail.com
LastEditTime: 2024-11-14 10:33:56
FilePath: /anti_withdrawal/revocation.py
Description: 防止撤回消息

Copyright (c) 2024 by sineom, All Rights Reserved.
'''
from bridge.context import ContextType
from channel.chat_message import ChatMessage
import plugins
import json
import os
import re
from threading import Timer
import time
from plugins import *
from common.log import logger
from channel.wechat.iPadWx import iPadWx
import xml.etree.ElementTree as ET
import datetime

@plugins.register(
    name="prevent_revoke",
    desire_priority=-1,
    namecn="防止撤回",
    desc="防止微信消息撤回插件",
    version="1.2",
    author="sineom",
)
class prevent_revoke(Plugin):
    def __init__(self):
        super().__init__()
        # 首先设置插件路径
        self.path = os.path.dirname(os.path.abspath(__file__))
        self.curdir = self.path  # 同时更新 curdir
        self.config = self.load_config()
        # 初始化 iPadWx 实例
        self.bot = iPadWx()
        self.load_config_again()
            
        self.handlers[Event.ON_RECEIVE_MESSAGE] = self.on_receive_message
        self.handlers[Event.ON_CONFIG_CHANGED] = self.on_config_changed
        logger.info("[PreventRevoke] initialized")
        
        # 初始消息存储
        self.msg_dict = {}
        
        # 初始化配置
        self.load_config()
        

        self.filehelper = "filehelper"

    def load_config_again(self):
        """加载配置"""
        self.monitor_groups = set(self.config.get("monitor_groups", {}).get("value", []))
        self.monitor_groups_id = self.get_chatroom_id()
        self.private_switch = self.config.get("private_switch", {}).get("value", False)
        self.group_switch = self.config.get("group_switch", {}).get("value", True)
        self.forward_private = self.config.get("forward_private", {}).get("value", [])
        self.pre_text = self.config.get("pre_text", {}).get("value", True)
        self.pre_pic = self.config.get("pre_pic", {}).get("value", True)
        self.pre_video = self.config.get("pre_video", {}).get("value", True)
        self.pre_voice = self.config.get("pre_voice", {}).get("value", True)
        self.pre_file = self.config.get("pre_file", {}).get("value", False)

    def on_config_changed(self, e_context: EventContext):
        """配置发生变更"""
        self.config = super().load_config()
        self.load_config_again()
        logger.info("[PreventRevoke] config changed")

    def clean_expired_messages(self):
        """清理超过3分钟的消息"""
        current_time = int(time.time())
        for uuid in list(self.msg_dict.keys()):
            create_time_str = self.msg_dict[uuid].create_time
            create_time = datetime.datetime.strptime(create_time_str, "%Y-%m-%d %H:%M:%S").timestamp()
            if (current_time - create_time) > 180:  # 3分钟
                self.msg_dict.pop(uuid)

    def handle_revoke(self, msg, is_group=False):
        """处理撤回消息"""
        try:
            root = ET.fromstring(msg.content)
            revoke_msg = root.find('revokemsg')
            if revoke_msg is None:
                return
                
            original_msg_id = revoke_msg.find('newmsgid').text
            if original_msg_id not in self.msg_dict:
                return

            old_msg = self.msg_dict[original_msg_id]
            
            # 确定发送目标
            if is_group:
                target_id = msg.other_user_id
            else:
                # 私聊消息转发给指定的群
                if self.forward_private:
                    target_id = self.forward_private[0]  # 使用第一个转发目标
                else:
                    target_id = self.filehelper
            
            # 构建撤回提示
            prefix = f"群：【{msg.other_user_nickname}】的【{msg.actual_user_nickname}】" if is_group else f"【{msg.from_user_nickname}】"
            
            try:
                # 根据消息类型和开关处理
                if old_msg.ctype == ContextType.TEXT and self.pre_text:
                    text = f"{prefix}撤回了消息：{old_msg.content}"
                    self.bot.send_message(target_id, text)
                
                elif old_msg.ctype == ContextType.IMAGE and self.pre_pic:
                    text = f"{prefix}撤回了一张图片"
                    self.bot.send_message(target_id, text)
                    time.sleep(1)
                    self.bot.forward_img(target_id, old_msg.content)
                    
                elif old_msg.ctype == ContextType.VIDEO and self.pre_video:
                    text = f"{prefix}撤回了一个视频"
                    self.bot.send_message(target_id, text)
                    time.sleep(1)
                    self.bot.forward_video(target_id, old_msg.content)
                    
                elif old_msg.ctype == ContextType.VOICE and self.pre_voice:
                    text = f"{prefix}撤回了一条语音"
                    self.bot.send_message(target_id, text)
                    time.sleep(1)
                    xml_data = old_msg.content
                    root2 = ET.fromstring(xml_data)
                    voicemsg = root2.find('voicemsg')
                    msg_id = old_msg.msg_id
                    uuid = old_msg._rawmsg.get("uuid")
                    if voicemsg is not None:
                        clientmsgid = voicemsg.get('clientmsgid')
                        voicelength = voicemsg.get('voicelength')
                        length = voicemsg.get('length')
                        ret = self.bot.forward_voice(target_id, uuid, msg_id, clientmsgid, voicelength, length)
                        logger.info(f"转发语音消息成功{ret}")


                    
                elif old_msg.ctype == ContextType.FILE and self.pre_file:
                    text = f"{prefix}撤回了一个文件"
                    self.bot.send_message(target_id, text)
                    time.sleep(1)
                    title, totallen, attachid, cdnattachurl, aeskey, filekey, md5, file_extension = self.extract_file_xml(
                        old_msg.content)
                    if attachid and aeskey and filekey:
                        self.bot.forward_file(target_id, title, totallen, attachid, cdnattachurl, aeskey, filekey, md5,
                                              file_extension)

            except Exception as e:
                logger.error(f"Failed to forward message: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to handle revoke message: {e}")

    def handle_msg(self, msg, is_group=False):
        """处理消息"""
        # 检查开关状态
        if is_group and not self.group_switch:
            return
        if not is_group and not self.private_switch:
            return

        # 检查是否是监控的群
        if is_group and msg.other_user_id not in self.monitor_groups_id:
            return

        try:
            # 清理过期消息
            self.clean_expired_messages()
            
            if msg.ctype == ContextType.REVOKE_MESSAGE:
                self.handle_revoke(msg, is_group)
                return

            # 处理不同类型的消息
            if msg.ctype in [ContextType.TEXT, ContextType.IMAGE, ContextType.VIDEO, ContextType.FILE, ContextType.VOICE]:
                uuid = str(msg._rawmsg.get("uuid"))
                self.msg_dict[uuid] = msg

        except Exception as e:
            logger.error(f"Failed to handle message: {e}")

    def on_receive_message(self, e_context: EventContext):
        try:
            logger.debug("[Revocation] on_receive_message: %s" % e_context)
            context = e_context['context']
            cmsg: ChatMessage = context['msg']
            if cmsg.is_group:
                self.handle_group_msg(cmsg)
                if cmsg.ctype == ContextType.REVOKE_MESSAGE:
                    e_context.action = EventAction.BREAK_PASS
                    return
            else:
                self.handle_single_msg(cmsg)
        except Exception as e:
            logger.error(f"处理消息失败: {str(e)}")

    def handle_single_msg(self, msg):
        """处理私聊消息"""
        self.handle_msg(msg, False)
        return None

    def handle_group_msg(self, msg):
        """处理群聊消息"""
        self.handle_msg(msg, True)
        return None

    def get_chatroom_id(self):
        monitor_groups_id=[]
        for group in self.monitor_groups:
            for key, item in self.bot.shared_wx_contact_list.items():
                if item and key.endswith("@chatroom"):
                    if item['chatRoomId'] != "" and item['nickName'] != "" \
                        and (item['nickName'].lower() ==group or key ==group) :
                        monitor_groups_id.append(key)
                        break
            else:
                logger.info({f"{group}不在通讯录中，请先保存到通讯录"})
        return monitor_groups_id
    def extract_file_xml(self,content):

        # 解析XML字符串
        root = ET.fromstring(content)

        # 定位到appmsg标签，因为所需的数据主要位于此标签内
        appmsg = root.find('appmsg')

        # 提取所需属性
        title = appmsg.find('title').text
        totallen = appmsg.find('appattach').find('totallen').text
        attachid = appmsg.find('appattach').find('attachid')
        if attachid is not None:
            attachid = attachid.text
        else:
            attachid = ""
        cdnattachurl = appmsg.find('appattach').find('cdnattachurl')
        if cdnattachurl is not None:
            cdnattachurl = cdnattachurl.text
        else:
            cdnattachurl = ""
        aeskey = appmsg.find('appattach').find('aeskey')
        if aeskey is not None:
            aeskey = aeskey.text
        else:
            aeskey = ""
        filekey = appmsg.find('appattach').find('filekey')
        if filekey is not None:
            filekey = filekey.text
        else:
            filekey = ""
        md5 = appmsg.find('md5').text
        file_extension = appmsg.find('appattach').find('fileext')
        if file_extension is not None:
            file_extension = file_extension.text
        else:
            file_extension  = os.path.splitext(title)[1][1:].lower()

        # 输出这些值
        print(f"Title: {title}")
        print(f"Total Length: {totallen}")
        print(f"Attach ID: {attachid}")
        print(f"Cdn Attach URL: {cdnattachurl}")
        print(f"AES Key: {aeskey}")
        print(f"File Key: {filekey}")
        print(f"MD5: {md5}")
        return title, totallen, attachid, cdnattachurl, aeskey, filekey, md5, file_extension