# PaperCarator - 数学建模论文一体化 Skill

PaperCarator 当前更准确的定位是：

一个供上层 AI 使用的、面向**数学建模类题目**的端到端 skill。

它已经能够把题目分析、基础数学建模、二维/三维可视化、LaTeX 论文生成串成一条可验证链路。
它不是“任意开放域题目都能全自动完成研究与写作”的通用研究代理。

## 当前能力

- **题目分析**：识别关键词、研究方法、应用领域和适合的建模类型
- **数学建模**：当前内置支持
  - 方程组
  - 优化问题
  - 多目标优化
  - 微分方程
  - 偏微分方程（热方程风格）
  - 排队系统
  - 马尔可夫链
  - 统计回归
  - 网络流 / 最短路径
  - 时间序列预测
  - 博弈论 / 纳什均衡
  - 控制理论 / PID 稳定性
  - 聚类分析 / K-means
- **结果求解与验证**：自动调用 SymPy / SciPy 完成求解并输出结果摘要
- **可视化生成**：自动生成二维图表和数学型三维示意
- **论文输出**：自动生成摘要、方法、实验、结果、结论，并编译 LaTeX/PDF
- **CLI / Web 演示**：支持命令行和 Gradio 页面验证完整流程

## 当前边界

下面这些能力，当前版本**还不能诚实宣称已经做到**：

- 不能保证“随便一个题目”都能自动建模并写出可信论文
- 不能替代真实文献检索、学术综述和开放域研究设计
- 不能替代工业级 CAD / Solid modeling / 任意复杂 3D 建模
- 不能在没有扩展模型库的前提下覆盖高复杂度跨学科题目

换句话说：它现在更适合做“数学建模自动化骨架 skill”，而不是“通用科研全自动体”。

## 技术栈

- **核心语言**: Python 3.10+
- **数学建模**: SymPy, NumPy, SciPy, Pyomo
- **3D建模**: Blender Python API, trimesh, matplotlib-3d
- **论文生成**: LaTeX, Jinja2, pylatex
- **配置管理**: Pydantic
- **CLI**: Click / Typer

## 快速开始

```bash
# 安装依赖
python3.12 -m pip install -e ".[dev]"

# 运行示例脚本
python3.12 examples/basic_usage.py

# 运行 CLI
python3.12 -m papercarator.cli run "基于优化理论的资源配置问题研究"

# 查看帮助
python3.12 -m papercarator.cli --help
```

说明：

- 当前推荐入口是 `python3.12 -m papercarator.cli`
- `python3.12 -m papercarator` 目前不是可执行入口
- Windows 终端下已做过 `gbk` 兼容修复，避免 `rich` 的 emoji / spinner 直接崩溃

## 已验证状态

- 最新全量测试已通过
- `examples/basic_usage.py` 可跑通
- `python3.12 -m papercarator.cli run ...` 可在 Windows 终端跑通
- PDF 可生成
- 论文写作模块已改为**按模型类型生成内容**，不再所有题目都套同一份优化叙事
- 当前测试基线：`93/93` 通过
- 已完成真实 demo 输出：
  - 输出目录：`C:\Users\24560\Desktop\study\paperskilldemo`
  - 示例题目：`多服务台排队系统性能分析与等待时间优化研究`
  - 已生成：PDF、LaTeX、队列演化图、排队指标图、3D 排队系统示意

## Skill Assets

For downstream agent invocation, the repo now includes:

- [SKILL.md](/C:/Users/24560/Desktop/study/opendemo/papercarator/SKILL.md)
- [CLAUDE.md](/C:/Users/24560/Desktop/study/opendemo/papercarator/CLAUDE.md)
- [docs/skill_integration.md](/C:/Users/24560/Desktop/study/opendemo/papercarator/docs/skill_integration.md)
- [configs/skill_codex.yaml](/C:/Users/24560/Desktop/study/opendemo/papercarator/configs/skill_codex.yaml)
- [configs/skill_claude.yaml](/C:/Users/24560/Desktop/study/opendemo/papercarator/configs/skill_claude.yaml)

Recommended agent flow:

1. Use `python3.12 -m papercarator.cli analyze "<topic>"` when topic fit is uncertain.
2. Run `python3.12 -m papercarator.cli run "<topic>" --output <target_dir> --no-github --no-vscode`.
3. Verify `paper.tex`, `paper.pdf`, charts, and any expected 3D visualization.
4. If the topic is review/open-domain/citation-heavy, label the output as a modeling approximation instead of publication-ready research.

## 后续方向

### A. 数学建模专用能力继续做深

- 增加更多模型类型
- 扩展题目到模型的路由规则
- 提高结果到章节内容的贴合度
- 明确二维图表与三维示意的输出规范

### B. 更广泛题目类型扩展

- 更强的开放域题目理解
- 文献检索与引用管理
- 更多专业建模器与专业求解器
- 更明确的工程 3D / CAD 集成边界

## 项目结构

```
papercarator/
├── papercarator/          # 主包
│   ├── planner/           # 题目分析与规划
│   ├── math_modeling/     # 数学建模
│   ├── visualization/     # 可视化与3D建模
│   ├── paper_writer/      # 论文写作
│   └── github_publisher/  # GitHub发布
├── configs/               # 配置文件
├── tests/                 # 测试
├── docs/                  # 文档
└── examples/              # 示例
```

## 许可证

MIT License
