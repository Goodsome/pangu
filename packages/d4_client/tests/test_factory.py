"""D4Client 自动查找与 1, 2 / 3, 4 网格几何排序单元测试套件。"""

from unittest.mock import MagicMock, patch

import pytest

from d4_client.factory import (
    WindowRectInfo,
    create_d4_client_by_index,
    create_d4_clients,
    sort_window_rects,
)


def test_sort_window_rects_2x2_grid() -> None:
    """测试 4 窗口 2x2 网格 (1, 2 / 3, 4) 几何位置排序算法。

    模拟屏幕布局:
    (left=0, top=0)     [Win 1]  |  (left=1000, top=0)    [Win 2]
    -------------------------------------------------------------
    (left=0, top=1080)  [Win 3]  |  (left=1000, top=1080) [Win 4]
    """
    win_1 = WindowRectInfo(hwnd=101, left=0, top=0, right=960, bottom=540)
    win_2 = WindowRectInfo(
        hwnd=102, left=1000, top=5, right=1960, bottom=545
    )  # 带微小容差偏离
    win_3 = WindowRectInfo(hwnd=103, left=0, top=1080, right=960, bottom=1620)
    win_4 = WindowRectInfo(hwnd=104, left=1000, top=1082, right=1960, bottom=1622)

    # 以无序乱序数组作为输入
    raw_windows = [win_4, win_1, win_3, win_2]

    # 执行 1, 2 / 3, 4 排序
    sorted_wins = sort_window_rects(raw_windows, row_tolerance=50)

    # 验证排序结果顺序精确等于 [win_1, win_2, win_3, win_4]
    assert [w.hwnd for w in sorted_wins] == [101, 102, 103, 104]


@patch("d4_client.factory.find_d4_window_rects")
def test_create_d4_clients_factory(mock_find: MagicMock) -> None:
    """测试基于模拟 HWND 列表的 create_d4_clients 工厂构建。"""
    # 模拟找到 2 个窗口
    mock_find.return_value = [
        WindowRectInfo(hwnd=1001, left=0, top=0, right=800, bottom=600),
        WindowRectInfo(hwnd=1002, left=800, top=0, right=1600, bottom=600),
    ]

    clients = create_d4_clients()
    assert len(clients) == 2
    assert clients[0].hwnd == 1001
    assert clients[1].hwnd == 1002

    # 测试根据 index 获取单一 Client
    client_0 = create_d4_client_by_index(index=0)
    client_1 = create_d4_client_by_index(index=1)
    assert client_0.hwnd == 1001
    assert client_1.hwnd == 1002

    # 测试超出索引界限抛出 IndexError
    with pytest.raises(IndexError):
        create_d4_client_by_index(index=2)
