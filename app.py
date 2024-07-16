# encoding:utf-8

import os
import signal
import sys
import time

from channel import channel_factory
from common import const
from config import load_config
from plugins import *
import threading
from quart import jsonify,render_template,send_file
import concurrent.futures
import asyncio
from channel.wechat.wechat_message import *
from channel.wechat.wechat_channel import message_handler,WechatChannel

from quart import Quart, request, Response
import traceback
quart_app = Quart(__name__)
max_worker = 5


def sigterm_handler_wrap(_signo):
    old_handler = signal.getsignal(_signo)

    def func(_signo, _stack_frame):
        logger.info("signal {} received, exiting...".format(_signo))
        conf().save_user_datas()
        if callable(old_handler):  #  check old_handler
            return old_handler(_signo, _stack_frame)
        sys.exit(0)

    signal.signal(_signo, func)


def start_channel(channel_name: str):
    channel = channel_factory.create_channel(channel_name)
    if channel_name in ["wx", "wxy", "terminal", "wechatmp", "wechatmp_service", "wechatcom_app", "wework",
                        const.FEISHU, const.DINGTALK]:
        PluginManager().load_plugins()

    if conf().get("use_linkai"):
        try:
            from common import linkai_client
            threading.Thread(target=linkai_client.start, args=(channel,)).start()
        except Exception as e:
            pass
    channel.startup()


def run():

    try:
        # load config
        load_config()
        # ctrl + c
        sigterm_handler_wrap(signal.SIGINT)
        # kill signal
        sigterm_handler_wrap(signal.SIGTERM)

        # create channel
        channel_name = conf().get("channel_type", "wx")

        if "--cmd" in sys.argv:
            channel_name = "terminal"

        if channel_name == "wxy":
            os.environ["WECHATY_LOG"] = "warn"

        start_channel(channel_name)

        #while True:
        #    time.sleep(1)
    except Exception as e:
        logger.error("App startup failed!")
        logger.exception(e)
run()

@quart_app.route("/chat", methods=["POST"])
async def chat():
    # 绫诲父閲�
    FAILED_MSG = '{"success": false}'
    SUCCESS_MSG = '{"success": true}'
    MESSAGE_RECEIVE_TYPE = "8001"

    ch = WechatChannel()
    try:
        try:
            msg = await request.get_json()
            logger.debug(f"[Wechat] receive request: {msg}")
        except Exception as e:
            logger.error(e)
            return FAILED_MSG


        try:
            cmsg = WechatMessage(msg, True)
        except NotImplementedError as e:
            logger.debug("[WX]group message {} skipped: {}".format(msg["msg_id"], e))
            return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_worker):
            asyncio.create_task(
                #.handle_group(cmsg)
                message_handler(cmsg, ch)
            ).add_done_callback(callback)


        # return a response
        return Response("Message received", mimetype='text/plain')

    except Exception as error:
        logger.error("".join(traceback.format_exc()))
        traceback.print_exc()
        logger.error(f"An error occurred: {error}")

        return Response(str(error), mimetype='text/plain')

@quart_app.route('/pic/<path:filename>')
async def serve_pic(filename):
    return await send_file(f'pic/{filename}')
def callback(worker):
    worker_exception = worker.exception()
    if worker_exception:
        logger.error(worker_exception)
@quart_app.route("/rooms", methods=["GET"])
def rooms():

    response_data = iPadWx().get_room_list()  # assuming this returns a list of room names
    data = response_data.get("data")
    if data:
        if isinstance(data,dict):

            return render_template('dict.html', data=data)
        elif isinstance(data,list):
            #return render_template('list.html', data=data)
            return jsonify(data)
        else:
            return jsonify({"code": 0,"response":"绛惧埌鎴愬姛"})
    return jsonify({"code": -1,"response":"鑾峰彇鎴块棿鍒楄〃澶辫触"})
@quart_app.route("/send_msg", methods=["GET"])
def send_msg():
    to_id = request.args.get('to_id')
    text = request.args.get('text')
    at_id = request.args.get('at_id')
    

    if not to_id or not text:
        return jsonify({"code": -1, "message": "Both 'to_id' and 'text' parameters are required."}), 400
    if at_id:
        
        displayName,nickname = iPadWx().get_chatroom_nickname(to_id,at_id)
        content = "@"+nickname+" "+text
        result = iPadWx().send_at_msg(to_id=to_id,at_ids=at_id,nickname=nickname, content=content)
    else:
        result = iPadWx().send_txt_msg(to_id=to_id, text=text)
    if result:
        return jsonify({"code": 0, "message": "Message sent successfully."})
    else:
        return jsonify({"code": -1, "message": "Failed to send message."}), 500


if __name__ == "__main__":
    '''
    todo 1 灏唚eb妗嗘灦淇�敼涓篺lask 鎴栬€匭uart OK
    todo 2 鎺ユ敹鍥剧墖鏃跺垽鏂�槸鍚︿负绌猴紝濡傛灉涓虹┖锛屽垯鍙戦€佹彁閱� OK
    todo 3 鍙戦€佽秴杩�1024鏃讹紝瑕佸垎娈靛彂閫�
    todo 4 鐢诲浘鏃讹紝缁撴灉鍙�互at 骞舵樉绀烘彁绀鸿瘝銆倅es
    todo 5 鐢诲浘鏃讹紝鍏堝彂閫佷竴涓�瓑寰呮秷鎭�紝鎻愮ず姝ｅ湪澶勭悊涓� NA
    todo 6 help鍜岃彍鍗曞姛鑳�
    todo 7 澶氫釜API鎺ュ叆鐐癸紝濡備綍鍒囨崲鍜屾�鏌ラ敊璇�紝涓诲姩灞忚斀缁忓父涓嶅彲鐢ㄦ湇鍔″櫒 銆� 鍔熻兘鍜屾ā鍨嬪�搴�
    todo 8 閮ㄧ讲鍒伴�娓�湇鍔″櫒
    
    '''
    port = conf().get("wechatipad_port", 5711)
    quart_app.run("0.0.0.0", port, use_reloader=False,debug=True)


