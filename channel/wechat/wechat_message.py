import re

from bridge.context import ContextType
from channel.chat_message import ChatMessage
from common.log import logger
from common.tmp_dir import TmpDir
import json
import os
import xml.etree.ElementTree as ET



#from lib import itchat
#from lib.itchat.content import *

from channel.wechat.iPadWx import iPadWx
class WechatMessage(ChatMessage):
    '''

    '''

    def __init__(self, itchat_msg, is_group=False):
        super().__init__(itchat_msg)
        self.msg_id = itchat_msg["msg_id"]
        self.create_time = itchat_msg["arr_at"]
        self.is_group = itchat_msg["group"]
        self.room_id = itchat_msg["room_id"]
        self.bot = iPadWx()
        if itchat_msg["type"] in ['8001','9001']   :
            self.ctype = ContextType.TEXT
            self.content = itchat_msg["msg"]
        elif itchat_msg["type"]   in ['8002','9002']:#群聊图片
            self.ctype = ContextType.IMAGE
            #self.content = TmpDir().path() + itchat_msg.get("FileName")  # content直接存临时目录路径
            #self._prepare_fn = lambda: itchat_msg.download(self.content)
        elif itchat_msg["type"] in ['8003', '9003']:
            self.ctype = ContextType.VIDEO
        elif itchat_msg["type"]  in ['8004','9004'] :#群聊语音消息
            self.ctype = ContextType.VOICE
            self.content = TmpDir().path() + itchat_msg.get("FileName")  # content直接存临时目录路径
            #self._prepare_fn = lambda: itchat_msg.download(self.content)
        elif itchat_msg["type"] in ['8005', '9005']:#群聊红包、文件、链接、小程序等类型
            self.ctype = ContextType.XML
            self.content = itchat_msg["msg"]
        elif itchat_msg["type"] in ['8006', '9006']:  # 群聊地图位置消息
            self.ctype = ContextType.MAP
        elif itchat_msg["type"] in ['8007', '9007']:#群聊表情包
            self.ctype = ContextType.EMOJ
        elif itchat_msg["type"] in ['8008', '9008']:#群聊名片
            self.ctype = ContextType.CARD
        elif itchat_msg["type"] in ['7005']:
            result = self.parse_wechat_message( itchat_msg["msg"])
            if result['message_type'] =='sysmsgtemplate' and  result['subtype'] =='invite' :
                # 这里只能得到nickname， actual_user_id还是机器人的id
                self.ctype = ContextType.JOIN_GROUP
                self.content = itchat_msg["msg"]
                self.actual_user_nickname = result['joiners_usernames'][0]['nickname']
                #self.content= f"{result['inviter_username']['nickname']} 邀请 {self.actual_user_nickname } 加入了群聊!"

            elif result['message_type'] =='pat':

                self.ctype = ContextType.PATPAT

                self.content = itchat_msg["msg"]

                if is_group:
                    self.actual_user_id = result['from_username']
                    displayName, nickname = self.get_chatroom_nickname(self.room_id, self.actual_user_id)
                    self.actual_user_nickname = displayName or nickname

            elif is_group and ("移出了群聊" in itchat_msg["msg"]):
                self.ctype = ContextType.EXIT_GROUP
                self.content = itchat_msg["msg"]
                self.actual_user_nickname = re.findall(r"\"(.*?)\"", itchat_msg["Content"])[0]
                    
            elif "你已添加了" in itchat_msg["msg"]:  #通过好友请求
                self.ctype = ContextType.ACCEPT_FRIEND
                self.content = itchat_msg["msg"]

            else:
                raise NotImplementedError("Unsupported note message: " + itchat_msg["Content"])
        elif itchat_msg["type"] in ['8005','9005']:
            self.ctype = ContextType.FILE
            #self.content = TmpDir().path() + itchat_msg.get("FileName")  # content直接存临时目录路径
            if self.content:
                pass
                #self._prepare_fn = lambda: itchat_msg.download(self.content)
        elif itchat_msg["type"] == '9006':
            self.ctype = ContextType.XML
            self.content = itchat_msg.get("msg")

        else:
            raise NotImplementedError("Unsupported message type: Type:{} MsgType:{}".format(itchat_msg["type"], itchat_msg["type"]))
        self.from_user_id = itchat_msg["from_id"]

        self.to_user_id = itchat_msg["to_id"]

        # 虽然from_user_id和to_user_id用的少，但是为了保持一致性，还是要填充一下
        # 以下很繁琐，一句话总结：能填的都填了。
        #other_user_id: 对方的id，如果你是发送者，那这个就是接收者id，如果你是接收者，那这个就是发送者id，如果是群消息，那这一直是群id(必填)

        try:  # 陌生人时候, User字段可能不存在
            # my_msg 为True是表示是自己发送的消息
            self.my_msg = itchat_msg["bot_id"] == itchat_msg["from_id"]
            if self.is_group:
                self.other_user_id = itchat_msg["room_id"]
                displayName,nickname = self.get_chatroom_nickname(self.room_id, self.from_user_id)

                self.from_user_nickname = nickname
                self.self_display_name =  displayName or nickname
                _,self.to_user_nickname  = self.get_chatroom_nickname(self.room_id, self.to_user_id)

                self.to_user_nickname = self.get_chatroom_nickname(self.room_id, self.to_user_id)
                self.other_user_nickname = iPadWx.shared_wx_contact_list[self.room_id]['nickName']
            else:
                if itchat_msg['bot_id']==itchat_msg['from_id']:#机器人发送
                    self.other_user_id = itchat_msg["to_id"]
                    self.other_user_nickname = self.to_user_nickname
                else:
                    self.other_user_id = itchat_msg["from_id"]
                    self.other_user_nickname = self.from_user_nickname
            if itchat_msg["from_id"]:
                pass
                # 自身的展示名，当设置了群昵称时，该字段表示群昵称
                #self.self_display_name = self.from_user_nickname
        except KeyError as e:  # 处理偶尔没有对方信息的情况
            logger.warn("[WX]get other_user_id failed: " + str(e))

        if self.is_group:
            self.is_at = False if len(itchat_msg["at_ids"])==0 else True
            self.at_list = itchat_msg["at_ids"]
            #self.at_list_member = self.bot.shared_wx_contact_list[self.room_id]['chatRoomMembers']
            self.actual_user_id = itchat_msg["from_id"]
            if self.ctype not in [ContextType.JOIN_GROUP, ContextType.PATPAT, ContextType.EXIT_GROUP]:
                pass
                self.actual_user_nickname = self.self_display_name #发送者的群昵称 还是本身的昵称

    def get_user(self,users, username):
        # 使用 filter 函数通过给定的 userName 来找寻符合条件的元素
        if not isinstance(users,list):
            return None
        res = list(filter(lambda user: user['userName'] == username, users))

        return res[0] if res else None  # 如果找到了就返回找到的元素（因为 filter 返回的是列表，所以我们取第一个元素），否则返回 None
    def get_chatroom_nickname(self, room_id: str = 'null', wxid: str = 'ROOT'):
        '''
        获取群聊中用户昵称 Get chatroom's user's nickname
        群成员如果变了，没有获取到，则重新获取
        :param room_id: 群号(以@chatroom结尾) groupchatid(end with@chatroom)
        :param wxid: wxid(新用户的wxid以wxid_开头 老用户他们可能修改过 现在改不了) wechatid(start with wxid_)
        :return: Dictionary
        '''
        if room_id.endswith("@chatroom") and not wxid.endswith("@chatroom"):
            if room_id in iPadWx.shared_wx_contact_list :
                logger.debug("无需网络获取，本地读取")
                #print(iPadWx.shared_wx_contact_list[room_id])
                member = iPadWx.shared_wx_contact_list[room_id]['chatRoomMembers']
                #logger.info(member)
                member_info = self.get_user(member, wxid)

            else:
                #本地不存在群信息，网络获取
                room_info = self.bot.get_room_info(room_id)
                iPadWx.shared_wx_contact_list[room_id] = room_info['data']
                members = self.bot.get_chatroom_memberlist(room_id)
                member_info = self.get_user(members['data'], wxid)
                iPadWx.shared_wx_contact_list[room_id]['chatRoomMembers'] =members['data']
                self.save_contact()
            #本地群存在，但是成员没找到，需要网络获取
            if not member_info:
                members = self.bot.get_chatroom_memberlist(room_id)
                member_info = self.get_user(members['data'], wxid)
                iPadWx.shared_wx_contact_list[room_id]['chatRoomMembers'] = members['data']
                self.save_contact()

            return  member_info['displayName'] , member_info['nickName']
        return None,None

    def parse_wechat_message(self,xml_data):
        def get_member_info(member_element):
            if member_element is not None:
                username = member_element.findtext('.//username').strip()
                nickname = member_element.findtext('.//nickname').strip()
                return {
                    'username': username,
                    'nickname': nickname
                }
            else:
                return None

        # 解析XML
        root = ET.fromstring(xml_data)

        # 获取消息类型
        message_type = root.get('type')

        # 根据消息类型提取信息
        if message_type == 'pat':
            # 拍一拍消息
            from_username = root.find('.//fromusername').text if root.find('.//fromusername') is not None else None
            template_content = root.find('.//template').text if root.find('.//template') is not None else None
            return {
                'message_type': message_type,
                'from_username': from_username,
                'action': template_content
            }
        elif message_type == 'sysmsgtemplate':
            # 系统消息，可能是邀请或撤回
            sub_type = root.find('./subtype').text if root.find('./subtype') is not None else None
            sub_type = root.find('.//sysmsgtemplate/content_template[@type="tmpl_type_profile"]')
            if sub_type:

                # 获取邀请者信息
                inviter_link = root.find('.//link_list/link[@name="username"]')
                inviter = get_member_info(inviter_link.find('.//member') if inviter_link is not None else None)

                # 获取加入群聊的成员信息
                names_link = root.find('.//link_list/link[@name="names"]')
                members = names_link.findall('.//memberlist/member') if names_link is not None else []
                joiners = [get_member_info(member) for member in members if get_member_info(member)]

                return {
                    'message_type': message_type,
                    'subtype': "invite",
                    'inviter_username': inviter,
                    'joiners_usernames': joiners
                }
            else:
                return {'message_type': message_type, 'subtype': sub_type, 'info': '未知系统消息类型'}
        elif message_type == 'revokemsg':
            # 消息撤回
            session = root.find('./session').text if root.find('./session') is not None else None
            msgid = root.find('./revokemsg/msgid').text if root.find('./revokemsg/msgid') is not None else None
            newmsgid = root.find('./revokemsg/newmsgid').text if root.find('./revokemsg/newmsgid') is not None else None
            replacemsg = root.find('./revokemsg/replacemsg').text if root.find(
                './revokemsg/replacemsg') is not None else None

            # 返回撤回消息的字典
            return {
                'message_type': 'revokemsg',
                'session': session,
                'original_message_id': msgid,
                'new_message_id': newmsgid,
                'replace_message': replacemsg
            }

        else:
            return {'message_type': message_type, 'info': '未知消息类型'}

    def load_contact(self):
        if os.path.exists("contact.json"):
            iPadWx.shared_wx_contact_list = json.load(open("contact.json",'r',encoding='utf-8'))
            logger.info(f"读取联系人!")
            pass
    def save_contact(self):

        json.dump(iPadWx.shared_wx_contact_list,open("contact.json",'w',encoding='utf-8'))
        logger.info(f"保存联系人!{iPadWx.shared_wx_contact_list}")