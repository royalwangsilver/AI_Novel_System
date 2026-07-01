"""
数据管理模块，负责管理小说创作过程中的状态和历史数据
"""

import os
from typing import Dict, List, Optional


class ContentDataManager:
    """
    内容数据管理器，用于管理小说创作会话状态和历史生成文本
    """

    def __init__(self):
        """
        初始化数据管理器
        
        内部定义：
        - _session_state: 字典，用于暂存小说会话状态（如当前章节、排版设置等）
        - _history_queue: 列表，用于记录历史生成文本队列
        """
        # 小说会话状态字典
        self._session_state: Dict[str, any] = {
            "current_chapter": 1,           # 当前章节号
            "chapter_title": "",            # 当前章节标题
            "layout_settings": {            # 排版设置
                "font_size": 14,
                "line_spacing": 1.5,
                "paragraph_spacing": 2,
            },
            "theme": "",                    # 小说主题
            "genre": "",                    # 小说类型
            "style": "",                    # 写作风格
            "outline": "",                  # 小说大纲
            "title": "",                    # 小说标题
        }
        
        # 历史生成文本队列（每次大模型生成的章节内容追加到队尾）
        self._history_queue: List[Dict[str, str]] = []

    def load_outline(self, file_path: str = "outline.txt") -> Dict[str, str]:
        """
        读取本地初始化大纲文件
        
        Args:
            file_path: 大纲文件路径，默认为 "outline.txt"
        
        Returns:
            包含大纲信息的字典
        
        如果文件存在，读取内容并存入状态字典；
        如果文件不存在，捕获错误并创建默认大纲字典，避免程序崩溃
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # 解析大纲内容并存入状态字典
                outline_data = self._parse_outline(content)
                self._session_state["outline"] = content
                self._session_state["title"] = outline_data.get("title", "未命名小说")
                
                return outline_data
            else:
                # 文件不存在，创建默认大纲字典
                return self._create_default_outline()
                
        except IOError as e:
            # 优雅地捕获IO错误（如权限问题），返回默认大纲
            print(f"读取大纲文件时发生错误: {e}")
            return self._create_default_outline()
        except Exception as e:
            # 捕获其他意外错误，避免程序崩溃
            print(f"处理大纲文件时发生未知错误: {e}")
            return self._create_default_outline()

    def _parse_outline(self, content: str) -> Dict[str, str]:
        """
        解析大纲文本内容
        
        Args:
            content: 大纲文本内容
        
        Returns:
            解析后的大纲字典
        """
        outline_data: Dict[str, str] = {
            "title": "未命名小说",
            "summary": "",
            "characters": [],
            "chapters": [],
            "raw_content": content,
        }
        
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            # 尝试提取标题（通常以 "标题:" 或 "小说标题:" 开头）
            if line.startswith("标题:") or line.startswith("小说标题:"):
                outline_data["title"] = line.split(":")[1].strip()
            # 尝试提取简介
            elif line.startswith("简介:") or line.startswith("故事简介:"):
                outline_data["summary"] = line.split(":")[1].strip()
        
        return outline_data

    def _create_default_outline(self) -> Dict[str, str]:
        """
        创建默认大纲字典
        
        Returns:
            默认大纲字典
        """
        default_outline: Dict[str, str] = {
            "title": "未命名小说",
            "summary": "这是一个待创作的小说，请先生成大纲。",
            "characters": [],
            "chapters": [],
            "raw_content": "",
        }
        
        # 将默认大纲存入状态字典
        self._session_state["outline"] = ""
        self._session_state["title"] = default_outline["title"]
        
        return default_outline

    def add_to_history(self, chapter_index: int, chapter_title: str, content: str) -> None:
        """
        将生成的章节内容追加到历史队列
        
        Args:
            chapter_index: 章节序号
            chapter_title: 章节标题
            content: 章节内容
        """
        history_entry: Dict[str, str] = {
            "chapter_index": str(chapter_index),
            "chapter_title": chapter_title,
            "content": content,
            "timestamp": self._get_timestamp(),
        }
        self._history_queue.append(history_entry)

    def get_session_state(self) -> Dict[str, any]:
        """
        获取当前会话状态
        
        Returns:
            会话状态字典
        """
        return self._session_state.copy()

    def update_session_state(self, key: str, value: any) -> None:
        """
        更新会话状态
        
        Args:
            key: 状态键名
            value: 状态值
        """
        if key in self._session_state:
            self._session_state[key] = value

    def get_history_queue(self) -> List[Dict[str, str]]:
        """
        获取历史生成文本队列
        
        Returns:
            历史文本队列列表
        """
        return self._history_queue.copy()

    def clear_history(self) -> None:
        """
        清空历史生成文本队列
        """
        self._history_queue.clear()

    def _get_timestamp(self) -> str:
        """
        获取当前时间戳
        
        Returns:
            格式化的时间戳字符串
        """
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")