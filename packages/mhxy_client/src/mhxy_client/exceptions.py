"""mhxy_client 异常模块。"""


class MhxyClientError(Exception):
    """MHXY Client 基础异常。"""


class WindowNotFoundError(MhxyClientError):
    """未找到指定的梦幻西游窗口异常。"""
