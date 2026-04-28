# Changelog

## [0.1.1] - 2026-04-27

### 改进
- 修复混合关键词题目分类优先级，避免“优化理论”类题目误判为 theoretical
- 重写 `section_writer.py`，按模型类型生成论文内容，强化数学建模专用场景
- 修复多处 LaTeX 脆弱点，避免普通文本中的下划线污染编译
- `latex_generator.py` 改为使用局部文件名调用 `xelatex`，更适合 Windows 路径环境
- 成功编译后自动清理陈旧 `compile.log`，避免后续维护误判
- CLI 去除 `gbk` 终端不安全的 emoji / spinner，Windows 终端真实可跑
- 新增 `network_flow` 与 `time_series` 模型类型，覆盖分析、建模、求解、图表和 3D 输出
- 新增 `multi_objective` 与 `pde` 模型类型，覆盖分析、建模、求解、图表和 3D 输出
- 新增 `queueing` 与 `markov_chain` 模型类型，覆盖分析、建模、求解、图表和 3D 输出
- 补齐 `SKILL.md`、`CLAUDE.md`、`docs/skill_integration.md` 与 skill 预设配置
- 新增排队系统 demo 验证产物，输出到 `C:\Users\24560\Desktop\study\paperskilldemo`

### 测试
- 新增 `paper_writer` 回归测试，覆盖模型类型写作、Windows 编译调用和 LaTeX 输出稳定性
- 当前全量测试基线已提升为 `73/73` 通过

## [0.1.0] - 2024-04-26

### 新增
- 项目初始版本
- 完整的Pipeline架构
- 题目分析模块 (TopicAnalyzer, TaskPlanner)
- 数学建模模块 (ModelBuilder, ModelSolver, ModelValidator)
  - 支持方程组、优化、微分方程、统计模型
- 可视化模块 (ChartGenerator, Model3DGenerator)
  - 2D图表生成
  - 3D模型生成 (trimesh/matplotlib)
- 论文写作模块 (LaTeXGenerator, SectionWriter, TemplateManager)
  - 支持 IEEE/ACM/Springer/Custom 模板
  - 中文支持
- GitHub发布模块 (GitHubPublisher)
- CLI接口 (Click)
- 配置文件系统 (Pydantic + YAML)
- 完整测试覆盖
- 文档 (架构/API/开发/路线图)
