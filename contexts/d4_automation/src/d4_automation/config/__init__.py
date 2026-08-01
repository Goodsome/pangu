"""d4_automation 天梯榜采集任务配置加载器。

从 capture_task.yaml 加载任务级配置，供行为树节点使用。
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

# 配置文件路径（与本模块同目录）
_CONFIG_PATH = Path(__file__).parent / "capture_task.yaml"


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

    player_class: str
    start_page: int
    end_page: int
    output_dir: Path
    timing: TimingConfig
    retry: RetryConfig


@lru_cache(maxsize=1)
def load_capture_task_config(config_path: Path = _CONFIG_PATH) -> CaptureTaskConfig:
    """加载并缓存采集任务 YAML 配置（进程内单例）。"""
    with config_path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)

    timing_raw = data.get("timing", {})
    retry_raw = data.get("retry", {})

    return CaptureTaskConfig(
        player_class=data["player_class"],
        start_page=data["start_page"],
        end_page=data["end_page"],
        output_dir=Path(data["output_dir"]),
        timing=TimingConfig(
            after_select_class=timing_raw.get("after_select_class", 1.0),
            after_click_row=timing_raw.get("after_click_row", 0.8),
            after_open_config=timing_raw.get("after_open_config", 1.5),
            after_hover_slot=timing_raw.get("after_hover_slot", 0.5),
            after_close_config=timing_raw.get("after_close_config", 0.6),
            after_next_page=timing_raw.get("after_next_page", 1.5),
        ),
        retry=RetryConfig(
            max_attempts=retry_raw.get("max_attempts", 3),
            retry_delay=retry_raw.get("retry_delay", 1.0),
        ),
    )
