"""
工程化工具 —— Prompt 模板引擎

功能：
- 安全的模板变量替换
- 模板完整性验证
- 列出模板中的所有变量
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


class PromptTemplate:
    """Prompt 模板引擎"""

    def __init__(self, template: str):
        self.template = template
        self._validate()

    def _validate(self):
        """验证模板的完整性"""
        open_count = self.template.count("{") - self.template.count("{{") * 2
        close_count = self.template.count("}") - self.template.count("}}") * 2
        if open_count != close_count:
            raise ValueError("模板中的花括号不匹配")

    def render(self, **kwargs) -> str:
        """渲染模板"""
        result = self.template
        for key, value in kwargs.items():
            placeholder = "{" + key + "}"
            result = result.replace(placeholder, str(value))
        return result

    def list_variables(self) -> list[str]:
        """列出模板中的所有变量"""
        return re.findall(r"\{(\w+)\}", self.template)


if __name__ == "__main__":
    qa_template = PromptTemplate("""你是一位{role}。

【背景信息】
{context}

【问题】
{question}

【要求】
- 回答风格：{style}
- 详细程度：{detail_level}
- 输出语言：{language}

请回答：""")

    print("模板变量:", qa_template.list_variables())

    prompt = qa_template.render(
        role="Python技术专家",
        context="用户正在学习Python异步编程，已掌握基础语法",
        question="asyncio和threading有什么区别？什么时候用哪个？",
        style="通俗易懂，适合初学者",
        detail_level="详细，包含代码示例",
        language="中文",
    )
    print("\n【渲染后的 Prompt】")
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