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
    dxgi_backend = Win32DXGIBackend(hwnd=1001, use_screen_dc=True)

    assert printwindow_backend.hwnd == 1001
    assert dxgi_backend.hwnd == 1001
    assert dxgi_backend.use_screen_dc is True

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

        with pytest.raises(UnsupportedPlatformError):
            await pw_backend.begin_frame()

        dxgi_backend = Win32DXGIBackend(hwnd=12345)
        assert dxgi_backend.is_available() is False

        with pytest.raises(UnsupportedPlatformError):
            await dxgi_backend.capture()

        with pytest.raises(UnsupportedPlatformError):
            await dxgi_backend.begin_frame()

        await pw_backend.close()
        await dxgi_backend.close()


@pytest.mark.anyio
async def test_frame_cache_priority_and_cropping() -> None:
    """测试 Backend 的帧缓存优先机制与 ROI 剪裁提取。"""
    pw_backend = Win32PrintWindowBackend(hwnd=100)
    dxgi_backend = Win32DXGIBackend(hwnd=100)

    # 构造一个 10x10 的假全帧图像
    mock_data = b"\x01\x02\x03\x04" * 100
    mock_frame = ImageResult(
        data=mock_data,
        width=10,
        height=10,
        channels=4,
        color_format=ColorFormat.BGRA,
        timestamp=1000.0,
        stride=40,
    )

    for backend in (pw_backend, dxgi_backend):
        # 显式注入缓存帧
        backend._cached_frame = mock_frame

        # 不传 region，直接获取优先缓存的全帧
        res_full = await backend.capture()
        assert res_full == mock_frame

        # 传递 region，从缓存帧中直接裁剪
        roi = Region(x=2, y=2, width=4, height=4)
        res_roi = await backend.capture(region=roi)
        assert res_roi.width == 4
        assert res_roi.height == 4
        assert res_roi.stride == 16
        assert len(res_roi.data) == 4 * 16

        # 清除缓存
        backend.clear_frame_cache()
        assert backend._cached_frame is None

        await backend.close()


def test_exceptions_hierarchy() -> None:
    """测试异常继承层级。"""
    err = WindowNotFoundError("Window not found", code=404)
    assert isinstance(err, VisionStreamError)
    assert str(err) == "[404] Window not found"
