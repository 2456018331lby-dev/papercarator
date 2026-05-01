# Model Profiles Reference

Detailed profiles for each supported mathematical model type.
SectionWriter and ChartGenerator use these profiles to generate
type-specific narrative, equations, and visualizations.

## equation_system
- Label: 方程组模型
- Focus: 多个变量之间的平衡关系与约束一致性
- Workflow: 建立变量关系、整理等式约束、采用符号或数值方法求解
- Evaluation: 残差大小、解的唯一性与变量解释性
- Benchmarks: 解析求解, 数值根搜索, 迭代修正法
- Typical equations: 线性/非线性方程组
- Key references: Kelley (1995), Ortega & Rheinboldt (2000)
- Future: 非线性、多层级耦合方程组

## optimization
- Label: 优化模型
- Focus: 目标函数、约束条件与资源配置效率
- Workflow: 定义决策变量、构造目标函数、描述约束并执行优化求解
- Evaluation: 目标值、迭代效率、约束满足度与稳定性
- Benchmarks: 梯度法, 二次规划, 启发式搜索
- Key references: Bertsekas (1999), Fletcher (1987), Boyd & Vandenberghe (2004)
- Future: 多目标、鲁棒与动态优化场景

## multi_objective
- Label: 多目标优化模型
- Focus: 多个目标之间的权衡关系与帕累托最优结构
- Workflow: 构造多个目标函数、设计权重或偏好、搜索折中解与帕累托前沿
- Evaluation: 目标权衡效果、帕累托分布、折中解稳定性与可解释性
- Benchmarks: 加权和法, 约束法, 帕累托前沿采样
- Key references: Deb (2001), Coello Coello (2007)
- Future: NSGA-II 等更复杂的多目标算法

## differential
- Label: 微分方程模型
- Focus: 系统状态随时间或空间的连续演化规律
- Workflow: 建立状态方程、设置初始条件、进行数值积分与轨迹分析
- Evaluation: 轨迹合理性、相图特征、数值稳定性与收敛精度
- Benchmarks: 解析近似, 数值积分, 相空间分析
- Key references: Butcher (2008), Hairer & Wanner (1996)
- Future: 偏微分与多尺度动力系统

## pde
- Label: 偏微分方程模型
- Focus: 时空分布、边界条件与连续介质演化规律
- Workflow: 建立 PDE、设置边界与初值、采用离散化方法进行数值求解
- Evaluation: 数值稳定性、场分布合理性、边界满足情况与时空解释性
- Benchmarks: 有限差分法, 有限元法, 解析近似
- Key references: LeVeque (2007), Strikwerda (2004)
- Future: 更高维、更复杂边界条件的 PDE 系统

## queueing
- Label: 排队系统模型
- Focus: 到达率、服务率、等待时间与系统利用率
- Workflow: 定义到达过程与服务过程、构造稳态指标、分析排队性能
- Evaluation: 平均等待时间、平均队长、系统稳定性与服务效率
- Benchmarks: M/M/1, M/M/c, 离散事件仿真
- Key references: Gross & Harris (1998), Kleinrock (1975)
- Future: 优先级排队与网络排队系统

## markov_chain
- Label: 马尔可夫链模型
- Focus: 状态转移、稳态分布与长期演化规律
- Workflow: 构造转移矩阵、定义初始分布、分析多步转移与稳态行为
- Evaluation: 分布收敛性、稳态误差、状态解释性与转移合理性
- Benchmarks: 矩阵幂法, 稳态分布求解, 状态转移图分析
- Key references: Norris (1997), Bremaud (2020)
- Future: 隐马尔可夫模型与连续时间马尔可夫过程

## network_flow
- Label: 网络流模型
- Focus: 节点连接关系、路径代价与流量分配效率
- Workflow: 构建网络节点与边、定义容量或代价、执行路径或流量求解
- Evaluation: 路径代价、流量可行性、边利用率与网络解释性
- Benchmarks: 最短路径法, 最大流方法, 最小费用流
- Key references: Ahuja (1993), Cormen et al. (2009)
- Future: 更大规模的动态交通与物流网络

## time_series
- Label: 时间序列模型
- Focus: 趋势项、季节项与未来时刻预测能力
- Workflow: 整理时序观测、拟合趋势与季节结构、执行未来预测
- Evaluation: 预测误差、趋势拟合质量、季节性解释与稳定性
- Benchmarks: 移动平均, 指数平滑, 季节趋势回归
- Key references: Box & Jenkins (2015), Hyndman & Athanasopoulos (2018)
- Future: ARIMA、状态空间与多变量时序模型

## game_theory
- Label: 博弈论模型
- Focus: 参与者策略、收益矩阵、均衡结构与最优响应关系
- Workflow: 构造策略集合与收益矩阵、分析最优响应、求解均衡或博弈值
- Evaluation: 均衡稳定性、策略概率分布、博弈值与最优响应差距
- Benchmarks: 纯策略枚举, 混合策略线性规划, 最小最大分析
- Key references: Osborne & Rubinstein (1994), Fudenberg & Tirole (1991)
- Future: 非零和博弈、演化博弈与多主体动态博弈

## control_theory
- Label: 控制理论模型
- Focus: 反馈结构、控制参数、系统稳定性与动态响应特征
- Workflow: 建立闭环系统方程、设置控制参数、分析特征根与阶跃响应
- Evaluation: 稳定性、阻尼比、自然频率、响应速度与超调风险
- Benchmarks: Routh-Hurwitz 判据, PID 参数整定, 阶跃响应分析
- Key references: Ogata (2010), Franklin et al. (2014)
- Future: 状态空间控制、LQR 与鲁棒控制系统

## clustering
- Label: 聚类分析模型
- Focus: 样本分布、簇中心、类内距离与无监督结构发现
- Workflow: 构造样本特征空间、初始化聚类中心、迭代分配样本并更新中心
- Evaluation: 簇内误差、聚类中心稳定性、类别分离度与可解释性
- Benchmarks: K-means, 层次聚类, 密度聚类
- Key references: Hastie et al. (2009), Jain (2010)
- Future: 自动选簇、谱聚类与高维特征降维分析

## statistical
- Label: 统计回归模型
- Focus: 数据关系识别、参数估计与预测解释
- Workflow: 整理样本数据、建立回归关系、估计参数并分析误差
- Evaluation: 拟合优度、均方误差、残差结构与泛化稳定性
- Benchmarks: 最小二乘法, 稳健回归, 正则化回归
- Key references: Hastie et al. (2009), Draper & Smith (1998)
- Future: 非线性统计与时间序列建模

## bayesian
- Label: 贝叶斯推断模型
- Focus: 先验分布、似然函数、后验推断与不确定性量化
- Workflow: 设定先验、构造似然、执行共轭更新或MCMC采样、分析后验
- Evaluation: 后验均值、可信区间、先验敏感性与收敛诊断
- Benchmarks: Beta-Binomial共轭, 正态-逆Gamma, MCMC采样
- Key references: Gelman et al. (2013), Robert (2007)
- Future: 变分推断、层次贝叶斯模型、非参数贝叶斯

## graph_theory
- Label: 图论模型
- Focus: 节点连通性、路径优化、最小生成树与网络结构分析
- Workflow: 构建邻接矩阵、选择图算法（MST/最短路径/最大流）、分析结构特征
- Evaluation: 最小代价、连通分量、图密度与算法复杂度
- Benchmarks: Kruskal MST, Dijkstra最短路径, Ford-Fulkerson最大流
- Key references: Cormen et al. (2009), West (2001)
- Future: 有向图、加权超图、动态网络分析

## fuzzy_logic
- Label: 模糊逻辑模型
- Focus: 隶属函数、模糊规则、推理机制与去模糊化
- Workflow: 定义模糊集合与隶属函数、建立规则库、执行模糊推理、重心法去模糊化
- Evaluation: 去模糊化输出、规则覆盖度、隶属函数合理性
- Benchmarks: Mamdani推理, Sugeno推理, 重心法去模糊化
- Key references: Zadeh (1965), Klir & Yuan (1995)
- Future: 自适应模糊系统、神经模糊混合模型
