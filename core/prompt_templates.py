class PromptTemplates:
    """提示词模板管理"""

    SYSTEM_ROLE = "你是一位才华横溢的小说家，擅长创作引人入胜的故事。你的文字优美、情节紧凑、人物刻画生动。"

    @classmethod
    def build_outline_prompt(cls, theme: str, genre: str, style: str) -> list[dict]:
        """构建生成大纲的提示词"""
        return [
            {"role": "system", "content": cls.SYSTEM_ROLE},
            {
                "role": "user",
                "content": (
                    f"请根据以下要求创作一个小说大纲：\n"
                    f"- 主题：{theme}\n"
                    f"- 类型：{genre}\n"
                    f"- 风格：{style}\n\n"
                    f"请包含以下内容：\n"
                    f"1. 小说标题\n"
                    f"2. 故事简介（200字以内）\n"
                    f"3. 主要人物介绍（至少3个角色）\n"
                    f"4. 章节规划（列出每章标题和简要内容）\n"
                ),
            },
        ]

    @classmethod
    def build_chapter_prompt(cls, outline: str, chapter_index: int, chapter_title: str, previous_content: str = "") -> list[dict]:
        """构建生成章节的提示词"""
        context = f"以下是前文内容摘要：\n{previous_content}\n\n" if previous_content else ""
        return [
            {"role": "system", "content": cls.SYSTEM_ROLE},
            {
                "role": "user",
                "content": (
                    f"以下是小说大纲：\n{outline}\n\n"
                    f"{context}"
                    f"请根据大纲撰写第{chapter_index}章：{chapter_title}\n"
                    f"要求：\n"
                    f"- 内容与大纲保持一致\n"
                    f"- 字数在1500-2500字之间\n"
                    f"- 注意情节衔接和人物塑造\n"
                ),
            },
        ]

    @classmethod
    def build_continue_prompt(cls, existing_content: str, direction: str = "") -> list[dict]:
        """构建续写的提示词"""
        direction_hint = f"\n续写方向提示：{direction}" if direction else ""
        return [
            {"role": "system", "content": cls.SYSTEM_ROLE},
            {
                "role": "user",
                "content": (
                    f"以下是已有内容：\n{existing_content}\n\n"
                    f"请续写接下来的内容，保持风格一致，情节自然发展。{direction_hint}\n"
                    f"续写字数约800-1500字。"
                ),
            },
        ]
