"""论文写作模块测试"""

from pathlib import Path
from types import SimpleNamespace

import pytest

from papercarator.paper_writer import LaTeXGenerator, SectionWriter, TemplateManager


class TestSectionWriter:
    """测试章节写作器"""

    def test_write_sections(self):
        """测试章节生成"""
        writer = SectionWriter()

        sections = writer.write_all_sections(
            topic="测试题目",
            plan={"paper_type": "modeling", "keywords": ["测试"], "application_domain": "general"},
            math_model={"model_type": "equation_system", "name": "测试模型", "equations": ["x+y=1"]},
            solution={"success": True, "values": {"x": 1}, "message": "成功"},
        )

        assert "title" in sections
        assert "abstract" in sections
        assert "introduction" in sections
        assert "methodology" in sections
        assert "results" in sections
        assert "conclusion" in sections

    def test_write_abstract(self):
        """测试摘要生成"""
        writer = SectionWriter()

        abstract = writer._write_abstract(
            "测试", {"paper_type": "modeling"},
            {"model_type": "equation"}, {"success": True, "message": "成功"}
        )

        assert len(abstract) > 0
        assert "测试" in abstract

    def test_write_methodology_uses_model_specific_profile(self):
        """测试方法章节会根据模型类型切换叙事"""
        writer = SectionWriter()

        methodology = writer._write_methodology(
            "资源配置问题",
            {"research_methods": ["optimization"]},
            {
                "model_type": "optimization",
                "name": "二次规划优化模型",
                "equations": ["x + y >= 1", "x >= 0"],
                "objective": "x**2 + y**2 - x",
                "objective_type": "minimize",
            },
            {
                "success": True,
                "statistics": {"optimal_value": -1.25, "iterations": 8},
            },
        )

        assert "优化模型" in methodology
        assert "目标函数" in methodology
        assert "optimal\\_value" in methodology

    def test_write_results_avoids_broken_latex_tokens(self):
        """测试结果章节不再生成损坏的 LaTeX 片段"""
        writer = SectionWriter()

        results = writer._write_results(
            "测试题目",
            {"application_domain": "general"},
            {"model_type": "statistical"},
            {
                "success": True,
                "message": "回归分析完成",
                "values": {"slope": 2.5},
                "statistics": {"r_squared": 0.91},
            },
        )

        assert "\\end{{table}}}}" not in results
        assert "统计回归模型" in results

    @pytest.mark.parametrize(
        ("model_type", "expected_label"),
        [
            ("game_theory", "博弈论模型"),
            ("control_theory", "控制理论模型"),
            ("clustering", "聚类分析模型"),
        ],
    )
    def test_write_methodology_for_new_model_profiles(self, model_type, expected_label):
        """测试新增模型类型不会回退到方程组写作画像"""
        writer = SectionWriter()

        methodology = writer._write_methodology(
            "测试题目",
            {"research_methods": ["mathematical_modeling"]},
            {"model_type": model_type, "name": "测试模型"},
            {"success": True, "statistics": {"score": 1.0}},
        )

        assert expected_label in methodology
        assert "方程组模型" not in methodology


class TestLaTeXGenerator:
    """测试 LaTeX 生成器"""

    def test_compile_uses_local_filename_on_windows(self, tmp_path, monkeypatch):
        """测试编译时使用局部文件名，避免 Windows 路径转义问题"""
        generator = LaTeXGenerator()
        output_dir = tmp_path / "paper"
        output_dir.mkdir()
        tex_path = output_dir / "paper.tex"
        tex_path.write_text("\\documentclass{article}\\begin{document}ok\\end{document}", encoding="utf-8")
        pdf_path = output_dir / "paper.pdf"
        pdf_path.write_bytes(b"%PDF-1.4")

        calls: list[list[str]] = []

        def fake_run(args, capture_output, text, timeout, cwd=None):
            calls.append(args)
            return SimpleNamespace(returncode=0, stdout=b"ok", stderr=b"")

        monkeypatch.setattr("papercarator.paper_writer.latex_generator.subprocess.run", fake_run)

        result = generator._compile_latex(tex_path, output_dir)

        assert result == pdf_path
        assert calls[1][-1] == "paper.tex"
        assert str(tex_path) not in calls[1]


class TestTemplateManager:
    """测试模板管理器"""

    def test_get_template(self):
        """测试获取模板"""
        tm = TemplateManager()

        template = tm.get_template("ieee")
        assert "documentclass" in template
        assert template["documentclass"] == "IEEEtran"

    def test_list_templates(self):
        """测试列出模板"""
        tm = TemplateManager()

        templates = tm.list_templates()
        assert "ieee" in templates
        assert "custom" in templates

    def test_get_preamble(self):
        """测试生成导言区"""
        tm = TemplateManager()

        preamble = tm.get_latex_preamble("custom", "zh")
        assert "\\documentclass" in preamble
        assert "ctex" in preamble
        assert "\\usepackage{float}" in preamble
