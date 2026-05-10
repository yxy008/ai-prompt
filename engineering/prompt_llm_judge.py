"""
工程化工具 —— LLM-as-Judge 评估

用 LLM 评估 LLM 的输出质量。
评估维度：准确性、完整性、清晰度、有用性等。
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL

client = create_client()


class LLMJudge:
    """用 LLM 评估 LLM 的输出"""

    def evaluate(
        self,
        question: str,
        answer: str,
        reference: str = None,
        criteria: list[str] = None,
    ) -> dict:
        """评估回答质量"""
        if criteria is None:
            criteria = ["准确性", "完整性", "清晰度", "有用性"]

        criteria_text = "\n".join([f"{i+1}. {c}" for i, c in enumerate(criteria)])
        reference_text = f"\n参考答案：{reference}" if reference else ""

        judge_prompt = f"""请评估以下回答的质量。

问题：{question}
{reference_text}
待评估回答：{answer}

请从以下维度评分（1-10分）：
{criteria_text}

请以JSON格式输出：
{{"scores": {{"准确性": 8, ...}}, "overall": 8.5, "comments": "总体评价"}}"""

        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": judge_prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        return json.loads(response.choices[0].message.content)


if __name__ == "__main__":
    judge = LLMJudge()

    question = "Python中的GIL是什么？"
    answer = "GIL是全局解释器锁，它确保同一时刻只有一个线程执行Python字节码。这导致CPU密集型任务无法利用多核，但IO密集型任务影响较小。"
    reference = "GIL（Global Interpreter Lock）是CPython中的互斥锁，保证同一时刻只有一个线程在执行Python字节码。它简化了内存管理，但限制了多线程并行。"

    result = judge.evaluate(
        question=question,
        answer=answer,
        reference=reference,
        criteria=["准确性", "完整性", "清晰度", "与参考答案的一致性"],
    )

    print("评估结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))