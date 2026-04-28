# PaperCarator API 文档

## 核心类

### Config

配置管理类，使用Pydantic进行类型验证。

```python
from papercarator.core.config import Config

# 使用默认配置
config = Config()

# 从YAML加载
config = Config.from_yaml("config.yaml")

# 保存到YAML
config.to_yaml("config.yaml")
```

### Pipeline

主流程控制类，协调各模块完成论文创作。

```python
from papercarator.core.config import Config
from papercarator.core.pipeline import Pipeline

config = Config()
pipeline = Pipeline(config)

# 注册模块
pipeline.register_module("planner", planner_instance)
pipeline.register_module("math_modeling", math_modeling_instance)
# ...

# 执行
result = pipeline.run("论文题目")
```

## Planner 模块

### TopicAnalyzer

```python
from papercarator.planner import TopicAnalyzer

analyzer = TopicAnalyzer()
result = analyzer.analyze("基于深度学习的图像分类方法研究")

# 结果包含:
# - topic: 题目
# - paper_type: 论文类型
# - keywords: 关键词列表
# - research_methods: 研究方法
# - required_math_tools: 需要的数学工具
# - required_visualizations: 需要的可视化
```

### TaskPlanner

```python
from papercarator.planner import TaskPlanner

planner = TaskPlanner()
plan = planner.create_plan(analysis_result)

# 结果包含:
# - tasks: 任务列表
# - estimated_sections: 预估章节
# - required_tools: 需要的工具
```

## MathModeling 模块

### ModelBuilder

```python
from papercarator.math_modeling import ModelBuilder

builder = ModelBuilder()
model = builder.build("题目", plan)

# 转换为字典
model_dict = builder.to_dict(model)
```

### ModelSolver

```python
from papercarator.math_modeling import ModelSolver

solver = ModelSolver(timeout=300)
solution = solver.solve(model)

# 结果包含:
# - success: 是否成功
# - values: 解的值
# - message: 状态消息
# - statistics: 统计信息
# - numerical_data: 数值数据
```

### ModelValidator

```python
from papercarator.math_modeling import ModelValidator

validator = ModelValidator(tolerance=1e-6)
result = validator.validate(model, solution)

# 结果包含:
# - is_valid: 是否有效
# - score: 验证得分 (0-1)
# - checks: 详细检查项
# - warnings: 警告信息
# - errors: 错误信息
```

## Visualization 模块

### ChartGenerator

```python
from papercarator.visualization import ChartGenerator

gen = ChartGenerator(dpi=300, figsize=(10, 6))
files = gen.generate(math_model, solution, output_dir)

# 生成自定义图表
gen.generate_paper_figure(
    data={"series1": {"x": [1,2,3], "y": [4,5,6]}},
    title="图表标题",
    output_path=Path("figure.png"),
    fig_type="line",
)
```

### Model3DGenerator

```python
from papercarator.visualization import Model3DGenerator

gen = Model3DGenerator(engine="trimesh")
files = gen.generate(topic, math_model, output_dir)

# 生成自定义网格
import numpy as np
vertices = np.array([[0,0,0], [1,0,0], [0,1,0]])
faces = np.array([[0, 1, 2]])
gen.generate_custom_mesh(vertices, faces, Path("model.stl"))
```

## PaperWriter 模块

### LaTeXGenerator

```python
from papercarator.paper_writer import LaTeXGenerator

generator = LaTeXGenerator(latex_compiler="xelatex")
sections, pdf_path = generator.generate(
    topic="题目",
    plan=plan,
    math_model=math_model,
    solution=solution,
    visualizations=[Path("fig1.png")],
    output_dir=Path("./output"),
)
```

### SectionWriter

```python
from papercarator.paper_writer import SectionWriter

writer = SectionWriter()
sections = writer.write_all_sections(
    topic="题目",
    plan=plan,
    math_model=math_model,
    solution=solution,
)

# 单独生成某章节
abstract = writer._write_abstract(topic, plan, math_model, solution)
```

### TemplateManager

```python
from papercarator.paper_writer import TemplateManager

tm = TemplateManager()

# 列出模板
templates = tm.list_templates()

# 获取模板配置
template = tm.get_template("ieee")

# 获取导言区
preamble = tm.get_latex_preamble("ieee", language="zh")
```

## GitHubPublisher 模块

### GitHubPublisher

```python
from papercarator.github_publisher import GitHubPublisher

publisher = GitHubPublisher(token="your_github_token")
url = publisher.publish(
    topic="题目",
    paper_pdf=Path("paper.pdf"),
    source_dir=Path("./output"),
    owner="username",
    repo_name="repo-name",
    private=False,
)
```

## CLI 命令

### 基本命令

```bash
# 运行完整流程
papercarator run "论文题目"

# 指定输出目录和模板
papercarator run "论文题目" -o ./output -t ieee

# 分析题目
papercarator analyze "论文题目"

# 列出模板
papercarator list-templates

# 生成配置文件
papercarator init-config -o config.yaml
```

### 选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `-c, --config` | 配置文件路径 | 无 |
| `-v, --verbose` | 详细输出 | False |
| `-o, --output` | 输出目录 | ./output |
| `-t, --template` | 论文模板 | custom |
| `--no-github` | 不发布到GitHub | False |
| `--depth` | 分析深度 | standard |
