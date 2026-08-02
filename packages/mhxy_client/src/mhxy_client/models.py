"""mhxy_client 领域数据模型与梦幻西游标题解析。"""

import re
from client_core import (
    BaseRegion,
    Element,
    ImageFrame,
    MatchResult,
    OcrResult,
    Point,
    Region,
    RelativePoint,
    RelativeRegion,
    SplitMode,
    WindowRectInfo as BaseWindowRectInfo,
)

# 梦幻西游客户端真实窗口标题正则解析: 梦幻西游 ONLINE - (畅玩服[天下无双] - 游易幽寒[39200278])
MHXY_TITLE_PATTERN = re.compile(
    r"梦幻西游\s*ONLINE\s*-\s*\((?P<server>.+?)\s*-\s*(?P<role_name>.+?)\[(?P<role_id>\d+)\]\)",
    re.IGNORECASE,
)


class WindowRectInfo(BaseWindowRectInfo):
    """扩展梦幻西游标题解析特性的 WindowRectInfo。"""

    @property
    def server_name(self) -> str:
        """从窗口标题中提取的服务器/大区名称 (如 '畅玩服[天下无双]')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("server").strip() if m else ""

    @property
    def role_name(self) -> str:
        """从窗口标题中提取的角色名字 (如 '游易幽寒')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_name").strip() if m else ""

    @property
    def role_id(self) -> str:
        """从窗口标题中提取的角色数字 ID (如 '39200278')。"""
        m = MHXY_TITLE_PATTERN.search(self.title)
        return m.group("role_id").strip() if m else ""


__all__ = [
    "BaseRegion",
    "Element",
    "ImageFrame",
    "MHXY_TITLE_PATTERN",
    "MatchResult",
    "OcrResult",
    "Point",
    "Region",
    "RelativePoint",
    "RelativeRegion",
    "SplitMode",
    "WindowRectInfo",
]
