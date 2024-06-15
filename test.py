
from aligo import set_config_folder, Aligo
# 提供 port 参数即可, 之后打开浏览器访问 http://<YOUR_IP>:<port>
ali = Aligo(port=8080)
set_config_folder('.')
# 创建 Aligo 对象前，先设置配置文件目录，默认是 <用户目录>/.aligo

# 会创建 /home/aligo/小号1.json 配置文件
from aligo import Aligo,set_config_folder
def login_ali():
    set_config_folder('./')
    ali = Aligo(name="zhao_config")  # 第一次使用，会弹出二维码，供扫描登录

login_ali()