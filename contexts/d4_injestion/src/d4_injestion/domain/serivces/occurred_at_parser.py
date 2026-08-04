"""榜单时间戳解析领域服务。

OCR 会丢失日期与时间之间的空格 (如 ``2026/8/321:02``)，但小时与分钟固定为
两位数字，因此从右向左锚定最后 5 个字符 ``HH:MM`` 作为时间部分，剩余前缀即为
``YYYY/M/D``，据此还原出 ``datetime``。
"""

from __future__ import annotations

from datetime import datetime


class OccurredAtParser:
    """榜单时间戳文本解析器。"""

    def parse(self, raw: str) -> datetime:
        """将 OCR 时间戳文本解析为 datetime。

        Args:
            raw: 形如 ``2026/8/321:02`` 的原始文本 (日期与时间粘连)。
        """
        ...
