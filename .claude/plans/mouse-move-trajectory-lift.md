# Plan: 把鼠标轨迹所有权上提到 BaseScreen（消除钟形分段）

## 目标
解决钟形曲线被分段切碎的问题：当前 `BaseScreen.mouse_move` 每个校准跳调一次 `window.smooth_mouse_move`，而每次调用都是从当前点出发的**完整钟形**（0→峰值→0），于是宏观轨迹变成 N 段"停-走-停-走"。把钟形插值上提到校准层，让它拥有**一整条轨迹**，直接调用原生 `window.mouse_move` 分步执行。顺带去掉无条件的 `ensure_cursor_in_window` 重置到中心。

## 决定设计的关键约束
CV 偏移测量（`_get_game_mouse`）需要游戏光标相对系统光标**静止**——游戏光标移动中滞后于系统光标（现有 `sleep(0.1)` 沉淀、`measure_cursor_offset.py` 的 0.5s 沉淀都印证了这点）。所以 CV 不能在钟形峰值处做，只能在**静止点**做。这意味着轨迹本质上是**钟形段 + 静止沉淀平台**串联，无法做到"一条不间断钟形内嵌 CV"。

因此上提的真正价值在于：校准层拥有这些段（代码清晰、修复 message 后端的 from-origin bug、可按段调参），并把分段降到最少——**一条主钟形 + 末端小修正钟形**（Woodworth 双成分模型），而不是 N 段等价阻尼钟形。结论：先大后小阻尼调度（0.8/0.6/0.4）**回退**为每迭代全量钟形，因为迭代式 CV 复测已使阻尼不再必要、而阻尼正是 N 钟形的根源。

## 改动文件

### 1. `packages/client_core/src/client_core/window.py`

**新增**私有共享钟形插值器（客户区坐标、后端无关）：
```python
async def _bell_move_steps(self, start: Point, target: Point,
                           steps: int, duration_sec: float) -> None:
    """从 start 到 target(客户区) 按 ease-in-out 钟形分步移动，每步调原生 mouse_move。"""
    if steps <= 1:
        await self.mouse_move(target)
        return
    interval = duration_sec / steps
    for i in range(1, steps + 1):
        r = i / steps
        eased = 3 * r * r - 2 * r * r * r          # smoothstep 钟形
        cur = Point(x=int(start.x + (target.x - start.x) * eased),
                    y=int(start.y + (target.y - start.y) * eased))
        await self.mouse_move(cur)                  # mouse_move 处理 client→screen
        jitter = interval * random.uniform(-0.15, 0.15)
        await asyncio.sleep(max(0.0, interval + jitter))
```
- 在**客户区坐标**从真实 `start` 插值（修复 message 后端 `abs_point.x * eased` 从原点插值的 bug）。
- 每步 `self.mouse_move(cur)`：hardware 走 client→screen，message 走 client，统一。

**重构** `smooth_mouse_move(point, steps=30, duration_sec=0.8)`（公开签名不变，脚本/测试依赖）：
- `abs_point = resolve_point`；`start = get_sys_cursor_client_pos() or Point(0,0)`。
- `await self._bell_move_steps(start, abs_point, steps, duration_sec)`。
- 闭环微调改写为**客户区坐标**：循环 3 次，`cur = get_sys_cursor_client_pos()`，`|abs_point - cur|<=1` 则 break，否则 `mouse_move(cur + err)`、sleep 0.03。替换原 screen 坐标闭环（其在 message 分支把 screen 坐标当 client 传入的 bug）。
- 删除原 per-branch screen 坐标插值（已并入 `_bell_move_steps`）。

### 2. `packages/mhxy_client/src/mhxy_client/screens/base.py`

**删除** `_APPROACH_RATIOS` 与 `approach_ratio` 阻尼机制。

**重写** `_get_cursor_region`——去掉无条件 recenter：
```python
async def _get_cursor_region(self) -> Region:
    sys_client_pos = self.window.get_sys_cursor_client_pos()
    win_w, win_h = self.window.width, self.window.height
    if (sys_client_pos is None
            or not (0 <= sys_client_pos.x <= win_w and 0 <= sys_client_pos.y <= win_h)):
        sys_client_pos = await self.window.ensure_cursor_in_window()  # 仅出窗时兜底
    radius = 50
    ...  # ROI 构建逻辑不变
```

**新增**测量助手，替换 `_calibrate_and_realign_mouse`：
```python
_TOLERANCE_PX = 10.0
_SETTLE_SEC = 0.1

async def _measure_game_cursor(self) -> tuple[Point, Point | None, bool]:
    """沉淀后测系统光标与游戏鼠标位置。返回 (sys_client_pos, game|None, is_pointer)。"""
    sys_pos = self.window.get_sys_cursor_client_pos()
    if sys_pos is None or <出窗>:
        sys_pos = await self.window.ensure_cursor_in_window()
    await asyncio.sleep(_SETTLE_SEC)       # 让游戏光标追上系统光标
    game, is_pointer = await self._get_game_mouse()
    return sys_pos, game, is_pointer
```

**重写** `mouse_move`（保留 `target_point` 形参名与 `-> bool`，`main_hud.py` 用关键字调用）：
```python
async def mouse_move(self, target_point: Point | RelativePoint,
                     max_retries: int = 5) -> bool:
    abs_target = self.window.resolve_point(target_point)
    assert abs_target is not None
    for _ in range(max_retries):
        sys_pos, game, is_pointer = await self._measure_game_cursor()
        if game is None:
            raise RuntimeError("未匹配到游戏鼠标模板 cursor.png")
        if is_pointer:
            return True
        if math.hypot(game.x - abs_target.x, game.y - abs_target.y) <= _TOLERANCE_PX:
            return True
        # offset 校正: aim = target - (game - sys)
        aim = Point(x=abs_target.x - (game.x - sys_pos.x),
                    y=abs_target.y - (game.y - sys_pos.y))
        # 单条钟形到 aim（首迭代=主弹道，后续=小修正），按距离缩放步数/时长
        dist = math.hypot(aim.x - sys_pos.x, aim.y - sys_pos.y)
        steps = max(8, min(30, int(dist / 20)))
        duration = max(0.15, min(0.8, dist / 1000))
        await self.window._bell_move_steps(sys_pos, aim, steps, duration)
        # 下次迭代开头的 _measure_game_cursor 的 sleep 负责 CV 前沉淀
    logger.warning("达到最大校准重试次数")
    return False
```
- `mouse_click` 不变（仍调 `self.mouse_move`）。

### 3. 测试（high-effort 补齐）
- `client_core/tests/test_window_core.py`：加 `test_smooth_mouse_move_interpolation`——mock input backend，调 `smooth_mouse_move`，断言 `mouse_move` 被调 `steps` 次、位置从 start 单调 ease 到 target、末点==target。
- 加 `test_bell_move_steps_easing`——直接测 `_bell_move_steps` 产出 smoothstep 曲线（中点 ≈ 半距、对称）。
- `mhxy_client/tests/unit/`：加 `test_base_screen_mouse_move_calibration.py`——构造具体 BaseScreen（子类或 MainHUD）+ `MagicMock(spec=Window)`，mock `_get_game_mouse` 返回受控偏移，断言 `_bell_move_steps` 用校正后的 aim 调用、容差内返回 True / 多迭代收敛。

### 4. 校验
- `/lint-fix`（ruff + basedpyright）作用于两个改动文件 + 新测试文件。
- `uv run pytest packages/client_core/tests/ packages/mhxy_client/tests/ packages/d4_client/tests/`——确保无回归（尤其 d4_client `test_screens.py:254` 的 mock 契约与 `test_window.py` 的 mouse_move 测试）。

## 行为变化
- 宏观轨迹：1 条主钟形（全量到 CV 估计的 aim）+ 仅在残差>容差时的小修正钟形。不再有 N 段阻尼钟形。钟形（ease-in-out + 抖动）保留。
- 修复 message 后端从原点插值的 bug（用真实 start）。
- `ensure_cursor_in_window` 不再在光标已在窗内时强制回到中心；仅作出窗兜底。

## 明确不做（延后）
- **钟形内中途 CV（连续闭环）**：需要游戏光标移动中即时渲染；现有证据（沉淀 sleep）表明有滞后。`_bell_move_steps` 将来可加 `on_step` 回调以支持，待实测游戏光标渲染滞后后再说。本轮不做。
- **85% 处中途精修**：相对迭代式收益边际，本轮跳过保持简洁。

## 待确认
- 回退先大后小阻尼、改为每迭代全量钟形（主弹道+小修正）——基于"迭代 CV 复测使阻尼多余"的判断。
- 接受"1 主钟形 + 末端小修正"而非"单一不间断钟形"（后者因 CV 需静止而不可行）。
