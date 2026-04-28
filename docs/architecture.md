# PaperCarator 架构文档

## 系统架构

PaperCarator 采用模块化Pipeline架构，将论文创作流程分解为多个独立模块，每个模块负责特定的任务。

```
┌─────────────────────────────────────────────────────────────┐
│                      PaperCarator                            │
│                    (Pipeline Orchestrator)                   │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Planner    │    │ MathModeling │    │Visualization │
│  (题目分析)   │    │  (数学建模)   │    │  (可视化)    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                   ┌──────────────┐
                   │ PaperWriter  │
                   │  (论文写作)   │
                   └──────────────┘
                              │
                              ▼
                   ┌──────────────┐
                   │GitHubPublisher│
                   │ (GitHub发布) │
                   └──────────────┘
```

## 模块说明

### 1. Planner (题目分析与规划)

**职责**: 解析论文题目，提取关键信息，生成执行计划

**核心组件**:
- `TopicAnalyzer`: 分析题目，提取关键词、研究方法、应用领域等
- `TaskPlanner`: 根据分析结果生成任务执行计划

**输出**:
- 论文类型 (modeling/optimization/theoretical/review)
- 难度评估
- 建议的数学工具
- 需要的可视化类型
- 任务执行计划

### 2. MathModeling (数学建模)

**职责**: 根据题目自动构建、求解和验证数学模型

**核心组件**:
- `ModelBuilder`: 构建数学模型（方程组、优化、微分方程、统计）
- `ModelSolver`: 求解模型（解析解、数值解）
- `ModelValidator`: 验证模型正确性和解的合理性

**支持的模型类型**:
- 线性/非线性方程组
- 优化问题（无约束/有约束）
- 常微分方程
- 统计回归模型

### 3. Visualization (可视化)

**职责**: 生成数据图表和3D模型

**核心组件**:
- `ChartGenerator`: 生成2D图表（折线图、柱状图、散点图、等高线图等）
- `Model3DGenerator`: 生成3D模型和可视化

**支持的图表类型**:
- 方程组解的可视化
- 优化问题的等高线图
- 微分方程的相空间图
- 回归分析的散点图和残差图
- 3D数学曲面
- 机械结构模型
- 流场可视化
- 温度场可视化

### 4. PaperWriter (论文写作)

**职责**: 生成完整的学术论文

**核心组件**:
- `TemplateManager`: 管理LaTeX模板（IEEE/ACM/Springer/Custom）
- `SectionWriter`: 生成各章节内容
- `LaTeXGenerator`: 生成完整LaTeX文档并编译为PDF

**支持的模板**:
- IEEE Conference
- ACM Conference
- Springer LNCS
- Custom (默认，支持中文)

### 5. GitHubPublisher (GitHub发布)

**职责**: 自动发布论文到GitHub

**核心功能**:
- 创建GitHub仓库
- 推送论文源码和PDF
- 生成README.md
- 创建Release并上传PDF

## 数据流

```
输入题目
    │
    ▼
┌─────────────┐
│   Planner   │ ──→ 分析结果 (JSON)
└─────────────┘
    │
    ▼
┌─────────────┐
│MathModeling │ ──→ 模型 + 解 + 验证结果
└─────────────┘
    │
    ▼
┌─────────────┐
│Visualization│ ──→ 图表文件 (PNG) + 3D模型 (STL/OBJ)
└─────────────┘
    │
    ▼
┌─────────────┐
│ PaperWriter │ ──→ LaTeX源文件 + PDF论文
└─────────────┘
    │
    ▼
┌─────────────┐
│GitHubPublisher│ ──→ GitHub仓库URL
└─────────────┘
```

## 扩展性设计

### 添加新的模型类型

在 `ModelBuilder` 中注册新的构建方法:

```python
def _build_new_type(self, topic, plan):
    # 实现新模型构建逻辑
    return MathModel(...)

# 在 __init__ 中注册
self.model_templates["new_type"] = self._build_new_type
```

### 添加新的图表类型

在 `ChartGenerator` 中添加新的绘图方法:

```python
def _plot_new_type(self, math_model, solution, output_dir):
    # 实现新图表绘制逻辑
    return [filepath]
```

### 添加新的论文模板

在 `TemplateManager.BUILTIN_TEMPLATES` 中添加:

```python
"new_template": {
    "name": "New Template",
    "documentclass": "newclass",
    "options": "",
    "packages": ["package1", "package2"],
}
```

## 配置系统

使用Pydantic进行类型安全的配置管理，支持:
- YAML配置文件
- 环境变量覆盖
- 默认值

配置层次:
1. 代码默认值
2. 配置文件
3. 环境变量
4. 命令行参数
