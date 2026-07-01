"""
AI 小说创作系统 - 主入口文件

整合 ContentDataManager 与 NovelAgentClient，
通过 Gradio 搭建现代化 Web 可视化交互界面。
"""

import os
import gradio as gr
from data_manager import ContentDataManager
from agent_client import NovelAgentClient
from utils.file_utils import export_novel


class NovelSystemGUI:
    """
    小说创作系统 GUI 类，封装界面初始化与交互逻辑
    """

    def __init__(self):
        # 实例化数据管理器和 Agent 客户端
        self.data_manager = ContentDataManager()
        self.agent_client = NovelAgentClient()
        # 界面内维护的对话历史（Gemini 格式）
        self._chat_history: list = []
        # 展示区累计文本
        self._display_text: str = ""

    # ================================================================
    # 交互回调
    # ================================================================

    def _on_load_outline(self):
        """点击'加载本地大纲'：读取 outline.txt，刷新标题与简介"""
        outline_data = self.data_manager.load_outline("outline.txt")
        state = self.data_manager.get_session_state()
        title = state.get("title") or outline_data.get("title", "未命名小说")
        summary = outline_data.get("summary", "暂无简介")
        raw = outline_data.get("raw_content", "")
        status = "[系统] 大纲加载成功！" if raw else "[系统] 未找到大纲文件，已使用默认配置。"
        return title, summary, raw, status

    def _on_generate(self, api_key, user_instruction, chapter_num, style, word_count, outline_text):
        """点击'开始创作/续写章节'：调用 Agent 生成内容"""
        # 空值校验
        if not api_key or not api_key.strip():
            return self._display_text, "[系统] 请先在左侧输入 API Key！"
        if not user_instruction or not user_instruction.strip():
            return self._display_text, "[系统] 请输入创作指令！"

        # 组装系统提示词
        system_instruction = (
            f"你是一位专业的小说创作助手。当前写作风格：{style or '不限'}，"
            f"目标字数：{word_count or '1500-2500'}字。"
            f"请根据用户的指令和以下大纲信息进行创作：\n{outline_text or '暂无大纲'}"
        )

        # 组装用户 prompt
        prompt = f"[第{chapter_num}章创作指令] {user_instruction}"

        # 调用 Agent
        result = self.agent_client.generate_chapter(
            api_key=api_key,
            prompt=prompt,
            system_instruction=system_instruction,
            chat_history=self._chat_history,
        )

        # 判断是否为错误信息
        if result.startswith("[错误]") or result.startswith("[警告]"):
            return self._display_text, f"[系统] {result}"

        # 成功：追加到历史队列和展示区
        self.data_manager.add_to_history(
            chapter_index=int(chapter_num),
            chapter_title=f"第{chapter_num}章",
            content=result,
        )

        # 更新对话历史（Gemini 格式）
        self._chat_history.append({"role": "user", "parts": [{"text": prompt}]})
        self._chat_history.append({"role": "model", "parts": [{"text": result}]})

        # 更新展示区
        chapter_header = f"--- 第{chapter_num}章 ---\n"
        self._display_text += f"\n{chapter_header}{result}\n"

        # 更新会话状态中的章节号
        self.data_manager.update_session_state("current_chapter", int(chapter_num) + 1)

        return self._display_text, f"[系统] 第{chapter_num}章生成完毕！字数：{len(result)}"

    def _on_save_chapter(self):
        """点击'保存/导出当前章节'"""
        history = self.data_manager.get_history_queue()
        if not history:
            return "[系统] 当前没有可导出的章节内容。"

        state = self.data_manager.get_session_state()
        title = state.get("title", "未命名小说")
        outline = state.get("outline", "")

        # 组装 story 字典
        chapters = {}
        for entry in history:
            idx = entry["chapter_index"]
            chapters[idx] = {
                "title": entry["chapter_title"],
                "content": entry["content"],
            }

        story = {
            "title": title,
            "outline": outline,
            "chapters": chapters,
        }

        filepath = export_novel(story)
        return f"[系统] 章节已成功保存至 output 文件夹！路径：{filepath}"

    def _on_clear_history(self):
        """点击'清空历史'"""
        self.data_manager.clear_history()
        self._chat_history.clear()
        self._display_text = ""
        return "", "[系统] 历史记录已清空。"

    # ================================================================
    # 界面构建
    # ================================================================

    def build_interface(self) -> gr.Blocks:
        """构建 Gradio 界面"""

        # 自定义 CSS：现代网页风格
        custom_css = """
        .main-title {
            text-align: center;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.2em;
            color: #2c3e50;
        }
        .sub-title {
            text-align: center;
            font-size: 1rem;
            color: #7f8c8d;
            margin-bottom: 1em;
        }
        .status-bar {
            background: #f0f4f8;
            border-radius: 8px;
            padding: 10px 14px;
            font-size: 0.9rem;
            color: #34495e;
            min-height: 40px;
        }
        .panel-header {
            font-size: 1.1rem;
            font-weight: 600;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 6px;
            margin-bottom: 10px;
        }
        """

        with gr.Blocks(
            theme=gr.themes.Soft(),
            css=custom_css,
            title="AI 小说创作系统",
        ) as app:

            # ---- 标题区 ----
            gr.HTML('<div class="main-title">AI 小说创作系统</div>')
            gr.HTML('<div class="sub-title">基于 Gemini 的智能小说创作助手 | 创作从未如此简单</div>')

            # ---- 主体两栏 ----
            with gr.Row(equal_height=True):

                # ======== 左侧控制面板 ========
                with gr.Column(scale=1, min_width=320):

                    gr.HTML('<div class="panel-header">控制面板</div>')

                    # API Key 输入
                    api_key_input = gr.Textbox(
                        label="API Key",
                        type="password",
                        placeholder="请输入 Gemini API Key...",
                        lines=1,
                    )

                    # 加载大纲
                    with gr.Row():
                        load_outline_btn = gr.Button("加载本地大纲", variant="secondary")
                    outline_status = gr.Textbox(label="大纲状态", interactive=False, lines=1)

                    # 大纲内容展示
                    outline_display = gr.Textbox(
                        label="大纲内容",
                        lines=6,
                        interactive=False,
                        placeholder="加载大纲后在此显示...",
                    )

                    # 小说信息展示
                    with gr.Row():
                        title_display = gr.Textbox(label="小说标题", interactive=False)
                        summary_display = gr.Textbox(label="故事简介", interactive=False)

                    gr.HTML('<div class="panel-header">创作参数</div>')

                    # 创作参数
                    chapter_num = gr.Number(label="当前章节号", value=1, precision=0)
                    style_input = gr.Textbox(
                        label="写作风格",
                        placeholder="例如：轻松幽默、沉稳大气...",
                        value="",
                    )
                    word_count_input = gr.Textbox(
                        label="目标字数",
                        placeholder="例如：2000",
                        value="2000",
                    )

                # ======== 右侧创作核心区 ========
                with gr.Column(scale=2, min_width=500):

                    gr.HTML('<div class="panel-header">创作区</div>')

                    # 文本主展示区
                    novel_display = gr.Textbox(
                        label="小说正文",
                        lines=22,
                        interactive=False,
                        placeholder="AI 生成的小说内容将在此展示...",
                       
                    )

                    # 用户交互输入
                    with gr.Row():
                        user_input = gr.Textbox(
                            label="创作指令",
                            placeholder="输入创作指令，如：续写主角与反派对决的场景...",
                            lines=3,
                            scale=5,
                        )

                    with gr.Row():
                        generate_btn = gr.Button("开始创作 / 续写章节", variant="primary", size="lg")
                        save_btn = gr.Button("保存 / 导出当前章节", variant="secondary")
                        clear_btn = gr.Button("清空历史", variant="stop")

                    # 系统状态栏
                    status_bar = gr.Textbox(
                        label="系统状态",
                        interactive=False,
                        elem_classes=["status-bar"],
                        lines=1,
                    )

            # ================================================================
            # 事件绑定
            # ================================================================

            # 加载大纲
            load_outline_btn.click(
                fn=self._on_load_outline,
                inputs=[],
                outputs=[title_display, summary_display, outline_display, outline_status],
            )

            # 开始创作
            generate_btn.click(
                fn=self._on_generate,
                inputs=[
                    api_key_input,
                    user_input,
                    chapter_num,
                    style_input,
                    word_count_input,
                    outline_display,
                ],
                outputs=[novel_display, status_bar],
            )

            # 保存/导出
            save_btn.click(
                fn=self._on_save_chapter,
                inputs=[],
                outputs=[status_bar],
            )

            # 清空历史
            clear_btn.click(
                fn=self._on_clear_history,
                inputs=[],
                outputs=[novel_display, status_bar],
            )

        return app

    def launch(self, server_name: str = "0.0.0.0", server_port: int = 7860):
        """启动应用"""
        app = self.build_interface()
        app.launch(server_name=server_name, server_port=server_port)


def main():
    gui = NovelSystemGUI()
    gui.launch()


if __name__ == "__main__":
    main()
