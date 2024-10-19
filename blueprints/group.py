# encoding:utf-8
from quart import render_template, jsonify, session, redirect, url_for, request
from quart import Blueprint
from config import load_config,conf
from models import Session_sql, User, WeChatAccount, WeChatGroup, WeChatGroupMember

# 创建蓝图对象
group_bp = Blueprint('group', __name__)
load_config()

channel_name = conf().get("channel_type", "wx")
if channel_name == "wx":
    from channel.wechat.wechat_channel import WechatChannel
    from channel.wechat.iPadWx import iPadWx

    ch = WechatChannel()
    wxbot = iPadWx()
elif channel_name == "wx-beta":
    from channel.wechat.wechat_channel_ipad import WechatChannel
    from channel.wechat.iPadWx_Beta import iPadWx_Beta

    wxbot = iPadWx_Beta()
    ch = WechatChannel()
elif channel_name == "wx-hook":
    from channel.wechat.wechat_channel_hook import WechatChannel

    ch = WechatChannel()
    from channel.wechat.Wx_Zhang import Wx_Zhang

    wxbot = Wx_Zhang()
@group_bp.route("/rooms", methods=["GET"])
def rooms():
    response_data = wxbot.get_room_list()  # assuming this returns a list of room names
    data = response_data.get("data")
    if data:
        if isinstance(data, dict):

            return render_template('dict.html', data=data)
        elif isinstance(data, list):
            # return render_template('list.html', data=data)
            return jsonify(data)
        else:
            return jsonify({"code": 0, "response": "签到成功"})
    return jsonify({"code": -1, "response": "获取房间列表失败"})


@group_bp.route('/wechat_group_management')
async def wechat_group_management():
    db_session = Session_sql()
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    user = db_session.query(User).filter_by(id=user_id).first()

    # Get all accounts for the user
    #accounts = db_session.query(WeChatAccount).filter_by(owner_wxid=user.owner_wxid).all()


    # Query only accounts belonging to the logged-in user
    if user.owner_wxid == "wxid_f3pa5bx7t77z22":
        accounts = db_session.query(WeChatAccount).all()
    else:
        accounts = db_session.query(WeChatAccount).filter_by(owner_wxid=user.owner_wxid).all()

    account_ids = [account.id for account in accounts]

    #groups = db_session.query(WeChatGroup).filter_by(account_id=int(accounts.account_id)).all()
    # Query only groups belonging to the user's accounts
    groups = db_session.query(WeChatGroup).filter(WeChatGroup.account_id.in_(account_ids)).all()

    return await render_template('wechat_groups.html', title='微信群管理', active='groups', groups=groups,accounts=accounts)


@group_bp.route('/wechat_groups/<account_id>', methods=['GET'])
async def get_wechat_groups(account_id):
    db_session = Session_sql()
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    user = db_session.query(User).filter_by(id=user_id).first()

    # Get all accounts for the user
    accounts = db_session.query(WeChatAccount).filter_by(owner_wxid=user.owner_wxid).all()

    account_ids = [account.id for account in accounts]

    # Query only groups belonging to the user's accounts
    #groups = db_session.query(WeChatGroup).filter(WeChatGroup.account_id.in_(account_ids)).all()
    # Query only groups belonging to the user's accounts
    groups = db_session.query(WeChatGroup).filter_by(account_id=int(account_id)).all()

    # 将成员信息转换为 JSON 格式
    groups_data = [
        {
            'bigHeadImgUrl': group.bigHeadImgUrl,
            'name': group.name,
            'chatRoomId': group.chatRoomId,
            'account_id': group.account_id,
            'chatRoomOwner': group.chatRoomOwner,
            'members_count': group.members_count

        } for group in groups
    ]

    return jsonify(groups_data)  # 返回 JSON 格式的群组数据
    #return await render_template('wechat_groups.html', title='微信群管理', active='groups', groups=groups)


@group_bp.route('/api/wechat_group_members/<chatRoomId>', methods=['GET'])
async def get_wechat_group_members(chatRoomId):
    # 获取指定群组的成员
    db_session=Session_sql()
    members = db_session.query(WeChatGroupMember).filter_by(chatRoomId=chatRoomId).all()

    # 将成员信息转换为 JSON 格式
    members_data = [
        {
            'bigHeadImgUrl': member.bigHeadImgUrl,
            'userName': member.userName,
            'nickName': member.nickName,
            'displayName': member.displayName,
            'sex': member.sex,
            'inviterUserName': member.inviterUserName,
            'isAdmin': member.isAdmin

        } for member in members
    ]

    return jsonify(members_data)


@group_bp.route('/wechat_groups/edit/<int:group_id>', methods=['POST'])
async def edit_group(group_id):
    data = await request.form
    group_name = data.get('name')
    members = data.get('members')
    db_session = Session_sql()
    group = db_session.query(WeChatGroup).get(group_id)
    if group:
        group.name = group_name
        group.members = members
        group.members_count = len(members.split(',')) if members else 0
        # try:
        #     # 尝试执行数据库操作
        #     db_session.commit()  # 提交事务
        # except Exception as e:
        #     db_session.rollback()  # 如果发生异常，回滚事务
        #     if isinstance(e, PendingRollbackError):
        #         print("检测到PendingRollbackError，事务已回滚。请检查并处理导致事务失败的原因。")
        #     else:
        #         raise  # 如果不是PendingRollbackError，再次抛出异常以便上层处理

    return redirect('/wechat_groups')
