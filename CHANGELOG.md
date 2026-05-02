# Changelog

## [Unreleased]

### 改进
- 为 `run` 命令补充 CLI 组装层回归测试，覆盖配置映射、模块注册和关键开关
- 同步项目版本元数据到 `0.2.0`，避免 `pyproject.toml`、运行时配置和生成产物说明不一致
- 清理维护文档中的过期指引，移除已修复的 LaTeX 紧急修复描述
- 为 `SKILL.md` 补齐 Codex skill frontmatter，并明确 analyze-first、降级模式和产物验收流程
- 同步 `CLAUDE.md`、`docs/skill_integration.md`、`README.md`、`HANDOVER.md` 和 `NEXT_AI_PROMPT.md` 的 skill 调用契约
- 新增 `tests/test_skill_assets.py`，锁定 skill frontmatter、调用协议和本地化预设
- 补齐 `game_theory`、`control_theory`、`clustering` 的题目分析入口、章节写作画像和图表生成函数
- 新增三类模型的 planner、math_modeling、visualization 和 paper_writer 回归覆盖

### 验证
- 当前会话已通过 `python3.12 -m pytest tests\test_cli.py -q`
- 当前会话已通过 `python3.12 -m pytest tests\test_skill_assets.py tests\test_cli.py -q`，`9 passed`
- 当前会话已通过 `python3.12 -m pytest tests\test_planner.py tests\test_math_modeling.py tests\test_visualization.py tests\test_paper_writer.py -q`，`77 passed`
- 当前会话已通过 `python3.12 -m pytest tests -q`，`93 passed`
- 当前会话已通过 `quick_validate.py papercarator`
- 当前会话已通过 `python3.12 -m papercarator.cli analyze "基于优化理论的资源配置问题研究"`，输出类型为 `optimization`
- 当前会话已通过三类新增模型的 CLI 分析验证：`game_theory`、`control_theory`、`clustering`

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
