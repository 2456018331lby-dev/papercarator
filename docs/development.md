# PaperCarator 开发文档

## 开发环境搭建

### 克隆仓库

```bash
git clone https://github.com/papercarator/papercarator.git
cd papercarator
```

### 安装依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"

# 安装所有依赖（包括Blender支持）
pip install -e ".[all]"
```

### 安装LaTeX

论文编译需要LaTeX环境:

**Windows**:
- 安装 [MiKTeX](https://miktex.org/) 或 [TeX Live](https://tug.org/texlive/)

**macOS**:
```bash
brew install --cask mactex
```

**Linux**:
```bash
sudo apt-get install texlive-full
```

## 项目结构

```
papercarator/
├── papercarator/              # 主包
│   ├── __init__.py
│   ├── cli.py                 # CLI入口
│   ├── core/                  # 核心模块
│   │   ├── config.py          # 配置管理
│   │   ├── pipeline.py        # Pipeline编排
│   │   └── utils.py           # 工具函数
│   ├── planner/               # 题目分析
│   │   ├── analyzer.py
│   │   └── task_planner.py
│   ├── math_modeling/         # 数学建模
│   │   ├── model_builder.py
│   │   ├── solver.py
│   │   └── validator.py
│   ├── visualization/         # 可视化
│   │   ├── chart_generator.py
│   │   └── model3d_generator.py
│   ├── paper_writer/          # 论文写作
│   │   ├── latex_generator.py
│   │   ├── section_writer.py
│   │   └── template_manager.py
│   └── github_publisher/      # GitHub发布
│       └── publisher.py
├── tests/                     # 测试
├── examples/                  # 示例
├── docs/                      # 文档
├── configs/                   # 配置文件
├── pyproject.toml             # 项目配置
└── README.md
```

补充的 skill-facing 资产：

- `SKILL.md`：给 Codex 类调用者的 skill 入口说明
- `CLAUDE.md`：给 Claude Code 的仓库使用说明
- `docs/skill_integration.md`：统一的 skill 调用契约
- `configs/skill_codex.yaml` / `configs/skill_claude.yaml`：副作用更小的调用预设

## 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块测试
pytest tests/test_math_modeling.py

# 生成覆盖率报告
pytest --cov=papercarator --cov-report=html

# 运行并显示详细输出
pytest -v -s
```

## 代码规范

使用以下工具保持代码质量:

```bash
# 格式化代码
black papercarator/ tests/

# 检查代码风格
ruff check papercarator/ tests/

# 类型检查
mypy papercarator/

# 运行pre-commit
pre-commit run --all-files
```

## 添加新功能

### 添加新的模型构建器

1. 在 `math_modeling/model_builder.py` 中添加新方法:

```python
def _build_my_model(self, topic: str, plan: dict[str, Any]) -> MathModel:
    """构建自定义模型"""
    # 实现模型构建逻辑
    return MathModel(
        name="自定义模型",
        description=f"基于'{topic}'的模型",
        # ...
    )
```

2. 在 `__init__` 中注册:

```python
self.model_templates["my_type"] = self._build_my_model
```

3. 在 `_infer_model_type` 中添加类型推断逻辑

4. 添加测试:

```python
def test_build_my_model(self):
    builder = ModelBuilder()
    model = builder.build("测试", {"paper_type": "my_type"})
    assert model.model_type == "my_type"
```

### 添加新的图表类型

1. 在 `visualization/chart_generator.py` 中添加方法:

```python
def _plot_my_chart(self, math_model: dict, solution: dict, output_dir: Path) -> list[Path]:
    """绘制自定义图表"""
    # 实现绘图逻辑
    return [filepath]
```

2. 在 `generate` 方法中调用

### 添加新的论文模板

1. 在 `paper_writer/template_manager.py` 的 `BUILTIN_TEMPLATES` 中添加:

```python
"my_template": {
    "name": "My Template",
    "documentclass": "myclass",
    "options": "",
    "packages": ["package1", "package2"],
}
```

## 调试技巧

### 启用详细日志

```bash
papercarator -v run "论文题目"
```

或在代码中:

```python
from loguru import logger
logger.add("debug.log", level="DEBUG")
```

### 单独测试模块

```python
from papercarator.planner import TopicAnalyzer

analyzer = TopicAnalyzer()
result = analyzer.analyze("测试题目")
print(result)
```

### 检查LaTeX编译日志

编译日志保存在输出目录的 `compile.log` 文件中。

## 发布流程

1. 更新版本号 (`papercarator/__init__.py` 和 `pyproject.toml`)
2. 更新 CHANGELOG
3. 运行测试确保全部通过
4. 构建包:

```bash
python -m build
```

5. 发布到PyPI:

```bash
python -m twine upload dist/*
```

## 贡献指南

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -am 'Add xxx'`)
4. 推送分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

### 提交规范

- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `test:` 测试相关
- `refactor:` 重构
- `style:` 代码格式
- `chore:` 构建/工具
