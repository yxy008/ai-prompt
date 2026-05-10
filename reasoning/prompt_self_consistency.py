"""
进阶推理技术 —— 自洽性（Self-Consistency）

核心思想：不是只让 LLM 推理一次，而是让它推理多次
（通过设置 temperature > 0），然后取出现频率最高的答案。

原理：一个复杂问题可能有多种推理路径，但正确答案应该
在不同的推理路径中反复出现。
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL

client = create_client()


class SelfConsistencyReasoner:
    """自洽性推理器"""

    def __init__(self, model: str = None):
        self.model = model or DEFAULT_MODEL

    def reason(
        self,
        question: str,
        n_samples: int = 5,
        temperature: float = 0.7,
    ) -> dict:
        """
        自洽性推理

        Args:
            question: 问题
            n_samples: 采样次数（建议5-10次）
            temperature: 温度参数（需要>0才能产生不同推理路径）
        """
        cot_prompt = f"""{question}

请一步一步地推理。先写出完整的推理过程，然后在最后一行给出最终答案。
最终答案请以"答案："开头。"""

        reasoning_paths = []
        answers = []

        for i in range(n_samples):
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": cot_prompt}],
                temperature=temperature,
            )
            full_response = response.choices[0].message.content

            answer = self._extract_answer(full_response)

            reasoning_paths.append(full_response)
            answers.append(answer)

        answer_counts = Counter(answers)
        most_common_answer = answer_counts.most_common(1)[0][0]
        confidence = answer_counts[most_common_answer] / n_samples

        return {
            "final_answer": most_common_answer,
            "confidence": confidence,
            "vote_distribution": dict(answer_counts),
            "all_reasoning_paths": reasoning_paths,
            "n_samples": n_samples,
        }

    def _extract_answer(self, response: str) -> str:
        """从完整响应中提取最终答案"""
        lines = response.strip().split("\n")
        for line in reversed(lines):
            if "答案：" in line or "答案:" in line:
                return line.split("答案：")[-1].split("答案:")[-1].strip()
        return lines[-1].strip() if lines else response.strip()


if __name__ == "__main__":
    reasoner = SelfConsistencyReasoner()

    question = """
一个商店有以下促销活动：
- 满100减20
- 满200减50
- 满300减90

小明买了以下商品：
- 商品A：85元
- 商品B：120元
- 商品C：95元

请问小明最少需要支付多少钱？（可以任意组合使用优惠券）
"""

    result = reasoner.reason(question, n_samples=5, temperature=0.8)

    print(f"最终答案: {result['final_answer']}")
    print(f"置信度: {result['confidence']:.0%}")
    print(f"投票分布: {result['vote_distribution']}")
    print(f"\n各推理路径:")
    for i, path in enumerate(result['all_reasoning_paths']):
        print(f"\n--- 路径 {i+1} ---")
        print(path[:200])