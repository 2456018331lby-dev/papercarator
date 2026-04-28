"""PaperCarator Web UI - Gradio交互界面

一键生成学术论文的Web界面。
"""

import tempfile
from pathlib import Path

import gradio as gr

from papercarator.planner import TopicAnalyzer
from papercarator.math_modeling import ModelBuilder, ModelSolver, ModelValidator
from papercarator.paper_writer import LaTeXGenerator, SectionWriter
from papercarator.visualization import ChartGenerator


def generate_paper(topic: str, progress=gr.Progress()):
    """生成完整论文

    Args:
        topic: 论文题目
        progress: Gradio进度条

    Returns:
        各章节内容、PDF文件路径、状态信息
    """
    if not topic or len(topic.strip()) < 5:
        return "请输入有效的论文题目（至少5个字符）", None, None, None, None, None, None, None, "错误：题目太短"

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            # Step 1: 题目分析
            progress(0.1, desc="正在分析题目...")
            analyzer = TopicAnalyzer()
            plan = analyzer.analyze(topic)

            # Step 2: 数学建模
            progress(0.25, desc="正在构建数学模型...")
            builder = ModelBuilder()
            solver = ModelSolver()
            validator = ModelValidator()

            model = builder.build(topic, plan)
            solution = solver.solve(model)
            validation = validator.validate(model, solution)

            math_model_data = {
                "model": builder.to_dict(model),
                "solution": {
                    "success": solution.success,
                    "values": solution.values,
                    "message": solution.message,
                    "statistics": solution.statistics,
                    "numerical_data": solution.numerical_data,
                },
                "validation": {
                    "is_valid": validation.is_valid,
                    "score": validation.score,
                },
            }

            # Step 3: 生成可视化
            progress(0.4, desc="正在生成图表...")
            chart_gen = ChartGenerator()
            viz_files = []
            if solution.success:
                viz_files = chart_gen.generate(
                    math_model_data["model"],
                    math_model_data["solution"],
                    output_dir / "charts",
                )

            # Step 4: 生成论文
            progress(0.6, desc="正在撰写论文...")
            generator = LaTeXGenerator()
            sections, pdf_path = generator.generate(
                topic=topic,
                plan=plan,
                math_model=math_model_data["model"],
                solution=math_model_data["solution"],
                visualizations=viz_files,
                output_dir=output_dir / "paper",
            )

            # 准备输出
            progress(0.9, desc="正在整理结果...")

            # 构建状态信息
            status = f"""
## 生成状态

- **题目**: {topic}
- **论文类型**: {plan.get('paper_type', '未知')}
- **数学模型**: {model.model_type}
- **求解状态**: {'成功' if solution.success else '失败'}
- **验证得分**: {validation.score:.2f}
- **生成章节**: {len(sections)} 个
- **图表数量**: {len(viz_files)} 个
- **PDF状态**: {'已生成' if pdf_path and pdf_path.exists() else '生成失败（但LaTeX源文件可用）'}
"""

            # 读取LaTeX源文件
            tex_path = output_dir / "paper" / "paper.tex"
            latex_source = ""
            if tex_path.exists():
                with open(tex_path, 'r', encoding='utf-8') as f:
                    latex_source = f.read()

            progress(1.0, desc="完成！")

            return (
                sections.get("abstract", ""),
                sections.get("introduction", ""),
                sections.get("methodology", ""),
                sections.get("experiments", ""),
                sections.get("results", ""),
                sections.get("conclusion", ""),
                latex_source,
                str(pdf_path) if pdf_path and pdf_path.exists() else None,
                status,
            )

    except Exception as e:
        return (
            f"生成过程中出现错误: {str(e)}",
            "", "", "", "", "", "", None,
            f"错误: {str(e)}"
        )


def create_ui():
    """创建Gradio界面"""

    with gr.Blocks(title="PaperCarator - 学术论文自动生成器") as demo:
        gr.Markdown("""
        # PaperCarator - 学术论文自动生成器

        输入论文题目，系统自动完成：
        1. **题目分析** - 识别研究领域和方法
        2. **数学建模** - 自动构建并求解数学模型
        3. **可视化** - 生成图表和3D模型
        4. **论文写作** - 生成完整学术论文（LaTeX/PDF）
        """)

        with gr.Row():
            with gr.Column(scale=1):
                # 输入区域
                topic_input = gr.Textbox(
                    label="论文题目",
                    placeholder="例如：基于优化理论的资源配置问题研究",
                    lines=2,
                )

                generate_btn = gr.Button("生成论文", variant="primary", size="lg")

                # 状态显示
                status_output = gr.Markdown("等待输入...")

            with gr.Column(scale=2):
                # 结果标签页
                with gr.Tabs():
                    with gr.TabItem("摘要"):
                        abstract_output = gr.Markdown(label="摘要")

                    with gr.TabItem("引言"):
                        intro_output = gr.Markdown(label="引言")

                    with gr.TabItem("方法"):
                        method_output = gr.Markdown(label="研究方法")

                    with gr.TabItem("实验"):
                        exp_output = gr.Markdown(label="实验设计")

                    with gr.TabItem("结果"):
                        results_output = gr.Markdown(label="实验结果")

                    with gr.TabItem("结论"):
                        conclusion_output = gr.Markdown(label="结论")

                    with gr.TabItem("LaTeX源码"):
                        latex_output = gr.Code(
                            label="LaTeX源代码",
                            language="latex",
                            lines=30,
                        )

                    with gr.TabItem("PDF下载"):
                        pdf_output = gr.File(
                            label="下载PDF",
                            file_types=[".pdf"],
                        )
                        gr.Markdown("如果PDF生成失败，可以复制LaTeX源码到本地编译")

        # 绑定按钮事件
        generate_btn.click(
            fn=generate_paper,
            inputs=[topic_input],
            outputs=[
                abstract_output,
                intro_output,
                method_output,
                exp_output,
                results_output,
                conclusion_output,
                latex_output,
                pdf_output,
                status_output,
            ],
        )

        # 示例
        gr.Examples(
            examples=[
                ["基于优化理论的资源配置问题研究"],
                ["基于深度学习的图像分类方法研究"],
                ["微分方程在人口增长模型中的应用"],
                ["线性规划在生产调度中的优化应用"],
            ],
            inputs=[topic_input],
            label="示例题目",
        )

        gr.Markdown("""
        ---
        **说明**：
        - 当前版本使用模板生成内容，未接入LLM
        - 数学建模使用SymPy/SciPy求解
        - PDF生成需要本地安装XeLaTeX
        - 生成的论文可作为初稿参考，建议人工审核修改
        """)

    return demo


if __name__ == "__main__":
    demo = create_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True,
    )
