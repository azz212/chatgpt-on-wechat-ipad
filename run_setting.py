
from channel.wechat.iPadWx import iPadWx
from config import conf,load_config

load_config()
wx = iPadWx()
port = conf().get('wechatipad_port')
port = '5711'
print(port)
http_hook = conf().get('http_hook')
print(http_hook)
wx.set_callback_url(http_hook)
