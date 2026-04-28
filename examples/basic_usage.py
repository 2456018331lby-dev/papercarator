"""基本使用示例 - 演示PaperCarator的核心功能"""

from papercarator.core.config import Config
from papercarator.core.pipeline import Pipeline
from papercarator.github_publisher import GitHubPublisher
from papercarator.math_modeling import ModelBuilder, ModelSolver, ModelValidator
from papercarator.paper_writer import LaTeXGenerator, SectionWriter, TemplateManager
from papercarator.planner import TaskPlanner, TopicAnalyzer
from papercarator.visualization import ChartGenerator, Model3DGenerator


def example_1_analyze_topic():
    """示例1: 分析论文题目"""
    print("=" * 60)
    print("示例1: 题目分析")
    print("=" * 60)

    analyzer = TopicAnalyzer()
    topic = "基于深度学习的图像分类方法研究"

    result = analyzer.analyze(topic)

    print(f"题目: {result['topic']}")
    print(f"类型: {result['paper_type']}")
    print(f"难度: {result['difficulty']}")
    print(f"关键词: {', '.join(result['keywords'])}")
    print(f"数学工具: {', '.join(result['required_math_tools'])}")
    print(f"可视化: {', '.join(result['required_visualizations'])}")
    print()


def example_2_math_modeling():
    """示例2: 数学建模"""
    print("=" * 60)
    print("示例2: 数学建模")
    print("=" * 60)

    builder = ModelBuilder()
    solver = ModelSolver()
    validator = ModelValidator()

    topic = "优化问题研究"
    plan = {"paper_type": "optimization"}

    # 构建模型
    model = builder.build(topic, plan)
    print(f"模型: {model.name}")
    print(f"类型: {model.model_type}")
    print(f"方程: {[str(eq) for eq in model.equations]}")

    # 求解
    solution = solver.solve(model)
    print(f"\n求解: {'成功' if solution.success else '失败'}")
    print(f"结果: {solution.values}")

    # 验证
    validation = validator.validate(model, solution)
    print(f"验证得分: {validation.score:.2f}")
    print()


def example_3_generate_paper():
    """示例3: 生成论文"""
    print("=" * 60)
    print("示例3: 论文生成")
    print("=" * 60)

    # 1. 分析题目
    analyzer = TopicAnalyzer()
    topic = "基于优化理论的资源配置问题研究"
    plan = analyzer.analyze(topic)

    # 2. 数学建模
    builder = ModelBuilder()
    solver = ModelSolver()
    model = builder.build(topic, plan)
    solution = solver.solve(model)

    math_model_data = {
        "model": builder.to_dict(model),
        "solution": {
            "success": solution.success,
            "values": solution.values,
            "message": solution.message,
            "statistics": solution.statistics,
            "numerical_data": solution.numerical_data,
        },
    }

    # 3. 生成可视化
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        viz_dir = Path(tmpdir)

        chart_gen = ChartGenerator()
        viz_files = chart_gen.generate(
            math_model_data["model"],
            math_model_data["solution"],
            viz_dir / "charts",
        )
        print(f"生成图表: {len(viz_files)} 个")

        # 4. 生成论文
        generator = LaTeXGenerator()
        sections, pdf_path = generator.generate(
            topic=topic,
            plan=plan,
            math_model=math_model_data["model"],
            solution=math_model_data["solution"],
            visualizations=viz_files,
            output_dir=viz_dir / "paper",
        )

        print(f"论文章节: {len(sections)} 个")
        print(f"PDF路径: {pdf_path}")
        print()


def example_4_full_pipeline():
    """示例4: 完整Pipeline"""
    print("=" * 60)
    print("示例4: 完整Pipeline")
    print("=" * 60)

    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        config = Config()
        config.system.output_dir = Path(tmpdir) / "output"
        config.system.temp_dir = Path(tmpdir) / "temp"
        config.github_publisher.enabled = False

        pipeline = Pipeline(config)

        # 注册模块
        pipeline.register_module("planner", TopicAnalyzer())
        pipeline.register_module("math_modeling", {
            "builder": ModelBuilder(),
            "solver": ModelSolver(),
            "validator": ModelValidator(),
            "build_and_solve": lambda topic, plan, matlab_bridge=None: _math_modeling_wrapper(topic, plan),
        })
        pipeline.register_module("visualization", {
            "chart": ChartGenerator(),
            "model3d": Model3DGenerator(),
            "generate": lambda topic, math_model, plan, output_dir, solidworks_bridge=None: _visualization_wrapper(
                topic, math_model, plan, output_dir
            ),
        })
        pipeline.register_module("paper_writer", {
            "generator": LaTeXGenerator(),
            "write": lambda topic, plan, math_model, visualizations, output_dir: _paper_writer_wrapper(
                topic, plan, math_model, visualizations, output_dir
            ),
        })

        result = pipeline.run("基于优化理论的资源配置问题研究")

        print(f"题目: {result.topic}")
        print(f"计划完成: {result.metadata.get('plan_completed')}")
        print(f"数学完成: {result.metadata.get('math_completed')}")
        print(f"可视化完成: {result.metadata.get('visualization_completed')}")
        print(f"论文完成: {result.metadata.get('paper_completed')}")
        print()


def _math_modeling_wrapper(topic: str, plan: dict):
    """数学建模包装函数"""
    builder = ModelBuilder()
    solver = ModelSolver()
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
        },
    }


def _visualization_wrapper(topic: str, math_model: dict, plan: dict, output_dir: "Path"):
    """可视化包装函数"""
    chart_gen = ChartGenerator()
    model3d_gen = Model3DGenerator()

    files = []
    if "solution" in math_model:
        files.extend(chart_gen.generate(
            math_model["model"],
            math_model["solution"],
            output_dir / "charts",
        ))
    files.extend(model3d_gen.generate(
        topic,
        math_model.get("model", {}),
        output_dir / "3d_models",
    ))
    return files


def _paper_writer_wrapper(topic: str, plan: dict, math_model: dict,
                         visualizations: list, output_dir: "Path"):
    """论文写作包装函数"""
    generator = LaTeXGenerator()
    return generator.generate(
        topic=topic,
        plan=plan,
        math_model=math_model.get("model", {}),
        solution=math_model.get("solution", {}),
        visualizations=visualizations,
        output_dir=output_dir,
    )


if __name__ == "__main__":
    example_1_analyze_topic()
    example_2_math_modeling()
    example_3_generate_paper()
    example_4_full_pipeline()
