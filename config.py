"""
ai-prompt 工程共享配置
"""
import os
from openai import OpenAI


def create_client() -> OpenAI:
    """创建 OpenAI 客户端实例"""
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    if not api_key:
        raise ValueError("请设置环境变量 OPENAI_API_KEY")
    kwargs = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    return OpenAI(**kwargs)


DEFAULT_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 4096