"""配置模块测试"""

from pathlib import Path

import pytest

from papercarator.core.config import Config


class TestConfig:
    """测试配置类"""

    def test_default_config(self):
        """测试默认配置"""
        config = Config()

        assert config.system.name == "PaperCarator"
        assert config.planner.enabled is True
        assert config.math_modeling.enabled is True

    def test_yaml_roundtrip(self, tmp_path):
        """测试YAML序列化/反序列化"""
        config = Config()
        config.system.log_level = "DEBUG"

        yaml_path = tmp_path / "test_config.yaml"
        config.to_yaml(yaml_path)

        loaded = Config.from_yaml(yaml_path)
        assert loaded.system.log_level == "DEBUG"

    def test_ensure_directories(self, tmp_path):
        """测试目录创建"""
        config = Config()
        config.system.output_dir = tmp_path / "output"
        config.system.temp_dir = tmp_path / "temp"

        config.ensure_directories()

        assert config.system.output_dir.exists()
        assert config.system.temp_dir.exists()
