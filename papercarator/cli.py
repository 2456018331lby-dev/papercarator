"""命令行接口 - PaperCarator主入口"""

from pathlib import Path

import click
from loguru import logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from papercarator.core.config import Config
from papercarator.core.pipeline import Pipeline
from papercarator.core.utils import generate_project_id, sanitize_filename
from papercarator.github_publisher import GitHubPublisher
from papercarator.math_modeling import ModelBuilder, ModelSolver, ModelValidator
from papercarator.paper_writer import LaTeXGenerator
from papercarator.planner import TaskPlanner, TopicAnalyzer
from papercarator.visualization import ChartGenerator, Model3DGenerator

console = Console()


def setup_logging(log_level: str = "INFO") -> None:
    """配置日志"""
    logger.remove()
    logger.add(
        lambda msg: console.print(msg, end=""),
        level=log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
    )


@click.group()
@click.option("--config", "-c", type=click.Path(exists=True), help="配置文件路径")
@click.option("--verbose", "-v", is_flag=True, help="详细输出")
@click.pass_context
def main(ctx: click.Context, config: str | None, verbose: bool) -> None:
    """PaperCarator - 全自动论文创作系统"""
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)

    # 加载配置
    if config:
        cfg = Config.from_yaml(config)
    else:
        cfg = Config()

    ctx.ensure_object(dict)
    ctx.obj["config"] = cfg


@main.command()
@click.argument("topic")
@click.option("--output", "-o", type=click.Path(), help="输出目录")
@click.option("--template", "-t", default="custom", help="论文模板")
@click.option("--no-github", is_flag=True, help="不发布到GitHub")
@click.option("--no-vscode", is_flag=True, help="不在VS Code中打开结果")
@click.option("--use-matlab", is_flag=True, help="使用MATLAB进行数学建模")
@click.option("--use-solidworks", is_flag=True, help="使用SolidWorks进行3D建模")
@click.option("--matlab-path", type=click.Path(), help="MATLAB可执行文件路径")
@click.option("--sw-visible", is_flag=True, help="显示SolidWorks窗口")
@click.option("--depth", type=click.Choice(["basic", "standard", "deep"]), default="standard")
@click.pass_context
def run(ctx: click.Context, topic: str, output: str | None,
        template: str, no_github: bool, no_vscode: bool,
        use_matlab: bool, use_solidworks: bool,
        matlab_path: str | None, sw_visible: bool,
        depth: str) -> None:
    """运行完整论文创作流程"""
    config: Config = ctx.obj["config"]

    # 更新配置
    config.planner.analysis_depth = depth  # type: ignore
    config.paper_writer.template = template  # type: ignore
    if output:
        config.system.output_dir = Path(output)  # type: ignore

    # 桥接器配置
    config.matlab.enabled = use_matlab  # type: ignore
    config.solidworks.enabled = use_solidworks  # type: ignore
    config.vscode.enabled = not no_vscode  # type: ignore
    if matlab_path:
        config.matlab.path = matlab_path  # type: ignore
    if sw_visible:
        config.solidworks.visible = True  # type: ignore

    console.print(Panel.fit(
        f"[bold blue]PaperCarator[/bold blue] - 全自动论文创作系统\n"
        f"题目: [green]{topic}[/green]\n"
        f"模板: [yellow]{template}[/yellow] | 深度: [yellow]{depth}[/yellow]",
        title="开始创作",
        border_style="blue",
    ))

    # 创建Pipeline
    pipeline = Pipeline(config)

    console.print("[bold]初始化模块...[/bold]")

    console.print(" - 注册题目分析模块")
    pipeline.register_module("planner", TopicAnalyzer())

    console.print(" - 注册数学建模模块")
    pipeline.register_module("math_modeling", {
        "builder": ModelBuilder(),
        "solver": ModelSolver(
            matlab_bridge=pipeline.matlab_bridge if use_matlab else None
        ),
        "validator": ModelValidator(),
        "build_and_solve": lambda topic, plan, matlab_bridge=None: _run_math_modeling(
            topic, plan, matlab_bridge
        ),
    })

    console.print(" - 注册可视化模块")
    pipeline.register_module("visualization", {
        "chart": ChartGenerator(),
        "model3d": Model3DGenerator(
            solidworks_bridge=pipeline.solidworks_bridge if use_solidworks else None
        ),
        "generate": lambda topic, math_model, plan, output_dir, solidworks_bridge=None: _run_visualization(
            topic, math_model, plan, output_dir, solidworks_bridge
        ),
    })

    console.print(" - 注册论文写作模块")
    pipeline.register_module("paper_writer", {
        "generator": LaTeXGenerator(),
        "write": lambda topic, plan, math_model, visualizations, output_dir: _run_paper_writer(
            topic, plan, math_model, visualizations, output_dir
        ),
    })

    if not no_github:
        console.print(" - 注册GitHub发布模块")
        pipeline.register_module("github_publisher", {
            "publisher": GitHubPublisher(),
            "publish": lambda topic, paper_pdf, source_dir: _run_github_publisher(
                topic, paper_pdf, source_dir
            ),
        })

    # 执行Pipeline
    console.print("\n[bold]开始执行创作流程...[/bold]\n")

    try:
        result = pipeline.run(topic)

        # 显示结果
        _display_results(result)

    except Exception as e:
        console.print(f"\n[bold red]执行出错: {e}[/bold red]")
        logger.exception("Pipeline执行失败")
        raise click.ClickException(str(e))


@main.command()
@click.argument("topic")
@click.pass_context
def analyze(ctx: click.Context, topic: str) -> None:
    """仅分析论文题目"""
    console.print(f"[bold]分析题目: {topic}[/bold]\n")

    analyzer = TopicAnalyzer()
    result = analyzer.analyze(topic)

    # 显示分析结果
    table = Table(title="题目分析结果")
    table.add_column("属性", style="cyan")
    table.add_column("值", style="green")

    table.add_row("研究主题", result.get("research_subject", "N/A"))
    table.add_row("论文类型", result.get("paper_type", "N/A"))
    table.add_row("难度", result.get("difficulty", "N/A"))
    table.add_row("应用领域", result.get("application_domain", "N/A"))
    table.add_row("关键词", ", ".join(result.get("keywords", [])))
    table.add_row("数学工具", ", ".join(result.get("required_math_tools", [])))
    table.add_row("可视化", ", ".join(result.get("required_visualizations", [])))

    console.print(table)


@main.command()
def list_templates() -> None:
    """列出可用模板"""
    from papercarator.paper_writer.template_manager import TemplateManager

    tm = TemplateManager()
    templates = tm.list_templates()

    table = Table(title="可用论文模板")
    table.add_column("模板名", style="cyan")
    table.add_column("说明", style="green")

    for name in templates:
        info = tm.get_template(name)
        table.add_row(name, info.get("name", "N/A"))

    console.print(table)


@main.command()
@click.option("--output", "-o", default="config.yaml", help="输出文件名")
def init_config(output: str) -> None:
    """生成默认配置文件"""
    config = Config()
    config.to_yaml(output)
    console.print(f"[green]配置文件已保存: {output}[/green]")


# ========== 辅助函数 ==========

def _run_math_modeling(topic: str, plan: dict, matlab_bridge=None) -> dict:
    """执行数学建模"""
    builder = ModelBuilder()
    solver = ModelSolver(matlab_bridge=matlab_bridge)
    validator = ModelValidator()

    model = builder.build(topic, plan)
    solution = solver.solve(model)
    validation = validator.validate(model, solution)

    return {
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
            "checks": validation.checks,
        },
    }


def _run_visualization(topic: str, math_model: dict, plan: dict, output_dir: Path,
                       solidworks_bridge=None) -> list[Path]:
    """执行可视化生成"""
    chart_gen = ChartGenerator()
    model3d_gen = Model3DGenerator(solidworks_bridge=solidworks_bridge)

    all_files = []

    # 生成图表
    if "solution" in math_model:
        chart_files = chart_gen.generate(
            math_model["model"],
            math_model["solution"],
            output_dir / "charts",
        )
        all_files.extend(chart_files)

    # 生成3D模型
    model3d_files = model3d_gen.generate(
        topic,
        math_model.get("model", {}),
        output_dir / "3d_models",
    )
    all_files.extend(model3d_files)

    return all_files


def _run_paper_writer(topic: str, plan: dict, math_model: dict,
                     visualizations: list[Path], output_dir: Path) -> tuple[dict, Path | None]:
    """执行论文写作"""
    generator = LaTeXGenerator()

    sections, pdf_path = generator.generate(
        topic=topic,
        plan=plan,
        math_model=math_model.get("model", {}),
        solution=math_model.get("solution", {}),
        visualizations=visualizations,
        output_dir=output_dir,
    )

    return sections, pdf_path


def _run_github_publisher(topic: str, paper_pdf: Path | None, source_dir: Path) -> str | None:
    """执行GitHub发布"""
    publisher = GitHubPublisher()
    return publisher.publish(topic, paper_pdf, source_dir)


def _display_results(ctx: "PipelineContext") -> None:
    """显示创作结果"""
    console.print("\n" + "=" * 60)
    console.print("[bold green]论文创作完成[/bold green]")
    console.print("=" * 60 + "\n")

    # 结果表格
    table = Table(title="创作结果汇总")
    table.add_column("阶段", style="cyan")
    table.add_column("状态", style="green")
    table.add_column("详情", style="yellow")

    table.add_row(
        "题目分析",
        "完成",
        f"类型: {ctx.plan.get('paper_type', 'N/A')}",
    )

    if ctx.metadata.get("math_completed"):
        model_type = ctx.math_model.get("model", {}).get("model_type", "N/A")
        solution = ctx.math_model.get("solution", {})
        table.add_row(
            "数学建模",
            "完成",
            f"模型: {model_type}, 求解: {'成功' if solution.get('success') else '失败'}",
        )

    if ctx.metadata.get("visualization_completed"):
        table.add_row(
            "可视化",
            "完成",
            f"生成 {len(ctx.visualizations)} 个文件",
        )

    if ctx.metadata.get("paper_completed"):
        pdf_status = "PDF已生成" if ctx.paper_pdf and ctx.paper_pdf.exists() else "LaTeX已生成"
        table.add_row(
            "论文写作",
            "完成",
            pdf_status,
        )

    if ctx.metadata.get("github_completed"):
        table.add_row(
            "GitHub发布",
            "完成",
            ctx.github_url or "N/A",
        )

    console.print(table)

    # 输出路径
    console.print(f"\n[bold]输出目录:[/bold] {ctx.config.system.output_dir}")
    if ctx.paper_pdf and ctx.paper_pdf.exists():
        console.print(f"[bold]PDF文件:[/bold] {ctx.paper_pdf}")
    if ctx.github_url:
        console.print(f"[bold]GitHub仓库:[/bold] {ctx.github_url}")

    console.print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
