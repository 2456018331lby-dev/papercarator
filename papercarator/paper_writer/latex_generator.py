"""LaTeX生成器 - 生成完整的LaTeX文档并编译为PDF"""

import subprocess
from pathlib import Path
from typing import Any

from loguru import logger

from papercarator.paper_writer.section_writer import SectionWriter
from papercarator.paper_writer.template_manager import TemplateManager
from papercarator.paper_writer.algorithm_writer import AlgorithmWriter
from papercarator.paper_writer.academic_enhancer import AcademicEnhancer
from papercarator.paper_writer.quality_scorer import PaperQualityScorer
from papercarator.paper_writer.llm_writer import LLMWriter


class LaTeXGenerator:
    """LaTeX论文生成器

    整合各章节内容，生成完整LaTeX文档，并编译为PDF。
    """

    def __init__(self, template_manager: TemplateManager | None = None,
                 section_writer: SectionWriter | None = None,
                 latex_compiler: str = "xelatex"):
        self.template_manager = template_manager or TemplateManager()
        self.section_writer = section_writer or SectionWriter()
        self.latex_compiler = self._detect_latex_compiler(latex_compiler)
        self.algorithm_writer = AlgorithmWriter()
        self.academic_enhancer = AcademicEnhancer()
        self.quality_scorer = PaperQualityScorer()
        self.llm_writer = LLMWriter()
        logger.info(f"初始化 LaTeXGenerator (编译器: {self.latex_compiler})")

    @staticmethod
    def _detect_latex_compiler(compiler: str) -> str:
        """检测可用的LaTeX编译器，支持WSL环境。"""
        import shutil
        import os

        # 先检查PATH中是否有
        if shutil.which(compiler):
            return compiler

        # WSL环境：尝试Windows MiKTeX路径
        wsl_miktex = "/mnt/c/Users/24560/AppData/Local/Programs/MiKTeX/miktex/bin/x64/xelatex.exe"
        if os.path.exists(wsl_miktex):
            logger.info(f"WSL环境检测到MiKTeX: {wsl_miktex}")
            return wsl_miktex

        # 尝试常见Windows路径
        for path in [
            r"C:\Users\24560\AppData\Local\Programs\MiKTeX\miktex\bin\x64\xelatex.exe",
            r"C:\texlive\2024\bin\win32\xelatex.exe",
        ]:
            wsl_path = "/mnt/" + path[0].lower() + path[2:].replace("\\", "/")
            if os.path.exists(wsl_path):
                logger.info(f"检测到LaTeX: {wsl_path}")
                return wsl_path

        logger.warning(f"未找到LaTeX编译器: {compiler}")
        return compiler

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

        # 1. 生成各章节内容 (LLM优先，规则兜底)
        if self.llm_writer.is_available():
            logger.info("使用 LLM 深度写作...")
            llm_sections = self.llm_writer.write_all_sections(
                topic, plan, math_model, solution
            )
            if llm_sections:
                # LLM 生成了部分内容，用规则模板补充缺失章节
                rule_sections = self.section_writer.write_all_sections(
                    topic, plan, math_model, solution
                )
                sections = {**rule_sections, **llm_sections}
                logger.info(f"LLM 写作完成: {len(llm_sections)}/{len(rule_sections)} 章节")
            else:
                logger.info("LLM 写作失败，使用规则模板")
                sections = self.section_writer.write_all_sections(
                    topic, plan, math_model, solution
                )
        else:
            logger.info("LLM 不可用，使用规则模板")
            sections = self.section_writer.write_all_sections(
                topic, plan, math_model, solution
            )

        # 1.5 学术用语增强
        sections = self.academic_enhancer.enhance_sections(sections)

        # 1.6 添加算法伪代码
        model_type = math_model.get("model_type", "")
        algorithm_code = self.algorithm_writer.generate(model_type)
        if algorithm_code and "methodology" in sections:
            sections["methodology"] += "\n\n\\subsection{算法描述}\n\n" + algorithm_code

        # 1.7 文献检索补充
        if "references" in sections:
            try:
                from papercarator.literature_search import LiteratureSearcher
                searcher = LiteratureSearcher()
                sections["references"] = searcher.enrich_references(
                    topic, model_type, sections["references"]
                )
            except Exception as e:
                logger.info(f"文献检索跳过: {e}")

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

        # 7. 质量评分
        chart_files = [Path(f) for f in (output_dir.glob("*.png"))]
        report = self.quality_scorer.score(latex_content, chart_files, model_type)
        logger.info(f"论文质量评分: {report.total_score:.1f}/100")
        for suggestion in report.suggestions[:3]:
            logger.info(f"  建议: {suggestion}")

        return sections, pdf_path

    CAPTION_MAP = {
        "queue_curve": "排队长度随时间演化曲线",
        "queue_metrics": "排队系统关键性能指标",
        "queueing_3d_profile": "排队系统三维可视化",
        "optimization_landscape": "优化目标函数等高线图",
        "optimization_stats": "优化求解统计信息",
        "differential_solution": "微分方程数值解（位移与相空间）",
        "regression_analysis": "回归分析与残差诊断图",
        "statistical_summary": "统计分析汇总",
        "network_flow_graph": "网络流最短路径图",
        "network_flow_allocation": "各边流量分配图",
        "time_series_forecast": "时间序列拟合与预测结果",
        "time_series_residuals": "预测残差分析",
        "pareto_front": "帕累托前沿近似",
        "pde_heatmaps": "偏微分方程温度场演化",
        "pde_surface": "偏微分方程解的三维曲面",
        "markov_distribution_evolution": "马尔可夫链状态分布演化",
        "markov_probability_heatmap": "状态概率热力图",
        "game_payoff_matrix": "博弈收益矩阵热力图",
        "game_strategy_distribution": "混合策略概率分布",
        "control_step_response": "控制系统阶跃响应曲线",
        "control_stability_metrics": "控制系统稳定性指标",
        "clustering_result": "聚类分析散点图",
        "clustering_metrics": "聚类质量指标",
        "equation_solution": "方程组求解结果",
    }

    def _process_figures(self, sections: dict[str, str],
                        visualizations: list[Path], output_dir: Path) -> dict[str, str]:
        """处理图片引用"""
        if not visualizations:
            return sections

        # 在结果章节添加图片
        figure_text = "\n\\subsection{图表展示}\n\n"
        for i, viz_path in enumerate(visualizations[:6]):  # 最多6张图
            filename = viz_path.name
            stem = viz_path.stem
            caption = self.CAPTION_MAP.get(stem, f"{stem} 可视化结果")
            figure_text += f"""\\begin{{figure}}[H]
\\centering
\\includegraphics[width=0.8\\textwidth]{{{filename}}}
\\caption{{{caption}}}
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

        try:
            # 检查编译器是否可用
            result = subprocess.run(
                [self.latex_compiler, "--version"],
                capture_output=True, text=False, timeout=10,
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

        # 判断是否使用Windows编译器（WSL环境）
        is_windows_compiler = self.latex_compiler.endswith(".exe")

        if is_windows_compiler:
            # Windows编译器需要Windows路径
            path_str = str(tex_path)
            out_str = str(output_dir.resolve())
            # Only convert if it's under /mnt/X/ (Windows drive mount)
            if path_str.startswith("/mnt/"):
                tex_arg = path_str.replace("/mnt/c/", "C:\\").replace("/mnt/d/", "D:\\").replace("/", "\\")
                out_arg = out_str.replace("/mnt/c/", "C:\\").replace("/mnt/d/", "D:\\").replace("/", "\\")
            else:
                # Non-Windows path, can't use Windows compiler
                logger.warning("Windows编译器无法访问WSL本地路径，跳过PDF编译")
                return None
        else:
            tex_filename = tex_path.name
            out_arg = str(output_dir.resolve())
            tex_arg = tex_filename

        # 编译（多次编译以解决引用）
        for i in range(2):
            try:
                if is_windows_compiler:
                    cmd = [self.latex_compiler, "-interaction=nonstopmode",
                           "-output-directory", out_arg, tex_arg]
                    cwd = None
                else:
                    cmd = [self.latex_compiler, "-interaction=nonstopmode",
                           "-output-directory", out_arg, tex_arg]
                    cwd = str(tex_path.parent)

                result = subprocess.run(
                    cmd, capture_output=True, text=False,
                    timeout=120, cwd=cwd,
                )
                stdout = self._decode_output(result.stdout)
                stderr = self._decode_output(result.stderr)
                if result.returncode != 0:
                    logger.warning(f"第{i+1}次编译有警告/错误")
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
        pdf_path = output_dir / "paper.pdf"
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
