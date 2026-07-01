import os
from openai import OpenAI
from config import API_CONFIG


class NovelGenerator:
    """AI小说生成器，负责调用大语言模型生成小说内容"""

    def __init__(self):
        self.client = OpenAI(
            api_key=API_CONFIG["api_key"],
            base_url=API_CONFIG["base_url"],
        )
        self.model = API_CONFIG["model"]

    def generate(self, messages: list[dict], temperature: float = 0.8, max_tokens: int = 2000) -> str:
        """调用大模型生成文本"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def generate_outline(self, theme: str, genre: str, style: str) -> str:
        """根据主题、类型和风格生成小说大纲"""
        from .prompt_templates import PromptTemplates
        messages = PromptTemplates.build_outline_prompt(theme, genre, style)
        return self.generate(messages)

    def generate_chapter(self, outline: str, chapter_index: int, chapter_title: str, previous_content: str = "") -> str:
        """根据大纲生成具体章节内容"""
        from .prompt_templates import PromptTemplates
        messages = PromptTemplates.build_chapter_prompt(outline, chapter_index, chapter_title, previous_content)
        return self.generate(messages, temperature=0.85, max_tokens=3000)

    def continue_writing(self, existing_content: str, direction: str = "") -> str:
        """续写已有内容"""
        from .prompt_templates import PromptTemplates
        messages = PromptTemplates.build_continue_prompt(existing_content, direction)
        return self.generate(messages, temperature=0.9, max_tokens=2000)
