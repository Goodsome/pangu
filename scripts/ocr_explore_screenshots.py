"""OCR 探查脚本：使用 cv_engine 对 output/screenshots 下的截图做文字识别。

用途：在不直接查看图片的前提下，通过 OCR 识别结果了解截图所含信息
（榜单记录、装备/技能/护身符 tooltip 文本与位置），为 d4_injestion 的
解析逻辑设计提供依据。属于一次性探查脚本，正式实现将落在 d4_injestion 上下文。

用法::

    uv run python scripts/ocr_explore_screenshots.py                       # 默认扫描 output/screenshots/BARBARIAN
    uv run python scripts/ocr_explore_screenshots.py path/to/img1.png ...   # 仅识别指定文件
    uv run python scripts/ocr_explore_screenshots.py some/dir               # 扫描指定目录
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2

from cv_engine import RapidOcrEngine
from cv_engine.models import OcrResult


def load_image(path: Path) -> cv2.typing.MatLike:
    """以 BGR 三通道矩阵加载图片。"""
    img = cv2.imread(str(path))
    if img is None:
        raise FileNotFoundError(f"无法读取图片: {path}")
    return img


def reading_order(results: list[OcrResult]) -> list[OcrResult]:
    """按人类阅读顺序（自上而下、从左到右）排序 OCR 结果。"""
    if not results:
        return []

    sorted_by_y = sorted(results, key=lambda r: (r.rect.y, r.rect.x))

    lines: list[list[OcrResult]] = []
    for r in sorted_by_y:
        appended = False
        if lines:
            ref = lines[-1][0].rect
            overlap = min(r.rect.bottom, ref.bottom) - max(r.rect.y, ref.y)
            if overlap > 0.5 * min(r.rect.height, ref.height):
                lines[-1].append(r)
                appended = True
        if not appended:
            lines.append([r])

    ordered: list[OcrResult] = []
    for line in lines:
        ordered.extend(sorted(line, key=lambda r: r.rect.x))
    return ordered


def ocr_image(engine: RapidOcrEngine, path: Path, confidence: float = 0.3) -> None:
    """识别单张图片并按阅读顺序打印结果。"""
    img = load_image(path)
    height, width = img.shape[:2]

    results = engine.ocr(img, confidence_threshold=confidence)
    ordered = reading_order(results)

    plain = " | ".join(r.text.strip() for r in ordered if r.text.strip())

    print(f"\n{'=' * 90}")
    print(f"FILE: {path}")
    print(f"SIZE: {width}x{height}   BLOCKS: {len(results)}")
    print(f"TEXT: {plain}")
    print("-" * 90)
    for r in ordered:
        rect = r.rect
        print(
            f"  [{r.confidence:0.2f}] {r.text!r:40} "
            f"@({rect.x:4},{rect.y:4}) {rect.width:3}x{rect.height:3}"
        )


def collect_targets(argv: list[str]) -> list[Path]:
    """根据参数收集待识别图片路径列表。"""
    if len(argv) <= 1:
        base = Path("output/screenshots/BARBARIAN")
    else:
        base = Path(argv[1])

    if base.is_file():
        return [base]

    targets: list[Path] = []
    if base.is_dir():
        targets.extend(sorted(base.glob("leaderboard_*.png")))
        for row_dir in sorted(p for p in base.iterdir() if p.is_dir()):
            targets.extend(sorted(row_dir.glob("*.png")))
    return targets


def main(argv: list[str]) -> int:
    targets = collect_targets(argv)
    if not targets:
        print(
            f"未找到待识别图片: {argv[1:] if len(argv) > 1 else 'output/screenshots/BARBARIAN'}"
        )
        return 1

    print(f"待识别图片数: {len(targets)}")
    engine = RapidOcrEngine()

    # 优先识别榜单整页截图，再识别各 row 目录下的 tooltip
    leaderboard = [p for p in targets if p.name.startswith("leaderboard_")]
    others = [p for p in targets if not p.name.startswith("leaderboard_")]
    for path in leaderboard + others:
        ocr_image(engine, path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
