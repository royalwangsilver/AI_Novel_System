import gradio as gr
from core.novel_generator import NovelGenerator
from core.story_manager import StoryManager
from utils.file_utils import export_novel


def create_interface():
    """创建Gradio界面"""
    generator = NovelGenerator()
    manager = StoryManager()

    # --- 生成大纲 ---
    def on_generate_outline(theme, genre, style):
        outline = generator.generate_outline(theme, genre, style)
        return outline

    # --- 生成章节 ---
    def on_generate_chapter(outline, chapter_index, chapter_title, previous_content):
        content = generator.generate_chapter(outline, chapter_index, chapter_title, previous_content)
        return content

    # --- 续写 ---
    def on_continue_writing(existing_content, direction):
        result = generator.continue_writing(existing_content, direction)
        return result

    # --- 保存故事 ---
    def on_save_story(title, theme, genre, style, outline, chapters_text):
        import json
        story = manager.create_story(title, theme, genre, style, outline)
        if chapters_text:
            try:
                chapters = json.loads(chapters_text)
                for idx, ch in chapters.items():
                    story = manager.add_chapter(story, int(idx), ch["title"], ch["content"])
            except json.JSONDecodeError:
                pass
        return f"故事 '{title}' 已保存！"

    # --- 导出小说 ---
    def on_export_novel(title, outline, chapters_text):
        story = manager.load_story(title)
        if not story:
            story = {"title": title, "outline": outline, "chapters": {}}
            import json
            if chapters_text:
                try:
                    story["chapters"] = json.loads(chapters_text)
                except json.JSONDecodeError:
                    pass
        filepath = export_novel(story)
        return filepath

    with gr.Blocks(title="AI 小说创作系统") as app:
        gr.Markdown("# AI 小说创作系统")
        gr.Markdown("基于大语言模型的智能小说创作助手")

        with gr.Tab("生成大纲"):
            with gr.Row():
                theme_input = gr.Textbox(label="小说主题", placeholder="例如：穿越、修仙、都市...")
                genre_input = gr.Textbox(label="小说类型", placeholder="例如：玄幻、言情、悬疑...")
                style_input = gr.Textbox(label="写作风格", placeholder="例如：轻松幽默、沉稳大气...")
            outline_btn = gr.Button("生成大纲", variant="primary")
            outline_output = gr.Textbox(label="生成的大纲", lines=20)
            outline_btn.click(on_generate_outline, [theme_input, genre_input, style_input], outline_output)

        with gr.Tab("生成章节"):
            outline_input = gr.Textbox(label="小说大纲", lines=10, placeholder="粘贴大纲内容...")
            with gr.Row():
                ch_index = gr.Number(label="章节序号", value=1)
                ch_title = gr.Textbox(label="章节标题")
            prev_content = gr.Textbox(label="前文内容（可选）", lines=5)
            chapter_btn = gr.Button("生成章节", variant="primary")
            chapter_output = gr.Textbox(label="生成的章节内容", lines=25)
            chapter_btn.click(on_generate_chapter, [outline_input, ch_index, ch_title, prev_content], chapter_output)

        with gr.Tab("续写"):
            existing_content = gr.Textbox(label="已有内容", lines=15, placeholder="粘贴已有小说内容...")
            direction_input = gr.Textbox(label="续写方向（可选）", placeholder="描述希望故事发展的方向...")
            continue_btn = gr.Button("续写", variant="primary")
            continue_output = gr.Textbox(label="续写结果", lines=20)
            continue_btn.click(on_continue_writing, [existing_content, direction_input], continue_output)

        with gr.Tab("保存与导出"):
            with gr.Row():
                save_title = gr.Textbox(label="小说标题")
                save_theme = gr.Textbox(label="主题")
                save_genre = gr.Textbox(label="类型")
                save_style = gr.Textbox(label="风格")
            save_outline = gr.Textbox(label="大纲", lines=5)
            save_chapters = gr.Textbox(label="章节JSON（可选）", lines=5, placeholder='{"1": {"title": "...", "content": "..."}}')
            with gr.Row():
                save_btn = gr.Button("保存故事", variant="primary")
                export_btn = gr.Button("导出为TXT")
            save_output = gr.Textbox(label="状态")
            export_output = gr.Textbox(label="导出路径")
            save_btn.click(on_save_story, [save_title, save_theme, save_genre, save_style, save_outline, save_chapters], save_output)
            export_btn.click(on_export_novel, [save_title, save_outline, save_chapters], export_output)

    return app
