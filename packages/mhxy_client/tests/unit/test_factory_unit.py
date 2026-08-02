"""mhxy_client 工厂与窗口排序算法单元测试。"""

from mhxy_client import WindowRectInfo, sort_window_rects


def test_window_rect_info_properties() -> None:
    """测试 WindowRectInfo 的长宽推算与标题角色信息解析属性。"""
    rect = WindowRectInfo(
        hwnd=1001,
        left=100,
        top=100,
        right=900,
        bottom=700,
        client_width=800,
        client_height=600,
        title="梦幻西游 ONLINE - (畅玩服[天下无双] - 游易幽寒[39200278])",
    )
    assert rect.window_width == 800
    assert rect.window_height == 600
    assert rect.width == 800
    assert rect.height == 600
    assert rect.server_name == "畅玩服[天下无双]"
    assert rect.role_name == "游易幽寒"
    assert rect.role_id == "39200278"


def test_sort_window_rects_empty() -> None:
    """测试空列表排序。"""
    assert sort_window_rects([]) == []


def test_sort_window_rects_grid_sorting() -> None:
    """测试网格坐标排序 (2x2 网格与偏落窗口排序)。"""
    w1 = WindowRectInfo(hwnd=1, left=0, top=0, right=800, bottom=600)
    w2 = WindowRectInfo(hwnd=2, left=800, top=10, right=1600, bottom=610)
    w3 = WindowRectInfo(hwnd=3, left=0, top=600, right=800, bottom=1200)
    w4 = WindowRectInfo(hwnd=4, left=800, top=590, right=1600, bottom=1190)

    unordered = [w4, w1, w3, w2]
    sorted_res = sort_window_rects(unordered, row_tolerance=50)

    assert [w.hwnd for w in sorted_res] == [1, 2, 3, 4]
