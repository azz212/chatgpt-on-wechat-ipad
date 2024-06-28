# encoding:utf-8

from enum import Enum
from collections import defaultdict
from typing import List, Union
class ReplyType(Enum):
    TEXT = 1  # 文本
    VOICE = 2  # 音频文件
    IMAGE = 3  # 图片文件
    IMAGE_URL = 4  # 图片URL
    VIDEO_URL = 5  # 视频URL
    FILE = 6  # 文件
    CARD = 7  # 微信名片，仅支持ntchat
    INVITE_ROOM = 8  # 邀请好友进群
    INFO = 9
    ERROR = 10
    TEXT_ = 11  # 强制文本
    VIDEO = 12
    MINIAPP = 13  # 小程序
    LINK = 14  # 链接
    CALL_UP = 15  # 打电话
    GIF = 16  # 发动图
    def __str__(self):
        return self.name


class Reply:
    '''
    增加ext信息，回复可能是多种形式，有可能是图片，文字，或者图片+文字
    '''
    def __init__(self, type: ReplyType = None, content=None,ext =None):
        self.type = type
        self.content = content
        self.ext = ext

    def __str__(self):
        return "Reply(type={}, content={}，ext= {})".format(self.type, self.content,self.ext)

class Reply2:
    def __init__(self, types:  Union[ReplyType, List[ReplyType]] = None, content: List[str] = None, ext: List[str] = None):
        if isinstance(types, ReplyType):
            types = [types]  # 将单个类型转换为列表
        if content is None:
            content = []  # 默认内容为空列表
        if ext is None:
            ext = []  # 默认扩展信息为空列表
        self.types = types  # 注意这里属性名改为复数形式 types
        self.content = content
        self.ext = ext

    def add_content(self, content_item):
        self.content.append(content_item)

    def add_ext(self, ext_item):
        self.ext.append(ext_item)

    def add_type(self, reply_type: ReplyType):
        if self.types is None:
            self.types=[]
        self.types.append(reply_type)
    def __str__(self):
        # 检查 self.types 是否为 None，如果是，则初始化为空列表
        if self.types is None:
            types_str = 'None'
        else:
            # 将类型列表转换为可读的字符串形式
            types_str = ', '.join(type_.name for type_ in self.types)

        # 格式化字符串，使用合适的占位符
        return "Reply(types=[{}], content={}, ext={})".format(types_str, self.content, self.ext)

