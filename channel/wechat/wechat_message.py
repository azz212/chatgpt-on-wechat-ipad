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
        elif itchat_msg["type"] in ['8005']:#群聊红包、文件、链接、小程序等类型
            self.ctype = ContextType.XML
            self.content = itchat_msg["msg"]
        elif itchat_msg["type"] in ['8006', '9006']:  # 群聊地图位置消息
            self.ctype = ContextType.MAP
        elif itchat_msg["type"] in ['8007', '9007']:#群聊表情包
            self.ctype = ContextType.EMOJI
        elif itchat_msg["type"] in ['8008', '9008']:#群聊名片
            self.ctype = ContextType.CARD
        elif itchat_msg["type"] in ['7005','9005']:
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
                    self.from_user_id = result['from_user_id']
                    self.actual_user_id = result['from_user_id']
                    displayName, nickname = self.get_chatroom_nickname(self.room_id, self.actual_user_id)
                    self.actual_user_nickname = displayName or nickname
                    self.content = result['action']
            elif result['message_type'] =='appmsg' and  result['subtype'] =='reference' :
                # 这里只能得到nickname， actual_user_id还是机器人的id
                self.ctype = ContextType.QUOTE
                self.content = result["title"] #引用说的话
            elif result['message_type'] ==19 and 'title' in  result  and  result['title'] =='群聊的聊天记录':

                # 这里只能得到nickname， actual_user_id还是机器人的id
                self.ctype = ContextType.LINK
                self.content = json.dumps(result["image_infos"]) # 内容 list
            elif "你已添加了" in itchat_msg["msg"]:  #通过好友请求
                self.ctype = ContextType.ACCEPT_FRIEND
                self.content = itchat_msg["msg"]
            elif is_group and ("移出了群聊" in itchat_msg["msg"]):
                self.ctype = ContextType.EXIT_GROUP
                self.content = itchat_msg["msg"]
                self.actual_user_nickname = re.findall(r"\"(.*?)\"", itchat_msg["msg"])
                    
            elif "你已添加了" in itchat_msg["msg"]:  #通过好友请求
                self.ctype = ContextType.ACCEPT_FRIEND
                self.content = itchat_msg["msg"]

            else:
                raise NotImplementedError("Unsupported note message: " + itchat_msg["msg"])
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
            raise NotImplementedError("Unsupported message type: Type:{} MsgType:{}".format(itchat_msg["type"],
                                                                                            itchat_msg["type"]))
        if not self.from_user_id:
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

                #self.to_user_nickname = self.get_chatroom_nickname(self.room_id, self.to_user_id)
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
            if not self.actual_user_id:
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
                #logger.info(iPadWx.shared_wx_contact_list[room_id])
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
        refermsg = root.find('.//refermsg')
        # 根据消息类型提取信息
        if message_type == 'pat':
            # 拍一拍消息
            from_username = root.find('.//fromusername').text if root.find('.//fromusername') is not None else None
            template_content = root.find('.//template').text if root.find('.//template') is not None else None
            return {
                'message_type': message_type,
                'from_user_id': from_username,
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
        elif message_type == 'NewXmlChatRoomAccessVerifyApplication':
            # 提取关键信息
            # 提取邀请人用户名
            inviter_username = root.find('.//inviterusername').text if root.find(
                './/inviterusername') is not None else "N/A"

            # 从 <text> 标签中提取邀请人的昵称
            text_content = root.find('.//text').text if root.find('.//text') is not None else ""
            start_index = text_content.find('"') + 1
            end_index = text_content.find('"', start_index + 1)
            inviter_nickname = text_content[start_index:end_index] if start_index < end_index else "N/A"

            room_name = root.find('.//RoomName').text if root.find('.//RoomName') is not None else "N/A"
            invitation_reason = root.find('.//invitationreason').text if root.find(
                './/invitationreason') is not None else "N/A"

            joiners = []
            memberlist = root.find('.//memberlist')
            if memberlist is not None:
                for member in memberlist.findall('member'):
                    username = member.find('username').text if member.find('username') is not None else "N/A"
                    nickname = member.find('nickname').text if member.find('nickname') is not None else "N/A"
                    headimgurl = member.find('headimgurl').text if member.find('headimgurl') is not None else "N/A"
                    joiners.append({
                        'username': username,
                        'nickname': nickname,
                        'headimgurl': headimgurl
                    })

                # 构建JSON结构
            message_info = {
                'message_type': 'NewXmlChatRoomAccessVerifyApplication',
                'subtype': 'invite',
                'inviter_username': inviter_username,
                'inviter_nickname': inviter_nickname,
                'room_name': room_name,
                'invitation_reason': invitation_reason,
                'joiners': joiners
            }

            return message_info

        elif refermsg is not None:
            # 这是一个引用消息
            logger.info("引用消息存在，提取关键信息：")

            appmsg = root.find('appmsg')
            title = appmsg.find('title').text if appmsg.find('title') is not None else "N/A"

            refer_type = refermsg.find('type').text if refermsg.find('type') is not None else "N/A"
            svrid = refermsg.find('svrid').text if refermsg.find('svrid') is not None else "N/A"
            fromusr = refermsg.find('fromusr').text if refermsg.find('fromusr') is not None else "N/A"
            chatusr = refermsg.find('chatusr').text if refermsg.find('chatusr') is not None else "N/A"
            displayname = refermsg.find('displayname').text if refermsg.find('displayname') is not None else "N/A"
            content = refermsg.find('content').text if refermsg.find('content') is not None else "N/A"
            message_info = {
                'message_type': 'appmsg',
                'title': title,
                'content': content
            }
            # 添加引用消息的信息
            message_info.update({
                'subtype': 'reference',
                'title': title,
                'reference': {
                    'type': refer_type,
                    'svrid': svrid,
                    'fromusr': fromusr,
                    'chatusr': chatusr,
                    'displayname': displayname,
                    'content': content.strip()
                }
            })
            # 输出提取的信息
            logger.info(f"消息内容: {title}")
            logger.info(f"引用消息类型: {refer_type}")
            logger.info(f"消息ID: {svrid}")
            logger.info(f"发送人: {fromusr}")
            logger.info(f"聊天群: {chatusr}")
            logger.info(f"显示名: {displayname}")
            logger.info(f"引用消息: {content}")
            return message_info
        else:
            # 提取关键信息
            title = root.find('.//title').text if root.find('.//title') is not None else ''
            message_type = root.find('.//type').text if root.find('.//type') is not None else ''
            if message_type.isdigit():
                message_type = int(message_type)
            if title =='群聊的聊天记录' and message_type ==19:
                from_username = root.find('.//fromusername').text if root.find('.//fromusername') is not None else ''
                # 提取图片信息
                images_info = []
                recorditem = root.findall(".//recorditem")
                # 遍历datalist中的所有dataitem元素
                root2 = ET.fromstring(recorditem[0].text)
                for dataitem in root2.findall('.//datalist/dataitem'):
                    # 提取dataitem中的信息
                    image_info = {
                        # 'htmlid': dataitem.get('htmlid'),
                        'datatype': dataitem.get('datatype'),
                        # 'dataid': dataitem.get('dataid'),
                        # 'messageuuid': dataitem.find('.//messageuuid').text if dataitem.find('.//messageuuid') is not None else '',
                        # 'cdnthumburl': dataitem.find('.//cdnthumburl').text if dataitem.find('.//cdnthumburl') is not None else '',
                        'sourcetime': dataitem.find('.//sourcetime').text if dataitem.find(
                            './/sourcetime') is not None else '',
                        # 'fromnewmsgid': dataitem.find('.//fromnewmsgid').text if dataitem.find('.//fromnewmsgid') is not None else '',
                        # 'datasize': dataitem.find('.//datasize').text if dataitem.find('.//datasize') is not None else '',
                        # 'thumbfullmd5': dataitem.find('.//thumbfullmd5').text if dataitem.find('.//thumbfullmd5') is not None else '',
                        'filetype': dataitem.find('.//filetype').text if dataitem.find(
                            './/filetype') is not None else '',
                        # 'cdnthumbkey': dataitem.find('.//cdnthumbkey').text if dataitem.find('.//cdnthumbkey') is not None else '',
                        'sourcename': dataitem.find('.//sourcename').text if dataitem.find(
                            './/sourcename') is not None else '',
                        'datadesc': dataitem.find('.//datadesc').text if dataitem.find(
                            './/datadesc') is not None else '',
                        # 'cdndataurl': dataitem.find('.//cdndataurl').text if dataitem.find('.//cdndataurl') is not None else '',
                        # 'sourceheadurl': dataitem.find('.//sourceheadurl').text if dataitem.find('.//sourceheadurl') is not None else '',
                        # 'fullmd5': dataitem.find('.//fullmd5').text if dataitem.find('.//fullmd5') is not None else ''
                    }
                    # 将提取的信息添加到images_info列表中
                    images_info.append(image_info)

                # 构建JSON结构
                message_info = {
                    'title': title,
                    'message_type': message_type,
                    'from_username': from_username,
                    'image_infos': images_info
                }

                # 将结果转换为JSON字符串
                json_result = json.dumps(message_info, ensure_ascii=False, indent=2)

                return  message_info
            return {'message_type': message_type, 'info': '未知消息类型'}

    def load_contact(self):
        if os.path.exists("contact.json"):
            iPadWx.shared_wx_contact_list = json.load(open("contact.json",'r',encoding='utf-8'))
            logger.info(f"读取联系人!")
            pass
    def save_contact(self):

        json.dump(iPadWx.shared_wx_contact_list,open("contact.json",'w',encoding='utf-8'))
        logger.info(f"保存联系人!{iPadWx.shared_wx_contact_list}")