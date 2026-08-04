"""mhxy_client MainHUD 页面布局配置。"""

from dataclasses import dataclass

from client_core import RelativeRegion


@dataclass(frozen=True)
class MainHudLayoutConfig:
    """梦幻西游常驻主界面 (MainHUD) 页面布局相对坐标配置。

    默认字段为未标定状态 (RelativeRegion(x=0, y=0, width=0, height=0))，
    供 calibrate_main_hud_roi.py 辅助脚本进行交互式框选标定后填入。
    """

    map_name_roi: RelativeRegion = RelativeRegion(
        x=0.0542, y=0.0769, width=0.0603, height=0.0330
    )
    task_list_roi: RelativeRegion = RelativeRegion(
        x=0.7488, y=0.2292, width=0.2414, height=0.4898
    )
    fu_roi: RelativeRegion = RelativeRegion(
        x=0.7562, y=0.3501, width=0.0246, height=0.0330
    )
    dialog_name_roi: RelativeRegion = RelativeRegion(x=0.1736, y=0.4443, width=0.1047, height=0.0455)

MAIN_HUD_LAYOUT_CONFIG = MainHudLayoutConfig()