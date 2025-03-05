#!/usr/bin/env python
# coding=utf-8

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from dataclasses import dataclass
from typing import Any, Dict, Optional

from .local_python_executor import (
    BASE_BUILTIN_MODULES,
    BASE_PYTHON_TOOLS,
    evaluate_python_code,
)
from .tools import PipelineTool, Tool


@dataclass
class PreTool:
    name: str
    inputs: Dict[str, str]
    output_type: type
    task: str
    description: str
    repo_id: str


class PythonInterpreterTool(Tool):
    name = "python_interpreter"
    description = "这是一个用于执行Python代码的工具。它可以用来进行计算。"
    inputs = {
        "code": {
            "type": "string",
            "description": "要在解释器中运行的Python代码",
        }
    }
    output_type = "string"

    def __init__(self, *args, authorized_imports=None, **kwargs):
        if authorized_imports is None:
            self.authorized_imports = list(set(BASE_BUILTIN_MODULES))
        else:
            self.authorized_imports = list(set(BASE_BUILTIN_MODULES) | set(authorized_imports))
        self.inputs = {
            "code": {
                "type": "string",
                "description": (
                    "要评估的代码片段。此片段中使用的所有变量都必须在同一片段中定义，"
                    f"否则你将收到错误。此代码只能导入以下Python库：{authorized_imports}。"
                ),
            }
        }
        self.base_python_tools = BASE_PYTHON_TOOLS
        self.python_evaluator = evaluate_python_code
        super().__init__(*args, **kwargs)

    def forward(self, code: str) -> str:
        state = {}
        output = str(
            self.python_evaluator(
                code,
                state=state,
                static_tools=self.base_python_tools,
                authorized_imports=self.authorized_imports,
            )[0]  # The second element is boolean is_final_answer
        )
        return f"标准输出:\n{str(state['_print_outputs'])}\n输出: {output}"


class FinalAnswerTool(Tool):
    name = "final_answer"
    description = "为给定的问题提供最终答案。"
    inputs = {"answer": {"type": "any", "description": "问题的最终答案"}}
    output_type = "any"

    def forward(self, answer: Any) -> Any:
        return answer


class UserInputTool(Tool):
    name = "user_input"
    description = "询问用户特定问题的输入"
    inputs = {"question": {"type": "string", "description": "要询问用户的问题"}}
    output_type = "string"

    def forward(self, question):
        user_input = input(f"{question} => 在此输入你的答案:")
        return user_input


class DuckDuckGoSearchTool(Tool):
    name = "web_search"
    description = """执行DuckDuckGo网络搜索（类似于谷歌搜索），然后返回最相关的搜索结果。"""
    inputs = {"query": {"type": "string", "description": "要执行的搜索查询。"}}
    output_type = "string"

    def __init__(self, max_results=10, **kwargs):
        super().__init__()
        self.max_results = max_results
        try:
            from duckduckgo_search import DDGS
        except ImportError as e:
            raise ImportError(
                "你必须安装`duckduckgo_search`包才能运行此工具：例如运行`pip install duckduckgo-search`。"
            ) from e
        self.ddgs = DDGS(**kwargs)

    def forward(self, query: str) -> str:
        results = self.ddgs.text(query, max_results=self.max_results)
        if len(results) == 0:
            raise Exception("未找到结果！请尝试使用限制更少/更短的查询。")
        postprocessed_results = [f"[{result['title']}]({result['href']})\n{result['body']}" for result in results]
        return "## 搜索结果\n\n" + "\n\n".join(postprocessed_results)


class GoogleSearchTool(Tool):
    name = "web_search"
    description = """执行谷歌网络搜索，然后返回最相关搜索结果的字符串。"""
    inputs = {
        "query": {"type": "string", "description": "要执行的搜索查询。"},
        "filter_year": {
            "type": "integer",
            "description": "可选择限制结果到特定年份",
            "nullable": True,
        },
    }
    output_type = "string"

    def __init__(self, provider: str = "serpapi"):
        super().__init__()
        import os

        self.provider = provider
        if provider == "serpapi":
            self.organic_key = "organic_results"
            api_key_env_name = "SERPAPI_API_KEY"
        else:
            self.organic_key = "organic"
            api_key_env_name = "SERPER_API_KEY"
        self.api_key = os.getenv(api_key_env_name)
        if self.api_key is None:
            raise ValueError(f"缺少API密钥。请确保你的环境变量中有'{api_key_env_name}'。")

    def forward(self, query: str, filter_year: Optional[int] = None) -> str:
        import requests

        if self.provider == "serpapi":
            params = {
                "q": query,
                "api_key": self.api_key,
                "engine": "google",
                "google_domain": "google.com",
            }
            base_url = "https://serpapi.com/search.json"
        else:
            params = {
                "q": query,
                "api_key": self.api_key,
            }
            base_url = "https://google.serper.dev/search"
        if filter_year is not None:
            params["tbs"] = f"cdr:1,cd_min:01/01/{filter_year},cd_max:12/31/{filter_year}"

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            results = response.json()
        else:
            raise ValueError(response.json())

        if self.organic_key not in results.keys():
            if filter_year is not None:
                raise Exception(
                    f"未找到查询：'{query}'（年份筛选={filter_year}）的结果。使用限制更少的查询或不要按年份筛选。"
                )
            else:
                raise Exception(f"未找到查询：'{query}'的结果。使用限制更少的查询。")
        if len(results[self.organic_key]) == 0:
            year_filter_message = f"（年份筛选={filter_year}）" if filter_year is not None else ""
            return f"未找到'{query}'{year_filter_message}的结果。尝试使用更通用的查询，或移除年份筛选。"

        web_snippets = []
        if self.organic_key in results:
            for idx, page in enumerate(results[self.organic_key]):
                date_published = ""
                if "date" in page:
                    date_published = "\n发布日期: " + page["date"]

                source = ""
                if "source" in page:
                    source = "\n来源: " + page["source"]

                snippet = ""
                if "snippet" in page:
                    snippet = "\n" + page["snippet"]

                redacted_version = f"{idx}. [{page['title']}]({page['link']}){date_published}{source}\n{snippet}"
                web_snippets.append(redacted_version)

        return "## 搜索结果\n" + "\n\n".join(web_snippets)


class VisitWebpageTool(Tool):
    name = "visit_webpage"
    description = (
        "访问给定URL的网页并将其内容读取为markdown字符串。使用此工具浏览网页。"
    )
    inputs = {
        "url": {
            "type": "string",
            "description": "要访问的网页的URL。",
        }
    }
    output_type = "string"

    def forward(self, url: str) -> str:
        try:
            import re

            import requests
            from markdownify import markdownify
            from requests.exceptions import RequestException

            from smolagents.utils import truncate_content
        except ImportError as e:
            raise ImportError(
                "你必须安装`markdownify`和`requests`包才能运行此工具：例如运行`pip install markdownify requests`。"
            ) from e
        try:
            # 发送GET请求到URL，超时时间为20秒
            response = requests.get(url, timeout=20)
            response.raise_for_status()  # 对错误状态码抛出异常

            # 将HTML内容转换为Markdown
            markdown_content = markdownify(response.text).strip()

            # 移除多个换行符
            markdown_content = re.sub(r"\n{3,}", "\n\n", markdown_content)

            return truncate_content(markdown_content, 10000)

        except requests.exceptions.Timeout:
            return "请求超时。请稍后重试或检查URL。"
        except RequestException as e:
            return f"获取网页时出错：{str(e)}"
        except Exception as e:
            return f"发生意外错误：{str(e)}"


class SpeechToTextTool(PipelineTool):
    default_checkpoint = "openai/whisper-large-v3-turbo"
    description = "这是一个将音频转录为文本的工具。它返回转录的文本。"
    name = "transcriber"
    inputs = {
        "audio": {
            "type": "audio",
            "description": "要转录的音频。可以是本地路径、URL或张量。",
        }
    }
    output_type = "string"

    def __new__(cls, *args, **kwargs):
        from transformers.models.whisper import (
            WhisperForConditionalGeneration,
            WhisperProcessor,
        )

        cls.pre_processor_class = WhisperProcessor
        cls.model_class = WhisperForConditionalGeneration
        return super().__new__(cls, *args, **kwargs)

    def encode(self, audio):
        from .agent_types import AgentAudio

        audio = AgentAudio(audio).to_raw()
        return self.pre_processor(audio, return_tensors="pt")

    def forward(self, inputs):
        return self.model.generate(inputs["input_features"])

    def decode(self, outputs):
        return self.pre_processor.batch_decode(outputs, skip_special_tokens=True)[0]


TOOL_MAPPING = {
    tool_class.name: tool_class
    for tool_class in [
        PythonInterpreterTool,
        DuckDuckGoSearchTool,
        VisitWebpageTool,
    ]
}

__all__ = [
    "PythonInterpreterTool",
    "FinalAnswerTool",
    "UserInputTool",
    "DuckDuckGoSearchTool",
    "GoogleSearchTool",
    "VisitWebpageTool",
    "SpeechToTextTool",
]
