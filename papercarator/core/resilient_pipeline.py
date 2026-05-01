"""弹性Pipeline - 带错误恢复的Pipeline包装器。

当某个步骤失败时，记录错误并继续执行后续步骤，
尽可能生成部分输出而非完全失败。
"""

from pathlib import Path
from typing import Any

from loguru import logger

from papercarator.core.pipeline import Pipeline, PipelineContext


class ResilientPipeline:
    """带错误恢复的Pipeline包装器。

    特性：
    - 步骤失败不阻断后续步骤
    - 记录每个步骤的成功/失败状态
    - 生成部分结果（如只有LaTeX没有PDF）
    - 输出详细的执行报告
    """

    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline
        self.step_results: list[dict[str, Any]] = []

    def run(self, topic: str) -> PipelineContext:
        """执行Pipeline，容错处理。"""
        logger.info(f"开始弹性执行 - 题目: {topic}")

        ctx = PipelineContext(topic=topic, config=self.pipeline.config)
        self.pipeline.config.ensure_directories()

        steps = [
            ("planner", self._safe_run_planner),
            ("math_modeling", self._safe_run_math),
            ("visualization", self._safe_run_visualization),
            ("paper_writer", self._safe_run_paper),
        ]

        if self.pipeline.config.github_publisher.enabled and "github_publisher" in self.pipeline._modules:
            steps.append(("github_publisher", self._safe_run_github))

        for step_name, step_func in steps:
            try:
                ctx = step_func(ctx)
                self.step_results.append({
                    "step": step_name,
                    "status": "success",
                })
            except Exception as e:
                logger.error(f"步骤 {step_name} 失败: {e}")
                self.step_results.append({
                    "step": step_name,
                    "status": "failed",
                    "error": str(e),
                })
                # 继续执行后续步骤

        self._print_report()
        return ctx

    def _safe_run_planner(self, ctx: PipelineContext) -> PipelineContext:
        if self.pipeline.config.planner.enabled and "planner" in self.pipeline._modules:
            logger.info("[1/5] 题目分析与规划...")
            ctx = self.pipeline._run_planner(ctx)
        return ctx

    def _safe_run_math(self, ctx: PipelineContext) -> PipelineContext:
        if self.pipeline.config.math_modeling.enabled and "math_modeling" in self.pipeline._modules:
            logger.info("[2/5] 数学建模...")
            ctx = self.pipeline._run_math_modeling(ctx)
        return ctx

    def _safe_run_visualization(self, ctx: PipelineContext) -> PipelineContext:
        if self.pipeline.config.visualization.enabled and "visualization" in self.pipeline._modules:
            logger.info("[3/5] 生成可视化...")
            ctx = self.pipeline._run_visualization(ctx)
        return ctx

    def _safe_run_paper(self, ctx: PipelineContext) -> PipelineContext:
        if self.pipeline.config.paper_writer.enabled and "paper_writer" in self.pipeline._modules:
            logger.info("[4/5] 撰写论文...")
            ctx = self.pipeline._run_paper_writer(ctx)
        return ctx

    def _safe_run_github(self, ctx: PipelineContext) -> PipelineContext:
        if "github_publisher" in self.pipeline._modules:
            logger.info("[5/5] 发布到GitHub...")
            ctx = self.pipeline._run_github_publisher(ctx)
        return ctx

    def _print_report(self) -> None:
        """打印执行报告。"""
        logger.info("=" * 50)
        logger.info("弹性Pipeline执行报告")
        logger.info("=" * 50)
        for result in self.step_results:
            icon = "✓" if result["status"] == "success" else "✗"
            logger.info(f"  {icon} {result['step']}: {result['status']}")
            if result.get("error"):
                logger.info(f"    Error: {result['error']}")

        success_count = sum(1 for r in self.step_results if r["status"] == "success")
        total = len(self.step_results)
        logger.info(f"成功: {success_count}/{total}")
