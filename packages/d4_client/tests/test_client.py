"""D4Client 聚合根与门面入口单元测试套件。"""

from unittest.mock import AsyncMock

import pytest

from d4_client import D4Client, MainHUD
from vision_stream import ImageResult as VisionImageResult


def test_d4client_create_factory() -> None:
    """测试 D4Client 工厂构建与底层组件自动组装。"""
    client = D4Client.create(hwnd=12345)

    assert client.hwnd == 12345
    assert client.window is not None
    assert isinstance(client.main_hud, MainHUD)


@pytest.mark.anyio
async def test_d4client_async_context_manager() -> None:
    """测试 D4Client 异步上下文管理器生命周期。"""
    client = D4Client.create(hwnd=12345)
    # 使用 AsyncMock 模拟视听层
    client.window.vision_backend = AsyncMock()
    client.window.vision_backend.capture.return_value = VisionImageResult(
        data=b"\x00" * 100, width=10, height=10, channels=4, timestamp=0.0
    )

    async with client as c:
        assert c.hwnd == 12345
        img = await c.capture()
        assert img.width == 10

    assert client.window.vision_backend.close.called
