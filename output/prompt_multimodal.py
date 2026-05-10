"""
结构化输出控制 —— 多模态 Prompt 设计

构建包含文本和图片的多模态 Prompt。
支持 detail_level: auto / low / high
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import create_client, DEFAULT_MODEL

client = create_client()


def build_multimodal_prompt(
    text_instruction: str,
    image_urls: list[str],
    detail_level: str = "auto",
) -> dict:
    """构建多模态 Prompt（文本 + 图片）"""
    content = [{"type": "text", "text": text_instruction}]

    for url in image_urls:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": url,
                "detail": detail_level,  # auto, low, high
            },
        })

    return {
        "model": DEFAULT_MODEL,
        "messages": [{"role": "user", "content": content}],
        "max_tokens": 1000,
    }


if __name__ == "__main__":
    prompt_config = build_multimodal_prompt(
        text_instruction="请描述这张图片中的内容，包括主要物体、颜色、场景和氛围。",
        image_urls=["https://example.com/sample-image.jpg"],
        detail_level="auto",
    )
    print("【构建的多模态 Prompt 配置】")
    print(f"模型: {prompt_config['model']}")
    print(f"消息数量: {len(prompt_config['messages'][0]['content'])} 个内容块")
    print(f"最大Token: {prompt_config['max_tokens']}")

    # 注意：实际调用需要替换为真实的图片URL
    # response = client.chat.completions.create(**prompt_config)
    # print(response.choices[0].message.content)