"""
进阶推理技术 —— ReAct 模式（Reasoning + Acting）

核心思想：将推理和行动交织在一起——LLM 不仅思考，
还能调用外部工具获取信息，然后基于新信息继续思考。

ReAct 循环：
思考 → 行动（查资料）→ 观察结果 → 思考 → 行动（计算）→ 观察结果 → 思考 → 答案
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL

client = create_client()


class ReActAgent:
    """ReAct 模式 Agent"""

    def __init__(self, model: str = None):
        self.model = model or DEFAULT_MODEL

        self.tools = {
            "search": self._search_knowledge_base,
            "calculate": self._calculate,
            "get_date": self._get_current_date,
        }

    def _search_knowledge_base(self, query: str) -> str:
        """模拟知识库搜索"""
        kb = {
            "Python GIL": "GIL（全局解释器锁）确保同一时刻只有一个线程执行Python字节码。CPU密集型任务受GIL影响大，IO密集型任务影响小。",
            "asyncio": "asyncio是Python的异步IO库，使用事件循环实现协程并发。适合IO密集型任务。",
            "多线程": "Python多线程由于GIL的存在，CPU密集型任务无法利用多核。但对于IO密集型任务，多线程仍然有效。",
        }
        for key, value in kb.items():
            if key.lower() in query.lower():
                return value
        return f"未找到关于'{query}'的相关信息"

    def _calculate(self, expression: str) -> str:
        """执行数学计算"""
        try:
            result = eval(expression)
            return f"计算结果：{expression} = {result}"
        except Exception as e:
            return f"计算错误：{str(e)}"

    def _get_current_date(self, _: str = "") -> str:
        """获取当前日期"""
        return f"当前日期：{datetime.now().strftime('%Y-%m-%d')}"

    def run(self, question: str, max_steps: int = 5) -> dict:
        """运行 ReAct 循环"""

        react_prompt = f"""你是一个能够使用工具的AI助手。请使用以下格式回答：

问题：需要回答的问题
思考：分析当前情况，决定下一步
行动：要使用的工具名称[工具的输入]
观察：工具返回的结果
...（可以重复思考-行动-观察多次）
思考：基于所有观察，我现在可以给出最终答案
最终答案：用中文给出的完整答案

可用工具：
- search[查询内容]：搜索知识库
- calculate[数学表达式]：执行计算
- get_date[]：获取当前日期

现在开始：

问题：{question}
"""

        messages = [{"role": "user", "content": react_prompt}]
        steps = []

        for step in range(max_steps):
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
            )
            output = response.choices[0].message.content
            steps.append(output)

            action_match = re.search(r"行动[：:]\s*(\w+)\[(.*?)\]", output)
            if action_match:
                tool_name = action_match.group(1)
                tool_input = action_match.group(2)

                if tool_name in self.tools:
                    observation = self.tools[tool_name](tool_input)
                    messages.append({"role": "assistant", "content": output})
                    messages.append({
                        "role": "user",
                        "content": f"观察：{observation}\n请继续。"
                    })
                else:
                    messages.append({"role": "assistant", "content": output})
                    messages.append({
                        "role": "user",
                        "content": f"观察：未知工具 '{tool_name}'"
                    })
            else:
                break

        final_answer = steps[-1] if steps else "无法生成答案"
        answer_match = re.search(
            r"最终答案[：:]\s*(.+)",
            final_answer,
            re.DOTALL,
        )
        if answer_match:
            final_answer = answer_match.group(1).strip()

        return {
            "answer": final_answer,
            "steps": steps,
            "total_steps": len(steps),
        }


if __name__ == "__main__":
    agent = ReActAgent()

    question = "Python中GIL对多线程有什么影响？asyncio能解决这个问题吗？"
    result = agent.run(question)

    print(f"最终答案:\n{result['answer']}")
    print(f"\n总步数: {result['total_steps']}")
    for i, step in enumerate(result['steps']):
        print(f"\n--- 步骤 {i+1} ---")
        print(step[:200])