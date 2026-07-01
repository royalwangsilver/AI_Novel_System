import os
from datetime import datetime


def export_novel(story: dict, output_dir: str = "output") -> str:
    """将小说导出为TXT文件"""
    os.makedirs(output_dir, exist_ok=True)
    title = story.get("title", "未命名")
    content = _format_novel(story)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title}_{timestamp}.txt"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return filepath


def _format_novel(story: dict) -> str:
    """将故事数据格式化为纯文本"""
    lines = [f"《{story.get('title', '未命名')}》\n"]
    if story.get("outline"):
        lines.append(f"【大纲】\n{story['outline']}\n")
    for idx in sorted(story.get("chapters", {}).keys(), key=lambda x: int(x)):
        ch = story["chapters"][idx]
        lines.append(f"\n{'='*40}")
        lines.append(f"第{idx}章 {ch['title']}\n")
        lines.append(ch["content"])
    return "\n".join(lines)
