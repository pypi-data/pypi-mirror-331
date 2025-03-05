from pathlib import Path


def srt_to_txt(filepath: Path) -> str:
    """Extract the text strings from a `.srt` file"""
    # SRT file structure: https://docs.fileformat.com/video/srt/
    assert filepath.suffix.casefold() == ".srt", "Expected `.srt` file"
    with open(filepath, "r", encoding="utf-8") as f:
        data = f.read()
    texts: list[str] = data.split(
        "\n\n"
    )  # Since each line is seperated by 1 blank line
    texts = [
        "\n".join(text.split("\n")[2:]) for text in texts
    ]  # Since each block has a numeric counter followed by timestamp
    return "\n".join(texts)
