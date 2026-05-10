"""
工程化工具 —— 分层 Prompt 架构

业界最佳实践：将 Prompt 分为四层

Layer 1: 系统层（System Prompt）
  - 角色定义、安全规则、全局约束
  - 不随对话变化，始终生效

Layer 2: 任务层（Task Prompt）
  - 当前任务的具体指令
  - 随任务类型变化

Layer 3: 上下文层（Context）
  - RAG检索结果、用户信息、对话历史
  - 随每次请求变化

Layer 4: 格式层（Format）
  - 输出格式约束、JSON Schema
  - 随输出需求变化
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


class LayeredPromptBuilder:
    """分层 Prompt 构建器"""

    def __init__(self):
        self.system_layer = ""
        self.task_layer = ""
        self.context_layer = ""
        self.format_layer = ""

    def set_system(self, role: str, rules: list[str] = None):
        """设置系统层"""
        self.system_layer = f"你是一位{role}。"
        if rules:
            self.system_layer += "\n\n【核心规则】\n" + "\n".join(
                [f"- {r}" for r in rules]
            )

    def set_task(self, task: str, steps: list[str] = None):
        """设置任务层"""
        self.task_layer = f"\n\n【当前任务】\n{task}"
        if steps:
            self.task_layer += "\n\n【执行步骤】\n" + "\n".join(
                [f"{i+1}. {s}" for i, s in enumerate(steps)]
            )

    def set_context(self, **kwargs):
        """设置上下文层"""
        parts = []
        for key, value in kwargs.items():
            if value:
                parts.append(f"【{key}】\n{value}")
        self.context_layer = "\n\n" + "\n\n".join(parts) if parts else ""

    def set_format(self, format_desc: str):
        """设置格式层"""
        self.format_layer = f"\n\n【输出格式】\n{format_desc}"

    def build(self) -> str:
        """构建完整 Prompt"""
        return (
            self.system_layer
            + self.task_layer
            + self.context_layer
            + self.format_layer
        )


if __name__ == "__main__":
    builder = LayeredPromptBuilder()
    builder.set_system(
        role="资深代码审查员，拥有10年Python经验",
        rules=[
            "只审查代码质量和安全性，不评价代码风格",
            "每个问题必须给出具体的修改建议",
            "如果代码没有问题，明确说明'未发现问题'",
        ],
    )
    builder.set_task(
        task="审查以下Python代码的安全性和性能问题",
        steps=["检查SQL注入风险", "检查资源泄露", "检查异常处理", "检查性能瓶颈"],
    )
    builder.set_context(
        代码文件="app.py",
        代码行数="156行",
        框架="FastAPI + SQLAlchemy",
    )
    builder.set_format("""
使用Markdown格式输出：
## 审查概要
## 发现的问题
### 问题1：[严重程度]
- 位置：第X行
- 描述：
- 建议：
""")

    prompt = builder.build()
    print("【分层构建的 Prompt】")
    print(prompt)

    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=DEFAULT_TEMPERATURE,
    )
    print(f"\n{'='*50}")
    print("【LLM 审查结果】")
    print(f"{'='*50}")
    print(response.choices[0].message.content)