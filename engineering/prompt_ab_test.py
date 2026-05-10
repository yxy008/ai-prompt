"""
工程化工具 —— Prompt A/B 测试框架

用于对比不同 Prompt 变体的效果，支持：
- 多测试用例批量运行
- 延迟、Token消耗、成本统计
- 自定义评估指标
"""
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL

client = create_client()


@dataclass
class ABTestResult:
    """A/B 测试结果"""
    variant_name: str
    prompt: str
    response: str
    latency: float
    token_count: int
    cost: float
    metrics: dict = field(default_factory=dict)


class PromptABTester:
    """Prompt A/B 测试框架"""

    def __init__(self):
        self.results: list[ABTestResult] = []

    def run_test(
        self,
        test_cases: list[str],
        variants: dict[str, str],
        evaluator: Callable[[str, str], dict],
        expected_outputs: list[str] = None,
    ) -> dict:
        """运行 A/B 测试"""
        summary = {}

        for variant_name, prompt_template in variants.items():
            variant_results = []

            for i, test_input in enumerate(test_cases):
                prompt = prompt_template.replace("{input}", test_input)

                start = time.time()
                response = client.chat.completions.create(
                    model=DEFAULT_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                latency = time.time() - start

                output = response.choices[0].message.content
                usage = response.usage

                expected = expected_outputs[i] if expected_outputs else None
                metrics = evaluator(output, expected) if evaluator else {}

                result = ABTestResult(
                    variant_name=variant_name,
                    prompt=prompt,
                    response=output,
                    latency=latency,
                    token_count=usage.total_tokens,
                    cost=self._calc_cost(usage),
                    metrics=metrics,
                )
                variant_results.append(result)
                self.results.append(result)

            summary[variant_name] = {
                "avg_latency": sum(r.latency for r in variant_results) / len(variant_results),
                "avg_tokens": sum(r.token_count for r in variant_results) / len(variant_results),
                "total_cost": sum(r.cost for r in variant_results),
                "metrics": self._aggregate_metrics(variant_results),
            }

        return summary

    def _calc_cost(self, usage) -> float:
        """计算成本（GPT-4o-mini价格）"""
        return (
            usage.prompt_tokens * 0.15 / 1_000_000
            + usage.completion_tokens * 0.6 / 1_000_000
        )

    def _aggregate_metrics(self, results: list[ABTestResult]) -> dict:
        """聚合指标"""
        if not results or not results[0].metrics:
            return {}
        aggregated = {}
        for key in results[0].metrics:
            values = [r.metrics[key] for r in results if key in r.metrics]
            if values:
                aggregated[key] = {
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                }
        return aggregated


def simple_evaluator(response: str, expected: str = None) -> dict:
    """简单的评估器"""
    return {
        "length": len(response),
        "has_bullet_points": 1 if ("-" in response or "1." in response) else 0,
    }


if __name__ == "__main__":
    tester = PromptABTester()

    variants = {
        "A_简洁版": "用一句话解释{input}",
        "B_详细版": """请详细解释{input}，包括：
1. 定义
2. 核心原理
3. 一个具体例子""",
    }

    test_cases = ["什么是机器学习", "什么是深度学习", "什么是神经网络"]

    summary = tester.run_test(
        test_cases=test_cases,
        variants=variants,
        evaluator=simple_evaluator,
    )

    for variant, stats in summary.items():
        print(f"\n{variant}:")
        print(f"  平均延迟: {stats['avg_latency']:.3f}s")
        print(f"  平均Token: {stats['avg_tokens']:.0f}")
        print(f"  总成本: ${stats['total_cost']:.6f}")
        print(f"  指标: {stats['metrics']}")