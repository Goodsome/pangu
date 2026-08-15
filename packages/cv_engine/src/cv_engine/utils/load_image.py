from pathlib import Path

import cv2
from cv_engine.models import MatLike

_IMAGE_CACHE: dict[str, MatLike] = {}

def load_image(path: Path) -> MatLike:
    path_key = str(path.resolve())
    if path_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[path_key]
    
    if not path.exists():
        raise FileNotFoundError(f"模板图片未找到: {path}")
        
    img = cv2.imread(path_key)
    if img is None:
        raise ValueError(f"无法读取图片: {path}")
        
    _IMAGE_CACHE[path_key] = img
    return img