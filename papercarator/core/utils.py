"""通用工具函数"""

import hashlib
import re
from pathlib import Path
from typing import Any

from loguru import logger


def sanitize_filename(name: str) -> str:
    """将字符串转换为安全的文件名"""
    # 替换非法字符
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    # 去除首尾空格和点
    name = name.strip(" .")
    # 限制长度
    if len(name) > 100:
        name = name[:100]
    return name


def generate_project_id(topic: str) -> str:
    """根据题目生成项目ID"""
    hash_obj = hashlib.md5(topic.encode("utf-8"))
    return hash_obj.hexdigest()[:8]


def ensure_dir(path: Path) -> Path:
    """确保目录存在，返回Path对象"""
    path.mkdir(parents=True, exist_ok=True)
    return path


def read_template(template_path: Path) -> str:
    """读取模板文件"""
    if not template_path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: Path, content: str) -> None:
    """写入文本文件"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.debug(f"已写入文件: {path}")


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """深度合并两个字典"""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result
