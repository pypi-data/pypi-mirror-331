#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : files
# @Time         : 2025/1/3 15:38
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 支持文档、图片、音频、视频问答
"""单一智能体
任意模型支持文档、图片、音频、视频问答
api形式
- /agents/v1
- /v1 前缀区分 agents-{model}【底层调用 /agents/v1】

todo: 记录上下文日志
"""

from meutils.pipe import *
from meutils.io.openai_files import file_extract

from meutils.llm.clients import AsyncOpenAI
from meutils.llm.openai_utils import to_openai_params

from meutils.schemas.openai_types import chat_completion, chat_completion_chunk, CompletionRequest, CompletionUsage


class Completions(object):

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key

    async def create(self, request: CompletionRequest):

        if image_urls := request.last_urls.get("image_url"):
            request.model = "doubao-1.5-vision-pro-32k"  # 6月过期

            request.messages = [
                {
                    'role': 'user',
                    "content": [
                        {"type": "text", "text": request.last_user_content},
                        {"type": "image_url", "image_url": {"url": image_urls[-1]}}
                    ]
                }
            ]
        else:
            for i, message in enumerate(request.messages[::-1], 1):
                if message.get("role") == "user":  # 每一轮还要处理
                    content = message.get("content")

                    if content.startswith("http"):
                        file_url, content = content.split(maxsplit=1)
                        file_content = await file_extract(file_url)

                        request.messages[-i] = {
                            'role': 'user',
                            'content': f"""{json.dumps(file_content, ensure_ascii=False)}\n\n
                            {content}
                            """
                        }
                        break

        logger.debug(request)

        data = to_openai_params(request)
        return await AsyncOpenAI(api_key=self.api_key).chat.completions.create(**data)


# data: {"event": "message", "task_id": "900bbd43-dc0b-4383-a372-aa6e6c414227", "id": "663c5084-a254-4040-8ad3-51f2a3c1a77c", "answer": "Hi", "created_at": 1705398420}\n\n
if __name__ == '__main__':
    c = Completions()

    request = CompletionRequest(
        # model="qwen-turbo-2024-11-01",
        # model="claude-3-5-sonnet-20241022",
        model="gpt-4o-mini",

        messages=[
            # {
            #     'role': 'system',
            #     'content': '你是一个文件问答助手'
            # },
            # {
            #     'role': 'user',
            #     # 'content': {
            #     #     "type": "file_url",
            #     #     "file_url": {"url": "https://oss.ffire.cc/files/招标文件备案表（第二次）.pdf", "detai": "auto"}
            #     # },
            #     'content': [
            #         {
            #             "type": "text",
            #             "text": "这个文件讲了什么？"
            #         },
            #         # 多轮的时候要剔除
            #         {
            #             "type": "file_url",
            #             "file_url": {"url": "https://oss.ffire.cc/files/招标文件备案表（第二次）.pdf", "detai": "auto"}
            #         }
            #     ]
            # },

            {
                'role': 'user',
                # "content": '你好',
                # "content": [
                #     {"type": "text", "text": "描述"},
                #
                #     {"type": "image_url", "image_url": "https://oss.ffire.cc/files/kling_watermark.png"}
                # ],

                # 'content': {
                #     "type": "file_url",
                #     "file_url": {"url": "https://mj101-1317487292.cos.ap-shanghai.myqcloud.com/ai/test.pdf", "detai": "auto"}
                # },
                # 'content': "https://oss.ffire.cc/files/%E6%8B%9B%E6%A0%87%E6%96%87%E4%BB%B6%E5%A4%87%E6%A1%88%E8%A1%A8%EF%BC%88%E7%AC%AC%E4%BA%8C%E6%AC%A1%EF%BC%89.pdf 这个文件讲了什么？",
                # 'content': "https://translate.google.com/?sl=zh-CN&tl=en&text=%E6%8F%90%E4%BE%9B%E6%96%B9&op=tr1anslate 这个文件讲了什么？",

                "content": "https://oss.ffire.cc/files/百炼系列手机产品介绍.docx 总结下"
                # "content": "https://mj101-1317487292.cos.ap-shanghai.myqcloud.com/ai/test.pdf\n\n总结下"

                # "content": "https://admin.ilovechatgpt.top/file/lunIMYAIzhinengzhushouduishenghuodocx_14905733.docx 总结"

            },

            # {'role': 'assistant', 'content': "好的"},
            # {
            #     'role': 'user',
            #     # 'content': {
            #     #     "type": "file_url",
            #     #     "file_url": {"url": "https://oss.ffire.cc/files/招标文件备案表（第二次）.pdf", "detai": "auto"}
            #     # },
            #     'content': [
            #         {
            #             "type": "text",
            #             "text": "错了 继续回答"
            #         },
            #         # {
            #         #     "type": "file_url",
            #         #     "file_url": {"url": "https://oss.ffire.cc/files/招标文件备案表（第二次）.pdf", "detai": "auto"}
            #         # }
            #     ]
            # }
        ]

    )

    arun(c.create(request))
