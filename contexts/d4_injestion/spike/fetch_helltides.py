"""Spike: 快速验证 helltides.com 数据抓取与解析。

验证目标:
  1. GET /api/tower/getAll        -> 榜单列表 (JSON 数组, 每行含 id/rank/player/class/tier/run_time_ms)
  2. GET /api/tower/getRun?id=... -> 单条完整 build (equipment/skills/paragon/talismans)

用途: 为 d4_injestion 从「截图 OCR」转向「第三方网站抓取」的方案验证。
不依赖 /tower HTML 页面 (1.7MB Nuxt SSR 载荷无需解析)。

用法::

    uv run python contexts/d4_injestion/spike/fetch_helltides.py
"""

from __future__ import annotations

import json
from pathlib import Path

import httpx

BASE_URL = "https://helltides.com"
SAMPLE_RUN_ID = "3a9be422-1563-57d9-88bf-6c5b7c14ba85"
OUTPUT_DIR = Path("/tmp/helltides_spike")


def fetch_leaderboard(client: httpx.Client) -> list[dict]:
    """抓取榜单列表。"""
    resp = client.get(f"{BASE_URL}/api/tower/getAll")
    resp.raise_for_status()
    return resp.json()


def fetch_run(client: httpx.Client, run_id: str) -> dict:
    """抓取单条 run 详情。"""
    resp = client.get(f"{BASE_URL}/api/tower/getRun", params={"id": run_id})
    resp.raise_for_status()
    return resp.json()


def format_ms(ms: int) -> str:
    """毫秒 -> m:ss.mmm 展示。"""
    minutes, rem = divmod(ms, 60000)
    seconds, millis = divmod(rem, 1000)
    return f"{minutes}:{seconds:02d}.{millis:03d}"


def summarize_leaderboard(rows: list[dict]) -> None:
    """榜单列表摘要。"""
    print("=" * 80)
    print(f"榜单总行数: {len(rows)}")
    print(f"行字段: {sorted(rows[0].keys())}")

    class_counts: dict[str, int] = {}
    for row in rows:
        class_counts[row["class"]] = class_counts.get(row["class"], 0) + 1
    print(f"职业分布: {dict(sorted(class_counts.items()))}")

    platform_counts: dict[str, int] = {}
    for row in rows:
        platform_counts[row["platform"]] = platform_counts.get(row["platform"], 0) + 1
    print(f"平台分布: {platform_counts}")

    print("\nTop 5 行采样 (rank/player/class/tier/run_time):")
    for row in rows[:5]:
        print(
            f"  #{row['rank']:>4} {row['playerName']:<20} {row['class']:<12} "
            f"tier={row['tier']:<3} {format_ms(row['run_time_ms'])} "
            f"id={row['id']}"
        )


def summarize_run(run: dict) -> None:
    """单条 run 详情摘要。"""
    print("\n" + "=" * 80)
    print(
        f"玩家: {run['playerName']} ({run['battle_tag']})  职业: {run['class']}  "
        f"tier={run['tier']}  用时={format_ms(run['run_time_ms'])}  "
        f"创建时间={run['runCreatedAt']}"
    )

    equipment = run.get("equipment") or []
    print(f"\n装备 ({len(equipment)} 件):")
    for eq in equipment:
        aspect = eq.get("aspect_power")
        sockets = eq.get("sockets") or []
        print(
            f"  - [{eq['slot']}] {eq['codename']} ({eq['item_type']}, "
            f"power={eq['item_power']}, 词缀={len(eq.get('statlines') or [])}, "
            f"插槽={len(sockets)}, 威能={aspect['codename'] if aspect else None})"
        )

    skills = run.get("skillsSNO") or []
    print(f"\n技能 ({len(skills)} 个):")
    for sk in skills:
        modifiers = ", ".join(
            f"{'★' if m.get('is_main') else '·'}{m['name']}"
            for m in sk.get("modifiers", [])
        )
        print(f"  - {sk['name']} (sno={sk['sno']}, id={sk['id']}) 分支: {modifiers}")

    paragon = run.get("paragon") or {}
    print(f"\n巅峰: 传奇节点={paragon.get('legendary_nodes')}")
    for board in paragon.get("boards", []):
        glyph = board.get("glyph")
        print(
            f"  - {board['codename']} (sno={board['sno']}, slot={board.get('slot')}"
            f"{' 起始盘' if board.get('is_starting_board') else ''}) "
            f"传奇={board.get('legendary_node')} 雕文={glyph['name'] if glyph else None}"
        )

    talismans = run.get("talismans") or {}
    seal = talismans.get("seal")
    charms = talismans.get("charms") or []
    print(f"\n护身符: 封印={seal['name'] if seal else None} 神符={len(charms)} 颗")
    for charm in charms:
        print(f"  - {charm['name']} ({charm['rarity']}, {charm['codename']})")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=60) as client:
        rows = fetch_leaderboard(client)
        (OUTPUT_DIR / "getAll.json").write_text(json.dumps(rows, ensure_ascii=False))

        run_id = rows[0]["id"] if rows else SAMPLE_RUN_ID
        run = fetch_run(client, run_id)
        (OUTPUT_DIR / "getRun.json").write_text(json.dumps(run, ensure_ascii=False))

    summarize_leaderboard(rows)
    summarize_run(run)
    print(f"\n原始 JSON 已落盘: {OUTPUT_DIR}/getAll.json, {OUTPUT_DIR}/getRun.json")


if __name__ == "__main__":
    main()
