"""通用任务与交互动作计算辅助模型。"""

from client_core import Point, Region


def calculate_substring_point(
    text: str,
    target_sub: str,
    rect: Region,
    get_next_word: bool = False,
) -> Point | None:
    """在单行 OCR 识别文本框中，基于字符分布横向比例精准计算特定子字符串的像素中心点。

    Args:
        text: OCR 识别出的完整行文本
        target_sub: 要定位的子字符串 (如 "师父", "父", "师")
        rect: 完整行文本的像素矩形 Region

    Returns:
        Point | None: 该子字符串的中心像素坐标 Point；若未找到子串则返回 None
    """
    if not text or not target_sub or target_sub not in text:
        return None

    n = len(text)
    if n == 0:
        return None

    start_idx = text.find(target_sub)
    end_idx = start_idx + len(target_sub)

    # 算得子字符串在整行字符宽度上的相对比例中心 (0.0 ~ 1.0)
    if get_next_word:
        center_ratio = (end_idx + 1 + end_idx + 2) / (2.0 * n)
    else:
        center_ratio = (start_idx + end_idx) / (2.0 * n)

    center_x = int(rect.x + rect.width * center_ratio)
    center_y = int(rect.y + rect.height / 2.0)

    return Point(x=center_x, y=center_y)
