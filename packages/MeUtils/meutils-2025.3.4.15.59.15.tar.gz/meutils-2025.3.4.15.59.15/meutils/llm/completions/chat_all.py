#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : chat_all
# @Time         : 2025/3/4 13:25
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 


from openai import AsyncOpenAI

from meutils.pipe import *
from meutils.io.files_utils import to_bytes
from meutils.decorators.retry import retrying

from meutils.llm.clients import qwen_client
from meutils.llm.openai_utils import to_openai_params

from meutils.config_utils.lark_utils import get_next_token_for_polling
from meutils.schemas.openai_types import chat_completion, chat_completion_chunk, CompletionRequest, CompletionUsage

FEISHU_URL = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=PP1PGr"

base_url = "https://chat.qwenlm.ai/api"

from fake_useragent import UserAgent

ua = UserAgent()

"""
# vision_model="doubao-1.5-vision-pro-32k"
# glm-4v-flash 

"""


class Completions(object):

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, reasoning_stream: bool = True):
        self.reasoning_stream = reasoning_stream

        self.client = AsyncOpenAI(
            base_url=base_url, api_key=api_key,
        )

    async def create(self, request: CompletionRequest):
        """适配任意客户端"""
        request.last_message



# "image_url": "http://ai.chatfire.cn/files/images/image-1725418399272-d7b71012f.png"
