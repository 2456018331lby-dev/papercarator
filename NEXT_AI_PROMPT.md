# 下一个AI的提示词

## 你的任务

继续完成 PaperCarator 项目。当前它已经更接近“数学建模论文一体化 skill”，基础流程、CLI 和 PDF 输出已跑通，下一步重点是继续把数学建模专用能力做深，再逐步准备更广泛题目类型的扩展。

## 项目位置
```
C:\Users\24560\Desktop\study\opendemo\papercarator
```

## 当前状态（阅读HANDOVER.md了解详情）

### ✅ 已完成
- Pipeline架构完整（Planner → MathModeling → Visualization → PaperWriter）
- section_writer.py 已修复f-string语法错误
- Gradio Web界面已创建（app.py）
- 数学建模和求解器工作正常（Python/SciPy）
- Windows 下 LaTeX 编译可生成 PDF
- 题目分析器已修复混合关键词优先级问题
- `section_writer.py` 已改成按模型类型写作
- `python3.12 -m papercarator.cli run ...` 已验证可在 Windows 终端跑通
- CLI 已修复 `gbk` 终端下 emoji / spinner 崩溃
- 已新增 `network_flow` 和 `time_series` 模型链路
- 已新增 `multi_objective` 和 `pde` 模型链路
- 已新增 `queueing` 和 `markov_chain` 模型链路
- 已补齐 `SKILL.md`、`CLAUDE.md`、`docs/skill_integration.md`
- 已补齐 `configs/skill_codex.yaml`、`configs/skill_claude.yaml`
- 73/73 测试通过
- 已验证 demo 输出目录：`C:\Users\24560\Desktop\study\paperskilldemo`

### ⚠️ 需要修复（按优先级）

#### P1 - 功能增强
1. **数学建模专用能力继续增强**
   - 增加更多模型类型（例如多目标优化、PDE、随机过程、图论扩展）
   - 扩展题目到模型的匹配规则
   - 提升章节内容与真实求解结果之间的贴合度

2. **Direction B 的准备工作**
   - 明确哪些题目还不属于当前 skill 的稳定覆盖范围
   - 整理开放域题目支持所需的能力缺口
   - 继续维护 README / HANDOVER / CHANGELOG，保证后续接手不被旧状态误导

#### P2 - 可选
3. **MATLAB Engine** - 未安装（可选，Python求解器已足够）
   - 位置：`C:\Program Files\MATLAB\R2024b`
   - 需要检查`extern/engines/python`目录是否存在

## 立即执行

1. **阅读文档**：
   ```
   C:\Users\24560\Desktop\study\opendemo\papercarator\HANDOVER.md
   C:\Users\24560\Desktop\study\opendemo\papercarator\QUICKFIX.md
   ```

2. **测试当前状态**：
   ```bash
   cd C:\Users\24560\Desktop\study\opendemo\papercarator
   python3.12 -m pytest tests -v
   python3.12 examples/basic_usage.py
   python3.12 -m papercarator.cli run "基于优化理论的资源配置问题研究" --output verify_output --no-github --no-vscode
   ```

3. **优先继续推进**：
   - 优先增强数学建模专用能力，不要先做开放域承诺
   - 如果继续改论文写作模块，保持“无额外 LLM 依赖”的前提
   - 每次改动后同步更新 `HANDOVER.md` / `README.md` / `CHANGELOG.md`
   - 保持 `SKILL.md` / `CLAUDE.md` / `skill_*` 配置与真实能力一致

## 当前重点示例（题目分析优先级）

```python
# 真实回归场景
result = analyzer.analyze("基于优化理论的资源配置问题研究")
assert result["paper_type"] == "optimization"
```

## 技术栈
- Python 3.12
- Pydantic, NumPy, SciPy, SymPy
- Gradio (Web界面)
- LaTeX (xelatex)
- Click, Rich (CLI)

## 注意事项
- Windows终端可能显示中文乱码，但文件内容正确
- 使用python3.12运行（不是python）
- 测试时使用临时目录，不会污染项目

## 成功标准
- [x] LaTeX编译PDF成功生成
- [x] 所有测试通过
- [x] 示例流程能完整跑通生成论文流程
- [x] CLI 在 Windows 终端可直接跑通
- [x] Codex / Claude Code skill 调用资产已具备
- [ ] 数学建模专用能力继续扩展
- [ ] README / HANDOVER / NEXT_AI_PROMPT 保持与真实状态一致

## 可选增强（如果时间允许）
- 接入LLM API提升内容质量
- 添加更多数学模型类型
- 优化题目分析器精度
- 实现文献自动检索

---

**开始工作前，先运行测试确认当前状态，然后优先修复LaTeX编译问题。**
