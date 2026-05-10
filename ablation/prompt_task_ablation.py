"""
Prompt 基础结构五要素 —— 任务指令（Task）消融实验

对比不同精确度的任务指令对 LLM 回答质量的影响：
- 级别1：模糊任务（效果不可控）
- 级别2：明确了做什么
- 级别3：明确了怎么做
- 级别4：明确了做到什么程度
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


def test_task_precision():
    """对比不同任务设定对回答质量的影响"""

    # 级别1：模糊任务（效果不可控）
    bad_task = "帮我写一个函数"

    # 级别2：明确了做什么
    better_task = "帮我写一个Python函数，用于验证邮箱地址格式"

    # 级别3：明确了怎么做
    good_task = """帮我写一个Python函数，用于验证邮箱地址格式。
要求：
- 使用正则表达式
- 返回布尔值
- 包含类型注解"""

    # 级别4：明确了做到什么程度
    best_task = """帮我写一个Python函数，用于验证邮箱地址格式。

【函数签名】
def validate_email(email: str) -> bool:

【验证规则】
1. 必须包含@符号，且@前后都有内容
2. 域名部分至少包含一个点号
3. 不允许连续两个点号
4. 总长度不超过254个字符
5. 只允许字母、数字、点号、下划线、百分号、加号、减号

【输出要求】
- 返回True表示格式有效，False表示无效
- 函数内部需要有清晰的注释
- 附带3个测试用例（2个有效，1个无效）

【不要做】
- 不要使用第三方库
- 不要发送真实邮件验证"""

    prompts = {
        "模糊任务（效果不可控）": bad_task,
        "明确了做什么": better_task,
        "明确了怎么做": good_task,
        "明确了做到什么程度": best_task,
    }

    results = {}
    for name, prompt in prompts.items():
        response = client.chat.completions.create(
            model=DEFAULT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=DEFAULT_TEMPERATURE,
        )
        results[name] = response.choices[0].message.content
        print(f"\n{'='*50}")
        print(f"【{name}】")
        print(f"{'='*50}")
        print(results[name][:300])

    return results


if __name__ == "__main__":
    results = test_task_precision()