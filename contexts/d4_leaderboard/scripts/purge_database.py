"""清空 d4_leaderboard 数据库中所有业务表的数据。

用法:
    uv run python scripts/purge_database.py          # 交互确认后清空
    uv run python scripts/purge_database.py --yes    # 跳过确认直接清空

说明:
    - 仅删除数据 (DELETE)，不删除表结构；如需重建表结构请使用 alembic。
    - 按外键依赖倒序逐表清理，避免违反外键约束。
"""

import argparse
import asyncio
import sys

from d4_leaderboard.config import Settings
from foundation.persistence.orm.base import BaseORM
import d4_leaderboard.infrastructure.persistence.models  # noqa: F401  # pyright: ignore[reportUnusedImport]  # 注册 ORM 模型

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine


async def purge(db_url: str) -> None:
    engine = create_async_engine(db_url)
    try:
        async with engine.begin() as conn:
            # sorted_tables 已按外键依赖拓扑排序，倒序删除子表在前
            for table in reversed(BaseORM.metadata.sorted_tables):
                result = await conn.execute(delete(table))
                print(f"已清空表 {table.name}: 删除 {result.rowcount} 行")
    finally:
        await engine.dispose()


class PurgeArgs(argparse.Namespace):
    yes: bool = False


def main() -> None:
    parser = argparse.ArgumentParser(description="清空 d4_leaderboard 数据库内容")
    parser.add_argument(
        "--yes",
        action="store_true",
        help="跳过交互确认，直接执行清空",
    )
    args = parser.parse_args(namespace=PurgeArgs())

    db_url = Settings().db_url  # pyright: ignore[reportCallIssue]
    print(f"目标数据库: {db_url}")

    if not args.yes:
        answer = input("此操作将删除所有表数据且不可恢复，确认继续? [y/N] ")
        if answer.strip().lower() not in ("y", "yes"):
            print("已取消。")
            sys.exit(0)

    asyncio.run(purge(db_url))
    print("数据库已清空。")


if __name__ == "__main__":
    main()
