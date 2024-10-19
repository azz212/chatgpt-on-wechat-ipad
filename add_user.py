from models import db_session, User, WeChatAccount, WeChatGroup, WeChatGroupMember, AutoReply
import random
import aiohttp
import json
import uuid
import time
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db_session,Session_sql
hashed_password = generate_password_hash('12345789', method='pbkdf2:sha256', salt_length=8)
from channel.wechat.iPadWx import iPadWx
from config import load_config
from sqlalchemy.exc import PendingRollbackError


def insert_wechat_data(json_file,account):
    # Create a db_session
    db_session  = Session_sql()

    # Read the JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for group_data in data.values():
        # Create or update the WeChat group
        group = db_session.query(WeChatGroup).filter_by(chatRoomId=group_data['chatRoomId']).first()
        if not group:
            group = WeChatGroup(chatRoomId=group_data['chatRoomId'])
            db_session.add(group)

        # Update group information
        group.name = group_data['nickName']
        group.members_count = int(group_data['memberCount'])
        group.bigHeadImgUrl = group_data['bigHeadImgUrl']  # 群组图标链接
        group.chatRoomOwner = group_data['chatRoomOwner']  # 群主
        group.chatRoomOwner = group_data['chatRoomOwner']  # 群主
        # Delete existing members if group is updated
        if group.id:
            db_session.query(WeChatGroupMember).filter_by(chatRoomId=group.chatRoomId).delete()

        #Add group members
        for member_data in group_data['chatRoomMembers']:
            member = WeChatGroupMember(
                chatRoomId=group.chatRoomId,
                userName=member_data['userName'],
                nickName=member_data['nickName'],
                displayName=member_data.get('displayName', ''),
                inviterUserName=member_data.get('inviterUserName', ''),
                isAdmin=member_data['isAdmin'],
                sex=member_data['sex'],
                bigHeadImgUrl=member_data['bigHeadImgUrl']
            )
            db_session.add(member)
        account_id = account.account_id  # Assuming user has one account for simplicity
        group.account_id = account_id# Assuming user has one account for simplicity

    # Commit changes and close the db_session
    try:
        # 尝试执行数据库操作
        db_session.commit()  # 提交事务
    except Exception as e:
        db_session.rollback()  # 如果发生异常，回滚事务
        if isinstance(e, PendingRollbackError):
            print("检测到PendingRollbackError，事务已回滚。请检查并处理导致事务失败的原因。")
        else:
            raise  # 如果不是PendingRollbackError，再次抛出异常以便上层处理
    db_session.close()

def add_user(username, password, wx_id):
    # Check if the user already exists
    existing_user = db_session.query(User).filter_by(username=username).first()
    if not existing_user:
        # Use generate_password_hash from werkzeug.security to generate the hash
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, owner_wxid=wx_id)
        db_session.add(new_user)
        try:
            # 尝试执行数据库操作
            db_session.commit()  # 提交事务
        except Exception as e:
            db_session.rollback()  # 如果发生异常，回滚事务
            if isinstance(e, PendingRollbackError):
                print("检测到PendingRollbackError，事务已回滚。请检查并处理导致事务失败的原因。")
            else:
                raise  # 如果不是PendingRollbackError，再次抛出异常以便上层处理
    return existing_user

def insert_wechat_account(json_data,user):
    # Create a db_session
    db_session = Session_sql()

    # Extract data from JSON
    data = json_data['data']
    wx_id = data['id']
    nickname = data['nickname']
    end_time = datetime.strptime(data['expiry_date'], '%Y-%m-%d %H:%M:%S')

    # Check if the WeChat account already exists
    account = db_session.query(WeChatAccount).filter_by(wx_id=wx_id).first()
    if not account:
        # Create a new WeChatAccount
        account = WeChatAccount(
            account_id=data['robot'],
            wx_id=wx_id,
            nickname=nickname,
            end_time=end_time,
            is_online=(data['status'] == 1),
            owner_wxid=user.owner_wxid ,
            province = data['province'] if data['province'] else account.province,
            city=data['city'] if data['city'] else account.city,
        )
        db_session.add(account)

    # Update existing account
    else:
        account.nickname = nickname
        account.end_time = end_time
        account.account_id = data['robot']

        account.wx_id = wx_id or data['robot']
        account.province = data['province']if data['province'] else account.province,
        account.city = data['city'] if data['city'] else account.city
        account.is_online = (data['status'] == 1)

    # Link User and WeChatAccount by belong_wxid
    # user = db_session.query(User).filter_by(belong_wxid=wx_id).first()
    # if user:
    #     account.belong_wxid = user.id
    #     user.belong_wxid = wx_id

    # Commit changes
    try:
        # 尝试执行数据库操作
        db_session.commit()  # 提交事务
    except Exception as e:
        db_session.rollback()  # 如果发生异常，回滚事务
        if isinstance(e, PendingRollbackError):
            print("检测到PendingRollbackError，事务已回滚。请检查并处理导致事务失败的原因。")
        else:
            raise  # 如果不是PendingRollbackError，再次抛出异常以便上层处理
    db_session.close()

#add_user('13923385611', '123456', "wxid_f3pa5bx7t77z22")
# Fetch admin user from the database
#admin_user = db_session.query(User).filter_by(username='13923385611').first()
def add_wechatuser(username,password,province,city):

    add_user(username, "123456", username)
    admin_user = db_session.query(User).filter_by(username=username).first()

    if len(admin_user.wechat_account) != 0:
        wechat_account = admin_user.wechat_account[0]
        auth = wechat_account.auth
        auth_account = wechat_account.auth_account
        city = wechat_account.city
        province = wechat_account.province
        token = wechat_account.token
        load_config()
        wxbot = iPadWx()
        wxbot.auth = auth
        wxbot.auth_account = auth_account
        wxbot.city = city
        wxbot.province = province
        wxbot.token = token

        # wxbot.confirm_login()

        json_data = wxbot.get_robot_info()

        # Insert data into the database
        insert_wechat_account(json_data, admin_user)
        wxbot.start_listen()
        wxbot.filter_msg()
        wxbot.set_callback_url(wechat_account.callback_url)
        # admin_user = db_session.query(User).filter_by(username='13923385611').first()
    else:
        account = WeChatAccount(
            account_id=username,
            wx_id=username,
            nickname="",
            end_time=datetime.today(),
            is_online=0,
            owner_wxid=username,
            province=province,
            city=city,
            auth_account = username,
            auth_password = password,
        )
        db_session.add(account)
        try:
            # 尝试执行数据库操作
            db_session.commit()  # 提交事务
        except Exception as e:
            db_session.rollback()  # 如果发生异常，回滚事务
            if isinstance(e, PendingRollbackError):
                print("检测到PendingRollbackError，事务已回滚。请检查并处理导致事务失败的原因。")
            else:
                raise  # 如果不是PendingRollbackError，再次抛出异常以便上层处理
if __name__ == '__main__':
    # #反射现有数据库结构

    username = 'admin'
    password = ""
    province = "四川省"
    city ="成都市"
    add_wechatuser(username,password,province,city)
