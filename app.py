"""PaperCarator Web UI - Gradio交互界面。

Usage:
    python app.py
    # 访问 http://localhost:7860
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

try:
    import gradio as gr
except ImportError:
    print("需要安装gradio: pip install gradio")
    sys.exit(1)

from scripts.run_paper import run


def generate_paper(topic, template, output_dir, data_file, paper_type_hint):
    """Gradio回调：生成论文。"""
    if not topic.strip():
        return "请输入题目", None, None

    output_dir = output_dir.strip() or None
    data_file = data_file.strip() or None
    paper_type_hint = paper_type_hint.strip() or None

    try:
        result = run(topic, output_dir, template, data_file, paper_type_hint)

        if not result.get("success"):
            return f"生成失败: {result.get('error')}", None, None

        summary_lines = [
            "=== 论文生成完成 ===",
            f"题目: {result['topic']}",
            f"论文类型: {result.get('paper_type_name', result['paper_type'])}",
            f"模型类型: {result['model_name']} ({result['model_type']})",
            f"关键词: {', '.join(result['keywords'])}",
            f"质量评分: {result['quality_score']}/100",
            f"图表数量: {result['chart_count']}",
            f"耗时: {result['elapsed_seconds']}秒",
            f"输出目录: {result['output_dir']}",
        ]
        if result.get("suggestions"):
            summary_lines.extend(["", "改进建议:"] +
                [f"  - {s}" for s in result["suggestions"]])

        pdf_path = result.get("pdf")
        tex_path = result.get("tex")
        return "\n".join(summary_lines), pdf_path, tex_path

    except Exception as e:
        return f"异常: {str(e)}", None, None


def analyze_topic(topic, paper_type_hint):
    """Gradio回调：仅分析题目。"""
    if not topic.strip():
        return "请输入题目"

    try:
        from papercarator.planner import TopicAnalyzer
        from papercarator.paper_writer.paper_types import PaperType

        analyzer = TopicAnalyzer()
        result = analyzer.analyze(topic)

        paper_type = PaperType.detect_type(topic, paper_type_hint or None)
        type_info = PaperType.get_type(paper_type)

        lines = [
            f"论文类型: {type_info['name']} ({paper_type})",
            f"引用格式: {type_info['citation_format']}",
            f"语言: {'中文' if type_info['language'] == 'zh' else 'English'}",
            f"建议页数: {type_info['min_pages']}+",
            f"难度: {result['difficulty']}",
            f"应用领域: {result['application_domain']}",
            f"关键词: {', '.join(result['keywords'])}",
            f"研究方法: {', '.join(result['research_methods'])}",
            f"数学工具: {', '.join(result['required_math_tools'])}",
            "",
            "章节结构:",
            *[f"  - {title}" for _, title in type_info["sections"]],
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"分析失败: {str(e)}"


# Build UI
with gr.Blocks(title="PaperCarator v0.3 — 学术论文生成器",
               theme=gr.themes.Soft()) as app:
    gr.Markdown("# PaperCarator v0.3")
    gr.Markdown("支持7种论文类型、16种数学模型、5种引用格式的端到端论文生成。")

    with gr.Tab("一键生成"):
        with gr.Row():
            with gr.Column(scale=2):
                topic_input = gr.Textbox(
                    label="论文题目",
                    placeholder="例如：基于排队论的医院门诊流程优化研究",
                    lines=2,
                )
                with gr.Row():
                    template_select = gr.Dropdown(
                        choices=["custom", "ieee", "acm", "springer_lncs", "cjm"],
                        value="custom", label="LaTeX模板",
                    )
                    type_select = gr.Dropdown(
                        choices=["", "thesis", "journal", "conference",
                                  "review", "experiment", "case_study", "math_modeling"],
                        value="", label="论文类型（可选，自动检测）",
                    )
                data_input = gr.Textbox(
                    label="数据文件（可选，CSV/Excel/JSON）",
                    placeholder="留空使用合成数据",
                )
                output_input = gr.Textbox(
                    label="输出目录（可选）",
                    placeholder="留空自动创建 ./output/<题目>/",
                )
                generate_btn = gr.Button("生成论文", variant="primary", size="lg")

            with gr.Column(scale=3):
                summary_output = gr.Textbox(label="生成结果", lines=15, interactive=False)
                with gr.Row():
                    pdf_file = gr.File(label="PDF文件")
                    tex_file = gr.File(label="LaTeX文件")

        generate_btn.click(
            generate_paper,
            inputs=[topic_input, template_select, output_input, data_input, type_select],
            outputs=[summary_output, pdf_file, tex_file],
        )

    with gr.Tab("题目分析"):
        analyze_input = gr.Textbox(
            label="输入题目",
            placeholder="输入题目进行分析，查看模型类型、关键词等",
            lines=2,
        )
        analyze_type = gr.Dropdown(
            choices=["", "thesis", "journal", "conference",
                      "review", "experiment", "case_study", "math_modeling"],
            value="", label="指定类型（可选）",
        )
        analyze_btn = gr.Button("分析")
        analyze_output = gr.Textbox(label="分析结果", lines=14, interactive=False)
        analyze_btn.click(
            analyze_topic,
            inputs=[analyze_input, analyze_type],
            outputs=analyze_output)

    with gr.Tab("能力概览"):
        gr.Markdown("""
### 论文类型 (7)
| ID | 名称 | 页数 | 引用格式 |
|----|------|------|----------|
| thesis | 毕业论文 | 30-100 | GB/T 7714 |
| journal | 期刊论文 | 6-15 | APA |
| conference | 会议论文 | 4-8 | IEEE |
| review | 综述论文 | 10-30 | APA |
| experiment | 实验论文 | 8-20 | APA |
| case_study | 案例研究 | 6-15 | APA |
| math_modeling | 数学建模 | 15-30 | GB/T 7714 |

### 数学模型 (16)
equation_system, optimization, multi_objective, differential, pde,
queueing, markov_chain, bayesian, statistical, network_flow,
time_series, game_theory, control_theory, clustering, graph_theory, fuzzy_logic

### 统计分析
描述统计, t检验 (Cohen's d), Pearson相关, 线性回归, ANOVA, 卡方检验, LaTeX表格输出

### 引用格式 (5)
GB/T 7714 | APA | IEEE | Chicago | MLA
""")


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)