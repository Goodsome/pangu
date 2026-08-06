"""mhxy_client MainHUD 页面布局配置。"""

from dataclasses import dataclass

from client_core import RelativeRegion


@dataclass(frozen=True)
class MainHudLayoutConfig:
    """梦幻西游常驻主界面 (MainHUD) 页面布局相对坐标配置。

    默认字段为未标定状态 (RelativeRegion(x=0, y=0, width=0, height=0))，
    供 calibrate_main_hud_roi.py 辅助脚本进行交互式框选标定后填入。
    """

    # map_name_roi: RelativeRegion = RelativeRegion( x=0.0542, y=0.0769, width=0.0603, height=0.0330 )
    map_name_roi: RelativeRegion = RelativeRegion(x=0.0443, y=0.1146, width=0.0788, height=0.0271)
    task_list_roi: RelativeRegion = RelativeRegion(x=0.7488, y=0.2292, width=0.2414, height=0.4898)
    task_panel_roi: RelativeRegion = RelativeRegion(x=0.4865, y=0.3801, width=0.2672, height=0.3937)
    dialog_roi: RelativeRegion = RelativeRegion(x=0.0764, y=0.4914, width=0.8485, height=0.2496)
    dialog_name_roi: RelativeRegion = RelativeRegion(x=0.1663, y=0.4630, width=0.1145, height=0.0483)
    confirm_give_roi: RelativeRegion = RelativeRegion(x=0.2771, y=0.7080, width=0.1268, height=0.0392)
    inventory_title_roi: RelativeRegion = RelativeRegion(x=0.1564, y=0.1554, width=0.1429, height=0.0543)
    inventory_grid_roi: RelativeRegion = RelativeRegion(x=0.0517, y=0.4962, width=0.3510, height=0.3424)
    feixingfu_map_changan_roi: RelativeRegion = RelativeRegion(x=0.5837, y=0.4314, width=0.1502, height=0.1388)


DB_CHANGAN_MAP: dict[str, RelativeRegion] = {
    "南北杂货店": RelativeRegion(x=0.7389, y=0.5475, width=0.0837, height=0.0241),
    "杂货店老板": RelativeRegion(x=0.4938, y=0.2474, width=0.0653, height=0.1448),
}