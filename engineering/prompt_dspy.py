"""
工程化工具 —— DSPy 自动化 Prompt 优化

DSPy 是斯坦福大学提出的 Prompt 自动优化框架。
核心思想：不手动写 Prompt，而是定义"你想要什么"，
让框架自动搜索最优的 Prompt。

核心概念：
- Signature：定义输入输出签名（类似函数签名）
- Module：定义处理逻辑（类似神经网络层）
- Optimizer：自动优化 Prompt（类似模型训练）

注意：需要安装 dspy-ai 库
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def demo_dspy_optimization():
    """DSPy 自动优化演示"""

    import dspy

    lm = dspy.LM("openai/gpt-4o-mini")
    dspy.configure(lm=lm)

    # 1. 定义任务签名
    class SentimentAnalysis(dspy.Signature):
        """分析文本的情感倾向"""
        text: str = dspy.InputField(desc="待分析的文本")
        sentiment: str = dspy.OutputField(desc="情感倾向：positive/negative/neutral")
        confidence: float = dspy.OutputField(desc="置信度 0-1")
        keywords: list[str] = dspy.OutputField(desc="关键情感词")

    # 2. 定义模块（使用CoT推理）
    class SentimentModule(dspy.Module):
        def __init__(self):
            super().__init__()
            self.analyzer = dspy.ChainOfThought(SentimentAnalysis)

        def forward(self, text: str):
            return self.analyzer(text=text)

    # 3. 准备训练数据
    trainset = [
        dspy.Example(
            text="这个产品太棒了，我非常喜欢！",
            sentiment="positive",
            confidence=0.95,
            keywords=["太棒了", "非常喜欢"],
        ).with_inputs("text"),
        dspy.Example(
            text="质量很差，用了两天就坏了，失望。",
            sentiment="negative",
            confidence=0.90,
            keywords=["很差", "坏了", "失望"],
        ).with_inputs("text"),
        dspy.Example(
            text="还行吧，没有特别好也没有特别差。",
            sentiment="neutral",
            confidence=0.75,
            keywords=["还行"],
        ).with_inputs("text"),
    ]

    # 4. 自动优化 Prompt
    optimizer = dspy.BootstrapFewShot(
        metric=lambda example, pred, trace=None:
            1.0 if example.sentiment == pred.sentiment else 0.0,
        max_bootstrapped_demos=3,
    )

    optimized_module = optimizer.compile(
        SentimentModule(),
        trainset=trainset,
    )

    # 5. 使用优化后的模块
    result = optimized_module(text="服务态度很好，但产品质量一般")
    print(f"情感: {result.sentiment}")
    print(f"置信度: {result.confidence}")
    print(f"关键词: {result.keywords}")

    return optimized_module


if __name__ == "__main__":
    print("DSPy 自动优化演示")
    print("=" * 50)
    print("注意：需要安装 dspy-ai 库: pip install dspy-ai")
    print()

    try:
        demo_dspy_optimization()
    except ImportError:
        print("dspy-ai 未安装，跳过演示。")
        print("请运行: pip install dspy-ai")
    except Exception as e:
        print(f"运行出错: {e}")