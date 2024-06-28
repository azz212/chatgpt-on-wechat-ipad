import urllib.parse
from channel.wechat.iPadWx import iPadWx
from config import conf,load_config

load_config()
wx = iPadWx()
port = conf().get('wechatipad_port')
http_hook = conf().get('http_hook')
parsed_url = urllib.parse.urlparse(http_hook)
protocol = parsed_url.scheme
domain = parsed_url.netloc.split(':')[0]
port = parsed_url.netloc.split(':')[1]
path = parsed_url.path
port = '5711'
# 组合
combined_url = urllib.parse.urlunparse((protocol, domain + ':' + port, path, '', '', ''))

wx.set_callback_url(combined_url)
