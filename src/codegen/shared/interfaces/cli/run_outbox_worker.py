import logging
import asyncio
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from codegen.shared.infrastructure.workers.neo4j_outbox_worker import Neo4jOutboxWorker
from codegen.shared.infrastructure.workers.outbox_worker import SqlalchemyOutboxWorker

logger = logging.getLogger(__name__)


@inject
async def _run_outbox_worker(
    sqlalchemy_worker: SqlalchemyOutboxWorker = Provide["shared_container.outbox_worker"],
    neo4j_worker: Neo4jOutboxWorker = Provide["shared_container.neo4j_outbox_worker"],
):
    """
    🚀 启动长期运行的发件箱中继进程 (Outbox Worker)
    """
    logger.info("准备启动发件箱 Worker...")
    try:
        async with asyncio.TaskGroup() as tg:
            tg.create_task(sqlalchemy_worker.run_forever())
            tg.create_task(neo4j_worker.run_forever())
    except asyncio.CancelledError:
        logger.info("🛑 收到退出信号，停止 Worker 轮询。")


def run_worker():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_run_outbox_worker())
    except KeyboardInterrupt:
        logger.info("🛑 收到退出信号，停止 Worker 轮询。")
