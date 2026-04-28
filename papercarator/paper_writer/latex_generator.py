"""LaTeX生成器 - 生成完整的LaTeX文档并编译为PDF"""

import subprocess
from pathlib import Path
from typing import Any

from loguru import logger

from papercarator.paper_writer.section_writer import SectionWriter
from papercarator.paper_writer.template_manager import TemplateManager


class LaTeXGenerator:
    """LaTeX论文生成器

    整合各章节内容，生成完整LaTeX文档，并编译为PDF。
    """

    def __init__(self, template_manager: TemplateManager | None = None,
                 section_writer: SectionWriter | None = None,
                 latex_compiler: str = "xelatex"):
        self.template_manager = template_manager or TemplateManager()
        self.section_writer = section_writer or SectionWriter()
        self.latex_compiler = latex_compiler
        logger.info(f"初始化 LaTeXGenerator (编译器: {latex_compiler})")

    def generate(self, topic: str, plan: dict[str, Any],
                 math_model: dict[str, Any], solution: dict[str, Any],
                 visualizations: list[Path], output_dir: Path) -> tuple[dict[str, str], Path | None]:
        """生成完整论文

        Args:
            topic: 论文题目
            plan: 题目分析结果
            math_model: 数学模型
            solution: 求解结果
            visualizations: 可视化文件路径列表
            output_dir: 输出目录

        Returns:
            (章节内容字典, PDF路径或None)
        """
        logger.info("开始生成论文...")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 1. 生成各章节内容
        sections = self.section_writer.write_all_sections(topic, plan, math_model, solution)

        # 2. 处理图片路径
        sections = self._process_figures(sections, visualizations, output_dir)

        # 3. 生成LaTeX文档
        latex_content = self._generate_latex_document(sections, plan)

        # 4. 保存LaTeX文件
        tex_path = output_dir / "paper.tex"
        with open(tex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        logger.info(f"LaTeX文件已保存: {tex_path}")

        # 5. 复制图片到输出目录
        self._copy_visualizations(visualizations, output_dir)

        # 6. 编译PDF
        pdf_path = self._compile_latex(tex_path, output_dir)

        return sections, pdf_path

    def _process_figures(self, sections: dict[str, str],
                        visualizations: list[Path], output_dir: Path) -> dict[str, str]:
        """处理图片引用"""
        if not visualizations:
            return sections

        # 在结果章节添加图片
        figure_text = "\n\n\\subsection{图表展示}\n\n"
        for i, viz_path in enumerate(visualizations[:6]):  # 最多6张图
            filename = viz_path.name
            figure_text += f"""\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{{{filename}}}
\\caption{{Figure {i+1}: Visualization result}}
\\end{{figure}}

"""

        if "results" in sections:
            sections["results"] += figure_text

        return sections

    def _generate_latex_document(self, sections: dict[str, str],
                                 plan: dict[str, Any]) -> str:
        """生成完整LaTeX文档"""
        template_name = plan.get("template", "custom")
        language = plan.get("language", "zh")

        # 获取导言区
        preamble = self.template_manager.get_latex_preamble(template_name, language)

        # 构建文档
        doc = preamble + "\n\n"

        # 标题信息
        doc += f"\\title{{{sections.get('title', 'Untitled')}}}\n"
        doc += f"\\author{{PaperCarator Automated System}}\n"
        doc += f"\\date{{\\today}}\n\n"

        doc += "\\begin{document}\n\n"
        doc += "\\maketitle\n\n"

        # 摘要
        if "abstract" in sections:
            doc += "\\begin{abstract}\n"
            doc += sections["abstract"] + "\n"
            doc += "\\end{abstract}\n\n"

        # 关键词
        keywords = plan.get("keywords", [])
        if keywords:
            doc += f"\\textbf{{Keywords:}} {', '.join(keywords)}\n\n"

        # 各章节
        section_order = [
            "introduction",
            "related_work",
            "methodology",
            "experiments",
            "results",
            "conclusion",
        ]

        for section in section_order:
            if section in sections:
                section_title = self._get_section_title(section, language)
                doc += f"\\section{{{section_title}}}\n"
                doc += sections[section] + "\n\n"

        # 参考文献
        if "references" in sections:
            doc += "\\bibliographystyle{plain}\n"
            doc += "\\begin{thebibliography}{99}\n"
            doc += sections["references"] + "\n"
            doc += "\\end{thebibliography}\n\n"

        doc += "\\end{document}\n"

        return doc

    def _get_section_title(self, section: str, language: str) -> str:
        """获取章节标题"""
        titles = {
            "zh": {
                "introduction": "引言",
                "related_work": "相关工作",
                "methodology": "方法",
                "experiments": "实验",
                "results": "结果与分析",
                "conclusion": "结论",
            },
            "en": {
                "introduction": "Introduction",
                "related_work": "Related Work",
                "methodology": "Methodology",
                "experiments": "Experiments",
                "results": "Results and Analysis",
                "conclusion": "Conclusion",
            },
        }
        return titles.get(language, titles["en"]).get(section, section.title())

    def _copy_visualizations(self, visualizations: list[Path], output_dir: Path) -> None:
        """复制可视化文件到输出目录"""
        import shutil
        for viz_path in visualizations:
            if viz_path.exists():
                dest = output_dir / viz_path.name
                shutil.copy2(viz_path, dest)
                logger.debug(f"复制图片: {viz_path} -> {dest}")

    def _compile_latex(self, tex_path: Path, output_dir: Path) -> Path | None:
        """编译LaTeX为PDF"""
        logger.info(f"编译LaTeX: {tex_path}")
        tex_filename = tex_path.name
        output_dir_arg = str(output_dir.resolve())

        try:
            # 检查编译器是否可用
            result = subprocess.run(
                [self.latex_compiler, "--version"],
                capture_output=True,
                text=False,
                timeout=10,
            )
            stdout = self._decode_output(result.stdout)
            stderr = self._decode_output(result.stderr)
            if result.returncode != 0:
                logger.warning(f"{self.latex_compiler} 不可用")
                return None

        except FileNotFoundError:
            logger.warning(f"编译器 {self.latex_compiler} 未找到")
            return None
        except subprocess.TimeoutExpired:
            logger.warning("编译器检查超时")
            return None

        # 编译（多次编译以解决引用）
        for i in range(2):
            try:
                result = subprocess.run(
                    [self.latex_compiler, "-interaction=nonstopmode",
                     "-output-directory", output_dir_arg,
                     tex_filename],
                    capture_output=True,
                    text=False,
                    timeout=120,
                    cwd=str(tex_path.parent),
                )
                stdout = self._decode_output(result.stdout)
                stderr = self._decode_output(result.stderr)
                if result.returncode != 0:
                    logger.warning(f"第{i+1}次编译有警告/错误")
                    # 记录错误日志
                    log_path = output_dir / "compile.log"
                    with open(log_path, 'w', encoding='utf-8') as f:
                        f.write(stdout)
                        f.write(stderr)

            except subprocess.TimeoutExpired:
                logger.error("LaTeX编译超时")
                return None
            except Exception as e:
                logger.error(f"编译出错: {e}")
                return None

        # 检查PDF是否生成
        pdf_path = output_dir / tex_path.with_suffix(".pdf").name
        if pdf_path.exists():
            log_path = output_dir / "compile.log"
            if log_path.exists():
                log_path.unlink()
            logger.info(f"PDF生成成功: {pdf_path}")
            return pdf_path
        else:
            logger.warning("PDF未生成")
            return None

    def _decode_output(self, payload: bytes | None) -> str:
        """以容错方式解码编译器输出。"""
        if not payload:
            return ""

        for encoding in ("utf-8", "gbk", "cp936"):
            try:
                return payload.decode(encoding)
            except UnicodeDecodeError:
                continue

        return payload.decode("utf-8", errors="ignore")
