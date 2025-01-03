# encoding:utf-8

import plugins
from bridge import context
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from config import conf
def open_admin_mode():
    curdir = os.path.dirname(__file__)
    config_path = os.path.join(curdir, "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    config['switch'] = True
    with open(config_path, 'w',encoding="utf-8") as f:
        json.dump(config, f,ensure_ascii=False, indent=4)
    return "管理员模式已开启\n仅管理员可以触发bot"
def close_admin_mode():
    curdir = os.path.dirname(__file__)
    config_path = os.path.join(curdir, "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    config['switch'] = False  # 将work_mode的值修改为5
    with open(config_path, 'w',encoding="utf-8") as f:
        json.dump(config, f,ensure_ascii=False, indent=4)
    return "管理员模式已关闭，所有人可触发bot"

def _set_reply_text(content: str, e_context: EventContext, level: ReplyType = ReplyType.ERROR):
    reply = Reply(level, content)
    e_context["reply"] = reply
    e_context.action = EventAction.BREAK_PASS
@plugins.register(
    name="admin",
    desire_priority=999,
    hidden=True,
    desc="管理员模式",
    version="0.1",
    author="francis",
)
class Admin(Plugin):

    def __init__(self):
        super().__init__()
        try:
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        except Exception as e:
            logger.error(f"[Admin]初始化异常：{e}")
            raise "[Admin] init failed, ignore "


    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [
            ContextType.TEXT,ContextType.IMAGE_CREATE,
            ContextType.PATPAT,ContextType.QUOTE
        ]:
            return
        user_id = e_context['context']['msg'].from_user_id
        context = e_context["context"]
        isgroup = context.get("isgroup", False)
        content = context.content
        curdir = os.path.dirname(__file__)
        config_path = os.path.join(curdir, "config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            # print(config)
        admin_id = config.get("admin_id", )
        switch = config.get("switch", False)
        group_diff=[]
        if not isgroup and content.startswith("刷新"):
            from channel.wechat.iPadWx import iPadWx

            self.bot = iPadWx()
            groups = self.bot.get_device_room_list()
            user_info = self.bot.get_user_info()
            groups_monitor = user_info['data']['whitelisted_group_ids']
            max_group = int(user_info['data']['max_group'])
            need_save=False
            if groups['code']==0:
                for room_id in groups['data']:
                    if room_id not in self.bot.shared_wx_contact_list:
                        logger.info(f"群还未查询过{room_id}")
                        room_info = self.bot.get_room_info(room_id)
                        iPadWx.shared_wx_contact_list[room_id] = room_info['data']
                        members = self.bot.get_chatroom_memberlist(room_id)
                        iPadWx.shared_wx_contact_list[room_id]['chatRoomMembers'] = members['data']
                        logger.info(f"群还未查询过{room_id},名称{room_info['data']['nickName']}")
                        need_save=True
                    else:
                        nickname = iPadWx.shared_wx_contact_list[room_id]['nickName']
                        if not nickname:
                            room_info = self.bot.get_room_info(room_id)
                            iPadWx.shared_wx_contact_list[room_id] = room_info['data']
                            members = self.bot.get_chatroom_memberlist(room_id)
                            iPadWx.shared_wx_contact_list[room_id]['chatRoomMembers'] = members['data']
                            logger.info(f"群还未查询过名称{room_id},更新名称{room_info['data']['nickName']}")
                            need_save=True



                if need_save:
                    self.bot.save_contact()


                group_need_monitors = []
                group_name_white_list=conf().get("group_name_white_list")
                for group_need_monitor in group_name_white_list:
                    for key,item in iPadWx.shared_wx_contact_list.items():
                        if item and key.endswith("@chatroom"):
                            if item['chatRoomId']!="" and item['nickName']!="" :
                                if item['nickName'].lower() ==group_need_monitor.lower():
                                    group_need_monitors.append(key)
                                    if len(group_need_monitors) > max_group:
                                        logger.info(f"群监控数量超过{max_group}个，退出")
                                        break
                                    break

                # 根据ID来监控，防止群名不匹配
                group_name_white_roomid_list = conf().get("group_name_white_roomid_list",{})
                for group_id ,group_name in group_name_white_roomid_list.items():

                    if group_id not in group_need_monitors:
                        if len(group_need_monitors) >= max_group:
                            logger.info(f"群监控数量超过{max_group}个，退出")
                            break
                        logger.debug(f"{group_id},{group_name}已加入监控")
                        group_need_monitors.append(group_id)
                if "ALL_GROUP" in group_name_white_list:
                    for room_id in groups['data']:
                        if room_id not in group_need_monitors and len(group_need_monitors) < max_group:
                            group_need_monitors.append(room_id)
                        if len(group_need_monitors)>=max_group:
                            break

                # for room_id in groups['data']:
                #     if room_id not in group_need_monitors and len(group_need_monitors)<10:
                #         group_need_monitors.append(room_id)
                group_diff = set(group_need_monitors) -set(groups_monitor)
                if group_diff:
                    logger.info(f"增加的群监控{group_diff}")
                not_monitor = set(groups['data']) - set(group_need_monitors)
                logger.info(f"当前群{groups['data']}")
                logger.info(f"需要监控的群{group_need_monitors}")
                logger.info(f"不需要监控的群{not_monitor}")
                for room_id in list(not_monitor):
                    logger.info(f"还未监控的群{room_id},群名{iPadWx.shared_wx_contact_list[room_id]['nickName']}")

                for room_id in list(group_need_monitors):
                    logger.info(f"监控的群{room_id},群名{iPadWx.shared_wx_contact_list[room_id]['nickName']}")


                #self.bot.filter_msg()
                if group_need_monitors:
                    payload = {"group": group_need_monitors}
                    ret = self.bot.group_listen(payload=payload)
                    logger.info(f"group_listen ret:{ret}")
                else:
                    logger.info(f"没有群需要监控{group_need_monitors}")
            if group_diff:
                group_nammes=[]
                for room_id in group_diff:
                    group_nammes.append(iPadWx.shared_wx_contact_list[room_id]['nickName'])
                text = f"增加群监控成功，增加监控群{group_nammes}"
            else:
                text = f"增加群监控成功，无需要增加的群"


            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content =text
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

        elif switch:#管理员开启，只回复管理员信息
            if user_id == admin_id:
                e_context.action = EventAction.CONTINUE
            else:
                logger.info(f"[Admin] user_id：{user_id}  已被屏蔽")
                e_context.action = EventAction.BREAK_PASS
       
        else:
            """丢到下一步"""
            e_context.action = EventAction.CONTINUE

    def get_help_text(self, **kwargs):
        help_text = "开启管理员模式，其他人无权提问"
        return help_text


