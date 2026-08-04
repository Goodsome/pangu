"""d4_automation 天梯榜采集任务配置。

使用 Python dataclass 进行硬编码配置管理。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from d4_types.enums.player_class import PlayerClass


@dataclass(frozen=True)
class TimingConfig:
    """各操作步骤间等待时间配置（秒）。"""

    after_select_class: float = 1.0
    after_click_row: float = 0.8
    after_open_config: float = 1.5
    after_hover_slot: float = 0.5
    after_close_config: float = 0.6
    after_next_page: float = 1.5


@dataclass(frozen=True)
class RetryConfig:
    """操作重试配置。"""

    max_attempts: int = 3
    retry_delay: float = 1.0


@dataclass(frozen=True)
class CaptureTaskConfig:
    """天梯榜采集任务完整配置。"""

    player_class: PlayerClass = PlayerClass.BARBARIAN
    start_page: int = 1
    end_page: int = 1
    output_dir: Path = field(default_factory=lambda: Path("output/screenshots"))
    timing: TimingConfig = field(default_factory=TimingConfig)
    retry: RetryConfig = field(default_factory=RetryConfig)


_DEFAULT_CONFIG = CaptureTaskConfig()


def load_capture_task_config() -> CaptureTaskConfig:
    """获取采集任务硬编码配置。"""
    return _DEFAULT_CONFIG
