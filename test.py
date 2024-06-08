res = {
  "created": 1717775180,
  "dailyLimit": False,
  "data": [
    {
      "url": "https://sf-bot-studio-plugin-resource.coze.com/obj/bot-studio-platform-plugin-sg/artist/image/edf1b8ca3c1a431fa99da69acf4b9181.png",
      "revised_prompt": "Here is the chibi version of major beautiful female characters from the Three Kingdoms:",
      "b64_json": ""
    }
  ],
  "suggestions": [
    "\u8fd9\u4e9bQ\u7248\u7f8e\u5973\u4eba\u7269\u662f\u6839\u636e\u54ea\u4e9b\u539f\u8457\u89d2\u8272\u8bbe\u8ba1\u7684\uff1f",
    "\u4f60\u80fd\u4e3a\u6211\u89e3\u91ca\u4e00\u4e0b\u4e09\u56fd\u4e3b\u8981\u7f8e\u5973\u4eba\u7269\u7684\u80cc\u666f\u6545\u4e8b\u5417\uff1f",
    "\u8fd9\u5f20\u56fe\u7247\u4e2d\u7684\u7f8e\u5973\u4eba\u7269\u5206\u522b\u662f\u8c01\uff1f"
  ]
}

print(res)

from urllib.parse import urlparse

url = "http://www.hdgame.top:5711/chat"
parsed_url = urlparse(url)

domain = parsed_url.netloc.split(':')[0]
port = parsed_url.port
scheme = parsed_url.scheme
url = "{}://{}:{}".format(scheme,domain,port)
print("端口号:", port)
print(url)