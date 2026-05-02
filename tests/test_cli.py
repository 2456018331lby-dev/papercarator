"""CLI测试"""

from click.testing import CliRunner
from types import SimpleNamespace

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

    def test_run_command_applies_cli_flags(self, tmp_path, monkeypatch):
        """测试 run 命令会把 CLI 选项写入配置并完成模块注册"""
        runner = CliRunner()
        captured: dict = {}

        class BridgeStub:
            def is_available(self):
                return False

        class FakePipeline:
            def __init__(self, config):
                captured["config"] = config
                captured["pipeline"] = self
                self.registered: list[str] = []
                self.matlab_bridge = BridgeStub()
                self.solidworks_bridge = BridgeStub()

            def register_module(self, name, module):
                self.registered.append(name)

            def run(self, topic):
                captured["topic"] = topic
                return SimpleNamespace(
                    plan={"paper_type": "optimization"},
                    math_model={
                        "model": {"model_type": "optimization"},
                        "solution": {"success": True},
                    },
                    metadata={
                        "math_completed": True,
                        "visualization_completed": True,
                        "paper_completed": True,
                    },
                    visualizations=[],
                    config=captured["config"],
                    paper_pdf=None,
                    github_url=None,
                )

        monkeypatch.setattr("papercarator.cli.Pipeline", FakePipeline)
        monkeypatch.setattr("papercarator.cli._display_results", lambda ctx: None)

        result = runner.invoke(
            main,
            [
                "run",
                "测试题目",
                "--output",
                str(tmp_path),
                "--template",
                "custom",
                "--depth",
                "deep",
                "--no-github",
                "--no-vscode",
                "--use-matlab",
                "--use-solidworks",
                "--matlab-path",
                r"C:\MATLAB\bin\matlab.exe",
                "--sw-visible",
            ],
        )

        assert result.exit_code == 0
        assert captured["topic"] == "测试题目"
        assert captured["config"].planner.analysis_depth == "deep"
        assert captured["config"].paper_writer.template == "custom"
        assert captured["config"].system.output_dir == tmp_path
        assert captured["config"].matlab.enabled is True
        assert captured["config"].matlab.path == r"C:\MATLAB\bin\matlab.exe"
        assert captured["config"].solidworks.enabled is True
        assert captured["config"].solidworks.visible is True
        assert captured["config"].vscode.enabled is False
        assert "planner" in captured["pipeline"].registered
        assert "paper_writer" in captured["pipeline"].registered
        assert "github_publisher" not in captured["pipeline"].registered

    def test_run_command_registers_github_publisher_by_default(self, monkeypatch):
        """测试未传 --no-github 时会注册 GitHub 发布模块"""
        runner = CliRunner()
        registered: list[str] = []

        class FakePipeline:
            def __init__(self, config):
                self.matlab_bridge = None
                self.solidworks_bridge = None

            def register_module(self, name, module):
                registered.append(name)

            def run(self, topic):
                return SimpleNamespace(
                    plan={"paper_type": "optimization"},
                    math_model={"model": {"model_type": "optimization"}, "solution": {"success": True}},
                    metadata={},
                    visualizations=[],
                    config=SimpleNamespace(system=SimpleNamespace(output_dir="output")),
                    paper_pdf=None,
                    github_url=None,
                )

        monkeypatch.setattr("papercarator.cli.Pipeline", FakePipeline)
        monkeypatch.setattr("papercarator.cli.GitHubPublisher", lambda: object())
        monkeypatch.setattr("papercarator.cli._display_results", lambda ctx: None)

        result = runner.invoke(main, ["run", "测试题目", "--no-vscode"])

        assert result.exit_code == 0
        assert "github_publisher" in registered
