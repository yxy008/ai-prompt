"""
工程化工具 —— Prompt 调试器

功能：
- 检查 Prompt 长度是否合理
- 检测关键元素（角色、任务、格式、约束）是否缺失
- 运行测试用例并收集结果
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL

client = create_client()


class PromptDebugger:
    """Prompt 调试工具"""

    def diagnose(self, prompt: str, test_inputs: list[str]) -> dict:
        """诊断 Prompt 的问题"""
        issues = []

        # 检查1：长度分析
        if len(prompt) > 4000:
            issues.append({
                "severity": "warning",
                "issue": "Prompt过长",
                "detail": f"当前{len(prompt)}字符，建议控制在2000以内",
                "fix": "精简指令，将详细说明移到外部文档",
            })

        # 检查2：关键元素检测
        checks = {
            "角色设定": ["你是", "你是一位", "作为"],
            "任务指令": ["请", "需要", "要求"],
            "输出格式": ["格式", "输出", "JSON", "表格", "列表"],
            "约束条件": ["不要", "禁止", "必须", "不能", "只"],
        }
        for element, keywords in checks.items():
            if not any(kw in prompt for kw in keywords):
                issues.append({
                    "severity": "suggestion",
                    "issue": f"缺少{element}",
                    "detail": f"Prompt中未检测到{element}相关指令",
                    "fix": f"添加明确的{element}说明",
                })

        # 检查3：测试运行
        test_results = []
        for test_input in test_inputs:
            response = client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt.replace("{input}", test_input)}],
                temperature=0.3,
            )
            output = response.choices[0].message.content
            test_results.append({
                "input": test_input,
                "output": output[:200],
                "tokens": response.usage.total_tokens,
            })

        return {
            "issues": issues,
            "test_results": test_results,
            "prompt_length": len(prompt),
            "estimated_input_tokens": len(prompt) // 2,
        }


if __name__ == "__main__":
    debugger = PromptDebugger()

    test_prompt = """你是一个客服助手。
请回答用户问题：{input}"""

    result = debugger.diagnose(
        prompt=test_prompt,
        test_inputs=["我想退货", "物流太慢了"],
    )

    print(f"Prompt长度: {result['prompt_length']} 字符")
    print(f"估计Token: {result['estimated_input_tokens']}")
    print(f"\n发现 {len(result['issues'])} 个问题:")
    for issue in result['issues']:
        print(f"  [{issue['severity']}] {issue['issue']}: {issue['detail']}")
        print(f"    修复建议: {issue['fix']}")

    print(f"\n测试结果:")
    for tr in result['test_results']:
        print(f"  输入: {tr['input']}")
        print(f"  输出: {tr['output'][:100]}...")
        print(f"  Token: {tr['tokens']}")
        print()