# Changelog

## [0.3.0] - 2026-05-06

### 重大改进 — 死代码集成
- latex_generator.py `_generate_latex_document()` 完全重写：根据 paper_type 自动路由
  - thesis → ThesisStructure（封面+中英文摘要+目录+致谢+章节）
  - 其他6种类型 → 模板+paper-type-aware section路由
- citation_formatter 正式接入：GB/T 7714 / APA / IEEE / Chicago / MLA
- statistical_analysis 注入论文：描述统计+t检验+回归结果自动生成 LaTeX subsection
- run_paper.py 新增 `_run_statistical_analysis()` 完整数据流

### 修复
- _detect_latex_compiler() 不再硬编码用户名，自动 getpass.getuser() + 遍历 /mnt/c/Users

### 清理
- 删除 templates.py（被 template_manager.py 替代的重复系统）
- 删除 resilient_pipeline.py（未使用的变体）
- 删除同步文档 HANDOVER.md / CLAUDE.md / NEXT_AI_PROMPT.md / QUICKFIX.md
- 删除根目录 Playwright 测试杂项和 mouse_keyboard_control.ps1
- 统一模板系统仅保留 template_manager.py + 内置6模板

## [Unreleased-v0.2]

### 改进
- 为 `run` 命令补充 CLI 组装层回归测试
- 同步项目版本元数据到 `0.2.0`
- 补齐 `game_theory`、`control_theory`、`clustering` 的题目分析入口
- 补齐 `SKILL.md` 的 Codex skill frontmatter

## [0.1.1] - 2026-04-27
- 修复混合关键词题目分类优先级
- 重写 section_writer.py 按模型类型生成内容
- 新增 network_flow / time_series / multi_objective / pde / queueing / markov_chain 模型

## [0.1.0] - 2024-04-26
- 项目初始版本：Pipeline架构、数学建模、可视化、LaTeX生成、CLI