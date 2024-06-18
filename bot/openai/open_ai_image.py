import time

import openai
import openai.error

from common.log import logger
from common.token_bucket import TokenBucket
from config import conf
import asyncio
import aiohttp
import os
import json
import re

# OPENAI提供的画图接口
class OpenAIImage(object):
    def __init__(self):
        openai.api_key = conf().get("open_ai_api_key")
        if conf().get("rate_limit_dalle"):
            self.tb4dalle = TokenBucket(conf().get("rate_limit_dalle", 50))

    def create_img(self, query, retry_count=0, api_key=None, api_base=None):
        '''
        将画图的提示词和图片URL返回
        '''
        prompt=""
        try:
            if conf().get("rate_limit_dalle") and not self.tb4dalle.get_token():
                return False, "请求太快了，请休息一下再问我吧"
            logger.info("[OPEN_AI] image_query={}".format(query))
            response = openai.Image.create(
                api_key=api_key,
                prompt=query,  # 图片描述
                n=1,  # 每次生成图片的数量
                model=conf().get("text_to_image") or "dall-e-2",

                # size=conf().get("image_create_size", "256x256"),  # 图片大小,可选有 256x256, 512x512, 1024x1024
            )
            #logger.info(response["data"])
            logger.debug(json.dumps(response, ensure_ascii=False))
            image_url = response["data"][0]["url"]
            prompt = response["data"][0]["revised_prompt"]
            logger.info("[OPEN_AI] image_url={}, prompt = {}".format(image_url,prompt))
            image_urls=[]
            for data in response["data"]:
                image_urls.append(data["url"])
            image_urls.pop(0)
            external={"prompt":prompt,"urls":image_urls}
            if image_url:
                if 'ad.bluead.ai' in image_url:
                    return False, "图片地址错误！",external
                else :
                    return True, image_url,external
            else:
                return False, image_url,external
        except openai.error.RateLimitError as e:
            logger.warn(e)
            if retry_count < 1:
                time.sleep(5)
                logger.warn("[OPEN_AI] ImgCreate RateLimit exceed, 第{}次重试".format(retry_count + 1))
                return self.create_img(query, retry_count + 1)
            else:
                return False, "画图出现问题，请休息一下再问我吧",prompt
        except Exception as e:
            logger.exception(e)
            return False, "画图出现问题，请休息一下再问我吧",prompt
