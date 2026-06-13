import logging
import asyncio
from dependency_injector.wiring import Provide, inject

# 导入你的容器和 Worker 类
from codegen.shared.infrastructure.workers.outbox_worker import OutboxWorker

logger = logging.getLogger(__name__)

@inject
async def _run_outbox_worker(
    worker: OutboxWorker = Provide["shared_container.outbox_worker"]
):
    """
    🚀 启动长期运行的发件箱中继进程 (Outbox Worker)
    """
    logger.info("准备启动发件箱 Worker...")
    
    await worker.run_forever()

def run_worker():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_run_outbox_worker())
    except KeyboardInterrupt:
        logger.info("🛑 收到退出信号，停止 Worker 轮询。")