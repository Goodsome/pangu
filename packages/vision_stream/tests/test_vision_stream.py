"""vision_stream 单元测试套件。"""

from dataclasses import is_dataclass
import sys

import pytest

from vision_stream import (
    ColorFormat,
    ImageResult,
    IWindowVisionBackend,
    Region,
    UnsupportedPlatformError,
    VisionStreamError,
    Win32DXGIBackend,
    Win32PrintWindowBackend,
    WindowNotFoundError,
)


def test_models_dataclass() -> None:
    """测试 Region 及 ImageResult 数据模型是否为 Dataclasses。"""
    assert is_dataclass(Region)
    assert is_dataclass(ImageResult)

    region = Region(x=10, y=20, width=100, height=200)
    assert region.x == 10
    assert region.y == 20
    assert region.width == 100
    assert region.height == 200

    img = ImageResult(
        data=b"\x00" * 400,
        width=10,
        height=10,
        channels=4,
        color_format=ColorFormat.BGRA,
        timestamp=1700000000.0,
    )
    assert img.width == 10
    assert img.height == 10
    assert img.color_format == ColorFormat.BGRA
    assert img.stride == 0


def test_backends_dataclass_and_interfaces() -> None:
    """测试 Backend 实现类为 Dataclasses 并且符合 Protocol。"""
    assert is_dataclass(Win32PrintWindowBackend)
    assert is_dataclass(Win32DXGIBackend)

    printwindow_backend = Win32PrintWindowBackend(hwnd=1001)
    dxgi_backend = Win32DXGIBackend(hwnd=1001)

    assert printwindow_backend.hwnd == 1001
    assert dxgi_backend.hwnd == 1001

    assert isinstance(printwindow_backend, IWindowVisionBackend)
    assert isinstance(dxgi_backend, IWindowVisionBackend)


@pytest.mark.anyio
async def test_platform_check_on_mac_async() -> None:
    """测试非 Windows (如 Mac) 环境下的异步平台防护逻辑。"""
    if sys.platform != "win32":
        pw_backend = Win32PrintWindowBackend(hwnd=12345)
        assert pw_backend.is_available() is False

        with pytest.raises(UnsupportedPlatformError):
            await pw_backend.capture()

        dxgi_backend = Win32DXGIBackend(hwnd=12345)
        assert dxgi_backend.is_available() is False

        with pytest.raises(UnsupportedPlatformError):
            await dxgi_backend.capture()

        await pw_backend.close()
        await dxgi_backend.close()


def test_exceptions_hierarchy() -> None:
    """测试异常继承层级。"""
    err = WindowNotFoundError("Window not found", code=404)
    assert isinstance(err, VisionStreamError)
    assert str(err) == "[404] Window not found"
