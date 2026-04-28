"""Pipeline集成测试"""

from pathlib import Path

import pytest

from papercarator.core.config import Config
from papercarator.core.pipeline import Pipeline, PipelineContext


class TestPipeline:
    """测试Pipeline"""

    def test_pipeline_context(self):
        """测试Pipeline上下文"""
        config = Config()
        ctx = PipelineContext(topic="测试", config=config)

        assert ctx.topic == "测试"
        assert ctx.config == config
        assert ctx.plan == {}

    def test_pipeline_initialization(self):
        """测试Pipeline初始化"""
        config = Config()
        pipeline = Pipeline(config)

        assert pipeline.config == config
        assert pipeline._modules == {}

    def test_register_module(self):
        """测试模块注册"""
        pipeline = Pipeline()
        pipeline.register_module("test", {"name": "test_module"})

        assert "test" in pipeline._modules

    def test_run_with_mock_modules(self, tmp_path):
        """测试带模拟模块的Pipeline运行"""
        config = Config()
        config.system.output_dir = tmp_path
        config.system.temp_dir = tmp_path / "temp"
        config.github_publisher.enabled = False

        pipeline = Pipeline(config)

        # 注册模拟模块
        pipeline.register_module("planner", MockPlanner())
        pipeline.register_module("math_modeling", MockMathModeling())
        pipeline.register_module("visualization", MockVisualization())
        pipeline.register_module("paper_writer", MockPaperWriter())

        result = pipeline.run("测试题目")

        assert result.topic == "测试题目"
        assert result.metadata.get("plan_completed")
        assert result.metadata.get("math_completed")


class MockPlanner:
    """模拟规划模块"""
    def analyze(self, topic: str):
        return {"topic": topic, "paper_type": "modeling"}


class MockMathModeling:
    """模拟数学建模模块"""
    def build_and_solve(self, topic: str, plan: dict, matlab_bridge=None):
        return {
            "model": {"model_type": "equation_system"},
            "solution": {"success": True, "values": {"x": 1}},
        }


class MockVisualization:
    """模拟可视化模块"""
    def generate(self, topic: str, math_model: dict, plan: dict, output_dir: Path, solidworks_bridge=None):
        return []


class MockPaperWriter:
    """模拟论文写作模块"""
    def write(self, topic: str, plan: dict, math_model: dict,
              visualizations: list, output_dir: Path):
        return ({"title": topic}, None)
