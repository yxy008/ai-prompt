"""
工程化工具 —— Prompt 版本管理器

功能：
- 保存 Prompt 新版本（自动计算内容哈希）
- 获取指定版本的 Prompt
- 列出所有版本历史
- 对比两个版本的差异
"""
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


class PromptVersionManager:
    """Prompt 版本管理器"""

    def __init__(self, storage_dir: str = None):
        if storage_dir is None:
            storage_dir = str(Path(__file__).resolve().parent / "prompt_versions")
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "index.json"
        self._load_index()

    def _load_index(self):
        """加载版本索引"""
        if self.index_file.exists():
            self.index = json.loads(self.index_file.read_text(encoding="utf-8"))
        else:
            self.index = {}

    def _save_index(self):
        """保存版本索引"""
        self.index_file.write_text(
            json.dumps(self.index, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def save_version(
        self,
        prompt_name: str,
        prompt_content: str,
        author: str = "",
        description: str = "",
        tags: list[str] = None,
    ) -> str:
        """保存一个新版本的 Prompt"""
        content_hash = hashlib.md5(prompt_content.encode()).hexdigest()[:8]

        if prompt_name not in self.index:
            self.index[prompt_name] = {"versions": [], "latest_version": 0}

        latest = self.index[prompt_name]["latest_version"]
        new_version = latest + 1
        version_id = f"v{new_version}_{content_hash}"

        prompt_file = self.storage_dir / f"{prompt_name}_{version_id}.txt"
        prompt_file.write_text(prompt_content, encoding="utf-8")

        metadata = {
            "version": new_version,
            "version_id": version_id,
            "content_hash": content_hash,
            "author": author,
            "description": description,
            "tags": tags or [],
            "created_at": datetime.now().isoformat(),
            "content_length": len(prompt_content),
        }
        meta_file = self.storage_dir / f"{prompt_name}_{version_id}.meta.json"
        meta_file.write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        self.index[prompt_name]["versions"].append(metadata)
        self.index[prompt_name]["latest_version"] = new_version
        self._save_index()

        return version_id

    def get_version(self, prompt_name: str, version: int = None) -> dict:
        """获取指定版本的 Prompt"""
        if prompt_name not in self.index:
            raise ValueError(f"Prompt '{prompt_name}' 不存在")

        versions = self.index[prompt_name]["versions"]
        if version is None:
            target = versions[-1]
        else:
            target = next((v for v in versions if v["version"] == version), None)
            if target is None:
                raise ValueError(f"版本 {version} 不存在")

        prompt_file = self.storage_dir / f"{prompt_name}_{target['version_id']}.txt"
        content = prompt_file.read_text(encoding="utf-8")

        return {
            "content": content,
            "metadata": target,
        }

    def list_versions(self, prompt_name: str) -> list[dict]:
        """列出所有版本"""
        if prompt_name not in self.index:
            return []
        return self.index[prompt_name]["versions"]

    def diff(self, prompt_name: str, v1: int, v2: int) -> str:
        """对比两个版本的差异"""
        content1 = self.get_version(prompt_name, v1)["content"]
        content2 = self.get_version(prompt_name, v2)["content"]

        lines1 = content1.split("\n")
        lines2 = content2.split("\n")

        diff_output = []
        max_len = max(len(lines1), len(lines2))

        for i in range(max_len):
            l1 = lines1[i] if i < len(lines1) else "(不存在)"
            l2 = lines2[i] if i < len(lines2) else "(不存在)"
            if l1 != l2:
                diff_output.append(f"行 {i+1}:")
                diff_output.append(f"  - {l1[:80]}")
                diff_output.append(f"  + {l2[:80]}")

        return "\n".join(diff_output)


if __name__ == "__main__":
    manager = PromptVersionManager()

    v1 = manager.save_version(
        prompt_name="customer_service",
        prompt_content="你是一个客服助手，请礼貌地回答用户问题。",
        author="张三",
        description="初始版本，基础客服Prompt",
        tags=["客服", "v1"],
    )

    v2 = manager.save_version(
        prompt_name="customer_service",
        prompt_content="""你是一个专业的客服助手。

【回复原则】
1. 先表达理解和共情
2. 再提供具体解决方案
3. 最后确认用户是否满意

【禁止行为】
- 不要承诺无法兑现的赔偿
- 不要泄露公司内部信息""",
        author="张三",
        description="增加了回复原则和禁止行为约束",
        tags=["客服", "v2", "改进"],
    )

    versions = manager.list_versions("customer_service")
    for v in versions:
        print(f"版本 {v['version']}: {v['description']} ({v['created_at'][:10]})")

    diff = manager.diff("customer_service", 1, 2)
    print(f"\n版本差异:\n{diff}")