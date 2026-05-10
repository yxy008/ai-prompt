"""
Prompt 基础结构五要素 —— 输出格式控制（Format）消融实验

对比不同格式控制方式的效果：
- 方式1：无格式控制
- 方式2：自然语言格式描述
- 方式3：JSON 格式约束
- 方式4：JSON Schema 原生约束（最可靠）
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL, DEFAULT_TEMPERATURE

client = create_client()


def compare_format_control(query: str):
    """对比不同格式控制方式的效果"""

    # 方式1：无格式控制
    no_format = f"分析以下内容的优缺点：{query}"

    # 方式2：自然语言格式
    natural_format = f"""分析以下内容的优缺点：{query}

请用以下结构输出：
- 优点：（列出3-5条）
- 缺点：（列出3-5条）
- 总结：（一句话）"""

    # 方式3：JSON格式
    json_format = f"""分析以下内容的优缺点：{query}

请严格使用以下JSON格式输出，不要输出任何其他内容：
{{
    "advantages": [
        {{"point": "优点描述", "importance": "高/中/低"}}
    ],
    "disadvantages": [
        {{"point": "缺点描述", "importance": "高/中/低"}}
    ],
    "summary": "一句话总结",
    "overall_score": 1-10的整数评分
}}"""

    # 方式4：带Schema约束的JSON（使用response_format参数）
    schema_format_prompt = f"""分析以下内容的优缺点：{query}

请输出结构化的分析结果。"""

    schema_format_config = {
        "type": "json_schema",
        "json_schema": {
            "name": "analysis",
            "schema": {
                "type": "object",
                "properties": {
                    "advantages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "point": {"type": "string"},
                                "importance": {
                                    "type": "string",
                                    "enum": ["高", "中", "低"]
                                }
                            },
                            "required": ["point", "importance"]
                        }
                    },
                    "disadvantages": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "point": {"type": "string"},
                                "importance": {
                                    "type": "string",
                                    "enum": ["高", "中", "低"]
                                }
                            },
                            "required": ["point", "importance"]
                        }
                    },
                    "summary": {"type": "string"},
                    "overall_score": {"type": "integer", "minimum": 1, "maximum": 10}
                },
                "required": ["advantages", "disadvantages", "summary", "overall_score"]
            }
        }
    }

    # 前三种方式：普通调用
    simple_prompts = {
        "无格式控制": no_format,
        "自然语言格式": natural_format,
        "JSON格式约束": json_format,
    }

    results = {}
    for name, prompt in simple_prompts.items():
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

    # 方式4：使用原生 JSON Schema
    response = client.chat.completions.create(
        model=DEFAULT_MODEL,
        messages=[{"role": "user", "content": schema_format_prompt}],
        temperature=0.1,
        response_format=schema_format_config,
    )
    results["JSON Schema原生约束"] = response.choices[0].message.content
    print(f"\n{'='*50}")
    print(f"【JSON Schema原生约束】")
    print(f"{'='*50}")
    print(results["JSON Schema原生约束"][:300])

    return results


if __name__ == "__main__":
    question = "这款 LED 护眼台灯采用环形灯头设计，支持无极调光调色（3000K～6000K），触控面板操作流畅。优点是光线柔和不刺眼，显色指数 Ra≥95，适合长时间阅读；灯臂可多向调节，适应不同桌面场景；能耗低，LED 灯珠寿命长达 25000 小时。缺点是底座较重占桌面空间，低频 PWM 调光在低亮度下可能存在轻微频闪，Type-C 供电线长度仅 1.5 米，远距离插座需延长线。整体性价比中等，适合学生和居家办公人群。"
    results = compare_format_control(question)