# encoding:utf-8
import random
import time
from datetime import datetime

from quart import request, session, flash, redirect, url_for, render_template, jsonify, current_app
from sqlalchemy.exc import PendingRollbackError
from werkzeug.security import generate_password_hash, check_password_hash
from quart import Blueprint, jsonify, request
from common.log import logger
from models import Session_sql, User, WeChatAccount, insert_wechat_data
from config import load_config,conf,save_config
from .decorators import login_required

# 创建蓝图对象
user_bp = Blueprint('user', __name__)

# 添加一个全局字典来缓存wxbot实例
wx_bot_instances = {}

@user_bp.app_template_filter('date_format')
def date_format(value):
    """Convert datetime to date string format."""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime('%Y-%m-%d')

load_config()

channel_name = conf().get("channel_type", "wx")
if channel_name == "wx":
    from channel.wechat.wechat_channel import WechatChannel
    from channel.wechat.iPadWx import iPadWx

    ch = WechatChannel()
    wxbot = iPadWx()


@user_bp.route('/login', methods=['GET', 'POST'])
@user_bp.route('/', methods=['GET', 'POST'])
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
        db_session.rollback()  # 如果��生异常，回滚事务
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
            db_session.rollback()  # 如果发生异常，回滚
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
    db_session = Session_sql()
    account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()
    
    if not account:
        return jsonify({'error': 'Account not found'})

    # 使用原始iPadWx
    from channel.wechat.iPadWx import iPadWx
    wxbot = iPadWx()
    wxbot.auth = account.auth
    wxbot.auth_account = account.auth_account
    wxbot.city = account.city
    wxbot.province = account.province
    wxbot.token = account.token

    # 获取原始版本的二维码
    qr_response = wxbot.get_qrcode(province=account.province, city=account.city)
    if qr_response and qr_response.get('code') == 0:
        qrcode_data = qr_response["data"]["qr"]
        return jsonify({
            'qrcode_data': qrcode_data,
            'is_wx_token': False
        })
    
    return jsonify({'error': '获取登录二维码失败！如果非首次登录，不需要获取二维码，点击二次即可'})

def check_wechat_status_beta(wxbot):
    """Check if WeChat is truly online for iPadWx_Beta"""
    # First check - online status
    status_check = wxbot.check_online()
    if status_check.get('ret') != 200 or not status_check.get('data'):
        return False
    
    # Second check - try sending a message
    test_msg = wxbot.send_txt_msg("filehelper", "Connection test")
    if test_msg.get('ret') != 200:
        return False
    
    return True

@user_bp.route('/check_qr_status_beta', methods=['POST'])
async def check_qr_status_beta():
    data = await request.get_json()
    account_id = data.get('account_id')
    
    # 从缓存中获取wxbot实例
    wxbot = wx_bot_instances.get(account_id)
    if not wxbot:
        return jsonify({
            "status": -1,
            "message": "登录会话已失效，请重新获取二维码"
        })
    
    response = wxbot.check_qr()
    if response and response.get("data"):
        status = response["data"].get("status")
        result = {"status": status}
        
        if status == 2:  # Login confirmed
            login_info = response['data']['loginInfo']
            result.update({
                "nickname": login_info['nickName'],
                "wxid": login_info['wxid'],
                "account_id": account_id  # 添加account_id到返回数据中
            })
            
            # 更新数据库信息
            db_session = Session_sql()
            account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()
            if account:
                account.nickname = login_info['nickName']
                account.wx_id = login_info['wxid']
                account.is_online = True
                db_session.commit()
            
            # 初始化wxbot
            try:
                wxbot.initialize()
            except Exception as e:
                logger.error(f"初始化wxbot失败: {str(e)}")
        
        return jsonify(result)
    
    return jsonify({"status": 0})

@user_bp.route('/check_qr_status_original', methods=['POST'])
async def check_qr_status_original():
    """For original iPadWx check login status"""
    data = await request.get_json()
    account_id = data.get('account_id')
    db_session = Session_sql()
    account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()
    
    if account:
        wxbot.auth = account.auth
        wxbot.auth_account = account.auth_account
        wxbot.city = account.city
        wxbot.province = account.province
        wxbot.token = account.token
        
        response = wxbot.check_qr()
        if response and response.get("data"):
            status = response["data"].get("status")
            result = {"status": status}
            
            if status == 2:  # Login confirmed
                login_info = response['data']['loginInfo']
                result.update({
                    "nickname": login_info['nickName'],
                    "wxid": login_info['wxid']
                })
                
                # Update account information
                account.nickname = login_info['nickName']
                account.wx_id = login_info['wxid']
                db_session.commit()
            
            return jsonify(result)
    
    return jsonify({"status": 0})

@user_bp.route('/confirm_login', methods=['POST'])
async def confirm_login():
    """For original iPadWx manual login confirmation"""
    data = await request.get_json()
    account_id = data.get('account_id')
    db_session = Session_sql()
    account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()
    
    if account and account.account_type ==1:
        from channel.wechat.iPadWx import iPadWx
        wxbot = iPadWx()
        wxbot.auth = account.auth
        wxbot.auth_account = account.auth_account
        wxbot.city = account.city
        wxbot.province = account.province
        wxbot.token = account.token

        result = wxbot.confirm_login()
        if result and result.get('code') == 0:
            return jsonify({'status_code': 200, 'message': 'Login successful'})
        else:
            return jsonify({'status_code': 500, 'message': 'Login failed'})
    
    return jsonify({'status_code': 404, 'message': 'Account not found'})


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
            account_type=1,
            max_group =10
        )

        # 添加操作，事务会隐式在提交或遇到异常时管理
        db_session.add(new_account)

        # 显式提交事务。如果在整个try没有异常，这行会被执行
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
            logger.info(f"callback_url:{account.callback_url}")
            result = wxbot.set_callback_url(account.callback_url)
            logger.info(result)
            if result and (result.get("code") == 0 or result.get("ret") == 0):
                return jsonify({'status_code': 200, 'message': '开启群聊消息回调成功！'})
            else:
                return jsonify({'status_code': 500, 'message': "开启失败，请检查回调地址是否正确！"})
        else:
            return jsonify({'status_code': 500, 'message': '开启群聊消息回调失败，回调地址为空！'})


@user_bp.route('/test_heartbeat', methods=['POST'])
async def test_heartbeat():
    form = await request.json
    account_id = form.get('account_id')
    db_session = Session_sql()
    account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()

    # 使用原始iPadWx
    from channel.wechat.iPadWx import iPadWx
    wxbot = iPadWx()
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


@user_bp.route('/update_robot_info2', methods=['POST'])
async def update_robot_info2():
    try:
        data = await request.json
        id = data.get('account_id')

        if not id:
            return jsonify({'status': 'error', 'message': '缺少 account_id'})
        # 更新数据库
        db_session=Session_sql()
        account = db_session.query(WeChatAccount).filter_by(account_id=id).first()
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
            wx_contact_list = wxbot.get_all_rooms()

            insert_wechat_data(wx_contact_list, account.id)


            db_session.commit()
            db_session.close()

            return jsonify({'status': 'success', 'message': '机器人信息已更新'})
        else:
            db_session.close()
            return jsonify({'status': 'error', 'message': '未找到对应的账号'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})


@user_bp.route('/wechat_accounts', methods=['GET'])
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

        #accounts = db_session.query(WeChatAccount).filter_by(owner_wxid=user.owner_wxid).all()
        # Query only accounts belonging to the logged-in user
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

def check_wechat_status(wxbot):
    """Check if WeChat is truly online through multiple verification steps"""
    # First check - online status
    status_check = wxbot.check_online()
    if status_check.get('ret') != 200 or not status_check.get('data'):
        return False
    
    # Second check - try sending a message
    test_msg = wxbot.send_txt_msg("filehelper", "Connection test")
    if test_msg.get('ret') != 200:
        return False
    
    return True

def get_login_qrcode(wxbot):
    """Get QR code for WeChat login"""
    qr_response = wxbot.get_qrcode()
    if not qr_response or not qr_response.get('data'):
        return None
    
    qrcode_data = qr_response['data'].get('qrImgBase64')
    return qrcode_data



@user_bp.route('/check_qr_status', methods=['POST'])
async def check_qr_status():
    data = await request.get_json()
    account_id = data.get('account_id')
    db_session = Session_sql()
    account = db_session.query(WeChatAccount).filter_by(account_id=account_id).first()
    
    if account:
        wxbot.auth = account.auth
        wxbot.auth_account = account.auth_account
        wxbot.city = account.city
        wxbot.province = account.province
        wxbot.token = account.token
        
        response = wxbot.check_qr()
        if response and response.get("data"):
            status = response["data"].get("status")
            result = {"status": status}
            
            if status == 2:  # Login confirmed
                login_info = response['data']['loginInfo']
                result.update({
                    "nickname": login_info['nickName'],
                    "wxid": login_info['wxid']
                })
                
                # Update account information
                account.nickname = login_info['nickName']
                account.wx_id = login_info['wxid']
                db_session.commit()
            
            return jsonify(result)
    
    return jsonify({"status": 0})

@user_bp.route('/complete_login', methods=['POST'])
async def complete_login():
    """���理登录成功后的操作"""
    data = await request.get_json()
    account_id = data.get('account_id')
    
    # 从缓存中获取已登录的wxbot实例
    wxbot = wx_bot_instances.get(account_id)
    if not wxbot:
        return jsonify({
            'status': 'error',
            'message': '登录会话已失效'
        })
    
    try:
        # 加载联系人信息
        wxbot.load_contact()
        
        # 更新配置
        conf().__setitem__("app_id", wxbot.app_id)
        save_config()
        
        # 清除缓存的wxbot实例
        wx_bot_instances.pop(account_id, None)
        
        return jsonify({
            'status': 'success',
            'message': '登录完成'
        })
    except Exception as e:
        logger.error(f"完成登录时发生错误: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '登录后处理失败'
        })

def process_end_time(end_time):
    if isinstance(end_time, str):
        # 如果是字符串，尝试使用 fromisoformat
        try:
            return datetime.fromisoformat(end_time)
        except ValueError:
            logger.error(f"Invalid ISO format for end_time: {end_time}")
            return None
    elif isinstance(end_time, (int, float)):
        # 如果是时间戳，转换为 datetime
        return datetime.fromtimestamp(end_time)
    else:
        logger.error(f"Unsupported type for end_time: {type(end_time)}")
        return None



