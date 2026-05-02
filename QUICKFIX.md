# PaperCarator 快速维护指南

## 当前优先事项

### 1. 先补齐开发依赖，再做验证

当前会话环境直接运行 `pytest` 会在收集阶段因缺少 `pydantic` 中断，这不是业务回归，而是环境未装齐。

```bash
cd C:\Users\24560\Desktop\study\opendemo\papercarator
python3.12 -m pip install -e ".[dev]"
python3.12 -m pytest tests -q
```

### 2. 重点维护 CLI 回归与真实文档状态

- 已新增 CLI 组装层回归测试，覆盖 `run` 命令的配置映射和模块注册
- 继续维护时，优先保证 `HANDOVER.md`、`NEXT_AI_PROMPT.md`、`CHANGELOG.md` 与真实代码状态一致
- 不要再按“先修 `latex_generator.py` 编码问题”推进，该问题已在当前代码中修复

### 3. MATLAB Engine 仍是可选项

```bash
Get-ChildItem "C:\Program Files\MATLAB\R2024b\extern\engines\python"
```

如果该目录不存在，继续使用 Python 求解链路即可，不要把 MATLAB 作为当前主阻塞。

## 一键验证命令

```bash
# 1. 安装依赖
python3.12 -m pip install -e ".[dev]"

# 2. 运行重点回归
python3.12 -m pytest tests/test_cli.py tests/test_paper_writer.py -v

# 3. 运行完整示例
python3.12 examples/basic_usage.py

# 4. 运行一次 CLI 验证
python3.12 -m papercarator.cli run "基于优化理论的资源配置问题研究" --output verify_output --no-github --no-vscode
```

## 当前维护关注文件

| 文件 | 状态 | 备注 |
|------|------|------|
| `tests/test_cli.py` | ✅ 已增强 | 增加 `run` 命令回归覆盖 |
| `HANDOVER.md` | ⚠️ 需同步 | 维护过程中持续更新真实进度 |
| `NEXT_AI_PROMPT.md` | ⚠️ 需同步 | 避免继续引用已过期任务 |
| `papercarator/math_modeling/*` | ⚠️ 有未提交修改 | 继续维护前先确认与当前作者改动不冲突 |

## 下一步建议

1. 先安装 `.[dev]` 后重跑测试，确认新增 CLI 测试通过。
2. 在不碰当前脏工作树数学建模文件的前提下，继续补 CLI / 文档 / 产物级回归。
3. 再继续扩展数学建模题型与题目匹配规则。
