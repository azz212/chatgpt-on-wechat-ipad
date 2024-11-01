# encoding:utf-8
import random
import time
from datetime import datetime
from sqlalchemy.exc import PendingRollbackError#
from quart import request, session, flash, redirect, url_for, render_template, jsonify
from sqlalchemy.exc import PendingRollbackError
from werkzeug.security import generate_password_hash, check_password_hash
from quart import Blueprint, jsonify, request
from common.log import logger
from models import Session_sql, User, WeChatAccount, insert_wechat_data
from config import load_config,conf,save_config
# 创建蓝图对象
user_bp = Blueprint('user', __name__)
load_config()

channel_name = conf().get("channel_type", "wx")
if channel_name == "wx":
    from channel.wechat.wechat_channel import WechatChannel
    from channel.wechat.wechat_message import WechatMessage
    from channel.wechat.wechat_channel import message_handler
    from channel.wechat.iPadWx import iPadWx

    ch = WechatChannel()
    wxbot = iPadWx()


@user_bp.route('/login', methods=['GET', 'POST'])

async def login():
    if request.method == 'POST':
        data = await request.form
        username = data.get('username')
        password = data.get('password')
        user = authenticate(username, password)
        if user:
            session['user_id'] = user.id
            await flash('登录成功！', 'success')
            return redirect(url_for('user.manage_wechat_accounts'))
        else:
            await flash('用户名或密码错误！', 'error')
            return await render_template('login.html')
    return await render_template('login.html')


def authenticate(username, password):
    # user = User.query.filter_by(username=username).first()
    db_session=Session_sql()
    user = db_session.query(User).filter_by(username=username).first()
    # 在你的路由或函数中
    try:
        # 数据库操作
        db_session.commit()  # 提交事务
    except Exception as e:
        db_session.rollback()  # 如果发生异常，回滚事务
        if isinstance(e, PendingRollbackError):
            logger.info("检测到PendingRollbackError，事务已回滚。请检查并处理导致事务失败的原因。")
        else:
            logger.info("发生异常1，事务已回滚。请检查并处理导致事务失败的原因。")
            raise  # 如果不是PendingRollbackError，再次抛出异常以便上层处理
    if user:
        logger.info(f"Stored hash: {user.password}")
        logger.info(f"Input password: {password}")
        logger.info(f"Generated hash: {generate_password_hash(password)}")
        check_result = check_password_hash(user.password, password)
        logger.info(f"Check result: {check_result}")
        if check_result:
            return user
        return None


@user_bp.route('/logout')
async def logout():
    # Implement your logout logic here
    # For example, clearing db_session data
    return redirect('/login')


@user_bp.route('/initialize_user', methods=['POST'])
async def initialize_user():
    data = await request.get_json()
    account_id = data.get('account_id')
    db_session = Session_sql()
    account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()

    if account:
        wxbot.auth_account = account.auth_account
        wxbot.auth_password = account.auth_password

        wxbot.city = account.city
        wxbot.province = account.province

        wxbot.auth = account.auth
        wxbot.token = account.token
        if not account.auth_account or not account.auth_password:
            return jsonify({'failed': '初始化失败！请先录入用户名，密码'})

    # Replace this with the actual logic to fetch user data
    user_data = {
    }
    # Call your method to create a user
    ret, data = wxbot.login()
    if ret:
        account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()

        token = data.get("token")
        auth = data.get("auth")
        account.auth = auth
        account.token = token
        config = conf()
        local_account = config.get("auth_account")
        try:
            # 尝试执行数据库操作
            db_session.commit()  # 提交事务
            # 尝试保存到配置中,如果用户名一样的话
            if local_account==account.auth_account or local_account=="":
                config.__setitem__("token", token)
                config.__setitem__("auth", auth)
                config.__setitem__("auth_account", account.auth_account)
                config.__setitem__("auth_password", account.auth_password)
                save_config()

        except Exception as e:
            db_session.rollback()  # 如果发生异常，回滚事务
            if isinstance(e, PendingRollbackError):
                print("检测到PendingRollbackError，事务已回滚。请检查并处理导致事务失败的原因。")
            else:
                raise  # 如果不是PendingRollbackError，再次抛出异常以便上层处理
            return jsonify({'failed': '初始化失败！'})

    result = wxbot.create_user(user_data)
    if result['code'] == 0:

        return jsonify({'status_code': 200, 'message': '初始化成功！'})
    else:
        return jsonify({'status_code': 500, 'message': result['message']})
    # return redirect(url_for('initialize_user'))  # Adjust this to your main page


@user_bp.route('/get_qrcode/<account_id>', methods=['GET'])
def get_qrcode_route(account_id):
    # qrcode_data = get_qrcode(province=None, city=None)  # Modify this as needed
    db_session=Session_sql()
    account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()
    if account:
        wxbot.auth = account.auth
        wxbot.auth_account = account.auth_account
        wxbot.city = account.city
        wxbot.province = account.province
        wxbot.token = account.token
        # ret=wxbot.confirm_login()
        ret = None
        logger.info(ret)
        if ret:
            if ret["code"] == 0:
                return jsonify({'success': '二次登录成功！'})

        qrcode_data = wxbot.get_qrcode(province=account.province, city=account.city)  # Modify this as needed
        # qrcode_data = '''
        # data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAQIAAAECAQMAAAAvgUsTAAAABlBMVEX///8AAABVwtN+AAAACXBIWXMAAA7EAAAOxAGVKw4bAAAB5UlEQVRoge2YYarEIAyEAx7AI3l1j+QBhKyZibbl7d+FN1Dplm79+iMkmSSavetdP1/N1xqtjPXQrXoZ8bLEW5cj1i+2R9zXFe82J0csw2jqrH1x66EMfiNKLAu57bOGz6SJghCc1ibuogSjEHt0XvsepwrEUYfH9VU//juxbV4WLudt4+3PkiDKyR84jM4LjTjWyhAZf+v/NFt7K6MitSAWcgQCsZe0sE/EZUFoqhEGIaBAoI7GdkcgyhGx4cgl3C0qENXh5lsRIuqoZaNznGf3KNQh7hrdzj246moE3HbqqKXG+T1OdQhay+bAKq3tzjZOjGi5Z9TriEjquOsRkVFsPaMIgaCI24lCHcKjjjZMOJ5dNXxJy7UINAQGpe50Hkedy3MyBIrorkN7MIiBB82oFhGdgWPgpP9QhyL+bv2pCtGQSM4Hq6nXzDE5grWTJzXZeo7dUgsSMRUM9m2RXZzcrjjVIegtNp0MR8qcX6eBOgQvdDk8fsqeoHY9gmNnWIsG2tPsu+dEiORQRI2DDcXiqqYyRGPhhCIYIjLPOx7qIEKY7W3U1MgojgSCBG0zTJvzKMVjKhAjCPFAcKKa6hLZ3NSeM1sOomKE7aYto5Df4ChNjqA62B44EYI5GKgR73rXT9cHm0MkB/PYTzMAAAAASUVORK5CYII=
        # '''
        # return jsonify({'qrcode_data': qrcode_data})
        logger.info(qrcode_data)
        if qrcode_data['code'] == 0:
            qrcode_data = qrcode_data["data"]["qr"]  # 获取二维码图像数据
            print(qrcode_data)
            # qrcode_data_base64 = base64.b64encode(qrcode_data).decode('utf-8')  # 转换为Base64
            return jsonify({'qrcode_data': qrcode_data})
        else:
            return jsonify({'error': '请检查是否真的掉线了，不掉线不用扫二维码！'})
    else:
        return jsonify({'error': 'Account not found'})


@user_bp.route('/confirm_login', methods=['POST'])
async def confirm_login():
    data = await request.get_json()
    account_id = data.get('account_id')
    db_session = Session_sql()
    # qrcode_data = get_qrcode(province=None, city=None)  # Modify this as needed
    account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()
    if account:
        wxbot.auth = account.auth
        wxbot.auth_account = account.auth_account
        wxbot.city = account.city
        wxbot.province = account.province
        wxbot.token = account.token

        reault = wxbot.confirm_login()
        print(reault)
        return jsonify({'status_code': 200, 'message': 'Login successful'})


@user_bp.route('/relogin', methods=['POST'])
async def relogin():
    data = await request.get_json()
    account_id = data.get('account_id')
    db_session = Session_sql()
    # qrcode_data = get_qrcode(province=None, city=None)  # Modify this as needed
    account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()
    if account:
        logger.info("开始二次登录")
        wxbot.auth = account.auth
        wxbot.auth_account = account.auth_account
        wxbot.city = account.city
        wxbot.province = account.province
        wxbot.token = account.token

        result = wxbot.relogin()
        if result['code']==0:
            logger.info("二次登录成功")
        logger.info(result)
        if result:
            if result['code'] == 0:
                return jsonify({'status_code': 200, 'message': '二次登录成功！'})
            else:
                return jsonify({'status_code': 500, 'message': result['message']})
        else:
            return jsonify({'status_code': 500, 'message': '二次登录失败！'})


@user_bp.route('/add_wechat_account', methods=['POST'])
async def add_wechat_account():
    try:
        # 尝试创建并添加新账户
        data = await request.get_json()
        db_session = Session_sql()
        existing_user = db_session.query(User).filter_by(username=data['auth_account']).first()
        if not existing_user:
            # Use generate_password_hash from werkzeug.security to generate the hash
            hashed_password = generate_password_hash("123456")
            new_user = User(username=data['auth_account'], password=hashed_password, owner_wxid=data['auth_account'])
            db_session.add(new_user)
        new_account = WeChatAccount(
            account_id=data['auth_account'],
            wx_id=data['auth_account'],
            owner_wxid = data['auth_account'],
            auth_account=data['auth_account'],
            auth_password=data['auth_password'],
            province=data['province'],
            city=data['city'],
            callback_url=data['callback_url'],
            max_group =10
        )

        # 添加操作，事务会隐式在提交或遇到异常时管理
        db_session.add(new_account)

        # 显式提交事务。如果在整个try块没有异常，这行会被执行
        db_session.commit()



    except Exception as e:
        # 捕获所有其他异常
        logger.error(f'An error occurred while adding account: {e}')
        db_session.rollback()  # 确保事务回滚
        return jsonify({'status': 'error', 'message': '添加账号时发生未知错误', 'details': str(e)})

    finally:
        # 无论事务是否成功，都确保session关闭
        db_session.close()

    # 如果没有异常，则操作成功
    return jsonify({'status': 'success', 'message': '账号添加成功'})


@user_bp.route('/startlisten', methods=['POST'])
async def startlisten():
    data = await request.get_json()
    account_id = data.get('account_id')
    db_session = Session_sql()
    # qrcode_data = get_qrcode(province=None, city=None)  # Modify this as needed
    account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()
    if account:
        wxbot.auth = account.auth
        wxbot.auth_account = account.auth_account
        wxbot.city = account.city
        wxbot.province = account.province
        wxbot.token = account.token

        reault = wxbot.start_listen()
        print(reault)
        wxbot.filter_msg()
        if account.callback_url:
            result = wxbot.set_callback_url(account.callback_url)
            if result['code'] == 0:
                return jsonify({'status_code': 200, 'message': '开启群聊消息回调成功！'})
            else:
                return jsonify({'status_code': 500, 'message': result['message']})
        else:
            return jsonify({'status_code': 500, 'message': '开启群聊消息回调失败，回调地址为空！'})


@user_bp.route('/test_heartbeat', methods=['POST'])
async def test_heartbeat():
    form = await request.json
    account_id = form.get('account_id')
    db_session = Session_sql()
    account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()
    if account:
        wxbot.auth = account.auth
        wxbot.auth_account = account.auth_account
        wxbot.city = account.city
        wxbot.province = account.province
        wxbot.token = account.token

        to_wxid = "filehelper"  # Replace with the actual wx_id
        content = "Test message " + str(random.randint(0, 100))

        result = wxbot.send_txt_msg(to_wxid, content)  # Assume this returns a status code

        # Return the status code in the response
        if result['code'] == 0:
            return jsonify({'status_code': 200})
        else:
            return jsonify({'status_code': 500})  # or any other code that indicates failure


@user_bp.route('/scan_qr', methods=['POST'])
async def scan_qr():
    form = await request.form
    account_id = form.get('account_id')

    # Initialize wxbot with the appropriate credentials or context
    # wxbot = None  # Replace with your actual wxbot initialization
    # success = login_proc(wxbot)
    # 获取登录二维码
    qr = wxbot.get_qrcode()
    if qr and qr.get("data"):
        wxbot.generate_qr_code_html(qr['data']['qrImgBase64'], "qrkh.html")
        # 循环检测扫码状态
        while True:
            response = wxbot.check_qr()
            if response and response.get("data"):
                status = response["data"].get("status")
                if status == 1:
                    logger.info("二维码已被扫码")
                elif status == 2:
                    logger.info("登录已确认")
                    return True

                elif status == 0:
                    logger.info("等待扫码...")
            time.sleep(5)  # 每5秒检测一次
    return False

    # Handle the success or failure of the login process
    return redirect(url_for('index'))


@user_bp.route('/contacts')
async def contacts():
    # 假设您有一个函数来获取联系人列表
    contacts =None # get_contacts()  # 获取联系人数据
    return await render_template('contacts.html', contacts=contacts)


def add_user(username, password, wx_id):
    db_session = Session_sql()
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


@user_bp.route('/update_robot_info', methods=['POST'])
async def update_robot_info():
    try:
        data = await request.json
        id = data.get('id')

        if not id:
            return jsonify({'status': 'error', 'message': '缺少 account_id'})
        # 更新数据库
        db_session=Session_sql()
        account = db_session.query(WeChatAccount).filter_by(id=id).first()
        if account:
            wxbot.auth = account.auth
            wxbot.auth_account = account.auth_account
            wxbot.city = account.city
            wxbot.province = account.province
            wxbot.token = account.token

            # 调用 get_robot_info API
            api_data = wxbot.get_user_info()
            if api_data.get('code') != 0:
                return jsonify({'status': 'error', 'message': 'API 调用失败'})
            api_data = api_data.get('data')
            api_data2 = wxbot.get_robot_info()
            if api_data2.get('code') != 0:
                return jsonify({'status': 'error', 'message': 'API 调用失败'})
            api_data2 = api_data2.get('data')
            # 从返回的数据中提取所需信息
            whitelisted_group_ids = api_data.get('whitelisted_group_ids')
            callback_url = api_data.get('callback_url')
            max_group = api_data.get('max_group') or 10
            push_needed = api_data.get('push_needed')

            robot_expiration_date = api_data2.get('expiry_date')
            account_id = api_data2.get('robot')
            wx_id = api_data2.get('id')

            account.whitelisted_group_ids = whitelisted_group_ids
            if callback_url:
                account.callback_url = callback_url
            account.max_group = int(max_group) if max_group else 10
            account.end_time = datetime.strptime(robot_expiration_date, '%Y-%m-%d %H:%M:%S') if robot_expiration_date else None
            account.push_needed = push_needed
            account.account_id = account_id
            account.wx_id = wx_id
            #wxbot.get_rooms()
            insert_wechat_data(iPadWx.shared_wx_contact_list,account.id)

            db_session.commit()
            db_session.close()

            return jsonify({'status': 'success', 'message': '机器人信息已更新'})
        else:
            db_session.close()
            return jsonify({'status': 'error', 'message': '未找到对应的账号'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@user_bp.route('/wechat_accounts', methods=['GET', 'POST'])

async def manage_wechat_accounts():
    db_session = Session_sql()
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not authenticated

    user = db_session.query(User).filter_by(id=user_id).first()
    # # 在你的路由或函数中
    # try:
    #     # 数据库操作
    #     db_session.commit()  # 提交事务
    # except Exception as e:
    #     db_session.rollback()  # 如果发生异常，回滚事务
    #     if isinstance(e, PendingRollbackError):
    #         print("检测到PendingRollbackError，事务已回滚。请检查并处理导致事务失败的原因。")
    #     else:
    #         raise  # 如果不是PendingRollbackError，再次抛出异常以便上层处理

    if request.method == 'POST':
        data = await request.form
        account_id = data.get('account_id')

        # Add account to the database associated with the user
        new_account = WeChatAccount(account_id=account_id, is_online=False, owner_wxid=user.owner_wxid)
        db_session.add(new_account)
        try:
            # 尝试执行数据库操作
            db_session.commit()  # 提交事务
        except Exception as e:
            db_session.rollback()  # 如果发生异常，回滚事务
            if isinstance(e, PendingRollbackError):
                print("检测到PendingRollbackError，事务已回滚。请检查并处理导致事务失败的原因。")
            else:
                raise  # 如果不是PendingRollbackError，再次抛出异常以便上层处理

    # Query only accounts belonging to the logged-in user
    if user.username == "admin":
        accounts = db_session.query(WeChatAccount).all()
    else:
        accounts = db_session.query(WeChatAccount).filter_by(owner_wxid=user.owner_wxid).all()
    return await render_template('wechat_accounts.html', title='WeChat Management', active='wechat', accounts=accounts)
