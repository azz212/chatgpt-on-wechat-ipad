# 简介

> chatgpt-on-wechat-ipad （简称CoW）修改于chatgpt-on-wechat ，底层将itchat替换为ipad协议版本。更安全和更普遍，并修改大量功能
> 项目是基于大模型的智能对话机器人，支持微信公众号、企业微信应用、飞书、钉钉接入，可选择GPT3.5/GPT4.0/Claude/Gemini2.0/LinkAI/ChatGLM/KIMI/文心一言/讯飞星火/通义千问/LinkAI/dify/，能处理文本、语音和图片，通过插件访问操作系统和互联网等外部资源，支持基于自有知识库定制企业AI应用。

最新版本支持的功能如下：
-  ✅   **具备原COW所有功能并保持更新：** 私聊及群聊的消息智能回复，支持多轮会话上下文记忆，支持 GPT-3.5, GPT-4, GPT-4o, Claude-3, Gemini, 文心一言, 讯飞星火, 通义千问，ChatGLM-4，Kimi(月之暗面)
-  ✅   **智能客服：** 智能聊天，智能客服，支持Dify,Maxkb(可自建知识库无限制）
-  ✅   **基础功能：** 自动同意好友，进群欢迎，天气，关键字触发
-  ✅   **插件功能丰富：** 看图猜成语，早报，定时任务，疯狂星期4文案，画图
-  ✅   **图像能力：** 支持图片生成、图片识别、图生图（如照片修复），可选择 Dall-E-3, stable diffusion, replicate, midjourney, CogView-3, vision模型
-  ✅   **丰富插件：** 支持个性化插件扩展，敏感词过滤、聊天记录总结、文档总结和对话、联网搜索，看图猜成语，KFC，早报，热榜等非常多的娱乐插件

<p>
 <img src="docs/images/KFC.jpg" width="300px" height="500px" >
</p>

<p>
 <img src="docs/images/morning.jpg" width="300px" height="500px" >
</p>


## 声明

1. 本项目遵循 [MIT开源协议](/LICENSE)，仅用于技术研究和学习，使用本项目时需遵守所在地法律法规、相关政策以及企业章程，禁止用于任何违法或侵犯他人权益的行为
2. 境内使用该项目时，请使用国内厂商的大模型服务，并进行必要的内容安全审核及过滤
3. 本项目主要接入协同办公平台，请使用公众号、企微自建应用、钉钉、飞书等接入通道，其他通道为历史产物，已不再维护
4. 任何个人、团队和企业，无论以何种方式使用该项目、对何对象提供服务，所产生的一切后果，本项目均不承担任何责任

## 交流群
<p align="center">
  <img src="docs/images/contact.jpg" width="600px" height="800px" alt=" Logo">
</p>
<p align="center">
 过期加个微:rongrong3938(人工拉), Cxiaoxin321(机器人自动拉群，发加群)
</p>


# 🚀 优点
**无需Windows 系统：**  无需Windows环境，Linux即可，可云服务器挂机

**成熟稳定：**  Linux可长期挂机使用，不掉线，不封号，一次扫码，长期在线，稳定就是最大的特点。

<p>
 <img src="docs/images/func1.png" width="600px" height="1020px" >
</p>

<p>
 <img src="docs/images/func2.png" width="600px" height="1020px" >
</p>

**带简单后台维护：** 登录，微信号管理，定时任务，素材管理等，支持手机和电脑登录，自动适配


<img src="docs/images/login.png" alt="登录" width="600px">


<p>
 <img src="docs/images/account.jpg" width="600px" height="1020px" >
</p>
<p>
 <img src="docs/images/group.png" width="600px" height="1020px" >
</p>


<p>
 <img src="docs/images/plugins.png" width="500px" height="350px" >
</p>
<p>
 <img src="docs/images/wechatmanage.png" width="950px" height="150px" >
</p>
<p>
 <img src="docs/images/accept_friends.jpg" width="600px" height="1020px" >
</p>
<p>
 <img src="docs/images/revoke.jpg" width="600px" height="1020px" >
</p>
<p>
 <img src="docs/images/welcome.jpg" width="600px" height="1020px" >
</p>

**插件可扩展：**  目前已适配修改大量插件，可定制开发


## 一、准备

### 1. 账号注册
申请ipad协议账号，每月30，非免费协议，长期维护
### 2.运行环境

支持 Linux、MacOS、Windows 系统（可在Linux服务器上长期运行)，同时需安装 `Python`。
> 建议Python版本3.8-3.10以上，推荐3.10版本在 MacOS，linux，windows可用


**(1) 克隆项目代码：**

```bash
git clone https://github.com/azz212/chatgpt-on-wechat-ipad
cd chatgpt-on-wechat-ipad/
```

**(2) 安装核心依赖 (必选)：**
> 注意需要申请ipad协议token，否则无法运行。也可以用其他的http服务版的协议，自己修改底层实现
```bash
pip3 install -r requirements.txt
```

**(3) 拓展依赖 (可选，建议安装)：**

```bash
pip3 install -r requirements-optional.txt
```
> 如果某项依赖安装失败可注释掉对应的行再继续

## 二、配置
### 方法1 手动获取token 写到配置中
配置文件的模板在根目录的`config-template.json`中，需复制该模板创建最终生效的 `config.json` 文件：

```bash
  cp config-template.json config.json
```

然后在`config.json`中填入配置，以下是对默认配置的说明，可根据需要进行自定义修改（注意实际使用时请去掉注释，保证JSON格式的完整）：

注意auth_account和auth_password 是开通时得到的用户名和密码
token 和auth 是文档中第一步common/login接口获取鉴权码得到的token 和auth

```bash
# config.json文件内容示例
{
  "model": "coze",                                   # 模型名称, 支持 gpt-3.5-turbo, gpt-4, gpt-4-turbo, wenxin, xunfei, glm-4, claude-3-haiku, moonshot
  "open_ai_api_key": "YOUR API KEY",                          # 如果使用openAI模型则填入上面创建的 OpenAI API KEY
  "proxy": "",                                                # 代理客户端的ip和端口，国内环境开启代理的需要填写该项，如 "127.0.0.1:7890"
  "single_chat_prefix": ["bot", "@bot"],                      # 私聊时文本需要包含该前缀才能触发机器人回复
  "single_chat_reply_prefix": "[bot] ",                       # 私聊时自动回复的前缀，用于区分真人
  "group_chat_prefix": ["@bot"],                              # 群聊时包含该前缀则会触发机器人回复
  "group_name_white_list": ["ChatGPT测试群", "ChatGPT测试群2"], # 开启自动回复的群名称列表
  "group_chat_in_one_session": ["ChatGPT测试群"],              # 支持会话上下文共享的群名称  
  "auth_account": "开通后的手机号",
  "auth_password": "开通后加密后的密码，长的那个",
  "token": "第一步common/login接口获取鉴权码得到的token", 
  "auth": "第一步common/login接口获取鉴权码得到的auth",
  "http_hook":"http://XXXX:port/chat",                       #本地的回调地址，用于ipad服务器http回调
  "base_url": ""                                             #远端IPAD服务器地址，用于发送消息等
}

```
### 方法2 用网页的方式添加
运行后，直接登录网页后台 http://127.0.0.1:5731/login

![img.png](docs/images/img.png)

登录后台，默认账号为admin，密码123456

![img_2.png](docs/images/img_2.png)

点击新增按钮

![img_1.png](docs/images/img_1.png)

输入后获取的用户名（手机号），密码（加密后的密码），省份是微信扫描用的，按照微信所在区域实际填写。回调地址是程序运行地址，有公网的填写外网地址+端口，只有内网的
使用frp内网穿透，然后填写外网地址+端口。

然后选中输入的账号，先点击初始化，然后再点击扫码，就会出现二维码界面，准备号微信号扫码登录

![img_3.png](docs/images/img_3.png)

扫码完成后，后台可以关闭，程序继续运行。

**配置说明：**

**1.个人聊天**

+ 个人聊天中，需要以 "bot"或"@bot" 为开头的内容触发机器人，对应配置项 `single_chat_prefix` (如果不需要以前缀触发可以填写  `"single_chat_prefix": [""]`)
+ 机器人回复的内容会以 "[bot] " 作为前缀， 以区分真人，对应的配置项为 `single_chat_reply_prefix` (如果不需要前缀可以填写 `"single_chat_reply_prefix": ""`)

**2.群组聊天**

+ 群组聊天中，群名称需配置在 `group_name_white_list ` 中才能开启群聊自动回复。如果想对所有群聊生效，可以直接填写 `"group_name_white_list": ["ALL_GROUP"]`
+ 默认只要被人 @ 就会触发机器人自动回复；另外群聊天中只要检测到以 "@bot" 开头的内容，同样会自动回复（方便自己触发），这对应配置项 `group_chat_prefix`
+ 可选配置: `group_name_keyword_white_list`配置项支持模糊匹配群名称，`group_chat_keyword`配置项则支持模糊匹配群消息内容，用法与上述两个配置项相同。（Contributed by [evolay](https://github.com/evolay))
+ `group_chat_in_one_session`：使群聊共享一个会话上下文，配置 `["ALL_GROUP"]` 则作用于所有群聊


**3.其他配置**

+ `model`: 模型名称，目前支持 `gpt-3.5-turbo`, `gpt-4o`, `gpt-4-turbo`, `gpt-4`, `wenxin` , `claude` , `gemini`, `glm-4`,  `xunfei`, `moonshot`
+ `temperature`,`frequency_penalty`,`presence_penalty`: Chat API接口参数，详情参考[OpenAI官方文档。](https://platform.openai.com/docs/api-reference/chat)
+ `proxy`：由于目前 `openai` 接口国内无法访问，需配置代理客户端的地址，详情参考  [#351](https://github.com/zhayujie/chatgpt-on-wechat/issues/351)
+ 对于图像生成，在满足个人或群组触发条件外，还需要额外的关键词前缀来触发，对应配置 `image_create_prefix `
+ 关于OpenAI对话及图片接口的参数配置（内容自由度、回复字数限制、图片大小等），可以参考 [对话接口](https://beta.openai.com/docs/api-reference/completions) 和 [图像接口](https://beta.openai.com/docs/api-reference/completions)  文档，在[`config.py`](https://github.com/zhayujie/chatgpt-on-wechat/blob/master/config.py)中检查哪些参数在本项目中是可配置的。
+ `conversation_max_tokens`：表示能够记忆的上下文最大字数（一问一答为一组对话，如果累积的对话字数超出限制，就会优先移除最早的一组对话）
+ `rate_limit_chatgpt`，`rate_limit_dalle`：每分钟最高问答速率、画图速率，超速后排队按序处理。
+ `clear_memory_commands`: 对话内指令，主动清空前文记忆，字符串数组可自定义指令别名。
+ `hot_reload`: 程序退出后，暂存等于状态，默认关闭。
+ `character_desc` 配置中保存着你对机器人说的一段话，他会记住这段话并作为他的设定，你可以为他定制任何人格      (关于会话上下文的更多内容参考该 [issue](https://github.com/zhayujie/chatgpt-on-wechat/issues/43))
+ `subscribe_msg`：订阅消息，公众号和企业微信channel中请填写，当被订阅时会自动回复， 可使用特殊占位符。目前支持的占位符有{trigger_prefix}，在程序中它会自动替换成bot的触发词。


**本说明文档可能会未及时更新，当前所有可选的配置项均在该[`config.py`](https://github.com/zhayujie/chatgpt-on-wechat/blob/master/config.py)中列出。**

## 三、运行

### 1.本地运行

如果是开发机 **本地运行**，直接在项目根目录下执行：

```bash
python3 app.py                                    # windows环境下该命令通常为 python app.py
```


### 2.服务器部署

使用nohup命令在后台运行程序：

```bash
nohup python3 app.py & tail -f nohup.out          # 在后台运行程序并通过日志输出二维码
```
或者用Supervisor 后台运行，更容易管理
> **多账号支持：** 将项目复制多份，分别启动程序，用不同账号扫码登录即可实现同时运行。

> **特殊指令：** 用户向机器人发送 **#reset** 即可清空该用户的上下文记忆。

感谢原项目作者，尽快弃掉itchat吧！

