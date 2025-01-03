# encoding:utf-8
from quart import render_template, jsonify, session, redirect, url_for, request
from quart import Blueprint
from models import Session_sql, User, WeChatAccount, WeChatGroup, WeChatGroupMember
from config import load_config,conf,save_config
import asyncio
from datetime import datetime,timedelta
from common.log import logger
import time
import concurrent.futures
from .decorators import login_required
import requests

# 创建蓝图对象
group_bp = Blueprint('group', __name__)
load_config()

channel_name = conf().get("channel_type", "wx")
if channel_name == "wx":
    from channel.wechat.wechat_channel import WechatChannel
    from channel.wechat.iPadWx import iPadWx

    ch = WechatChannel()
    wxbot = iPadWx()
@group_bp.route("/rooms", methods=["GET"])
@login_required
async def rooms():
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
@login_required
async def wechat_group_management():
    db_session = Session_sql()
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user.login'))  # Redirect to login if not authenticated

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
@login_required
async def get_wechat_groups(account_id):
    db_session = Session_sql()
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user.login'))

    user = db_session.query(User).filter_by(id=user_id).first()
    accounts = db_session.query(WeChatAccount).filter_by(owner_wxid=user.owner_wxid).all()

    account = db_session.query(WeChatAccount).filter_by(id=account_id).first()
    account_type = account.account_type
    if not account:
        return jsonify({"error": "Account not found"}), 404

    groups = db_session.query(WeChatGroup).filter_by(account_id=int(account_id)).all()
    
    # 更新本地变量，保存到本地文件
    groups_data=[]
    auth_account = account.auth_account
    config = conf()
    local_account = config.get("auth_account")
    if local_account == auth_account:
        if account_type==1:
            max_group = account.max_group
            for room_id, room_data in iPadWx.shared_wx_contact_list.items():
                if room_id.endswith("@chatroom"):
                    if room_id=="" or room_data['nickName']=="":
                        continue
                    groups_data.append({
                    'name': room_data['nickName'],
                    'chatRoomId': room_data['chatRoomId'],
                    #'account_id': group.account_id,
                    #'chatRoomOwner': group.chatRoomOwner,
                    'members_count': room_data['memberCount'],
                    'remark': ""  # 假设 remark 字段存在于 WeChatGroup 模型中
                    })
                else:
                    nickName = room_data.get('nickName', "")
                    chatRoomId = room_data.get('userName', "")
                    remark = room_data.get('remark', "")
                    groups_data.append({
                        'name': nickName,
                        'chatRoomId':chatRoomId,
                        # 'account_id': group.account_id,
                        # 'chatRoomOwner': group.chatRoomOwner,
                        'members_count': 0,
                        'remark': remark  # 假设 remark 字段存在于 WeChatGroup 模型���
                    })
        else:
            for room_id, room_data in iPadWx.shared_wx_contact_list.items():
                if room_id=="" or room_data.get('nickName',"")=="":
                    continue
                if room_id.endswith("@chatroom"):
                    nickName= room_data.get('nickName',"")
                    chatRoomId= room_data.get('chatroomId', "")
                    memberList = room_data.get('memberList', [])
                    remark = room_data.get('remark', "")
                    groups_data.append({
                    'name': nickName,
                    'chatRoomId': chatRoomId,
                    #'account_id': group.account_id,
                    #'chatRoomOwner': group.chatRoomOwner,
                    'members_count': 0 if memberList is None else len(memberList),
                    'remark': remark  # 假设 remark 字段存在于 WeChatGroup 模型中
                    })
                else:
                    nickName = room_data.get('nickName', "")
                    chatRoomId = room_data.get('userName', "")
                    remark = room_data.get('remark', "")
                    groups_data.append({
                        'name': nickName,
                        'chatRoomId':chatRoomId,
                        # 'account_id': group.account_id,
                        # 'chatRoomOwner': group.chatRoomOwner,
                        'members_count': 0,
                        'remark': remark  # 假设 remark 字段存在于 WeChatGroup 模型中
                    })

    else:
        groups_data = [
            {
                'name': group.name,
                'chatRoomId': group.chatRoomId,
                #'account_id': group.account_id,
                #'chatRoomOwner': group.chatRoomOwner,
                'members_count': group.members_count,
                'remark': group.remark  # 假设 remark 字段存在于 WeChatGroup 模型中
            } for group in groups
        ]

    # Send max_group and whitelisted_group_ids to the frontend
    response = {
        "groups": groups_data,
        "max_group": account.max_group,
        "whitelisted_group_ids": account.whitelisted_group_ids or []
    }
    return jsonify(response)


@group_bp.route('/save_selected_groups', methods=['POST'])
@login_required
async def save_selected_groups():
    data = await request.get_json()  # Await here to get JSON payload from request
    account_id = data.get('account_id')
    selected_group_ids = data.get('selected_group_ids', [])
    selected_group_names = data.get('selected_group_names', [])
    #将传入的ids和names 根据是否有@chatroom 进行分类,name 和id 一一对应,不能判断名字是否有@chatroom
    chatroom_ids = [id for id in selected_group_ids if id.endswith("@chatroom")]
    chatroom_names = [name for id, name in zip(selected_group_ids, selected_group_names) if id in chatroom_ids]

    #同样对于不是以@chatroom 结尾的，获取后保存到数组中
    private_ids = [id for id in selected_group_ids if not id.endswith("@chatroom")]
    private_names = [name for id,name in zip(selected_group_ids,selected_group_names) if id in private_ids ]
    db_session = Session_sql()

    try:
        # Fetch the WeChat account record and update `whitelisted_group_ids`
        account = db_session.query(WeChatAccount).filter_by(id=account_id).first()

        if not account:
            return jsonify({'error': 'Account not found'}), 404

        # Update whitelisted_group_ids with the selected group IDs
        account.whitelisted_group_ids = selected_group_ids
        db_session.commit()
        #todo  保存到配置中
        config = conf()
        current_group_names = config.get("group_name_white_list")
        if "ALL_GROUP" in current_group_names:
            chatroom_names.append("ALL_GROUP")
        local_account = config.get("auth_account")
        if local_account == account.auth_account or local_account == "":

            config.__setitem__("group_name_white_list", chatroom_names)
            #config.__setitem__("group_id_white_list", chatroom_ids)
            config.__setitem__("private_id_white_list", private_ids)
            config.__setitem__("private_name_white_list", private_names)
            save_config()

        # Prepare and send the updated groups for listening
        group_need_monitors = selected_group_ids
        payload = {"group": group_need_monitors}
        ret = wxbot.group_listen(payload=payload)

        if ret:
            return jsonify({'message': '群组设置成功'}), 200
        else:
            return jsonify({'error': '更新失败'}), 500

    except Exception as e:
        db_session.rollback()
        print(f"Database error: {e}")
        return jsonify({'error': '数据库更新失败'}), 500

    finally:
        db_session.close()

@group_bp.route('/api/wechat_group_members/<chatRoomId>', methods=['GET'])
@login_required
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
@login_required
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
@group_bp.route('/update_robot_basic', methods=['POST'])
@login_required
async def update_robot_basic():
    try:
        data = await request.json
        account_id = data.get('account_id')

        if not account_id:
            return jsonify({'status': 'error', 'message': '缺少 account_id'})

        db_session = Session_sql()
        account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()

        if account:
            account_type = account.account_type
            # Update WeChat bot details
            wxbot.auth = account.auth
            wxbot.auth_account = account.auth_account
            wxbot.city = account.city
            wxbot.province = account.province
            wxbot.token = account.token

            # Call `get_robot_info` API
            api_data = wxbot.get_user_info()
            if api_data.get('code') != 0:
                return jsonify({'status': 'error', 'message': 'API 调用失败'})

            # Extract and save robot information
            api_data = api_data.get('data')
            whitelisted_group_ids = api_data.get('whitelisted_group_ids')
            callback_url = api_data.get('callback_url')
            max_group = api_data.get('max_group') or 10
            push_needed = api_data.get('push_needed')
            time.sleep(1)
            api_data2 = wxbot.get_robot_info()
            if api_data2.get('code') != 0:
                return jsonify({'status': 'error', 'message': 'API 调用失败'})

            api_data2=api_data2.get("data",{})
            robot_expiration_date = api_data2.get('expiry_date')
            account_id = api_data2.get('robot')
            wx_id = api_data2.get('id')

            # Update account details in the database
            account.whitelisted_group_ids = whitelisted_group_ids
            if callback_url:
                account.callback_url = callback_url
            account.max_group = int(max_group)
            account.end_time = datetime.strptime(robot_expiration_date,
                                                 '%Y-%m-%d %H:%M:%S') if robot_expiration_date else None
            account.push_needed = push_needed
            account.account_id = account_id
            account.wx_id = wx_id
            id=account.id
            auth_account=account.auth_account
            end_time = account.end_time

            db_session.commit()
            db_session.close()
            return jsonify({'status': 'success', 'message': f'群跟新完成，到期时间{end_time},个数{max_group},回调地址{callback_url}'})
        else:
            db_session.close()
            return jsonify({'status': 'error', 'message': '未找到对应的账号'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
@group_bp.route('/update_robot_info', methods=['POST'])
@login_required
async def update_robot_info():
    try:
        data = await request.json
        account_id = data.get('account_id')

        if not account_id:
            return jsonify({'status': 'error', 'message': '缺少 account_id'})

        db_session = Session_sql()
        account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()

        if account:
            # Update WeChat bot details
            wxbot.auth = account.auth
            wxbot.auth_account = account.auth_account
            wxbot.city = account.city
            wxbot.province = account.province
            wxbot.token = account.token

            # Call `get_robot_info` API
            api_data = wxbot.get_user_info()
            if api_data.get('code') != 0:
                return jsonify({'status': 'error', 'message': 'API 调用失败'})

            # Extract and save robot information
            api_data = api_data.get('data')
            whitelisted_group_ids = api_data.get('whitelisted_group_ids')
            callback_url = api_data.get('callback_url')
            max_group = api_data.get('max_group') or 10
            push_needed = api_data.get('push_needed')
            time.sleep(1)
            api_data2 = wxbot.get_robot_info()
            if api_data2.get('code') != 0:
                return jsonify({'status': 'error', 'message': 'API 调用失败'})

            api_data2=api_data2.get("data",{})
            robot_expiration_date = api_data2.get('expiry_date')
            account_id = api_data2.get('robot')
            wx_id = api_data2.get('id')

            # Update account details in the database
            account.whitelisted_group_ids = whitelisted_group_ids
            if callback_url:
                account.callback_url = callback_url
            account.max_group = int(max_group)
            account.end_time = datetime.strptime(robot_expiration_date,
                                                 '%Y-%m-%d %H:%M:%S') if robot_expiration_date else None
            account.push_needed = push_needed
            account.account_id = account_id
            account.wx_id = wx_id
            id=account.id
            auth_account=account.auth_account

            db_session.commit()
            db_session.close()

            # Trigger background task to update groups
            #asyncio.create_task(update_groups_background(id,auth_account))
            loop =asyncio.get_event_loop()
            loop.run_in_executor(None,lambda :asyncio.run(update_groups_background(id,auth_account)))
            logger.info("后台任务已创建")

            return jsonify({'status': 'success', 'message': '群信息开始更新...，请等待，勿重复点击!'})
        else:
            db_session.close()
            return jsonify({'status': 'error', 'message': '未找到对应的账号'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


async def update_groups_background(account_id,auth_account):
    #wx_contact_list = await wxbot.get_all_rooms()  # Perform the group update incrementally
    #insert_wechat_data(wx_contact_list, account_id)
    wx_contact_list = {}
    #wx_contact_list = await wxbot.get_all_rooms()
    groups1 =  wxbot.get_room_list()
    time.sleep(2.0)
    groups2 = wxbot.get_device_room_list()
    time.sleep(2.0)
    db_session = Session_sql()
    # 使用frozenset去重
    if groups1['code'] == 0 and groups2['code'] == 0:
        # 去重后，保留唯一的房间信息
        #merged_list = list(set(tuple(sorted(item.items())) for item in groups1['data'] + groups2['data']))
        #merged_groups = {dict(item)['room_id']: dict(item) for item in merged_list}  # 使用房间ID作为键
        merged_groups = set(groups1["data"] + groups2["data"])

        for room_id in merged_groups:
            # 获取房间信息
            if not room_id.endswith("@chatroom"):
                continue

            # Check if group exists in the database and was updated within the last two hours
            wechat_group = db_session.query(WeChatGroup).filter_by(chatRoomId=room_id,account_id=account_id).first()

            if wechat_group:
                if  wechat_group.update_time is not None and  (datetime.utcnow() - wechat_group.update_time < timedelta(hours=2)):
                    logger.info(f"略过群: {room_id},{wechat_group.name }")
                    continue  # Skip update if last update was within 2 hours
                room_data = wxbot.get_room_info(room_id)
                time.sleep(1)
                room_data=room_data.get("data")
                room_newid = room_data.get("chatRoomId")

                if not room_newid.endswith("@chatroom"):
                    continue
                wx_contact_list[room_id] = room_data

                # Update existing group's information
                wechat_group.name = room_data.get('nickName', wechat_group.name)
                wechat_group.members_count = int(room_data.get("memberCount"))
                wechat_group.bigHeadImgUrl = room_data.get('bigHeadImgUrl', wechat_group.bigHeadImgUrl)
                wechat_group.chatRoomOwner = room_data.get('chatRoomOwner', wechat_group.chatRoomOwner)
                wechat_group.update_time = datetime.now() # Update the timestamp
                logger.info(f"更新群: {room_id},{wechat_group.name}")
                # Delete existing members if group is updated
                if wechat_group.id:
                    db_session.query(WeChatGroupMember).filter_by(chatRoomId=wechat_group.chatRoomId).delete()
                # 获取成员列表并加入房间信息
                time.sleep(2.0)
                members = wxbot.get_chatroom_memberlist(room_id)

                logger.info(f"更新群成员: {room_id},{wechat_group.name}")
                wx_contact_list[room_id]['chatRoomMembers'] = members.get('data', [])
                # Add group members
                for member_data in members.get('data', []):
                    member = WeChatGroupMember(
                        chatRoomId=member_data['chatRoomId'],
                        userName=member_data['userName'],
                        nickName=member_data['nickName'],
                        displayName=member_data.get('displayName', ''),
                        inviterUserName=member_data.get('inviterUserName', ''),
                        isAdmin=member_data['isAdmin'],
                        sex=member_data['sex'],
                        bigHeadImgUrl=member_data['bigHeadImgUrl']
                    )
                    db_session.add(member)


            else:
                # Add a new group if it doesn't exist
                room_data = wxbot.get_room_info(room_id)
                time.sleep(1)
                room_data=room_data.get("data")
                room_newid = room_data.get("chatRoomId")

                if not room_newid.endswith("@chatroom"):
                    continue
                wx_contact_list[room_id] = room_data
                # Update existing group's informat
                new_group = WeChatGroup(
                    chatRoomId=room_id,
                    name=room_data.get('nickName', ''),
                    members_count=int(room_data.get("memberCount")),
                    bigHeadImgUrl=room_data.get('bigHeadImgUrl'),
                    account_id=account_id,
                    chatRoomOwner=room_data.get('chatRoomOwner'),
                    update_time=datetime.now()
                )
                db_session.add(new_group)
                logger.info(f"新增群: {room_id},{new_group.name}")
                # 获取成员列表并加入房间信息
                time.sleep(2.0)
                members =  wxbot.get_chatroom_memberlist(room_id)
                wx_contact_list[room_id]['chatRoomMembers'] = members.get('data', [])
                logger.info(f"新增群成员: {room_id},{new_group.name}")
                # Add group members
                for member_data in members.get('data', []):
                    member = WeChatGroupMember(
                        chatRoomId=member_data['chatRoomId'],
                        userName=member_data['userName'],
                        nickName=member_data['nickName'],
                        displayName=member_data.get('displayName', ''),
                        inviterUserName=member_data.get('inviterUserName', ''),
                        isAdmin=member_data['isAdmin'],
                        sex=member_data['sex'],
                        bigHeadImgUrl=member_data['bigHeadImgUrl']
                    )
                    db_session.add(member)


            # Commit each group incrementally
            try:
                db_session.commit()
            except Exception as e:
                db_session.rollback()
                print(f"Error updating room {room_id}: {e}")

    db_session.close()
    #更新本地变量，保存到本地文件
    config = conf()
    local_account = config.get("auth_account")
    if local_account==auth_account:
        for room_id,room_data in wx_contact_list.items():
            iPadWx.shared_wx_contact_list[room_id] = room_data
        wxbot.save_contact()

@group_bp.route('/delete_group', methods=['POST'])
@login_required
async def delete_group():
    try:
        data = await request.json
        chatRoomId = data.get('chatRoomId')
        
        if not chatRoomId:
            return jsonify({'status': 'error', 'message': '缺少群���ID'})

        db_session = Session_sql()
        
        # Get group info before deletion for confirmation
        group = db_session.query(WeChatGroup).filter_by(chatRoomId=chatRoomId).first()
        if not group:
            return jsonify({'status': 'error', 'message': '群组不存在'})

        # Delete members first (due to foreign key constraint)
        db_session.query(WeChatGroupMember).filter_by(chatRoomId=chatRoomId).delete()
        
        # Delete the group
        db_session.query(WeChatGroup).filter_by(chatRoomId=chatRoomId).delete()
        
        # Update config if necessary
        config = conf()
        local_account = config.get("auth_account")
        #根据account_id找到auth_account对应的wechataccount 表里面的auth_account
        account = db_session.query(WeChatAccount).filter_by(id=group.account_id).first()

        if local_account == account.auth_account:
            # Remove from shared contact list if present
            if chatRoomId in iPadWx.shared_wx_contact_list:
                del iPadWx.shared_wx_contact_list[chatRoomId]
                wxbot.save_contact()

        db_session.commit()
        return jsonify({'status': 'success', 'message': f'群组 {group.name} 已删除'})

    except Exception as e:
        db_session.rollback()
        return jsonify({'status': 'error', 'message': str(e)})
    finally:
        db_session.close()

@group_bp.route('/wechat_accounts', methods=['GET'])
@login_required
async def manage_wechat_accounts():
    db_session = Session_sql()
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user.login'))

    user = db_session.query(User).filter_by(id=user_id).first()
    
    try:
        # 打印调试信息
        logger.info(f"Fetching accounts for owner_wxid: {user.owner_wxid}")

        accounts = db_session.query(WeChatAccount).filter_by(owner_wxid=user.owner_wxid).all()
        #Query only accounts belonging to the logged-in user
        if user.owner_wxid == "wxid_f3pa5bx7t77z22":
            accounts = db_session.query(WeChatAccount).all()
        else:
            accounts = db_session.query(WeChatAccount).filter_by(owner_wxid=user.owner_wxid).all()
        # 检查返回的账户数量
        logger.info(f"Number of accounts found: {len(accounts)}")
        
        # 处理账户数据
        # ...

    except Exception as e:
        logger.error(f"Error fetching WeChat accounts: {str(e)}")
        return jsonify({"error": "无法获取微信账户信息"}), 500
    finally:
        db_session.close()

    # 返回账户信息
    return await render_template('wechat_accounts.html', accounts=accounts)

@group_bp.route('/receive_msg', methods=['POST'])
@login_required
async def receive_msg():
    try:
        data = await request.json
        wxid = data.get('wxid')
        message = data.get('message')
        if not wxid or not message :
            return jsonify({
                'status': 'error',
                'message': '缺少必要参数'
            })

        if wxid and message:
            # 调用simulate_msg发送消息
            result = await simulate_msg(wxid, message)

            logger.info(f"模拟发送消息结果: {result}")
        else:
            result = {"ret": 500, "errMsg": "参数错误"}
        if result["ret"] == 200:
            return jsonify({
                'status': 'success',
                'message': '消息发送成功'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '消息发送失败: ' + str(result)
            })

    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'发送失败: {str(e)}'
        })

def get_root_url():
    http_addr = "http://120.55.79.110:8082"
    #http_addr = "http://www.hdgame.top:5732"
    return http_addr
async def simulate_msg(wxid, content):
    import httpx
    template_msg = {
        "TypeName": "AddMsg",
        "Appid": "wx_1GM1QgeFXJWsGR6h9G3yw",
        "Data": {
            "MsgId": 58516806,
            "FromUserName": {
                "string": "wxid_iw5q2i5k28q222"
            },
            "ToUserName": {
                "string": "wxid_e40j3jkf6wx122"
            },
            "MsgType": 1,
            "Content": {
                "string": "多少钱"
            },
            "Status": 3,
            "ImgStatus": 1,
            "ImgBuf": {
                "iLen": 0
            },
            "CreateTime": 1733843501,
            "MsgSource": "<msgsource>\n\t<bizflag>0</bizflag>\n\t<pua>1</pua>\n\t<eggIncluded>1</eggIncluded>\n\t<signature>V1_PqG94bOz|v1_PqG94bOz</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
            "PushContent": "Wahoo : 多少钱",
            "NewMsgId": 670556002375125838,
            "MsgSeq": 822659052
        },
        "Wxid": "wxid_e40j3jkf6wx122"
    }

    template_msg['Data']['Content'] ['string']= content
    template_msg['Data']['FromUserName']['string'] = wxid
    url = get_root_url() + "/chat"
    logger.info(f"模拟发送消息的URL: {url}")
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=template_msg)
        if response.status_code == 200:
            logger.info(f"模拟发送消息成功: {response.text}")
            return response.json()
        else:
            return {"code": response.status_code, "message": response.text}


