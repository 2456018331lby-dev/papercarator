"""核心Pipeline - 协调各模块完成论文创作全流程"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from loguru import logger

from papercarator.core.config import Config
from papercarator.integrations.vscode_bridge import VSCodeBridge
from papercarator.math_modeling.matlab_bridge import MATLABBridge
from papercarator.visualization.solidworks_bridge import SolidWorksBridge


@dataclass
class PipelineContext:
    """Pipeline执行上下文 - 在各模块间传递数据"""
    topic: str
    config: Config
    # 各阶段输出
    plan: dict[str, Any] = field(default_factory=dict)
    math_model: dict[str, Any] = field(default_factory=dict)
    visualizations: list[Path] = field(default_factory=list)
    paper_content: dict[str, Any] = field(default_factory=dict)
    paper_pdf: Path | None = None
    github_url: str | None = None
    # 元数据
    metadata: dict[str, Any] = field(default_factory=dict)


class Pipeline:
    """论文创作Pipeline

    协调以下模块完成全流程：
    1. Planner - 题目分析与任务规划
    2. MathModeling - 数学建模
    3. Visualization - 3D可视化
    4. PaperWriter - 论文写作
    5. GitHubPublisher - GitHub发布
    """

    def __init__(self, config: Config | None = None):
        self.config = config or Config()
        self._modules: dict[str, Any] = {}

        # 初始化外部工具桥接器
        self.matlab_bridge: MATLABBridge | None = None
        self.solidworks_bridge: SolidWorksBridge | None = None
        self.vscode_bridge: VSCodeBridge | None = None
        self._init_bridges()

    def _init_bridges(self) -> None:
        """初始化外部工具桥接器"""
        # MATLAB
        if self.config.matlab.enabled:
            try:
                self.matlab_bridge = MATLABBridge(matlab_path=self.config.matlab.path)
                if self.matlab_bridge.is_available():
                    logger.info("MATLAB桥接器已启用")
                else:
                    logger.warning("MATLAB不可用，将使用Python求解器")
            except Exception as e:
                logger.warning(f"MATLAB桥接器初始化失败: {e}")

        # SolidWorks
        if self.config.solidworks.enabled:
            try:
                self.solidworks_bridge = SolidWorksBridge(visible=self.config.solidworks.visible)
                if self.solidworks_bridge.is_available():
                    logger.info("SolidWorks桥接器已启用")
                else:
                    logger.warning("SolidWorks不可用，将使用Python 3D引擎")
            except Exception as e:
                logger.warning(f"SolidWorks桥接器初始化失败: {e}")

        # VS Code
        if self.config.vscode.enabled:
            try:
                self.vscode_bridge = VSCodeBridge(self.config.vscode)
                if self.vscode_bridge.is_available():
                    logger.info("VS Code桥接器已启用")
                else:
                    logger.warning("VS Code不可用")
            except Exception as e:
                logger.warning(f"VS Code桥接器初始化失败: {e}")

    def register_module(self, name: str, module: Any) -> None:
        """注册处理模块"""
        self._modules[name] = module
        logger.info(f"已注册模块: {name}")

    def run(self, topic: str) -> PipelineContext:
        """执行完整Pipeline"""
        logger.info(f"开始论文创作流程 - 题目: {topic}")
        self.config.ensure_directories()

        ctx = PipelineContext(topic=topic, config=self.config)

        # Step 1: 题目分析与规划
        if self.config.planner.enabled and "planner" in self._modules:
            logger.info("[1/5] 题目分析与规划...")
            ctx = self._run_planner(ctx)

        # Step 2: 数学建模
        if self.config.math_modeling.enabled and "math_modeling" in self._modules:
            logger.info("[2/5] 数学建模...")
            ctx = self._run_math_modeling(ctx)

        # Step 3: 3D可视化
        if self.config.visualization.enabled and "visualization" in self._modules:
            logger.info("[3/5] 生成可视化...")
            ctx = self._run_visualization(ctx)

        # Step 4: 论文写作
        if self.config.paper_writer.enabled and "paper_writer" in self._modules:
            logger.info("[4/5] 撰写论文...")
            ctx = self._run_paper_writer(ctx)

        # Step 5: GitHub发布
        if self.config.github_publisher.enabled and "github_publisher" in self._modules:
            logger.info("[5/5] 发布到GitHub...")
            ctx = self._run_github_publisher(ctx)

        logger.info("论文创作流程完成!")
        return ctx

    def _run_planner(self, ctx: PipelineContext) -> PipelineContext:
        """执行题目分析"""
        module = self._modules["planner"]
        ctx.plan = module.analyze(ctx.topic)
        ctx.metadata["plan_completed"] = True
        return ctx

    def _run_math_modeling(self, ctx: PipelineContext) -> PipelineContext:
        """执行数学建模"""
        module = self._modules["math_modeling"]
        # 支持两种注册方式：直接对象或包含build_and_solve函数字典
        if isinstance(module, dict) and "build_and_solve" in module:
            ctx.math_model = module["build_and_solve"](
                topic=ctx.topic,
                plan=ctx.plan,
                matlab_bridge=self.matlab_bridge,
            )
        else:
            ctx.math_model = module.build_and_solve(
                topic=ctx.topic,
                plan=ctx.plan,
                matlab_bridge=self.matlab_bridge,
            )
        ctx.metadata["math_completed"] = True
        return ctx

    def _run_visualization(self, ctx: PipelineContext) -> PipelineContext:
        """执行可视化生成"""
        module = self._modules["visualization"]
        if isinstance(module, dict) and "generate" in module:
            ctx.visualizations = module["generate"](
                topic=ctx.topic,
                math_model=ctx.math_model,
                plan=ctx.plan,
                output_dir=self.config.system.output_dir / "visualizations",
                solidworks_bridge=self.solidworks_bridge,
            )
        else:
            ctx.visualizations = module.generate(
                topic=ctx.topic,
                math_model=ctx.math_model,
                plan=ctx.plan,
                output_dir=self.config.system.output_dir / "visualizations",
                solidworks_bridge=self.solidworks_bridge,
            )
        ctx.metadata["visualization_completed"] = True
        return ctx

    def _run_paper_writer(self, ctx: PipelineContext) -> PipelineContext:
        """执行论文写作"""
        module = self._modules["paper_writer"]
        if isinstance(module, dict) and "write" in module:
            ctx.paper_content, ctx.paper_pdf = module["write"](
                topic=ctx.topic,
                plan=ctx.plan,
                math_model=ctx.math_model,
                visualizations=ctx.visualizations,
                output_dir=self.config.system.output_dir / "paper",
            )
        else:
            ctx.paper_content, ctx.paper_pdf = module.write(
                topic=ctx.topic,
                plan=ctx.plan,
                math_model=ctx.math_model,
                visualizations=ctx.visualizations,
                output_dir=self.config.system.output_dir / "paper",
            )
        ctx.metadata["paper_completed"] = True

        # 在VS Code中打开生成的论文
        if self.vscode_bridge and self.vscode_bridge.is_available():
            tex_path = self.config.system.output_dir / "paper" / "paper.tex"
            self.vscode_bridge.open_paper_workspace(
                tex_path=tex_path,
                pdf_path=ctx.paper_pdf,
                output_dir=self.config.system.output_dir,
            )

        return ctx

    def _run_github_publisher(self, ctx: PipelineContext) -> PipelineContext:
        """执行GitHub发布"""
        module = self._modules["github_publisher"]
        if isinstance(module, dict) and "publish" in module:
            ctx.github_url = module["publish"](
                topic=ctx.topic,
                paper_pdf=ctx.paper_pdf,
                source_dir=self.config.system.output_dir,
            )
        else:
            ctx.github_url = module.publish(
                topic=ctx.topic,
                paper_pdf=ctx.paper_pdf,
                source_dir=self.config.system.output_dir,
            )
        ctx.metadata["github_completed"] = True
        return ctx
