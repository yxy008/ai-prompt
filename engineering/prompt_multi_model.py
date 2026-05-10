"""
工程化工具 —— 多模型 Prompt 适配器

不同模型对 Prompt 的响应特性不同：
- GPT-4/4o: System Prompt 敏感度高
- Claude 3.5: 偏好 XML 标签格式
- DeepSeek: 中文能力极好
- Gemini: 长上下文遵循极好
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class MultiModelPromptAdapter:
    """多模型 Prompt 适配器"""

    MODEL_CONFIGS = {
        "gpt-4o": {
            "system_prompt_position": "first",
            "prefer_xml": False,
            "max_tokens": 4096,
        },
        "claude-3.5-sonnet": {
            "system_prompt_position": "first",
            "prefer_xml": True,
            "max_tokens": 4096,
        },
        "deepseek-chat": {
            "system_prompt_position": "first",
            "prefer_xml": False,
            "max_tokens": 4096,
        },
    }

    def __init__(self, model_name: str):
        self.model_name = model_name
        self.config = self.MODEL_CONFIGS.get(model_name, {})

    def adapt(self, prompt: str) -> str:
        """根据目标模型调整 Prompt"""
        if self.config.get("prefer_xml"):
            prompt = prompt.replace("【", "<").replace("】", ">")

        return prompt


if __name__ == "__main__":
    original_prompt = """你是一位【Python专家】。

【任务】
分析以下代码的性能问题。

【约束】
不要修改代码逻辑。"""

    print("原始 Prompt:")
    print(original_prompt)

    for model in ["gpt-4o", "claude-3.5-sonnet", "deepseek-chat"]:
        adapter = MultiModelPromptAdapter(model)
        adapted = adapter.adapt(original_prompt)
        print(f"\n适配 {model}:")
        print(adapted[:200])
        if adapter.config.get("prefer_xml"):
            print("  (已将【】替换为XML标签<>)")