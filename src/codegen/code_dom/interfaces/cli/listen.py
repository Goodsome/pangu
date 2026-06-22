import logging
import asyncio
from dependency_injector.wiring import Provide
from dependency_injector.wiring import inject
from codegen.shared.infrastructure.gateways.redis_stream_subscriber import (
    RedisStreamSubscriber,
)

logger = logging.getLogger(__name__)


@inject
async def _listen_redis(
    subscriber: RedisStreamSubscriber = Provide[
        "code_dom_container.redis_subscriber"
    ],
):
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
        loop.run_until_complete(_listen_redis())
    except KeyboardInterrupt:
        logger.info("🛑 收到退出信号，轮询。")
