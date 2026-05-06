# 下一个 AI 的提示词

## 项目位置

C:\Users\24560\Desktop\study\opendemo\papercarator

## 当前能力（2026-05-02）

PaperCarator 已是全类型学术论文生成系统：

- **7 种论文类型**：毕业论文/期刊/会议/综述/实验/案例/数学建模
- **16 种数学模型**：全部有构建器+求解器
- **5 种引用格式**：GB/T 714/APA/IEEE/Chicago/MLA
- **统计分析**：描述统计/t检验/相关/回归/ANOVA/卡方
- **文献检索**：Semantic Scholar + CrossRef
- **概念图**：纯 matplotlib，8 种模型类型
- **两种模式**：A) AI 自主写作 B) 一键自动

## 使用方式

**Mode A（推荐）**：
```
python scripts/generate_data.py "题目" --output ./output/xxx
→ 读 JSON 写章节 → 保存 sections.json
→ python scripts/assemble_paper.py --context context.json --sections sections.json
```

**Mode B**：
```
python scripts/run_paper.py "题目" --output ./output/xxx
```

## 继续改进的方向

1. **内容深度** — 论文质量取决于写作 AI 本身。Mode A 下 Claude/GPT 写的内容好于 Mode B 的 MiniMax
2. **真实数据** — 用户提供 CSV 数据时，统计分析会自动运行。数据质量决定结果可信度
3. **论文终稿** — 当前是初稿生成器，要发表还需人工审核和补充
4. **测试回归** — HANDOVER.md 中 93/93 的基线可能已变化，新 AI 接手后应重新跑测试

## 技术栈

Python 3.12 | SymPy/SciPy/NumPy | Matplotlib | LaTeX (xelatex) | Gradio | Click/Rich

## 注意事项

- 读取 HANDOVER.md 了解完整文件结构
- 不要改动 ~/.hermes/config.yaml（MCP 配置已稳定）
- GitHub push 需要: unset GIT_EXEC_PATH && export GIT_EXEC_PATH=/usr/lib/git-core
- xelatex 在 WSL 中自动检测 Windows MiKTeX 路径