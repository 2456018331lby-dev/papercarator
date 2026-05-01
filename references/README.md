# PaperCarator Reference — Model Profiles (compact)

Each model type has: label, focus, workflow, evaluation, benchmarks, key refs.

| Type | Label | Focus | Key Refs |
|------|-------|-------|----------|
| equation_system | 方程组 | 变量平衡与约束一致性 | Kelley (1995) |
| optimization | 优化 | 目标函数与约束 | Boyd (2004) |
| multi_objective | 多目标 | 帕累托权衡 | Deb (2001) |
| differential | 微分方程 | 状态连续演化 | Butcher (2008) |
| pde | 偏微分方程 | 时空分布与边界 | LeVeque (2007) |
| queueing | 排队系统 | 到达率/服务率/等待时间 | Gross (1998), Kleinrock (1975) |
| markov_chain | 马尔可夫链 | 状态转移与稳态 | Norris (1997) |
| bayesian | 贝叶斯推断 | 先验/后验/不确定性 | Gelman (2013) |
| statistical | 统计回归 | 数据关系与预测 | Hastie (2009) |
| network_flow | 网络流 | 路径代价与流量分配 | Ahuja (1993) |
| graph_theory | 图论 | 连通性与MST | Cormen (2009) |
| time_series | 时间序列 | 趋势/季节/预测 | Box (2015), Hyndman (2018) |
| game_theory | 博弈论 | 策略/收益/均衡 | Osborne (1994) |
| control_theory | 控制理论 | 反馈/稳定性/响应 | Ogata (2010) |
| clustering | 聚类分析 | 簇中心与无监督发现 | Hastie (2009) |
| fuzzy_logic | 模糊逻辑 | 隶属函数与推理 | Zadeh (1965) |

## Domain Backgrounds (for introduction)

- computer_vision: 数据规模与算力提升，复杂视觉问题适合数学建模
- transportation: 交通网络资源配置、路径选择与调度具有典型建模需求
- energy_systems: 多变量耦合、强约束、高稳定性要求
- finance: 资产定价、风险评估、投资组合优化
- medical: 流行病传播、药物动力学、医学影像
- environmental: 动态变化、约束协调、效果评估
- general: 将复杂问题抽象为可分析、可求解的形式化对象
