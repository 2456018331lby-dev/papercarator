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


def generate_paper(topic, template, output_dir):
    """Gradio回调：生成论文。"""
    if not topic.strip():
        return "请输入题目", None, None

    output_dir = output_dir.strip() or None

    try:
        result = run(topic, output_dir, template)

        if not result.get("success"):
            return f"生成失败: {result.get('error')}", None, None

        # Format summary
        summary_lines = [
            f"=== 论文生成完成 ===",
            f"题目: {result['topic']}",
            f"模型类型: {result['model_type']}",
            f"关键词: {', '.join(result['keywords'])}",
            f"难度: {result['difficulty']}",
            f"质量评分: {result['quality_score']}/100",
            f"求解状态: {'成功' if result['solution_success'] else '失败'}",
            f"求解信息: {result['solution_message']}",
            f"图表数量: {result['chart_count']}",
            f"算法伪代码: {'是' if result['has_algorithm'] else '否'}",
            f"耗时: {result['elapsed_seconds']}秒",
            f"输出目录: {result['output_dir']}",
        ]
        if result.get("suggestions"):
            summary_lines.append("")
            summary_lines.append("改进建议:")
            for s in result["suggestions"]:
                summary_lines.append(f"  - {s}")

        summary = "\n".join(summary_lines)

        pdf_path = result.get("pdf")
        tex_path = result.get("tex")

        return summary, pdf_path, tex_path

    except Exception as e:
        return f"异常: {str(e)}", None, None


def analyze_topic(topic):
    """Gradio回调：仅分析题目。"""
    if not topic.strip():
        return "请输入题目"

    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from papercarator.planner import TopicAnalyzer
        analyzer = TopicAnalyzer()
        result = analyzer.analyze(topic)

        lines = [
            f"论文类型: {result['paper_type']}",
            f"难度: {result['difficulty']}",
            f"应用领域: {result['application_domain']}",
            f"关键词: {', '.join(result['keywords'])}",
            f"研究方法: {', '.join(result['research_methods'])}",
            f"数学工具: {', '.join(result['required_math_tools'])}",
            f"可视化: {', '.join(result['required_visualizations'])}",
        ]
        return "\n".join(lines)
    except Exception as e:
        return f"分析失败: {str(e)}"


# Build UI
with gr.Blocks(title="PaperCarator - 数学建模论文生成器", theme=gr.themes.Soft()) as app:
    gr.Markdown("# PaperCarator - 数学建模论文生成器")
    gr.Markdown("输入题目，一键生成包含数学建模、图表、算法伪代码的完整学术论文。")

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
                        choices=["custom", "ieee", "acm", "cjm", "springer_lncs", "thesis"],
                        value="custom",
                        label="论文模板",
                    )
                    output_input = gr.Textbox(
                        label="输出目录（可选）",
                        placeholder="留空自动创建",
                    )
                generate_btn = gr.Button("生成论文", variant="primary", size="lg")

            with gr.Column(scale=3):
                summary_output = gr.Textbox(label="生成结果", lines=15, interactive=False)
                with gr.Row():
                    pdf_file = gr.File(label="PDF文件")
                    tex_file = gr.File(label="LaTeX文件")

        generate_btn.click(
            generate_paper,
            inputs=[topic_input, template_select, output_input],
            outputs=[summary_output, pdf_file, tex_file],
        )

    with gr.Tab("题目分析"):
        analyze_input = gr.Textbox(
            label="输入题目",
            placeholder="输入题目进行分析，查看模型类型、关键词等",
            lines=2,
        )
        analyze_btn = gr.Button("分析")
        analyze_output = gr.Textbox(label="分析结果", lines=10, interactive=False)
        analyze_btn.click(analyze_topic, inputs=analyze_input, outputs=analyze_output)

    with gr.Tab("支持的模型"):
        gr.Markdown("""
        | 类型 | 说明 |
        |------|------|
        | equation_system | 方程组 |
        | optimization | 优化问题 |
        | multi_objective | 多目标优化 |
        | differential | 微分方程 |
        | pde | 偏微分方程 |
        | queueing | 排队系统 |
        | markov_chain | 马尔可夫链 |
        | bayesian | 贝叶斯推断 |
        | statistical | 统计回归 |
        | network_flow | 网络流 |
        | graph_theory | 图论 |
        | time_series | 时间序列 |
        | game_theory | 博弈论 |
        | control_theory | 控制理论 |
        | clustering | 聚类分析 |
        | fuzzy_logic | 模糊逻辑 |
        """)


if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=False)
