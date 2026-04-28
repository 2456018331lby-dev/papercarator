"""CLI测试"""

from click.testing import CliRunner

from papercarator.cli import main


class TestCLI:
    """测试命令行接口"""

    def test_main_help(self):
        """测试主命令帮助"""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "PaperCarator" in result.output

    def test_analyze_command(self):
        """测试分析命令"""
        runner = CliRunner()
        result = runner.invoke(main, ["analyze", "测试题目"])

        assert result.exit_code == 0
        assert "分析结果" in result.output or "题目分析" in result.output

    def test_list_templates(self):
        """测试列出模板命令"""
        runner = CliRunner()
        result = runner.invoke(main, ["list-templates"])

        assert result.exit_code == 0
        assert "ieee" in result.output.lower()

    def test_init_config(self, tmp_path):
        """测试生成配置命令"""
        runner = CliRunner()
        config_path = tmp_path / "config.yaml"

        result = runner.invoke(main, ["init-config", "--output", str(config_path)])

        assert result.exit_code == 0
        assert config_path.exists()
