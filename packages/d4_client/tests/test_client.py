"""D4Client 聚合根与门面入口单元测试套件。"""

from unittest.mock import AsyncMock

import pytest

from d4_client import D4Client, MainHUD
from vision_stream import ImageResult as VisionImageResult


def test_d4client_instantiation() -> None:
    """测试 D4Client 手动构建。"""
    mock_window = AsyncMock()
    client = D4Client(hwnd=12345, window=mock_window)

    assert client.hwnd == 12345
    assert client.window == mock_window
    assert isinstance(client.main_hud, MainHUD)


@pytest.mark.anyio
async def test_d4client_async_context_manager() -> None:
    """测试 D4Client 异步上下文管理器生命周期。"""
    mock_window = AsyncMock()
    mock_window.capture.return_value = VisionImageResult(
        data=b"\x00" * 100, width=10, height=10, channels=4, timestamp=0.0
    )

    client = D4Client(hwnd=12345, window=mock_window)

    async with client as c:
        assert c.hwnd == 12345
        _ = await c.capture()

    assert mock_window.close.called
