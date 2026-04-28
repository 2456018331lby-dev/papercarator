"""VS Code桥接模块 - 在VS Code中打开生成的文件"""

import subprocess
from pathlib import Path
from typing import Any

from loguru import logger

from papercarator.core.config import VSCodeConfig


class VSCodeBridge:
    """VS Code桥接器

    在VS Code中自动打开生成的LaTeX源文件和PDF，
    提供流畅的论文编辑体验。
    """

    def __init__(self, config: VSCodeConfig | None = None):
        self.config = config or VSCodeConfig()
        self._available = self._check_vscode()
        logger.info(f"VSCodeBridge初始化 (可用: {self._available}, 路径: {self.config.path})")

    def _check_vscode(self) -> bool:
        """检查VS Code是否可用"""
        try:
            vscode_path = Path(self.config.path)
            if vscode_path.exists():
                return True
            # 尝试从环境变量查找
            import shutil
            return shutil.which("code") is not None
        except Exception:
            return False

    def is_available(self) -> bool:
        """检查VS Code是否可用"""
        return self._available

    def open_file(self, file_path: Path, wait: bool = False) -> bool:
        """在VS Code中打开文件

        Args:
            file_path: 文件路径
            wait: 是否等待VS Code关闭

        Returns:
            是否成功
        """
        if not self._available:
            logger.warning("VS Code不可用，无法打开文件")
            return False

        try:
            cmd = [self.config.path, str(file_path)]
            if wait:
                cmd.insert(1, "--wait")

            subprocess.Popen(cmd, shell=False)
            logger.info(f"在VS Code中打开: {file_path}")
            return True

        except Exception as e:
            logger.error(f"打开文件失败: {e}")
            return False

    def open_folder(self, folder_path: Path) -> bool:
        """在VS Code中打开文件夹

        Args:
            folder_path: 文件夹路径

        Returns:
            是否成功
        """
        if not self._available:
            logger.warning("VS Code不可用，无法打开文件夹")
            return False

        try:
            subprocess.Popen([self.config.path, str(folder_path)], shell=False)
            logger.info(f"在VS Code中打开文件夹: {folder_path}")
            return True

        except Exception as e:
            logger.error(f"打开文件夹失败: {e}")
            return False

    def open_files(self, file_paths: list[Path]) -> bool:
        """在VS Code中同时打开多个文件

        Args:
            file_paths: 文件路径列表

        Returns:
            是否成功
        """
        if not self._available:
            return False

        try:
            valid_paths = [str(p) for p in file_paths if p.exists()]
            if not valid_paths:
                return False

            cmd = [self.config.path] + valid_paths
            subprocess.Popen(cmd, shell=False)
            logger.info(f"在VS Code中打开 {len(valid_paths)} 个文件")
            return True

        except Exception as e:
            logger.error(f"打开多个文件失败: {e}")
            return False

    def open_paper_workspace(self, tex_path: Path | None,
                             pdf_path: Path | None,
                             output_dir: Path) -> bool:
        """打开论文工作区

        在VS Code中打开LaTeX源文件和PDF（如果可用）。

        Args:
            tex_path: LaTeX文件路径
            pdf_path: PDF文件路径
            output_dir: 输出目录

        Returns:
            是否成功
        """
        if not self._available:
            return False

        files_to_open: list[Path] = []

        if self.config.auto_open_tex and tex_path and tex_path.exists():
            files_to_open.append(tex_path)

        if self.config.auto_open_pdf and pdf_path and pdf_path.exists():
            files_to_open.append(pdf_path)

        if files_to_open:
            return self.open_files(files_to_open)

        # 如果没有具体文件，打开文件夹
        if output_dir.exists():
            return self.open_folder(output_dir)

        return False
