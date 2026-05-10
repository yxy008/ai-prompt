"""
进阶推理技术 —— 少样本提示（Few-shot Prompting）

核心思想：在 Prompt 中提供 2-5 个"输入-输出"示例，
让 LLM 通过模式匹配来理解期望。

示例选择策略：
- similarity: 选择与当前查询最相似的示例
- diversity: 选择覆盖不同情况的示例
- difficulty: 选择难度递增的示例（课程学习）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


def select_few_shot_examples(
    query: str,
    example_pool: list[dict],
    n: int = 3,
    strategy: str = "similarity",
) -> list[dict]:
    """
    从示例池中选择最优的 few-shot 示例

    策略：
    - similarity: 选择与当前查询最相似的示例（语义匹配）
    - diversity: 选择覆盖不同情况的示例（多样性）
    - difficulty: 选择难度递增的示例（课程学习）
    """
    if strategy == "similarity":
        query_words = set(query.lower().split())
        scored = []
        for ex in example_pool:
            ex_words = set(ex["input"].lower().split())
            score = len(query_words & ex_words) / len(query_words | ex_words) if query_words | ex_words else 0
            scored.append((score, ex))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [ex for _, ex in scored[:n]]

    elif strategy == "diversity":
        selected = []
        used_labels = set()
        for ex in example_pool:
            label = ex.get("label", "")
            if label not in used_labels or len(selected) < n:
                selected.append(ex)
                used_labels.add(label)
            if len(selected) >= n:
                break
        return selected

    elif strategy == "difficulty":
        sorted_pool = sorted(example_pool, key=lambda x: x.get("difficulty", 5))
        return sorted_pool[:n]

    return example_pool[:n]


def build_few_shot_prompt(
    task_description: str,
    examples: list[dict],
    query: str,
    output_format: str = "",
) -> str:
    """构建 Few-shot Prompt"""

    prompt = f"""{task_description}

以下是几个示例，请参考这些示例的格式和风格来处理最后的输入：

"""

    for i, ex in enumerate(examples):
        prompt += f"""--- 示例 {i+1} ---
输入：{ex['input']}
输出：{ex['output']}

"""

    prompt += f"""--- 现在请处理以下输入 ---
输入：{query}
"""

    if output_format:
        prompt += f"""
请按照以下格式输出：
{output_format}
"""

    prompt += """
输出："""

    return prompt


if __name__ == "__main__":
    example_pool = [
        {
            "input": "这个产品质量太差了，用了两天就坏了",
            "output": '{"sentiment": "negative", "confidence": 95, "keywords": ["质量差", "坏了"]}',
            "label": "negative",
            "difficulty": 1,
        },
        {
            "input": "物流很快，包装也很好，满意",
            "output": '{"sentiment": "positive", "confidence": 90, "keywords": ["物流快", "包装好", "满意"]}',
            "label": "positive",
            "difficulty": 1,
        },
        {
            "input": "东西还行吧，没有想象中那么好，但也不算差",
            "output": '{"sentiment": "neutral", "confidence": 80, "keywords": ["还行", "一般"]}',
            "label": "neutral",
            "difficulty": 2,
        },
        {
            "input": "客服态度让我无语，但产品质量确实没话说",
            "output": '{"sentiment": "mixed", "confidence": 75, "keywords": ["客服差", "质量好"], "positive_aspects": ["产品质量"], "negative_aspects": ["客服态度"]}',
            "label": "mixed",
            "difficulty": 3,
        },
    ]

    query = "快递太慢了等了一周才到，不过打开后东西还挺精致的"
    examples = select_few_shot_examples(query, example_pool, n=2, strategy="similarity")
    prompt = build_few_shot_prompt(
        task_description="你是一个情感分析助手。请分析用户评论的情感倾向，输出JSON格式。",
        examples=examples,
        query=query,
    )
    print("【构建的 Few-shot Prompt】")
    print(prompt)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=DEFAULT_TEMPERATURE,
    )
    print(f"\n{'='*50}")
    print("【LLM 分析结果】")
    print(f"{'='*50}")
    print(response.choices[0].message.content)