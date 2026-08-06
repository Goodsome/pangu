import asyncio
import logging
from pathlib import Path
from foundation import configure_logging 
from mhxy_client import create_mhxy_client_by_index
from mhxy_client.models.npcs.fu_zhuang_dian_lao_ban import FuZhuangDianLaoBan
from mhxy_client.screens.dialogs.zhen_yuan_da_xian import ZhenYuanDaXianDialog
from mhxy_client.screens.panels.give_panel import GivePanel
from mhxy_client.screens.panels.shop_panel import ShopPanel
from mhxy_client.screens.scenes.zhang_ji_bu_zhuang import ZhangJiBuZhuangScene

log_dir = Path(__file__).resolve().parent.parent.parent.parent / "logs"
configure_logging(app_name="mhxy_client", log_dir=log_dir, log_level=logging.INFO)
logger = logging.getLogger(__name__)


async def async_main() -> None:
    client = create_mhxy_client_by_index(0, init_cv_engines=True)
    logger.info("=" * 70)
    logger.info(f"  * 目标窗口 HWND : {client.hwnd} ({hex(client.hwnd)})")
    logger.info(f"  * 目标窗口标题 : {client.title}")
    logger.info(f"  * 窗口分辨率   : {client.window.width} x {client.window.height}")
    logger.info("=" * 70)
    async with client:
        client.activate()
        hud = client.main_hud
        # check_result = await hud.check_dialog_visible("1")
        # check_result = await hud.dialogs.zhen_yuan_da_xian.claim_task()
        # check_result = await hud.lead_to_npc_house(target=FuZhuangDianLaoBan())
        # check_result = await hud.inventory.use_fei_xing_fu(target=FeiXingFuMap.CHANG_AN)
        # check_result = await GivePanel(hud.window).confirm_give()
        # check_result = await hud.panels.shop_panel.choose_item(0, 3)
        check_result = await hud.panels.given_panel.check_visible()
        
        logger.info(f"{check_result=}")


    logger.info("=" * 70)


def main() -> None:
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
