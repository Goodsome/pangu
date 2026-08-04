"""d4_injestion 领域异常定义。"""

from __future__ import annotations


class LeaderboardParseError(Exception):
    """榜单 OCR 结果解析失败异常。"""
