# -*- coding: utf-8 -*-
"""验证梦幻西游窗口组装与 client 实例化 (01_verify_factory.py)。

运行方式：
    uv run python packages/mhxy_client/examples/01_verify_factory.py
"""

import sys
from pathlib import Path

pkg_src = Path(__file__).resolve().parent.parent / "src"
if str(pkg_src) not in sys.path:
    sys.path.insert(0, str(pkg_src))

from mhxy_client import create_mhxy_clients  # noqa: E402


def main() -> None:
    print("=" * 70)
    print("  [MHXY Client] 梦幻西游客户端初始化验证脚本")
    print("=" * 70)

    print("\n[Search] 正在检索系统上的梦幻游戏窗口...")
    clients = create_mhxy_clients()

    print(
        f"[OK] 系统成功检索到 {len(clients)} 个真实梦幻窗口 (按 2D 网格排布完成组装)："
    )

    for idx, client in enumerate(clients, 1):
        print(f"\n  * [Client #{idx}]")
        print(f"     - HWND     : {client.hwnd} ({hex(client.hwnd)})")
        print(f"     - 完整标题 : {client.title}")
        print(f"     - 大区服务器: {client.server_name or '未识别/未知'}")
        print(f"     - 角色名称 : {client.role_name or '未识别/未知'}")
        print(f"     - 角色 ID  : {client.role_id or '未识别/未知'}")
        print(f"     - 客户区尺寸: {client.window.width} x {client.window.height}")

    print("\n" + "=" * 70)
    print("  MhxyClient 实例验证完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
