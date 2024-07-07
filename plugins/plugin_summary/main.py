# encoding:utf-8

import json
import os,re
import time
from bot import bot_factory
from bridge.bridge import Bridge
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_channel import check_contain, check_prefix
from channel.chat_message import ChatMessage
from config import conf
import plugins
from plugins import *
from common.log import logger
from common import const
import sqlite3
from chatgpt_tool_hub.chains.llm import LLMChain
from chatgpt_tool_hub.models import build_model_params
from chatgpt_tool_hub.models.model_factory import ModelFactory
from chatgpt_tool_hub.prompts import PromptTemplate
import xml.etree.ElementTree as ET

TRANSLATE_PROMPT = '''
You are now the following python function: 
```# {{translate text to commands}}"
        def translate_text(text: str) -> str:
```
Only respond with your `return` value, Don't reply anything else.

Commands:
{{Summary chat logs}}: "summary", args: {{("duration_in_seconds"): <integer>, ("count"): <integer>}}
{{Do Nothing}}:"do_nothing",  args:  {{}}

argument in brackets means optional argument.

You should only respond in JSON format as described below.
Response Format: 
{{
    "name": "command name", 
    "args": {{"arg name": "value"}}
}}
Ensure the response can be parsed by Python json.loads.

Input: {input}
'''
def find_json(json_string):
    json_pattern = re.compile(r"\{[\s\S]*\}")
    json_match = json_pattern.search(json_string)
    if json_match:
        json_string = json_match.group(0)
    else:
        json_string = ""
    return json_string
@plugins.register(name="summary", desire_priority=-1,
                  desc="A simple plugin to summary messages", version="0.3.2", author="lanvent")
class Summary(Plugin):
    def __init__(self):
        super().__init__()
        
        try:
            curdir = os.path.dirname(__file__)
            db_path = os.path.join(curdir, "chat.db")
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            c = self.conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS chat_records
                        (sessionid TEXT, msgid INTEGER, user TEXT, content TEXT, type TEXT, timestamp INTEGER,user_id TEXT, room_id TEXT,is_triggered INTEGER,
                        PRIMARY KEY (msgid, user_id))''')

            # 后期增加了is_triggered字段，这里做个过渡，这段代码某天会删除
            # c = c.execute("PRAGMA table_info(chat_records);")
            # column_exists = False
            #
            # for column in c.fetchall():
            #     logger.debug("[Summary] column: {}" .format(column))
            #     if column[1] == 'user_id':
            #         column_exists = True
            #         break
            # if not column_exists:
            #     #self.conn.execute("ALTER TABLE chat_records ADD COLUMN room_id TEXT DEFAULT '';")
            #     #self.conn.execute("UPDATE chat_records SET room_id = '';")
            #
            #     self.conn.execute("ALTER TABLE chat_records ADD COLUMN user_id TEXT DEFAULT '';")
            #     self.conn.execute("UPDATE chat_records SET user_id = '';")
            # self.conn.commit()
            #
            # c = c.execute("PRAGMA table_info(chat_records);")
            # column_exists = False
            # for column in c.fetchall():
            #     logger.debug("[Summary] column: {}".format(column))
            #     if column[1] == 'room_id':
            #         column_exists = True
            #         break
            # if not column_exists:
            #     self.conn.execute("ALTER TABLE chat_records ADD COLUMN room_id TEXT DEFAULT '';")
            #     self.conn.execute("UPDATE chat_records SET room_id = '';")
            #
            # self.conn.commit()

            btype = Bridge().btype['chat']
            # if btype not in [const.OPEN_AI, const.CHATGPT, const.CHATGPTONAZURE, const.LINKAI]:
            #     raise Exception("[Summary] init failed, not supported bot type")
            self.bot = bot_factory.create_bot(Bridge().btype['chat'])
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            self.handlers[Event.ON_RECEIVE_MESSAGE] = self.on_receive_message
            logger.info("[Summary] inited")
        except Exception as e:
            logger.error(f"[summary]初始化异常：{e}")
            raise "[summary] init failed, ignore "
    def _insert_record(self, session_id, msg_id, user, content, msg_type, timestamp,room_id,user_id,is_triggered = 0):
        c = self.conn.cursor()
        logger.debug("[Summary] insert record: {} {} {} {} {} {} {} {} {}" .format(session_id, msg_id, user, content, msg_type, timestamp, room_id,user_id,is_triggered))
        # c.execute("""
        #     INSERT OR REPLACE INTO chat_records
        #     VALUES (:session_id, :msgid, :user, :content, :msg_type, :timestamp, :room_id, :user_id, :is_triggered)
        # """, {
        #     'session_id': session_id,
        #     'msgid': msg_id,
        #     'user': user,
        #     'content': content,
        #     'msg_type': msg_type,
        #     'timestamp': timestamp,
        #     'room_id': room_id,
        #     'user_id': user_id,
        #     'is_triggered': is_triggered
        # })
        # 执行 SQL 插入语句
        try:
            c.execute(
                "INSERT INTO chat_records (sessionid, msgid, user, content, type, timestamp, room_id, user_id, is_triggered) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (session_id, msg_id, user, content, msg_type, timestamp, room_id, user_id, is_triggered))

            #c.execute("INSERT OR REPLACE INTO chat_records VALUES (?,?,?,?,?,?,?,?,?)", (session_id, msg_id, user, content, msg_type, timestamp, room_id,user_id,is_triggered))
            self.conn.commit()
        except Exception as e:
            print(e)

    def _get_records(self, session_id,room_id, start_timestamp=0, limit=9999):

        c = self.conn.cursor()
        if session_id:
            sql = "SELECT * FROM chat_records WHERE user_id=? and room_id=? and timestamp>? ORDER BY timestamp DESC LIMIT ?"
            c.execute(sql, (session_id,room_id, start_timestamp, limit))
        else:
            sql ="SELECT * FROM chat_records WHERE  room_id=? and timestamp>? ORDER BY timestamp DESC LIMIT ?"
            c.execute(
                sql,
                ( room_id, start_timestamp, limit))
        return c.fetchall()

    def on_receive_message(self, e_context: EventContext):
        if e_context['context']['msg'].ctype==ContextType.XML:
            return
        context = e_context['context']
        cmsg : ChatMessage = e_context['context']['msg']

        username = None
        room_id=cmsg.other_user_id
        session_id = cmsg.from_user_id
        user_id =cmsg.from_user_id
        if conf().get('channel_type', 'wx') == 'wx' and cmsg.from_user_id is not None:
            session_id = cmsg.from_user_id # itchat channel id会变动，只好用群名作为session id

        if context.get("isgroup", False):
            username = cmsg.actual_user_nickname
            if username is None:
                username = cmsg.actual_user_id
            room_id = cmsg.other_user_id
        else:
            username = cmsg.from_user_nickname
            if username is None:
                username = cmsg.from_user_id

        is_triggered = False
        content =context.content
        if context.get("isgroup", False): # 群聊
            # 校验关键字
            match_prefix = check_prefix(content, conf().get('group_chat_prefix'))
            match_contain = check_contain(content, conf().get('group_chat_keyword'))
            if match_prefix is not None or match_contain is not None:
                is_triggered = True
            if context['msg'].is_at and not conf().get("group_at_off", False):
                is_triggered = True
        else: # 单聊
            match_prefix = check_prefix(content, conf().get('single_chat_prefix',['']))
            room_id = cmsg.from_user_id
            if match_prefix is not None:
                is_triggered = True
        try:
            self._insert_record(session_id, cmsg.msg_id, username, context.content, str(context.type),
                                cmsg.create_time,room_id,user_id, int(is_triggered))
            # logger.debug("[Summary] {}:{} ({})" .format(username, context.content, session_id))
        except Exception as e:
            print(e)
    def _translate_text_to_commands(self, text):
        llm = ModelFactory().create_llm_model(**build_model_params({
            "openai_api_key": conf().get("open_ai_api_key", ""),
            "proxy": conf().get("proxy", ""),
        }))

        prompt = PromptTemplate(
            input_variables=["input"],
            template=TRANSLATE_PROMPT,
        )
        bot = LLMChain(llm=llm, prompt=prompt)
        content = bot.run(text)
        return content

    def _check_tokens(self, records, max_tokens=3600):
        query = ""
        for record in records[::-1]:
            username = record[2]
            content = record[3]
            if not content:
                continue
            times = record[5]
            is_triggered = record[8]
            if record[4] in [str(ContextType.IMAGE),str(ContextType.VOICE)]:
                content = f"[{record[4]}]"

            sentence = ""

            sentence += f'[{username}][{times}]' + ": \"" + content + "\"\n"
            if is_triggered:
                sentence += " <T>"
            query += "\n\n"+sentence
        prompt = "你是一位群聊机器人，需要对聊天记录进行简明扼要的总结，用列表的形式输出。\n聊天记录格式：[x]是emoji表情或者是对图片和声音文件的说明，消息最后出现<T>表示消息触发了群聊机器人的回复，内容通常是提问，若带有特殊符号如#和$则是触发你无法感知的某个插件功能，聊天记录中不包含你对这类消息的回复，可降低这些消息的权重。请不要在回复中包含聊天记录格式中出现的符号。\n"
        prompt = '''    
        总结群聊记录，群记录格式为[人物A][时间]:内容\n[人物B][时间]:内容\n
        [x]是emoji表情或者是对图片和声音文件的说明，消息最后出现<T>表示消息触发了群聊机器人的回复，若带有特殊符号如#和$则是触发你无法感知的某个插件功能，
        聊天记录中不包含你对这类消息的回复，可降低这些消息的权重。请不要在回复中包含聊天记录格式中出现的符号，要求控制输出的文字少于1000字，话题不要超过4个，超过的部分在其他中简略提及
        主要话题：
        1. 请列出群里讨论的主要话题。
        主要观点：
        - 针对每个主要话题，请总结每个人的主要观点。
            - 人物A：人物A在每个主要话题中的核心观点是什么？
            - 人物B：人物B在每个主要话题中的核心观点是什么？
        ---
        示例：
        ```
        总结群聊记录：
        1. 话题一：社交媒体的影响
            - 小明：认为社交媒体对人际关系有负面影响。
            - 小红：提到社交媒体可以更好地促进信息传播。
        2. 话题二：最新技术发展
            - 小刚：认为人工智能将带来革命性的变化。
            - 小李：关注区块链技术的发展和应用前景。
        这样调整可以确保对聊天记录的总结更清楚，有条理，并且能捕捉到每个人的主要观点和讨论焦点。
        '''

        firstmsg_id = records[0][1]
        session = self.bot.sessions.build_session(firstmsg_id, prompt)

        session.add_query("需要你总结的聊天记录如下：%s"%query)
        if  session.calc_tokens() > max_tokens:
            # logger.debug("[Summary] summary failed, tokens: %d" % session.calc_tokens())
            return None
        return session

    def _split_messages_to_summarys(self, records, max_tokens_persession=3600 , max_summarys=8):
        summarys = []
        count = 0
        self.bot.args["max_tokens"] = 400
        while len(records) > 0 and len(summarys) < max_summarys:
            session = self._check_tokens(records,max_tokens_persession)
            last = 0
            if session is None:
                left,right = 0, len(records)
                while left < right:
                    mid = (left + right) // 2
                    logger.debug("[Summary] left: %d, right: %d, mid: %d" % (left, right, mid))
                    session = self._check_tokens(records[:mid], max_tokens_persession)
                    if session is None:
                        right = mid - 1
                    else:
                        left = mid + 1
                session = self._check_tokens(records[:left-1], max_tokens_persession)
                last = left
                logger.debug("[Summary] summary %d messages" % (left))
            else:
                last = len(records)
                logger.debug("[Summary] summary all %d messages" % (len(records)))
            if session is None:
                logger.debug("[Summary] summary failed, session is None")
                break
            logger.debug("[Summary] session query: %s, prompt_tokens: %d" % (session.messages, session.calc_tokens()))
            result = self.bot.reply_text(session)
            total_tokens, completion_tokens, reply_content = result['total_tokens'], result['completion_tokens'], result['content']
            logger.debug("[Summary] total_tokens: %d, completion_tokens: %d, reply_content: %s" % (total_tokens, completion_tokens, reply_content))
            if completion_tokens == 0:
                if len(summarys) == 0:
                    return count,reply_content
                else:
                    break
            summary = reply_content
            summarys.append(summary)
            records = records[last:]
            count += last
        return count,summarys


    def on_handle_context(self, e_context: EventContext):

        if e_context['context'].type == ContextType.TEXT:

        
            content = e_context['context'].content

            logger.debug("[Summary] on_handle_context. content: %s" % content)
            trigger_prefix = conf().get('plugin_trigger_prefix', "$")
            clist = content.split()
            if clist[0].startswith(trigger_prefix):
                limit = 99
                duration = -1

                if "总结" in clist[0]:
                    flag = False
                    if trigger_prefix+"总结" in clist[0]:
                        flag = True
                        if len(clist) > 1:
                            try:
                                limit = int(clist[1])
                                logger.debug("[Summary] limit: %d" % limit)
                            except Exception as e:
                                flag = False
                    if not flag:
                        if trigger_prefix =="":
                            split_char = " "
                        else:
                            split_char =trigger_prefix
                        text = content.split(split_char,maxsplit=1)[1]
                        try:
                            command_json = find_json(self._translate_text_to_commands(text))
                            command = json.loads(command_json)
                            name = command["name"]
                            if name.lower() == "summary":
                                limit = int(command["args"].get("count", 99))
                                if limit < 0:
                                    limit = 299
                                duration = int(command["args"].get("duration_in_seconds", -1))
                                logger.debug("[Summary] limit: %d, duration: %d seconds" % (limit, duration))
                        except Exception as e:
                            logger.error("[Summary] translate failed: %s" % e)
                            return
                else:
                    return

                start_time = int(time.time())
                if duration > 0:
                    start_time = start_time - duration
                else:
                    start_time = 0



                msg:ChatMessage = e_context['context']['msg']
                session_id = msg.from_user_id
                if clist[0]=="总结":
                    session_id = msg.from_user_id
                elif "总结" in content and "所有人" in content:
                    session_id= ''
                room_id = msg.other_user_id
                #if conf().get('channel_type', 'wx') == 'wx' and msg.from_user_nickname is not None:
                #    session_id = msg.from_user_nickname # itchat channel id会变动，只好用名字作为session id
                records = self._get_records(session_id,room_id, start_time, limit)
                for i in range(len(records)):
                    record=list(records[i])
                    content = record[3]
                    if content:
                        clist = re.split(r'\n- - - - - - - - -.*?\n', content)
                        if len(clist) > 1:
                            record[3] = clist[1]
                            records[i] = tuple(record)
                if len(records) <= 1:
                    reply = Reply(ReplyType.INFO, "无聊天记录可供总结")
                    e_context['reply'] = reply
                    e_context.action = EventAction.BREAK_PASS
                    return

                max_tokens_persession = 3600

                count, summarys = self._split_messages_to_summarys(records, max_tokens_persession)
                if count == 0 :
                    if isinstance(summarys,str):
                        reply = Reply(ReplyType.ERROR, summarys)
                    else:
                        reply = Reply(ReplyType.ERROR, "总结聊天记录失败")
                    e_context['reply'] = reply
                    e_context.action = EventAction.BREAK_PASS
                    return


                if len(summarys) == 1:
                    reply = Reply(ReplyType.TEXT, f"本次总结了{count}条消息。\n\n"+summarys[0])
                    e_context['reply'] = reply
                    e_context.action = EventAction.BREAK_PASS
                    return

                self.bot.args["max_tokens"] = None
                query = ""
                for i,summary in enumerate(reversed(summarys)):
                    query += summary + "\n----------------\n\n"
                prompt = "你是一位群聊机器人，聊天记录已经在你的大脑中被你总结成多段摘要总结，你需要对它们进行摘要总结，最后输出一篇完整的摘要总结，用列表的形式输出。\n"

                session = self.bot.sessions.build_session(session_id, prompt)
                session.add_query(query)
                result = self.bot.reply_text(session)
                total_tokens, completion_tokens, reply_content = result['total_tokens'], result['completion_tokens'], result['content']
                logger.debug("[Summary] total_tokens: %d, completion_tokens: %d, reply_content: %s" % (total_tokens, completion_tokens, reply_content))
                if completion_tokens == 0:
                    reply = Reply(ReplyType.ERROR, "合并摘要失败，"+reply_content+"\n原始多段摘要如下：\n"+query)
                else:
                    reply = Reply(ReplyType.TEXT, f"本次总结了{count}条消息。\n\n"+reply_content)
                e_context['reply'] = reply
                e_context.action = EventAction.BREAK_PASS # 事件结束，并跳过处理context的默认逻辑

        elif e_context['context'].type == ContextType.QUOTE:
            content = e_context['context'].content
            if isinstance(content, str):
                command = content.split(" ")

                if command[0] in ['总结文章',"总结这篇文章","总结一下","分析","分析一下",'总结']:
                    url =command[1]
                    logger.info(f"要总结的文章链接：{url}")
                    prompt = "你是一个文章总结专家，请总结下面这个URL的文章:"
                    reply = Reply(ReplyType.TEXT, prompt+url)
                    e_context['reply'] = reply
                    e_context['context'].content = prompt+url
                    e_context['context'].type =ContextType.TEXT
                    e_context.action = EventAction.BREAK



    def get_help_text(self, verbose = False, **kwargs):
        help_text = "聊天记录总结插件。\n"
        if not verbose:
            return help_text
        trigger_prefix = conf().get('plugin_trigger_prefix', "$")
        help_text += f"使用方法:输入\"{trigger_prefix}总结 最近消息数量\"，我会帮助你总结聊天记录。\n例如：\"{trigger_prefix}总结 100\"，我会总结最近100条消息。\n\n你也可以直接输入\"{trigger_prefix}总结前99条信息\"或\"{trigger_prefix}总结3小时内的最近10条消息\"\n我会尽可能理解你的指令。"
        return help_text
