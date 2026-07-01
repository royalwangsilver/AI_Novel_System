"""
Agent 客户端模块，负责调用 Gemini API 生成小说内容

安全策略：
- 严禁硬编码 API Key
- api_key 完全由外部传入，与 UI 密码输入框解耦
- 不引入任何持久化保存密钥的机制，Key 随用随走，关闭即销毁
"""

from typing import List, Optional


class NovelAgentClient:
    """
    小说 Agent 客户端，负责与 Gemini API 交互生成小说章节内容

    本类不持有、不存储、不持久化任何 API Key，
    所有密钥均由调用方在每次请求时临时传入。
    """

    # 模型名称，适合 Agent 快速响应
    MODEL_NAME = "gemini-1.5-flash"

    def generate_chapter(
        self,
        api_key: str,
        prompt: str,
        system_instruction: str = None,
        chat_history: list = None,
    ) -> str:
        """
        调用 Gemini API 生成小说章节内容

        Args:
            api_key: Gemini API 密钥，由外部（如 UI 密码框）实时传入，不持久化
            prompt: 用户当前的情节指令 / 生成提示词
            system_instruction: 系统提示词（如小说助手角色设定），可选
            chat_history: 历史对话列表，格式为 [{"role": "user/model", "parts": [{"text": "..."}]}]，可选

        Returns:
            生成的纯文本内容；若出错则返回友好的报错字符串
        """
        # 参数校验
        if not api_key or not api_key.strip():
            return "[错误] API Key 不能为空，请在界面中输入有效的密钥。"

        if not prompt or not prompt.strip():
            return "[错误] 生成提示词不能为空。"

        try:
            import google.generativeai as genai

            # 动态初始化客户端：每次调用时用传入的 api_key 配置，不持久化
            genai.configure(api_key=api_key)

            # 创建模型实例，附带系统提示词
            model = genai.GenerativeModel(
                model_name=self.MODEL_NAME,
                system_instruction=system_instruction,
            )

            # 组装历史对话（如有）
            history = chat_history if chat_history else []

            # 开启对话会话
            chat = model.start_chat(history=history)

            # 发送当前 prompt 并获取响应
            response = chat.send_message(prompt)

            # 提取纯文本内容
            if response.text:
                return response.text
            else:
                return "[警告] 模型未返回有效内容，请稍后重试。"

        except ConnectionError:
            return "[错误] 网络连接失败，请检查网络设置后重试。"

        except TimeoutError:
            return "[错误] 请求超时，服务器响应时间过长，请稍后重试。"

        except Exception as e:
            error_msg = str(e)
            # 识别常见异常类型，返回友好提示
            if "API_KEY_INVALID" in error_msg or "API key not valid" in error_msg:
                return "[错误] API Key 无效，请检查密钥是否正确。"
            elif "quota" in error_msg.lower() or "RESOURCE_EXHAUSTED" in error_msg:
                return "[错误] API 调用配额已耗尽，请稍后重试或更换密钥。"
            elif "permission" in error_msg.lower() or "PERMISSION_DENIED" in error_msg:
                return "[错误] 权限不足，该 API Key 可能未启用 Gemini 服务。"
            elif "timeout" in error_msg.lower():
                return "[错误] 请求超时，请检查网络连接后重试。"
            else:
                return f"[错误] 生成内容时发生异常：{error_msg}"
