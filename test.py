import json
import xml.etree.ElementTree as ET


# XML消息字符串
xml_data_invite = '''
<sysmsg type="sysmsgtemplate">\n\t<sysmsgtemplate>\n\t\t<content_template type="tmpl_type_profile">\n\t\t\t<plain><![CDATA[]]></plain>\n\t\t\t<template><![CDATA["$username$"邀请"$names$"加入了群聊]]></template>\n\t\t\t<link_list>\n\t\t\t\t<link name="username" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_gqhxp9ipfxv222]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[🌙 周星星🌙(管理)]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t</link>\n\t\t\t\t<link name="names" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[zhaokaihui123]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[大辉辉]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t\t<separator><![CDATA[、]]></separator>\n\t\t\t\t</link>\n\t\t\t</link_list>\n\t\t</content_template>\n\t</sysmsgtemplate>\n</sysmsg>
'''
xml_data_invite2 ='''
<sysmsg type="sysmsgtemplate">\n\t<sysmsgtemplate>\n\t\t<content_template type="tmpl_type_profile">\n\t\t\t<plain><![CDATA[]]></plain>\n\t\t\t<template><![CDATA["$username$"邀请"$names$"加入了群聊]]></template>\n\t\t\t<link_list>\n\t\t\t\t<link name="username" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_gqhxp9ipfxv222]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[🌙 周星星🌙(管理)]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t</link>\n\t\t\t\t<link name="names" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_yr9kqgy0sx6s22]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[帅哥]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t\t<separator><![CDATA[、]]></separator>\n\t\t\t\t</link>\n\t\t\t</link_list>\n\t\t</content_template>\n\t</sysmsgtemplate>\n</sysmsg>
'''
xml_data_invite3 ='''
<sysmsg type="sysmsgtemplate">\n\t<sysmsgtemplate>\n\t\t<content_template type="tmpl_type_profile">\n\t\t\t<plain><![CDATA[]]></plain>\n\t\t\t<template><![CDATA["$username$"邀请"$names$"加入了群聊]]></template>\n\t\t\t<link_list>\n\t\t\t\t<link name="username" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_gqhxp9ipfxv222]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[🌙 周星星🌙(管理)]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t</link>\n\t\t\t\t<link name="names" type="link_profile">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_yr9kqgy0sx6s22]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[帅哥]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t\t<separator><![CDATA[、]]></separator>\n\t\t\t\t</link>\n\t\t\t</link_list>\n\t\t</content_template>\n\t</sysmsgtemplate>\n</sysmsg>
'''
xml_data_pai ='''
<sysmsg type="pat">\n<pat>\n  <fromusername>wxid_gqhxp9ipfxv222</fromusername>\n  <chatusername>26516713149@chatroom</chatusername>\n  <pattedusername>wxid_6q3ar4xb7m1922</pattedusername>\n  <patsuffix><![CDATA[]]></patsuffix>\n  <patsuffixversion>0</patsuffixversion>\n\n\n\n\n  <template><![CDATA["${wxid_gqhxp9ipfxv222}" 拍了拍我]]></template>\n\n\n\n\n</pat>\n</sysmsg>
'''

xml_data_revokemsg='''
<sysmsg type="revokemsg"><revokemsg><session>26516713149@chatroom</session><msgid>1645246305</msgid><newmsgid>1793967667995376130</newmsgid><replacemsg><![CDATA["🌙 周星星🌙(管理)" 撤回了一条消息]]></replacemsg><announcement_id><![CDATA[]]></announcement_id></revokemsg></sysmsg>
'''
xml_data_revokemsg2='''
<sysmsg type="revokemsg"><revokemsg><session>26516713149@chatroom</session><msgid>1645246345</msgid><newmsgid>573030870260826826</newmsgid><replacemsg><![CDATA["🌙 周星星🌙(管理)" 撤回了一条消息]]></replacemsg><announcement_id><![CDATA[]]></announcement_id></revokemsg></sysmsg>
'''
def parse_wechat_invite_message(xml_data):
    # 解析XML
    root = ET.fromstring(xml_data)

    # 辅助函数，用于获取成员的用户名和昵称
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

    # 检查是否是邀请消息
    invite_message = root.find('.//sysmsgtemplate/content_template[@type="tmpl_type_profile"]')
    if invite_message is None:
        print("这不是一条邀请消息。")
        return False, None, None

    # 获取邀请者信息
    inviter_link = root.find('.//link_list/link[@name="username"]')
    inviter = get_member_info(inviter_link.find('.//member') if inviter_link is not None else None)

    # 获取加入群聊的成员信息
    names_link = root.find('.//link_list/link[@name="names"]')
    members = names_link.findall('.//memberlist/member') if names_link is not None else []
    joiners = [get_member_info(member) for member in members if get_member_info(member)]

    # 返回结果
    return True,inviter, joiners



# 调用函数并打印结果
is_invite,inviter, joiners = parse_wechat_invite_message(xml_data_pai)
if is_invite:
    if isinstance(inviter, dict) and isinstance(joiners, list):
        print(f"邀请者: {inviter['nickname']} ({inviter['username']})")
        for joiner in joiners:
            print(f"加入群聊的成员: {joiner['nickname']} ({joiner['username']})")
    else:
        print(inviter)
else:
    print("这不是一条邀请消息。")

import xml.etree.ElementTree as ET


def parse_wechat_message(xml_data):
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
        if sub_type :

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



# 调用函数并打印结果
parsed_message = parse_wechat_message(xml_data_invite3)
print(parsed_message)
#print(f"{parsed_message['inviter_username']['nickname']} 邀请 {parsed_message['joiners_usernames'][0]['nickname'] } 加入了群聊!")
