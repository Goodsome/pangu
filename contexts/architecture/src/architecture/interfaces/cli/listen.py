import logging
import asyncio
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from codegen.shared.infrastructure.gateways.redis_stream_subscriber import (
    RedisStreamSubscriber,
)

logger = logging.getLogger(__name__)


@inject
async def _run_outbox_worker(
    subscriber: RedisStreamSubscriber = Provide[
        "architecture_container.redis_subscriber"
    ],
):
    """
    🚀 启动长期运行的发件箱中继进程 (Outbox Worker)
    """
    logger.info("准备启动 subscriber ...")
    try:
        await subscriber.start()
        await subscriber.run_forever()
    finally:
        logger.info("正在关闭 subscriber ...")
        await subscriber.stop()


def listen():
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_run_outbox_worker())
    except KeyboardInterrupt:
        logger.info("🛑 收到退出信号，轮询。")
