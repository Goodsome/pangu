"""暗黑破坏神 IV (D4Client) 窗口实例化手动执行验证脚本。

本脚本用于手动执行并演示 D4Client 在不同运行环境/窗口状态下的实例化过程：
1. 未启动游戏：检索窗口，展示未找到窗口时的返回结果及索引获取捕获日志。
2. 启动游戏是窗口全屏：展示主显示器分辨率、窗口尺寸、全屏判定日志及生成的 D4Client 对象。
3. 启动游戏为窗口化：展示窗口物理坐标、客户区尺寸、窗口化判定日志及生成的 D4Client 对象。

日志系统基于 foundation.logging_setup 基础设施配置，输出保存到 logs/client_instantiation.log 并在控制台打印。

使用方法:
    # 1. 默认检索 "暗黑破坏神IV" 游戏窗口:
    uv run python packages/d4_client/examples/01_verify_client_instantiation.py

    # 2. 手动指定其他窗口 (如 "记事本") 进行演示验证:
    uv run python packages/d4_client/examples/01_verify_client_instantiation.py --title "记事本"
"""

import argparse
import logging
from pathlib import Path
import sys
from typing import NamedTuple

from d4_client.factory import (
    WindowRectInfo,
    create_d4_client_by_index,
    create_d4_clients,
    find_d4_window_rects,
)
from foundation.logging_setup import configure_logging


class DisplayResolution(NamedTuple):
    width: int
    height: int


def get_primary_display_resolution() -> DisplayResolution | None:
    """获取 Windows 主显示器真实物理分辨率 (开启 DPI Awareness)，如果非 Win 系统或获取失败则返回 None。"""
    if sys.platform != "win32":
        return None
    try:
        import ctypes

        user32 = ctypes.windll.user32
        try:
            user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
        except Exception:
            try:
                user32.SetProcessDPIAware()
            except Exception:
                pass

        return DisplayResolution(
            width=int(user32.GetSystemMetrics(0)),
            height=int(user32.GetSystemMetrics(1)),
        )
    except Exception:
        return None


def is_fullscreen_window(
    rect: WindowRectInfo, screen_res: DisplayResolution | None
) -> bool:
    """根据窗口坐标与客户区尺寸判断是否为全屏/无边框全屏。"""
    if screen_res is not None:
        if (
            rect.width >= screen_res.width
            and rect.height >= screen_res.height
            and rect.left <= 0
            and rect.top <= 0
        ):
            return True
    if (
        rect.left == 0
        and rect.top == 0
        and rect.window_width == rect.width
        and rect.window_height == rect.height
    ):
        return True
    return False


def run_verification(title_keyword: str, logger: logging.Logger) -> None:
    logger.info("=" * 75)
    logger.info("开始执行 D4Client 窗口实例化逻辑验证")
    logger.info(f"检索窗口标题关键字: '{title_keyword}'")
    logger.info("=" * 75)

    # 1. 查找窗口 Rect 信息
    rects = find_d4_window_rects(title_keyword=title_keyword)
    logger.info(f"[检索结果] 匹配标题 '{title_keyword}' 的窗口数量: {len(rects)}")

    # 情况 1: 未启动游戏 (未找到匹配窗口)
    if not rects:
        logger.info(
            "\n---------------------------------------------------------------------------"
        )
        logger.info("[情况 1: 未启动游戏 / 未找到窗口]")
        logger.info(
            "---------------------------------------------------------------------------"
        )
        logger.info(f"1. find_d4_window_rects('{title_keyword}') 返回: [] (空列表)")

        clients = create_d4_clients(title_keyword=title_keyword)
        logger.info(
            f"2. create_d4_clients('{title_keyword}') 返回: [] (空 Client 列表)"
        )

        logger.info("3. 尝试调用 create_d4_client_by_index(0):")
        try:
            create_d4_client_by_index(index=0, title_keyword=title_keyword)
        except IndexError as e:
            logger.info(f"   -> 捕获异常 IndexError: {e}")

        logger.info("\n[提示] 当前未检索到目标游戏窗口。")
        logger.info("       若要在没有运行游戏时测试窗口全屏或窗口化实例化流程，")
        logger.info(
            "       可以使用 --title 参数指定其他已有窗口 (如 Notepad 记事本、浏览器等)。"
        )
        logger.info(
            '       示例: uv run python packages/d4_client/examples/01_verify_client_instantiation.py --title "记事本"'
        )

    # 情况 2 & 3: 启动游戏 (找到匹配窗口，进行全屏/窗口化识别与 Client 实例化演示)
    else:
        screen_res = get_primary_display_resolution()
        screen_str = f"{screen_res.width}x{screen_res.height}" if screen_res else "未知"
        logger.info(f"[环境信息] 当前 Windows 主显示器物理分辨率: {screen_str}")

        # 调用批量实例化工厂
        clients = create_d4_clients(title_keyword=title_keyword)
        logger.info(f"成功构建 {len(clients)} 个 D4Client 实例。\n")

        for i, rect in enumerate(rects):
            client = clients[i]
            is_fullscreen = is_fullscreen_window(rect, screen_res)

            if is_fullscreen:
                mode_desc = "[情况 2: 启动游戏为窗口全屏 / 无边框全屏]"
            else:
                mode_desc = "[情况 3: 启动游戏为窗口化]"

            logger.info(f"--- 窗口 #{i + 1} 识别与实例化结果 ---")
            logger.info(f" 运行模式判定  : {mode_desc}")
            logger.info(f" 窗口句柄 (HWND): 0x{rect.hwnd:X} ({rect.hwnd})")
            logger.info(
                f" 窗口外框 Rect : (Left={rect.left}, Top={rect.top}, Right={rect.right}, Bottom={rect.bottom})"
            )
            logger.info(f" 外框总尺寸    : {rect.window_width} x {rect.window_height}")
            logger.info(f" 客户区物理尺寸: {rect.width} x {rect.height}")
            logger.info(f" D4Client 实例 : {client}")
            logger.info(
                f" Window 规格 : HWND=0x{client.hwnd:X}, Width={client.window.width}, Height={client.window.height}"
            )

            # 演示按索引创建单个 Client
            single_client = create_d4_client_by_index(i, title_keyword=title_keyword)
            logger.info(f" 按索引(Index={i})独立创建结果: {single_client}\n")

    logger.info("=" * 75)
    logger.info("验证脚本执行完成。完整日志已保存至 logs/client_instantiation.log")
    logger.info("=" * 75)


def main() -> None:
    parser = argparse.ArgumentParser(description="D4Client 窗口实例化手动执行验证脚本")
    parser.add_argument(
        "--title",
        type=str,
        default="暗黑破坏神IV",
        help="检索的窗口标题关键词 (默认: '暗黑破坏神IV')",
    )
    args = parser.parse_args()

    # 使用 foundation 统一配置日志系统
    configure_logging(
        app_name="client_instantiation",
        log_dir=Path.cwd() / "logs",
        console_output=True,
    )
    logger = logging.getLogger("d4_client_verify")

    run_verification(title_keyword=args.title, logger=logger)


if __name__ == "__main__":
    main()
