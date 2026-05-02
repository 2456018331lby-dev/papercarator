"""配置管理模块 - 使用Pydantic进行类型安全的配置管理"""

from pathlib import Path
from typing import Any, Optional
try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import yaml
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class SystemConfig(BaseModel):
    """系统基础配置"""
    name: str = "PaperCarator"
    version: str = "0.2.0"
    log_level: str = "INFO"
    output_dir: Path = Path("./output")
    temp_dir: Path = Path("./temp")

    @field_validator("output_dir", "temp_dir", mode="before")
    @classmethod
    def _resolve_path(cls, v: Any) -> Path:
        return Path(v)


class PlannerConfig(BaseModel):
    """题目分析模块配置"""
    enabled: bool = True
    analysis_depth: Literal["basic", "standard", "deep"] = "standard"
    max_iterations: int = 3
    output_format: str = "json"


class SolverConfig(BaseModel):
    """求解器配置"""
    default: Literal["scipy", "sympy", "pyomo", "cvxpy", "matlab"] = "scipy"
    timeout: int = 300


class MATLABConfig(BaseModel):
    """MATLAB桥接配置"""
    enabled: bool = True
    path: str = r"C:\Program Files\MATLAB\R2024b\bin\matlab.exe"
    use_engine: bool = True
    timeout: int = 300


class SolidWorksConfig(BaseModel):
    """SolidWorks桥接配置"""
    enabled: bool = True
    visible: bool = False
    output_formats: list[str] = Field(default_factory=lambda: ["sldprt", "step", "stl", "png"])


class VSCodeConfig(BaseModel):
    """VS Code集成配置"""
    enabled: bool = True
    path: str = r"C:\Users\24560\AppData\Local\Programs\Microsoft VS Code\code.exe"
    auto_open_tex: bool = True
    auto_open_pdf: bool = True


class ValidationConfig(BaseModel):
    """模型验证配置"""
    enabled: bool = True
    tolerance: float = 1e-6


class MathVisualizationConfig(BaseModel):
    """数学可视化配置"""
    enabled: bool = True
    format: str = "png"
    dpi: int = 300


class MathModelingConfig(BaseModel):
    """数学建模模块配置"""
    enabled: bool = True
    solver: SolverConfig = Field(default_factory=SolverConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)
    visualization: MathVisualizationConfig = Field(default_factory=MathVisualizationConfig)


class RenderConfig(BaseModel):
    """渲染配置"""
    width: int = 1920
    height: int = 1080
    samples: int = 128


class VisualizationConfig(BaseModel):
    """3D可视化模块配置"""
    enabled: bool = True
    engine: Literal["blender", "trimesh", "matplotlib", "solidworks"] = "trimesh"
    render: RenderConfig = Field(default_factory=RenderConfig)
    output_format: str = "png"


class PaperWriterConfig(BaseModel):
    """论文写作模块配置"""
    enabled: bool = True
    template: str = "ieee"
    templates_dir: Path = Path("./papercarator/paper_writer/templates")
    latex_compiler: str = "xelatex"
    compile_iterations: int = 3
    auto_abstract: bool = True
    auto_keywords: bool = True
    language: str = "zh"

    @field_validator("templates_dir", mode="before")
    @classmethod
    def _resolve_path(cls, v: Any) -> Path:
        return Path(v)


class RepoConfig(BaseModel):
    """仓库配置"""
    owner: str = ""
    name: str = ""
    private: bool = False


class PublishConfig(BaseModel):
    """发布配置"""
    create_release: bool = True
    include_pdf: bool = True
    include_source: bool = True


class GitHubPublisherConfig(BaseModel):
    """GitHub发布模块配置"""
    enabled: bool = True
    repo: RepoConfig = Field(default_factory=RepoConfig)
    publish: PublishConfig = Field(default_factory=PublishConfig)
    auto_readme: bool = True


class LLMConfig(BaseModel):
    """LLM配置"""
    provider: Literal["openai", "anthropic", "local"] = "anthropic"
    model: str = "claude-3-sonnet-20240229"
    temperature: float = 0.3
    max_tokens: int = 4096
    api_key: str = ""


class PaperStructureConfig(BaseModel):
    """论文结构配置"""
    sections: list[str] = Field(default_factory=lambda: [
        "abstract",
        "introduction",
        "related_work",
        "methodology",
        "experiments",
        "results",
        "conclusion",
        "references",
    ])
    min_words_per_section: int = 500
    max_words_per_section: int = 2000


class Config(BaseSettings):
    """全局配置类"""
    model_config = SettingsConfigDict(
        env_prefix="PAPERCARATOR_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    system: SystemConfig = Field(default_factory=SystemConfig)
    planner: PlannerConfig = Field(default_factory=PlannerConfig)
    math_modeling: MathModelingConfig = Field(default_factory=MathModelingConfig)
    visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
    paper_writer: PaperWriterConfig = Field(default_factory=PaperWriterConfig)
    github_publisher: GitHubPublisherConfig = Field(default_factory=GitHubPublisherConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    paper_structure: PaperStructureConfig = Field(default_factory=PaperStructureConfig)
    matlab: MATLABConfig = Field(default_factory=MATLABConfig)
    solidworks: SolidWorksConfig = Field(default_factory=SolidWorksConfig)
    vscode: VSCodeConfig = Field(default_factory=VSCodeConfig)

    @classmethod
    def from_yaml(cls, path: Path | str) -> "Config":
        """从YAML文件加载配置"""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"配置文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls.model_validate(data)

    def to_yaml(self, path: Path | str) -> None:
        """保存配置到YAML文件"""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(
                self.model_dump(mode="json"),
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

    def ensure_directories(self) -> None:
        """确保所有必要的目录存在"""
        self.system.output_dir.mkdir(parents=True, exist_ok=True)
        self.system.temp_dir.mkdir(parents=True, exist_ok=True)
        self.paper_writer.templates_dir.mkdir(parents=True, exist_ok=True)
