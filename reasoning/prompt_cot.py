"""
进阶推理技术 —— 思维链提示（Chain-of-Thought, CoT）

核心思想：让 LLM 在给出最终答案之前，先展示推理过程。

三种实现方式：
- zero_shot: 零样本CoT，只加"让我们一步步思考"
- few_shot: 少样本CoT，提供带推理过程的示例
- auto_cot: 自动CoT，让LLM自己生成推理步骤再回答
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


def build_cot_prompt(
    question: str,
    cot_type: str = "zero_shot",
    examples: list[dict] = None,
) -> str:
    """
    构建思维链 Prompt

    cot_type:
    - zero_shot: 零样本CoT，只加"让我们一步步思考"
    - few_shot: 少样本CoT，提供带推理过程的示例
    - auto_cot: 自动CoT，让LLM自己生成推理步骤再回答
    """

    if cot_type == "zero_shot":
        return f"""{question}

让我们一步一步地思考这个问题。"""

    elif cot_type == "few_shot":
        prompt = "请参考以下示例的推理方式，逐步分析问题。\n\n"
        for i, ex in enumerate(examples or []):
            prompt += f"""--- 示例 {i+1} ---
问题：{ex['question']}

推理过程：
{ex['reasoning']}

答案：{ex['answer']}

"""
        prompt += f"""--- 现在请回答 ---
问题：{question}

推理过程：
"""
        return prompt

    elif cot_type == "auto_cot":
        return f"""请按以下两个阶段回答：

【第一阶段：推理分析】
请详细分析这个问题，列出所有需要考虑的因素、可能的解法、以及每种解法的优劣。

【第二阶段：最终答案】
基于第一阶段的推理，给出最终答案。

问题：{question}"""


def cot_effect_experiment():
    """对比普通 Prompt 和 CoT Prompt 在推理任务上的效果"""

    test_cases = [
        {
            "question": "一个水池，进水管3小时注满，出水管5小时排空。两管同时开，几小时注满？",
            "answer": "7.5小时",
            "type": "数学推理",
        },
        {
            "question": "如果所有的猫都怕水，Tom是一只猫，那么Tom怕水吗？请解释你的推理。",
            "answer": "是，根据三段论推理",
            "type": "逻辑推理",
        },
        {
            "question": "设计一个简单的用户注册系统的数据库表结构，需要支持邮箱验证。",
            "answer": "需要users表和verification_tokens表",
            "type": "规划设计",
        },
    ]

    for case in test_cases:
        normal_prompt = case["question"]

        cot_prompt = f"""{case['question']}

请按以下步骤思考：
1. 理解问题的核心要求
2. 列出需要考虑的所有因素
3. 逐步推导解决方案
4. 验证你的答案是否合理
5. 给出最终答案"""

        print(f"\n{'='*60}")
        print(f"任务类型: {case['type']}")
        print(f"问题: {case['question'][:50]}...")
        print(f"普通Prompt长度: {len(normal_prompt)} 字符")
        print(f"CoT Prompt长度: {len(cot_prompt)} 字符")
        print(f"预期答案关键词: {case['answer']}")


if __name__ == "__main__":
    math_examples = [
        {
            "question": "一个水果店有120个苹果，上午卖了35个，下午卖了42个，还剩多少个？",
            "reasoning": """1. 初始苹果数量：120个
2. 上午卖出：35个，剩余：120 - 35 = 85个
3. 下午卖出：42个，剩余：85 - 42 = 43个
4. 验证：35 + 42 + 43 = 120，与初始数量一致""",
            "answer": "还剩43个苹果",
        },
        {
            "question": "小明有50元，买了3本书，每本12元，他还剩多少钱？",
            "reasoning": """1. 小明初始金额：50元
2. 每本书价格：12元
3. 3本书总价：12 x 3 = 36元
4. 剩余金额：50 - 36 = 14元
5. 验证：36 + 14 = 50，与初始金额一致""",
            "answer": "还剩14元",
        },
    ]

    question = "一个班级有45人，男生比女生多5人，问男生和女生各有多少人？"

    print("=" * 60)
    print("【Zero-shot CoT】")
    print("=" * 60)
    prompt_zero = build_cot_prompt(question, cot_type="zero_shot")
    print(prompt_zero)

    print("\n" + "=" * 60)
    print("【Few-shot CoT】")
    print("=" * 60)
    prompt_few = build_cot_prompt(question, cot_type="few_shot", examples=math_examples)
    print(prompt_few)

    print("\n" + "=" * 60)
    print("【Auto CoT】")
    print("=" * 60)
    prompt_auto = build_cot_prompt(question, cot_type="auto_cot")
    print(prompt_auto)

    # 使用 Few-shot CoT 调用 LLM
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt_few}],
        temperature=DEFAULT_TEMPERATURE,
    )
    print(f"\n{'='*60}")
    print("【LLM 推理结果】")
    print(f"{'='*60}")
    print(response.choices[0].message.content)

    print("\n" + "=" * 60)
    print("【CoT 效果对比实验（仅展示 Prompt 差异）】")
    print("=" * 60)
    cot_effect_experiment()