def count_words(text: str) -> int:
    """统计文本字数（中文字符+英文单词）"""
    count = 0
    in_word = False
    for char in text:
        if "\u4e00" <= char <= "\u9fff":
            count += 1
            in_word = False
        elif char.isalpha():
            if not in_word:
                count += 1
                in_word = True
        else:
            in_word = False
    return count


def truncate_text(text: str, max_length: int = 500) -> str:
    """截断文本，保留前max_length个字符"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."
