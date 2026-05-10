"""
工程化工具 —— 中文 Prompt 优化

中文 Prompt 的独特挑战：
- 分词歧义：中文无空格，LLM可能错误分词
- 量词复杂：中文量词丰富
- 敬语系统："您"vs"你"影响语气
- 标点符号：中英文标点混用
- 成语俗语：LLM可能误解
- 多音字：可能影响理解
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


def build_chinese_prompt(task: str, context: str = "") -> str:
    """构建中文友好的 Prompt"""
    prompt = f"""你是一位专业的中文助手。

【任务】
{task}
"""

    if context:
        prompt += f"""
【背景信息】
{context}
"""

    prompt += """
【中文输出规范】
- 使用简体中文，避免繁体字
- 专业术语首次出现时标注英文（如：检索增强生成（RAG））
- 数字和英文单词前后加空格（如：使用 3 个 GPU 训练）
- 代码注释使用中文
- 避免使用生僻成语和文言文表达
- 标点符号统一使用中文全角标点（，。！？）
"""

    return prompt


if __name__ == "__main__":
    prompt = build_chinese_prompt(
        task="解释什么是向量数据库，以及它在RAG系统中的作用",
        context="读者是有1-2年Python经验的开发者，对数据库有基本了解",
    )
    print("【中文优化 Prompt】")
    print(prompt)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=DEFAULT_TEMPERATURE,
    )
    print(f"\n{'='*50}")
    print("【LLM 回答】")
    print(f"{'='*50}")
    print(response.choices[0].message.content)