import json
import os
from datetime import datetime


class StoryManager:
    """故事管理器，负责小说项目的创建、保存和加载"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def create_story(self, title: str, theme: str, genre: str, style: str, outline: str) -> dict:
        """创建新的小说项目"""
        story = {
            "title": title,
            "theme": theme,
            "genre": genre,
            "style": style,
            "outline": outline,
            "chapters": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self._save_story(story)
        return story

    def add_chapter(self, story: dict, chapter_index: int, chapter_title: str, content: str) -> dict:
        """添加章节内容"""
        story["chapters"][str(chapter_index)] = {
            "title": chapter_title,
            "content": content,
        }
        story["updated_at"] = datetime.now().isoformat()
        self._save_story(story)
        return story

    def get_full_text(self, story: dict) -> str:
        """获取完整小说文本"""
        parts = [f"# {story['title']}\n"]
        for idx in sorted(story["chapters"].keys(), key=int):
            ch = story["chapters"][idx]
            parts.append(f"\n## {ch['title']}\n\n{ch['content']}")
        return "\n".join(parts)

    def _save_story(self, story: dict):
        """保存故事到文件"""
        filename = self._get_filename(story["title"])
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(story, f, ensure_ascii=False, indent=2)

    def load_story(self, title: str) -> dict | None:
        """从文件加载故事"""
        filename = self._get_filename(title)
        filepath = os.path.join(self.data_dir, filename)
        if not os.path.exists(filepath):
            return None
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def list_stories(self) -> list[str]:
        """列出所有已保存的故事标题"""
        if not os.path.exists(self.data_dir):
            return []
        return [f.replace(".json", "") for f in os.listdir(self.data_dir) if f.endswith(".json")]

    @staticmethod
    def _get_filename(title: str) -> str:
        return f"{title}.json"
