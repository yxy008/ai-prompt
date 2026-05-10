"""
结构化输出控制 —— Markdown/表格格式输出

用于构建表格输出的 Prompt 模板。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


def build_table_output_prompt(data_description: str) -> str:
    """构建表格输出的 Prompt"""
    return f"""{data_description}

请使用Markdown表格格式输出，要求：
1. 表头清晰，列名准确
2. 数据对齐（数字右对齐，文字左对齐）
3. 如果数据量超过10行，只展示前10行并注明总数
4. 表格下方附简要说明

输出格式示例：
| 列1 | 列2 | 列3 |
|:-----|:----:|----:|
| 左对齐 | 居中 | 右对齐 |
"""


if __name__ == "__main__":
    prompt = build_table_output_prompt(
        "请列出Python中常用的5个内置数据结构，包括名称、是否可变、是否有序、典型使用场景"
    )
    print("【构建的表格输出 Prompt】")
    print(prompt)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=DEFAULT_TEMPERATURE,
    )
    print(f"\n{'='*50}")
    print("【LLM 表格输出】")
    print(f"{'='*50}")
    print(response.choices[0].message.content)