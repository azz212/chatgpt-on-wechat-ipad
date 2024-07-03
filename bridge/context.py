# encoding:utf-8

from enum import Enum


class ContextType(Enum):

    TEXT = 1  # 文本消息
    VOICE = 2  # 音频消息
    IMAGE = 3  # 图片消息
    FILE = 4  # 文件信息
    VIDEO = 5  # 视频信息
    LINK = 6  # 分享链接
    EMOJI=7  #表情图片
    QUOTE=8   #引用消息
    CARD = 9 #微信名片
    IMAGE_CREATE = 10  # 创建图片命令
    MINIAPP = 11 # 小程序
    SYSTEM =12 # 系统消息
    WCPAY = 13 # 微信转账
    MUSIC = 14 #音乐类型
    WECHAT_VIDEO = 15 #视频号
    MP = 16 #微信公众号文字消息
    EXIT_GROUP = 18 #踢出群聊
    LEAVE_GROUP = 19 #主动退出群聊
    JOIN_GROUP = 20  # 加入群聊
    PATPAT = 21  # 拍了拍
    FUNCTION = 22  # 函数调用
    MP_LINK =23  #公众号推文
    XML = 24
    ACCEPT_FRIEND =25
    MAP =26
    SHARING = 27  # 分享信息

    def __str__(self):
        return self.name


class Context:
    def __init__(self, type: ContextType = None, content=None, kwargs=dict()):
        self.type = type
        self.content = content
        self.kwargs = kwargs

    def __contains__(self, key):
        if key == "type":
            return self.type is not None
        elif key == "content":
            return self.content is not None
        else:
            return key in self.kwargs

    def __getitem__(self, key):
        if key == "type":
            return self.type
        elif key == "content":
            return self.content
        else:
            return self.kwargs[key]

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        if key == "type":
            self.type = value
        elif key == "content":
            self.content = value
        else:
            self.kwargs[key] = value

    def __delitem__(self, key):
        if key == "type":
            self.type = None
        elif key == "content":
            self.content = None
        else:
            del self.kwargs[key]

    def __str__(self):
        return "Context(type={}, content={}, kwargs={})".format(self.type, self.content, self.kwargs)
