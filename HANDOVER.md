# PaperCarator 项目维护文档

## 项目概述

PaperCarator 是一个 AI 驱动的全类型学术论文生成系统。支持 7 种论文类型、16 种数学模型、5 种引用格式、统计分析、文献检索、概念图生成，以及 AI 自主写作 + 一键自动两种模式。

## 当前状态（2026-05-02）

### 核心能力

| 能力 | 说明 |
|------|------|
| 论文类型 | 毕业论文/期刊/会议/综述/实验/案例/数学建模 |
| 数学模型 | 16 种（优化/方程/ODE/PDE/排队/马尔可夫/贝叶斯/统计/网络流/时间序列/博弈/控制/聚类/图论/模糊逻辑/多目标） |
| 引用格式 | GB/T 7714 / APA / IEEE / Chicago / MLA |
| 统计分析 | 描述统计/t检验/相关/回归/ANOVA/卡方 + LaTeX表格输出 |
| 文献检索 | Semantic Scholar + CrossRef 真实文献抓取 |
| 概念图 | 纯 matplotlib 生成，8 种模型类型，无需 GPU |
| 写作模式 | Mode A: AI 自主写 / Mode B: 调外部 LLM 全自动 |
| 质量评分 | 7 维度 0-100 分自动评分 |
| 模板 | 6 种（standard/ieee/acm/cjm/springer_lncs/thesis） |
| 输出格式 | LaTeX + PDF + JSON 摘要 |
| Web UI | Gradio 交互界面 |
| 批量处理 | 多题目批量生成 |

### 两种使用模式

**Mode A（推荐）— AI 自主写作**：
```
Step 1: python scripts/generate_data.py "题目" → 建模+求解+图表+统计分析 → context.json
Step 2: AI 读 context.json 写 6-8 个章节 → sections.json
Step 3: python scripts/assemble_paper.py → PDF
```

**Mode B — 一键自动**：
```
python scripts/run_paper.py "题目" → 调外部 LLM 全自动出 PDF
```

## 文件结构

```
papercarator/
├── SKILL.md                              # Skill 入口（AI 读这个）
├── scripts/
│   ├── run_paper.py                      # Mode B: 一键生成
│   ├── generate_data.py                  # Mode A Step 1: 建模+分析
│   ├── assemble_paper.py                 # Mode A Step 3: 组装PDF
│   ├── quick_check.py                    # 快速质量检查
│   ├── batch_run.py                      # 批量处理
│   ├── sensitivity_analysis.py           # 参数敏感性扫描
│   └── validate_output.py                # 输出产物验证
├── references/
│   └── README.md                         # 模型画像参考表
└── papercarator/
    ├── planner/                          # 题目分析+参数提取
    ├── math_modeling/                    # 16种模型构建+求解
    ├── visualization/                    # 图表+3D+概念图
    ├── paper_writer/                     # LaTeX生成+算法+学术增强+质量评分+LLM写作
    ├── core/                             # Pipeline+配置+容错
    ├── data_importer.py                  # CSV/Excel/JSON导入
    ├── literature_search.py              # 文献检索
    └── statistical_analysis.py           # 统计分析
```

## 技术栈

- Python 3.12 | Pydantic | NumPy | SciPy | SymPy
- Matplotlib | trimesh
- LaTeX (xelatex via MiKTeX) | Jinja2
- Gradio (Web UI) | Click | Rich | loguru
- httpx (API 调用) | Git (版本管理)

## 环境要求

- Python 3.10+
- xelatex (MiKTeX 或 TeX Live)
- WSL 环境自动检测 Windows MiKTeX 路径
- Mode B 需要 HIAPI_API_KEY 或 OPENAI_API_KEY

## 注意事项

1. CLI 入口: `python3.12 -m papercarator.cli`，不是 `python3.12 -m papercarator`
2. Windows 终端已做 gbk 兼容修复
3. MATLAB Engine 未安装（可选，Python 求解器已足够）
4. SolidWorks 桥接未启用
5. 能力边界: 论文初稿生成器，非终稿生成器

---

**最后更新**: 2026-05-02
**当前版本**: 0.4.0
**GitHub**: https://github.com/2456018331lby-dev/papercarator