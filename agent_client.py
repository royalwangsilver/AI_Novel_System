"""
Agent 客户端模块，负责调用 DeepSeek API 生成小说内容

安全策略：
- 严禁硬编码 API Key
- api_key 完全由外部传入，与 UI 密码输入框解耦
- 不引入任何持久化保存密钥的机制，Key 随用随走，关闭即销毁
"""

from typing import List, Optional


class NovelAgentClient:
    """
    小说 Agent 客户端，负责与 DeepSeek API 交互生成小说章节内容

    本类不持有、不存储、不持久化任何 API Key，
    所有密钥均由调用方在每次请求时临时传入。
    """

    # 模型名称，DeepSeek 快速响应模型
    MODEL_NAME = "deepseek-chat"

    # DeepSeek API 基础地址（OpenAI 兼容格式）
    BASE_URL = "https://api.deepseek.com"

    def generate_chapter(
        self,
        api_key: str,
        prompt: str,
        system_instruction: str = None,
        chat_history: list = None,
    ) -> str:
        """
        调用 DeepSeek API 生成小说章节内容

        Args:
            api_key: DeepSeek API 密钥，由外部（如 UI 密码框）实时传入，不持久化
            prompt: 用户当前的情节指令 / 生成提示词
            system_instruction: 系统提示词（如小说助手角色设定），可选
            chat_history: 历史对话列表，格式为 [{"role": "user/assistant", "content": "..."}]，可选

        Returns:
            生成的纯文本内容；若出错则返回友好的报错字符串
        """
        if not api_key or not api_key.strip():
            return "[错误] API Key 不能为空，请在界面中输入有效的密钥。"

        if not prompt or not prompt.strip():
            return "[错误] 生成提示词不能为空。"

        try:
            from openai import OpenAI

            # 动态初始化客户端：每次调用时用传入的 api_key 配置，不持久化
            client = OpenAI(
                api_key=api_key,
                base_url=self.BASE_URL,
            )

            # 组装消息列表
            messages = []

            # 系统提示词（放在最前面）
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})

            # 历史对话
            if chat_history:
                messages.extend(chat_history)

            # 当前用户消息
            messages.append({"role": "user", "content": prompt})

            # 发送请求
            response = client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=messages,
                temperature=0.8,
                max_tokens=3000,
            )

            # 提取纯文本内容
            if response.choices and response.choices[0].message.content:
                return response.choices[0].message.content
            else:
                return "[警告] 模型未返回有效内容，请稍后重试。"

        except ConnectionError:
            return "[错误] 网络连接失败，请检查网络设置后重试。"

        except TimeoutError:
            return "[错误] 请求超时，服务器响应时间过长，请稍后重试。"

        except Exception as e:
            error_msg = str(e)
            # 识别常见异常类型，返回友好提示
            if "Authentication" in error_msg or "Unauthorized" in error_msg or "401" in error_msg:
                return "[错误] API Key 无效，请检查密钥是否正确。"
            elif "insufficient" in error_msg.lower() or "balance" in error_msg.lower() or "quota" in error_msg.lower():
                return "[错误] API 调用额度不足，请充值或更换密钥。"
            elif "permission" in error_msg.lower() or "forbidden" in error_msg.lower() or "403" in error_msg:
                return "[错误] 权限不足，该 API Key 可能未启用对应服务。"
            elif "timeout" in error_msg.lower():
                return "[错误] 请求超时，请检查网络连接后重试。"
            elif "Rate limit" in error_msg or "rate_limit" in error_msg or "429" in error_msg:
                return "[错误] 请求过于频繁，请稍后再试。"
            else:
                return f"[错误] 生成内容时发生异常：{error_msg}"
