"""
结构化输出控制 —— JSON 结构化输出

可靠性层级：
- 级别1：Prompt中描述 → 可靠性 60-70%
- 级别2：Few-shot示例 → 可靠性 80-90%
- 级别3：response_format参数 → 可靠性 95-99%
- 级别4：Function Calling → 可靠性 99%+
"""
import json
import re
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL

client = create_client()


class StructuredOutputExtractor:
    """结构化输出提取器"""

    def __init__(self, model: str = None):
        self.model = model or DEFAULT_MODEL

    def extract_json(
        self,
        prompt: str,
        schema: Optional[dict] = None,
        use_native: bool = True,
    ) -> dict:
        """
        提取JSON结构化输出

        Args:
            prompt: 用户指令
            schema: JSON Schema（可选）
            use_native: 是否使用API原生的response_format
        """
        if use_native and schema:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个结构化数据提取助手。请严格按照要求的JSON格式输出。"},
                    {"role": "user", "content": prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "extraction",
                        "schema": schema,
                    }
                },
                temperature=0.1,
            )
            return json.loads(response.choices[0].message.content)

        else:
            schema_desc = json.dumps(schema, ensure_ascii=False, indent=2) if schema else ""
            full_prompt = f"""{prompt}

请严格按照以下JSON Schema输出，不要输出任何其他内容：
{schema_desc}

输出："""

            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.1,
            )

            content = response.choices[0].message.content
            return self._parse_json(content)

    def _parse_json(self, text: str) -> dict:
        """从文本中提取JSON（容错处理）"""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass

        raise ValueError(f"无法从响应中提取JSON: {text[:200]}")


if __name__ == "__main__":
    extractor = StructuredOutputExtractor()

    person_schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "姓名"},
            "age": {"type": "integer", "description": "年龄"},
            "skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "技能列表"
            },
            "experience_years": {"type": "integer", "description": "工作年限"},
        },
        "required": ["name", "skills"],
    }

    result = extractor.extract_json(
        prompt="从以下简历中提取信息：张三，28岁，5年Python开发经验，擅长Django、FastAPI、Docker。",
        schema=person_schema,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))