# PaperCarator — AI 学术论文生成 Skill

一站式学术论文生成系统。支持 7 种论文类型、16 种数学模型、统计分析、文献检索、AI 自主写作。从题目到 PDF，两种模式任选。

## 快速开始

```bash
cd <project-dir>
pip install -e ".[dev]"

# Mode A: AI 自主写作（推荐）
python3 scripts/generate_data.py "基于排队论的医院门诊流程优化研究" --output ./output/my_paper
# → 读 context.json → AI 写章节 → 保存 sections.json
python3 scripts/assemble_paper.py --context context.json --sections sections.json

# Mode B: 一键自动
python3 scripts/run_paper.py "基于贝叶斯推断的药物疗效评估研究" --output ./output/auto_paper
```

## 核心能力

| 功能 | 说明 |
|------|------|
| 论文类型 | 毕业论文 / 期刊 / 会议 / 综述 / 实验 / 案例 / 数学建模 |
| 数学模型 | 16 种（优化、方程组、ODE/PDE、排队、马尔可夫、贝叶斯、统计、网络流、图论、时间序列、博弈论、控制理论、聚类、多目标、模糊逻辑） |
| 引用格式 | GB/T 7714 / APA / IEEE / Chicago / MLA |
| 统计分析 | 描述统计、t检验、相关分析、回归分析、ANOVA、卡方检验 |
| 文献检索 | Semantic Scholar + CrossRef 真实文献抓取 |
| 概念图 | 纯 matplotlib 生成专业示意图（8 种模型类型，无需 GPU） |
| 质量评分 | 7 维度 0-100 分自动评分 |
| 模板 | ieee / acm / cjm / springer_lncs / thesis |
| 输出格式 | LaTeX + PDF + JSON 摘要 |
| Web UI | Gradio 交互界面 |

## 论文类型详情

| 类型 | 语言 | 页数 | 章节数 | 适用场景 |
|------|------|------|--------|----------|
| thesis | 中文 | 30-100 | 8 | 本科/硕士/博士毕业论文 |
| journal | 英文 | 6-15 | 6 | SCI/EI 期刊论文 |
| conference | 英文 | 4-8 | 6 | 学术会议论文 |
| review | 中文 | 10-30 | 7 | 文献综述/系统综述 |
| experiment | 英文 | 8-20 | 6 | 实验研究论文 |
| case_study | 中文 | 6-15 | 7 | 案例分析/调研 |
| math_modeling | 中文 | 15-30 | 8 | 数学建模竞赛/研究 |

## 环境要求

- Python 3.10+
- xelatex (MiKTeX 或 TeX Live)
- Mode B 需要 HIAPI_API_KEY 或 OPENAI_API_KEY

## 文档

- [HANDOVER.md](HANDOVER.md) — 完整维护文档
- [NEXT_AI_PROMPT.md](NEXT_AI_PROMPT.md) — 下一个 AI 的提示词

## 许可证

MIT License