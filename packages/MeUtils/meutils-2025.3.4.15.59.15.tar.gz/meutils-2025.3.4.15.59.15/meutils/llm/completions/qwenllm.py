#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : qwen
# @Time         : 2025/1/17 16:45
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
"""
 File "/usr/local/lib/python3.10/site-packages/meutils/llm/completions/qwenllm.py", line 47, in create
    yield response.choices[0].message.content
AttributeError: 'str' object has no attribute 'choices'

"""

from openai import AsyncOpenAI

from meutils.pipe import *
from meutils.io.files_utils import to_bytes
from meutils.decorators.retry import retrying

from meutils.llm.clients import qwen_client
from meutils.llm.openai_utils import to_openai_params

from meutils.config_utils.lark_utils import get_next_token_for_polling
from meutils.schemas.openai_types import chat_completion, chat_completion_chunk, ChatCompletionRequest, CompletionUsage

FEISHU_URL = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=PP1PGr"

base_url = "https://chat.qwenlm.ai/api"

from fake_useragent import UserAgent

ua = UserAgent()


@retrying()
async def to_file(file, mime_type: str = "application/octet-stream"):
    file_bytes = await to_bytes(file)
    file = ("filename", file_bytes, mime_type)
    file_object = await qwen_client.files.create(file=file, purpose="file-extract")
    return file_object


async def create(request: ChatCompletionRequest, token: Optional[str] = None):  # ChatCompletionRequest 重构

    token = token or await get_next_token_for_polling(feishu_url=FEISHU_URL)

    client = AsyncOpenAI(
        base_url=base_url,
        api_key=token,
        default_headers={'User-Agent': ua.random}
    )

    # qwen结构
    if any(i in request.model.lower() for i in ("search",)):
        request.model = "qwen-max-latest"
        request.messages[-1]['chat_type'] = "search"

    if any(i in request.model.lower() for i in ("qwq", "think")):
        request.model = "qwen-max-latest"
        request.messages[-1]['feature_config'] = {"thinking_enabled": True}

    # 多模态: todo
    # if any(i in request.model.lower() for i in ("-vl", "qvq")):
    #     # await to_file
    last_message = request.messages[-1]
    logger.debug(last_message)
    if last_message.get("role") == "user":
        user_content = last_message.get("content")
        if isinstance(user_content, list):
            for i, content in enumerate(user_content):
                if content.get("type") == 'file_url':  # image_url file_url video_url
                    url = content.get(content.get("type")).get("url")
                    file_object = await to_file(url)

                    user_content[i] = {"type": "file", "file": file_object.id}

                elif content.get("type") == 'image_url':
                    url = content.get(content.get("type")).get("url")
                    file_object = await to_file(url, "image/png")

                    user_content[i] = {"type": "image", "image": file_object.id}

    data = to_openai_params(request)
    if request.stream:
        _chunk = ""
        async for chunk in await client.chat.completions.create(**data):
            chunk = chunk.choices[0].delta.content or ""
            yield chunk.removeprefix(_chunk)
            _chunk = chunk

    else:
        response = await client.chat.completions.create(**data)
        for i in range(3):
            if not isinstance(response, str):  # 报错
                yield response.choices[0].message.content
            else:
                logger.warning(f"重试 {i}\n{response}")


if __name__ == '__main__':
    # [
    #     "qwen-plus-latest",
    #     "qvq-72b-preview",
    #     "qwq-32b-preview",
    #     "qwen2.5-coder-32b-instruct",
    #     "qwen-vl-max-latest",
    #     "qwen-turbo-latest",
    #     "qwen2.5-72b-instruct",
    #     "qwen2.5-32b-instruct"
    # ]

    # user_content = [
    #     {
    #         "type": "text",
    #         "text": "解读图片"
    #     },
    #     {
    #         "type": "image_url",
    #         "image_url": {
    #             "url": "https://fyb-pc-static.cdn.bcebos.com/static/asset/homepage@2x_daaf4f0f6cf971ed6d9329b30afdf438.png"
    #         }
    #     }
    # ]

    user_content = [
        {
            "type": "text",
            "text": "总结下"
        },
        {
            "type": "file_url",
            "file_url": {
                "url": "https://oss.ffire.cc/files/%E6%8B%9B%E6%A0%87%E6%96%87%E4%BB%B6%E5%A4%87%E6%A1%88%E8%A1%A8%EF%BC%88%E7%AC%AC%E4%BA%8C%E6%AC%A1%EF%BC%89.pdf"
            }
        }

    ]

    request = ChatCompletionRequest(
        # model="qwen-turbo-2024-11-01",
        # model="qwen-max-latest",
        # model="qwen-max-latest-search",
        model="qwq-max",
        # model="qwen2.5-vl-72b-instruct",

        # model="qwen-plus-latest",

        messages=[
            {
                'role': 'user',
                # 'content': '今天南京天气',
                'content': "9.8 9.11哪个大",
                # 'content': '总结下',

                # "chat_type": "search",

                # 'content': user_content,

                # "content": [
                #     {
                #         "type": "text",
                #         "text": "总结下",
                #         "chat_type": "t2t",
                #         "feature_config": {
                #             "thinking_enabled": False
                #         }
                #     },
                #     {
                #         "type": "file",
                #         "file": "2d677df1-45b2-4f30-829f-0d42b2b07136"
                #     }
                # ]

                # "content": [
                #     {
                #         "type": "text",
                #         "text": "总结下",
                #         # "chat_type": "t2t"
                #
                #     },
                # {
                #     "type": "image",
                #     "image": "703dabac-b0d9-4357-8a85-75b9456df1dd"
                # },
                # {
                #     "type": "image",
                #     "image": "https://oss.ffire.cc/files/kling_watermark.png"
                #
                # }
                # ]

            },

        ],
        stream=True,

    )
    arun(create(request))

    # arun(to_file("/Users/betterme/PycharmProjects/AI/MeUtils/meutils/llm/completions/yuanbao.py"))
