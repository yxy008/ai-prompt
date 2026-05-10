"""
Prompt 基础结构五要素 —— 上下文注入（Context）消融实验

演示多层上下文的构建策略：
- 第1层：系统级上下文（领域知识）
- 第2层：检索到的相关文档（RAG结果）
- 第3层：对话历史（多轮对话上下文）
- 第4层：当前问题
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


def build_context_aware_prompt(
    user_query: str,
    retrieved_docs: list[str],
    conversation_history: list[dict] = None,
    domain_knowledge: str = None,
) -> str:
    """构建包含多层上下文的 Prompt"""

    prompt_parts = []

    # 第1层：系统级上下文（领域知识）
    if domain_knowledge:
        prompt_parts.append(f"""【领域知识】
{domain_knowledge}
""")

    # 第2层：检索到的相关文档
    if retrieved_docs:
        docs_text = "\n---\n".join([
            f"[文档{i+1}] {doc}" for i, doc in enumerate(retrieved_docs)
        ])
        prompt_parts.append(f"""【参考资料】
以下是与问题相关的文档片段，请基于这些资料回答：
{docs_text}

如果参考资料中没有相关信息，请明确说明"参考资料中未找到相关信息"，
不要编造内容。
""")

    # 第3层：对话历史
    if conversation_history:
        history_text = "\n".join([
            f"{'用户' if msg['role']=='user' else '助手'}: {msg['content']}"
            for msg in conversation_history[-6:]  # 只保留最近6轮
        ])
        prompt_parts.append(f"""【对话历史】
{history_text}
""")

    # 第4层：当前问题
    prompt_parts.append(f"""【当前问题】
{user_query}
""")

    return "\n".join(prompt_parts)


def test_context_effect(prompt: str):
    """测试上下文注入效果"""

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=DEFAULT_TEMPERATURE,
    )
    result = response.choices[0].message.content
    print(f"\n{'='*50}")
    print(f"【LLM 回答】")
    print(f"{'='*50}")
    print(result)

    return result


if __name__ == "__main__":
    prompt = build_context_aware_prompt(
        user_query="公司的年假政策是什么？",
        retrieved_docs=[
            "员工入职满1年享有5天年假，满3年享有10天年假。",
            "年假需提前一周在OA系统申请，经直属领导审批。",
        ],
        conversation_history=[
            {"role": "user", "content": "我想了解公司的假期政策"},
            {"role": "assistant", "content": "好的，公司假期包括年假、病假、婚假等，您想了解哪一种？"},
        ],
        domain_knowledge="该公司是一家互联网企业，员工平均年龄28岁。",
    )
    print("【构建的 Prompt】")
    print(prompt)

    results = test_context_effect(prompt)