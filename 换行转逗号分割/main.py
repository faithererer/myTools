import pyperclip
import sys


def process_clipboard():
    try:
        # 获取剪贴板内容
        clipboard_content = pyperclip.paste()
        print("原始剪贴板内容:")
        print(clipboard_content)

        # 分割行，过滤空行，并处理
        lines = [line.strip() for line in clipboard_content.splitlines() if line.strip()]
        processed_content = ",".join(lines) + ("," if lines else "")

        print("\n处理后的内容:")
        print(processed_content)

        # 将处理后的内容复制回剪贴板
        pyperclip.copy(processed_content)
        print("\n已复制处理后的内容到剪贴板")

    except Exception as e:
        print(f"发生错误: {e}", file=sys.stderr)


if __name__ == "__main__":
    process_clipboard()
