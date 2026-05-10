"""
进阶推理技术 —— 思维树（Tree of Thoughts, ToT）

核心思想：不只是线性推理，而是在每个步骤探索多个可能性，
形成一棵"思维树"，然后通过评估和搜索找到最优路径。

适用场景：需要创造性解决方案的开放问题、数学证明、
策略规划和方案设计、创意写作的大纲规划。

注意：ToT 的 API 调用成本很高（每步需要多次 LLM 调用），
仅适用于需要探索多路径的复杂任务。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL

client = create_client()


class TreeOfThoughts:
    """思维树推理框架（简化版）"""

    def __init__(self, model: str = None):
        self.model = model or DEFAULT_MODEL

    def generate_thoughts(
        self,
        problem: str,
        current_state: str = "",
        n_thoughts: int = 3,
    ) -> list[str]:
        """为一个状态生成多个可能的下一步思考"""
        prompt = f"""我正在解决以下问题：
{problem}

当前的分析状态：
{current_state if current_state else "（刚开始分析）"}

请提出 {n_thoughts} 个不同的下一步分析方向。每个方向应该从不同角度思考问题。
用"方向1："、"方向2："等标记区分。"""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
        )
        text = response.choices[0].message.content

        thoughts = []
        for line in text.split("\n"):
            for i in range(1, n_thoughts + 1):
                if f"方向{i}" in line or f"思路{i}" in line:
                    thoughts.append(line.split("：", 1)[-1].strip())

        return thoughts[:n_thoughts]

    def evaluate_thought(
        self,
        problem: str,
        thought: str,
        context: str = "",
    ) -> float:
        """评估一个思考方向的价值（返回0-1的分数）"""
        prompt = f"""问题：{problem}

当前上下文：{context}

待评估的分析方向：{thought}

请评估这个分析方向对解决最终问题的价值。
只输出一个0到100的整数分数（0=完全没用，100=极其关键）。
分数："""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        try:
            score = int(response.choices[0].message.content.strip())
            return min(max(score, 0), 100) / 100.0
        except ValueError:
            return 0.5

    def search(
        self,
        problem: str,
        max_depth: int = 3,
        beam_width: int = 2,
    ) -> dict:
        """
        束搜索思维树

        Args:
            problem: 要解决的问题
            max_depth: 最大搜索深度
            beam_width: 每层保留的最优分支数
        """
        beam = [("", 1.0)]

        for depth in range(max_depth):
            candidates = []

            for state, score in beam:
                thoughts = self.generate_thoughts(
                    problem, state, n_thoughts=3
                )

                for thought in thoughts:
                    thought_score = self.evaluate_thought(
                        problem, thought, state
                    )
                    new_state = state + "\n" + thought if state else thought
                    new_score = score * thought_score
                    candidates.append((new_state, new_score))

            candidates.sort(key=lambda x: x[1], reverse=True)
            beam = candidates[:beam_width]

            print(f"深度 {depth+1}: 保留了 {len(beam)} 个最优分支")

        best_path = beam[0][0]
        final_prompt = f"""基于以下分析过程，给出最终答案：

问题：{problem}

分析过程：
{best_path}

最终答案："""

        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": final_prompt}],
            temperature=0.3,
        )

        return {
            "answer": response.choices[0].message.content,
            "reasoning_path": best_path,
            "confidence": beam[0][1],
        }


if __name__ == "__main__":
    tot = TreeOfThoughts()

    problem = """
设计一个在线教育平台的推荐系统。
需要考虑：
1. 新用户冷启动问题
2. 课程完成率低的问题
3. 用户兴趣随时间变化
"""

    result = tot.search(problem, max_depth=2, beam_width=2)
    print(f"\n推荐方案:\n{result['answer']}")
    print(f"\n推理路径:\n{result['reasoning_path']}")
    print(f"\n置信度: {result['confidence']:.2%}")