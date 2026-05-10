"""
Prompt 基础结构五要素 —— 角色设定（Role）消融实验

对比不同角色设定对 LLM 回答质量的影响：
- 无角色：通用回答，风格随机
- 职业角色：激活专业术语和行业惯例
- 场景角色：激活情境感知和语气适配
- 复合角色：激活多维度能力
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


def test_role_effect(question: str):
    """对比不同角色设定对回答质量的影响"""

    # 无角色
    no_role_prompt = f"回答以下问题：{question}"

    # 职业角色
    role_prompt = f"""你是一位资深Python后端工程师，拥有10年开发经验。
请回答以下问题：{question}"""

    # 场景角色
    scene_prompt = f"""你是一位技术面试官，正在面试一位中级Python工程师。
请用面试提问的方式回答以下问题，并评估回答者应该达到的水平：
{question}"""

    # 复合角色
    composite_prompt = f"""你是一位拥有10年Python经验的架构师，
同时也是一位优秀的技术写作者，擅长用通俗易懂的方式解释复杂概念。
你的读者是有1-2年编程经验的初级开发者。
请回答以下问题：{question}"""

    prompts = {
        "无角色": no_role_prompt,
        "职业角色": role_prompt,
        "场景角色": scene_prompt,
        "复合角色": composite_prompt,
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
    question = "Python中的GIL是什么？它如何影响多线程编程？"
    results = test_role_effect(question)