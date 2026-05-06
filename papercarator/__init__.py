"""
PaperCarator - 全自动论文创作系统

从题目输入到完整论文输出的端到端自动化系统。
"""

__version__ = "0.3.0"
__author__ = "PaperCarator Team"

from papercarator.core.config import Config
from papercarator.core.pipeline import Pipeline

__all__ = ["Config", "Pipeline"]
