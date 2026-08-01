import sys
from pathlib import Path
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

from d4_leaderboard.config import Settings


def init_database() -> None:
    """自动创建数据库并运行 Alembic 迁移"""
    settings = Settings() # pyright: ignore[reportCallIssue]
    target_url = make_url(settings.db_url)
    db_name = target_url.database

    if not db_name:
        print("❌ 错误：未指定目标数据库名称！")
        sys.exit(1)

    # 1. 切换连接到 postgres 默认库以检查/创建目标库
    default_url = target_url.set(database="postgres")

    # 注意：PostgreSQL 的 CREATE DATABASE 不能在事务块中运行，需开启 AUTOCOMMIT
    sync_url = default_url.render_as_string(hide_password=False).replace(
        "postgresql+psycopg://", "postgresql+psycopg://"
    )
    engine = create_engine(sync_url, isolation_level="AUTOCOMMIT")

    with engine.connect() as conn:
        res = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
            {"dbname": db_name},
        )
        if not res.scalar():
            print(f"🛠️  数据库 '{db_name}' 不存在，正在自动创建...")
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            print(f"✅ 数据库 '{db_name}' 创建成功！")
        else:
            print(f"ℹ️  数据库 '{db_name}' 已存在。")

    engine.dispose()

    # 2. 运行 Alembic 迁移
    context_dir = Path(__file__).parent.parent / "contexts" / "d4_leaderboard"
    alembic_ini_path = context_dir / "alembic.ini"

    if alembic_ini_path.exists():
        print("🚀 正在运行 Alembic 数据库表结构迁移 (upgrade head)...")
        alembic_cfg = Config(str(alembic_ini_path))
        alembic_cfg.set_main_option("script_location", str(context_dir / "alembic"))
        command.upgrade(alembic_cfg, "head")
        print("✅ 数据库表结构迁移完成！")
    else:
        print(f"⚠️ 未找到 Alembic 配置文件: {alembic_ini_path}")


if __name__ == "__main__":
    init_database()
