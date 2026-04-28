# PaperCarator 项目交接文档

## 项目概述

PaperCarator 是一个自动化学术论文生成系统，能够根据用户输入的题目自动完成：
1. 题目分析与任务规划
2. 数学建模与求解
3. 可视化图表生成
4. LaTeX论文撰写与PDF编译

## 当前状态（2026-04-27）

### ✅ 已完成

#### 1. 核心模块
- **Pipeline架构** (`papercarator/core/pipeline.py`)
  - 5步流程：Planner → MathModeling → Visualization → PaperWriter → GitHubPublisher
  - 支持模块注册和上下文传递

- **题目分析器** (`papercarator/planner/analyzer.py`)
  - 基于关键词匹配识别论文类型
  - 支持：optimization, differential, equation_system, theoretical等类型
  - 输出：研究主题、方法、领域、关键词、难度等

- **数学建模模块** (`papercarator/math_modeling/`)
  - `model_builder.py`: 自动构建优化模型、方程组、微分方程
  - `solver.py`: 使用SciPy/SymPy求解，支持线性和非线性优化
  - `validator.py`: 验证求解结果
  - ✅ 已新增 `network_flow`（网络流/最短路径）与 `time_series`（时间序列预测）模型链路
  - ✅ 已新增 `multi_objective`（多目标优化）与 `pde`（偏微分方程）模型链路
  - ✅ 已新增 `queueing`（排队系统）与 `markov_chain`（马尔可夫链）模型链路

- **论文写作模块** (`papercarator/paper_writer/`)
  - `section_writer.py`: ✅ 已改成按模型类型输出章节内容，不再所有题目套同一份优化模板
  - `latex_generator.py`: ✅ Windows 编译调用已收紧，成功编译后会清理陈旧 `compile.log`
  - `template_manager.py`: 管理LaTeX模板

- **可视化模块** (`papercarator/visualization/`)
  - `chart_generator.py`: 生成优化图表、统计图表
  - `model3d_generator.py`: 生成3D模型（使用trimesh）
  - ✅ 已新增网络流图、流量分配图、时间序列预测图
  - ✅ 已新增网络结构 3D 示意、时间序列 3D 曲面
  - ✅ 已新增帕累托前沿图、PDE 热图
  - ✅ 已新增帕累托 3D 曲面、PDE 温度场 3D 曲面
  - ✅ 已新增排队曲线、排队指标图、马尔可夫状态演化图
  - ✅ 已新增排队系统 3D 示意、马尔可夫转移 3D 曲面

- **CLI界面** (`papercarator/cli.py`)
  - 基于Click的命令行界面
  - Rich终端美化
  - ✅ 已修复 Windows `gbk` 终端下 emoji / spinner 导致的崩溃

- **Web界面** (`app.py`)
  - 基于Gradio的交互式界面
  - 支持输入题目、查看进度、下载PDF

### ⚠️ 已知问题

#### 1. 内容模板化仍有改进空间
**位置**: `papercarator/paper_writer/section_writer.py`

**现状**: 已经按模型类型分支写作，但仍是规则驱动文本，深度有限

**改进方向**:
- 扩展更多数学建模题型
- 强化题目到模型的匹配规则
- 增加更贴近真实结果的章节叙事

#### 2. 通用化能力仍不足
**结论**: 目前适合“数学建模论文生成 skill”，不适合宣称“任意题目全自动研究代理”

**原因**:
- 题目理解仍以规则为主
- 模型库规模有限
- 3D 能力偏数学示意而非工业级 CAD
- 缺少文献检索和引用管理

#### 3. MATLAB Engine未集成
**位置**: `papercarator/math_modeling/matlab_bridge.py`

**问题**: MATLAB Engine for Python安装失败

**原因**: 桌面上的`matlab_engine`目录是从别处复制的，不是从实际MATLAB安装目录安装

**MATLAB位置**: `C:\Program Files\MATLAB\R2024b\bin\matlab.exe`

**正确安装方法**:
```bash
cd "C:\Program Files\MATLAB\R2024b\extern\engines\python"
python3.12 setup.py install
```

**注意**: 需要先确认`extern/engines/python`目录存在

## 文件结构

```
papercarator/
├── papercarator/
│   ├── __init__.py
│   ├── cli.py                    # CLI入口
│   ├── core/
│   │   ├── config.py            # Pydantic配置管理
│   │   ├── pipeline.py          # 核心Pipeline
│   │   └── utils.py
│   ├── planner/
│   │   ├── analyzer.py          # 题目分析器
│   │   └── task_planner.py
│   ├── math_modeling/
│   │   ├── __init__.py
│   │   ├── matlab_bridge.py     # MATLAB桥接（未启用）
│   │   ├── model_builder.py     # 模型构建
│   │   ├── solver.py            # 求解器
│   │   └── validator.py         # 验证器
│   ├── paper_writer/
│   │   ├── __init__.py
│   │   ├── section_writer.py    # ✅ 章节生成（已修复）
│   │   ├── latex_generator.py   # LaTeX/PDF生成
│   │   └── template_manager.py
│   ├── visualization/
│   │   ├── chart_generator.py   # 图表生成
│   │   ├── model3d_generator.py # 3D模型
│   │   └── solidworks_bridge.py # SolidWorks桥接（未启用）
│   ├── github_publisher/
│   │   └── publisher.py         # GitHub发布（未启用）
│   └── integrations/
│       └── vscode_bridge.py     # VSCode集成
├── tests/                        # 测试文件
├── examples/
│   └── basic_usage.py           # 使用示例
├── app.py                        # ✅ Gradio Web界面
├── pyproject.toml               # 项目配置
└── README.md
```

## 快速开始

### 1. 安装依赖
```bash
cd C:\Users\24560\Desktop\study\opendemo\papercarator
python3.12 -m pip install -e ".[dev]"
```

### 2. 运行测试
```bash
python3.12 -m pytest tests/ -v
```

当前基线：`73/73` 通过

### 3. 运行示例
```bash
python3.12 examples/basic_usage.py
```

### 4. 启动Web界面
```bash
python3.12 app.py
# 访问 http://localhost:7860
```

### 5. CLI使用
```bash
python3.12 -m papercarator.cli run "基于优化理论的资源配置问题研究"
```

### 6. 真实 Demo
```bash
python3.12 -m papercarator.cli --config configs/skill_claude.yaml run "多服务台排队系统性能分析与等待时间优化研究" --output C:\Users\24560\Desktop\study\paperskilldemo --no-github --no-vscode
```

当前已验证产物：
- `C:\Users\24560\Desktop\study\paperskilldemo\paper\paper.pdf`
- `C:\Users\24560\Desktop\study\paperskilldemo\paper\paper.tex`
- `C:\Users\24560\Desktop\study\paperskilldemo\paper\queue_curve.png`
- `C:\Users\24560\Desktop\study\paperskilldemo\paper\queue_metrics.png`
- `C:\Users\24560\Desktop\study\paperskilldemo\paper\queueing_3d_profile.png`

## 关键代码示例

### 完整Pipeline使用
```python
from papercarator.core.config import Config
from papercarator.core.pipeline import Pipeline
from papercarator.planner import TopicAnalyzer
from papercarator.math_modeling import ModelBuilder, ModelSolver, ModelValidator
from papercarator.paper_writer import LaTeXGenerator, SectionWriter
from papercarator.visualization import ChartGenerator, Model3DGenerator

# 配置
config = Config()
config.system.output_dir = Path("./output")
config.system.temp_dir = Path("./temp")

# 创建Pipeline
pipeline = Pipeline(config)

# 注册模块
pipeline.register_module("planner", TopicAnalyzer())
pipeline.register_module("math_modeling", {
    "builder": ModelBuilder(),
    "solver": ModelSolver(),
    "validator": ModelValidator(),
    "build_and_solve": lambda topic, plan, matlab_bridge=None: {...}
})

# 运行
result = pipeline.run("基于优化理论的资源配置问题研究")
```

## 待办事项（优先级排序）

### P0 - 数学建模专用能力增强
1. [ ] 继续增加更多模型类型（多目标优化、PDE、图论扩展、随机过程）
2. [ ] 扩展题目到模型的匹配规则
3. [ ] 提升结果到章节文本的贴合度

### P1 - 稳定性与维护
4. [ ] 增加 CLI 真实运行回归测试
5. [ ] 增加 PDF/LaTeX 产物级验证
6. [ ] 继续清理 Windows / MiKTeX 环境差异问题

### P2 - 可选集成
7. [ ] 修复 MATLAB Engine 安装
8. [ ] 启用 GitHub 自动发布
9. [ ] 评估 SolidWorks 集成是否保留为可选桥接

### P3 - 向 Direction B 过渡
10. [ ] 文献检索与引用管理
11. [ ] 更强的开放域题目理解
12. [ ] 更明确的工程级 3D/CAD 边界

## Skill 调用资产

当前仓库已补齐：
- `SKILL.md`
- `CLAUDE.md`
- `docs/skill_integration.md`
- `configs/skill_codex.yaml`
- `configs/skill_claude.yaml`

这几份文件的目标是让后续 Codex / Claude Code 调用时，不需要重新猜：
- 适合什么题目
- 该用什么命令
- 会输出什么结果
- 当前不该过度承诺什么

## 技术栈

- **Python**: 3.12
- **配置管理**: Pydantic v2
- **数学计算**: NumPy, SciPy, SymPy
- **可视化**: Matplotlib, trimesh
- **文档生成**: Jinja2, LaTeX (xelatex)
- **Web界面**: Gradio
- **CLI**: Click, Rich
- **日志**: loguru

## 注意事项

1. **CLI入口**: 当前应使用 `python3.12 -m papercarator.cli`，不是 `python3.12 -m papercarator`
2. **终端兼容性**: Windows `gbk` 终端已避开 emoji / spinner，但后续新增终端美化时要继续克制字符集
3. **LaTeX依赖**: 需要安装 TeX Live 或 MiKTeX，并确保 `xelatex` 在 PATH 中
4. **MATLAB可选**: Python求解器已能满足当前内置题型
5. **能力边界**: 当前是数学建模专用 skill，不是任意题目的一体化研究代理

## 联系方式

项目路径: `C:\Users\24560\Desktop\study\opendemo\papercarator`
MATLAB路径: `C:\Program Files\MATLAB\R2024b`

---

**最后更新**: 2026-04-27
**当前版本**: 0.1.0
**完成度**: ~70%（基础功能可用，需优化内容质量和PDF生成）
