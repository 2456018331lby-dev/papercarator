"""模板管理器 - 管理论文LaTeX模板"""

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template
from loguru import logger


class TemplateManager:
    """LaTeX模板管理器

    管理各种论文模板（IEEE、ACM、Springer等）。
    """

    # 内置模板
    BUILTIN_TEMPLATES = {
        "ieee": {
            "name": "IEEE Conference",
            "documentclass": "IEEEtran",
            "options": "conference",
            "packages": [
                "amsmath", "amssymb", "graphicx", "booktabs",
                "algorithm", "algpseudocode", "hyperref", "xcolor", "float",
            ],
        },
        "acm": {
            "name": "ACM Conference",
            "documentclass": "acmart",
            "options": "",
            "packages": [
                "amsmath", "amssymb", "graphicx", "booktabs",
                "algorithm", "algpseudocode", "hyperref", "float",
            ],
        },
        "springer": {
            "name": "Springer LNCS",
            "documentclass": "llncs",
            "options": "",
            "packages": [
                "amsmath", "amssymb", "graphicx", "booktabs",
                "hyperref", "xcolor", "float",
            ],
        },
        "custom": {
            "name": "Custom Template",
            "documentclass": "article",
            "options": "a4paper,12pt",
            "packages": [
                "amsmath", "amssymb", "graphicx", "booktabs",
                "geometry", "hyperref", "xcolor", "ctex", "float",
            ],
        },
    }

    def __init__(self, templates_dir: Path | None = None):
        self.templates_dir = templates_dir or Path("./papercarator/paper_writer/templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            block_start_string='{%',
            block_end_string='%}',
            variable_start_string='{{',
            variable_end_string='}}',
            comment_start_string='{#',
            comment_end_string='#}',
        )
        logger.info(f"初始化 TemplateManager (目录: {self.templates_dir})")

    def get_template(self, template_name: str) -> dict[str, Any]:
        """获取模板配置"""
        if template_name in self.BUILTIN_TEMPLATES:
            return self.BUILTIN_TEMPLATES[template_name].copy()

        # 尝试从文件加载
        template_file = self.templates_dir / f"{template_name}.yaml"
        if template_file.exists():
            import yaml
            with open(template_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)

        logger.warning(f"模板 '{template_name}' 不存在，使用默认模板")
        return self.BUILTIN_TEMPLATES["custom"].copy()

    def list_templates(self) -> list[str]:
        """列出可用模板"""
        return list(self.BUILTIN_TEMPLATES.keys())

    def create_template(self, name: str, config: dict[str, Any]) -> None:
        """创建新模板"""
        import yaml
        template_file = self.templates_dir / f"{name}.yaml"
        with open(template_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        logger.info(f"已创建模板: {name}")

    def get_latex_preamble(self, template_name: str, language: str = "zh") -> str:
        """生成LaTeX导言区"""
        template = self.get_template(template_name)

        lines = []

        # 文档类
        docclass = template["documentclass"]
        options = template.get("options", "")
        if options:
            lines.append(f"\\documentclass[{options}]{{{docclass}}}")
        else:
            lines.append(f"\\documentclass{{{docclass}}}")

        # 中文支持
        if language == "zh":
            lines.append("\\usepackage{ctex}")

        # 包
        packages = []
        for pkg in template.get("packages", []):
            if pkg not in packages:
                packages.append(pkg)

        for pkg in packages:
            if pkg == "ctex" and language == "zh":
                continue  # 已添加
            lines.append(f"\\usepackage{{{pkg}}}")

        # 页面设置（自定义模板）
        if docclass == "article":
            lines.append("\\geometry{margin=2.5cm}")

        # 超链接设置
        lines.append("\\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}")

        # 算法包
        return "\n".join(lines)

    def render_template(self, template_name: str, context: dict[str, Any]) -> str:
        """渲染Jinja2模板"""
        try:
            template = self.jinja_env.get_template(f"{template_name}.tex")
            return template.render(**context)
        except Exception as e:
            logger.warning(f"模板渲染失败: {e}")
            return self._render_builtin(template_name, context)

    def _render_builtin(self, template_name: str, context: dict[str, Any]) -> str:
        """渲染内置模板"""
        # 简单的字符串模板
        template_str = self._get_default_template_str()
        template = Template(template_str)
        return template.render(**context)

    def _get_default_template_str(self) -> str:
        """获取默认模板字符串"""
        return r"""
\documentclass[a4paper,12pt]{article}
\usepackage{ctex}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{geometry}
\usepackage{hyperref}
\usepackage{xcolor}
\usepackage{float}
\geometry{margin=2.5cm}
\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}

\title{ {{title}} }
\author{ {{author}} }
\date{ {{date}} }

\begin{document}
\maketitle

\begin{abstract}
{{abstract}}
\end{abstract}

\section{引言}
{{introduction}}

\section{相关工作}
{{related_work}}

\section{方法}
{{methodology}}

\section{实验}
{{experiments}}

\section{结果与分析}
{{results}}

\section{结论}
{{conclusion}}

\bibliographystyle{plain}
\begin{thebibliography}{99}
{{references}}
\end{thebibliography}

\end{document}
"""
