"""
结构化输出控制 —— 代码生成与格式约束

构建代码生成的 Prompt，包含类型注解、注释、测试用例等要求。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


def build_code_generation_prompt(
    task: str,
    language: str = "python",
    include_tests: bool = True,
) -> str:
    """构建代码生成的 Prompt"""
    prompt = f"""请生成{language}代码来完成以下任务：

{task}

【代码要求】
1. 包含完整的类型注解（Type Hints）
2. 关键逻辑有中文注释
3. 函数/类有docstring说明
4. 遵循{language}的最佳实践和编码规范
5. 使用标准库优先，避免不必要的第三方依赖
"""

    if include_tests:
        prompt += """
【测试用例】
请同时生成3个测试用例（2个正常情况 + 1个边界情况）
"""

    prompt += f"""
【输出格式】
```{language}
# 代码在这里
```"""

    return prompt


if __name__ == "__main__":
    prompt = build_code_generation_prompt(
        task="实现一个LRU缓存（最近最少使用），支持get和put操作，时间复杂度O(1)",
        language="python",
        include_tests=True,
    )
    print("【构建的代码生成 Prompt】")
    print(prompt)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=DEFAULT_TEMPERATURE,
    )
    print(f"\n{'='*50}")
    print("【LLM 生成的代码】")
    print(f"{'='*50}")
    print(response.choices[0].message.content)