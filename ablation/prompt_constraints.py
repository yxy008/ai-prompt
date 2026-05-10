"""
Prompt 基础结构五要素 —— 约束条件（Constraints）

约束条件分为三类：
- 硬约束（Hard）：必须遵守，违反则输出无效
- 条件约束（Conditional）：满足特定条件时触发
- 软约束（Soft）：尽量遵守，但不强制
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


def build_constrained_prompt(
    task: str,
    context: str = "",
    constraints: list[dict] = None,
) -> str:
    """
    构建带约束条件的 Prompt

    Args:
        task: 任务描述
        context: 背景信息
        constraints: 约束列表，每项包含 type 和 rule
            type 可选: hard / conditional / soft
    """
    prompt = f"""【任务】
{task}
"""

    if context:
        prompt += f"""
【背景信息】
{context}
"""

    if not constraints:
        return prompt

    hard_constraints = [c for c in constraints if c.get("type") == "hard"]
    conditional_constraints = [c for c in constraints if c.get("type") == "conditional"]
    soft_constraints = [c for c in constraints if c.get("type") == "soft"]

    if hard_constraints:
        prompt += f"""
【必须遵守的规则】（违反任何一条都不可接受）
{chr(10).join([f"- {c['rule']}" for c in hard_constraints])}
"""

    if conditional_constraints:
        prompt += f"""
【条件规则】（根据情况判断是否适用）
{chr(10).join([f"- 如果{c['condition']}，则{c['action']}" for c in conditional_constraints])}
"""

    if soft_constraints:
        prompt += f"""
【建议遵守的规则】（尽量遵守，但不强制）
{chr(10).join([f"- {c['rule']}" for c in soft_constraints])}
"""

    return prompt


if __name__ == "__main__":
    prompt = build_constrained_prompt(
        task="根据客户投诉内容，生成一封回复邮件",
        context="客户投诉：购买的商品在运输中损坏，要求退款或换货",
        constraints=[
            {"type": "hard", "rule": "绝对不要承诺具体的赔偿金额"},
            {"type": "hard", "rule": "不要泄露公司内部流程信息"},
            {"type": "hard", "rule": "必须包含道歉语句"},
            {"type": "conditional", "condition": "客户情绪激动（包含多个感叹号或愤怒词汇）",
             "action": "先表达理解和共情，再提出解决方案"},
            {"type": "conditional", "condition": "客户是VIP会员",
             "action": "提供优先处理通道和额外补偿"},
            {"type": "soft", "rule": "回复控制在200字以内"},
            {"type": "soft", "rule": "语气温暖但不卑微"},
        ],
    )
    print(prompt)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=DEFAULT_TEMPERATURE,
    )
    print(f"\n{'='*50}")
    print("【LLM 生成的回复邮件】")
    print(f"{'='*50}")
    print(response.choices[0].message.content)