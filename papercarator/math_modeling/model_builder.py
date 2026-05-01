"""模型构建器 - 根据题目自动构建数学模型"""

import json
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
import sympy as sp
from loguru import logger


@dataclass
class MathModel:
    """数学模型"""
    name: str
    description: str
    # 符号定义
    symbols: dict[str, sp.Symbol] = field(default_factory=dict)
    # 方程/约束
    equations: list[sp.Expr] = field(default_factory=list)
    # 目标函数（优化问题）
    objective: sp.Expr | None = None
    objective_type: str = "minimize"  # minimize | maximize
    # 数值参数
    parameters: dict[str, float] = field(default_factory=dict)
    # 模型类型: equation_system | optimization | differential | statistical
    model_type: str = "equation_system"
    # 元数据
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelBuilder:
    """数学模型构建器

    根据论文题目和分析结果，自动构建相应的数学模型。
    支持：方程组、优化问题、微分方程、统计模型等。
    """

    def __init__(self):
        self.model_templates: dict[str, Callable] = {
            "equation_system": self._build_equation_system,
            "optimization": self._build_optimization,
            "multi_objective": self._build_multi_objective,
            "differential": self._build_differential,
            "pde": self._build_pde,
            "statistical": self._build_statistical,
            "network_flow": self._build_network_flow,
            "time_series": self._build_time_series,
            "queueing": self._build_queueing,
            "markov_chain": self._build_markov_chain,
            "game_theory": self._build_game_theory,
            "control_theory": self._build_control_theory,
            "clustering": self._build_clustering,
            "bayesian": self._build_bayesian,
            "graph_theory": self._build_graph_theory,
            "fuzzy_logic": self._build_fuzzy_logic,
        }
        logger.info("初始化 ModelBuilder")

    def build(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """根据题目构建数学模型

        Args:
            topic: 论文题目
            plan: 题目分析结果

        Returns:
            MathModel对象
        """
        logger.info(f"开始构建数学模型: {topic}")

        # 根据题目内容推断模型类型
        model_type = self._infer_model_type(topic, plan)
        logger.info(f"推断模型类型: {model_type}")

        # 使用对应模板构建模型
        builder_func = self.model_templates.get(model_type, self._build_equation_system)
        model = builder_func(topic, plan)

        logger.info(f"数学模型构建完成: {model.name}")
        return model

    def _infer_model_type(self, topic: str, plan: dict[str, Any]) -> str:
        """推断模型类型"""
        topic_lower = topic.lower()

        # 网络流/路径规划类
        if any(w in topic for w in ["最短路径", "网络流", "物流网络", "配送网络", "路径规划", "network flow", "shortest path"]):
            return "network_flow"

        # 排队系统类
        if any(w in topic for w in ["排队", "服务台", "排队系统", "到达率", "queueing", "service queue"]):
            return "queueing"

        # 马尔可夫链类
        if any(w in topic for w in ["马尔可夫", "状态转移", "转移概率", "markov chain", "state transition"]):
            return "markov_chain"

        # 博弈论类
        if any(w in topic for w in ["博弈", "Nash", "nash", "纳什", "博弈论", "game theory", "对策", "均衡", "优势策略", "占优"]):
            return "game_theory"

        # 控制理论类
        if any(w in topic for w in ["控制", "PID", "pid", "控制系统", "控制器", "稳定性", "反馈", "control theory", "LQR", "lqr", "最优控制"]):
            return "control_theory"

        # 聚类分析类
        if any(w in topic for w in ["聚类", "K-means", "k-means", "层次聚类", "clustering", "分类", "分群", "数据挖掘"]):
            return "clustering"

        # 贝叶斯推断类
        if any(w in topic for w in ["贝叶斯", "Bayesian", "bayesian", "先验", "后验", "概率推断"]):
            return "bayesian"

        # 图论类
        if any(w in topic for w in ["图论", "最小生成树", "连通性", "graph theory", "MST", "拓扑"]):
            return "graph_theory"

        # 模糊逻辑类
        if any(w in topic for w in ["模糊", "fuzzy", "隶属函数", "模糊推理", "模糊控制"]):
            return "fuzzy_logic"

        # 多目标优化类
        if any(w in topic for w in ["多目标", "帕累托", "pareto", "multi-objective"]):
            return "multi_objective"

        # 优化类关键词
        if any(w in topic for w in ["优化", "最优", "最大化", "最小化", "optimization", "optimal"]):
            return "optimization"

        # 偏微分方程类
        if any(w in topic for w in ["偏微分", "热方程", "扩散方程", "二维热传导", "pde", "partial differential"]):
            return "pde"

        # 微分方程类
        if any(w in topic for w in ["微分方程", "动力学", "dynamic", "differential", "波动", "热传导"]):
            return "differential"

        # 时间序列/预测类
        if any(w in topic for w in ["时间序列", "时序", "预测", "forecast", "trend"]):
            return "time_series"

        # 统计类
        if any(w in topic for w in ["统计", "回归", "概率", "预测", "regression", "statistical", "prediction"]):
            return "statistical"

        # 默认方程组
        return "equation_system"

    def _build_equation_system(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建方程组模型（示例：线性方程组）"""
        logger.info("构建方程组模型")

        # 定义符号 - 使用2个变量，避免过约束
        x, y = sp.symbols('x y', real=True)

        # 构建简单的2元线性方程组，有唯一解
        eq1 = sp.Eq(2*x + 3*y, 8)
        eq2 = sp.Eq(x - y, 1)

        model = MathModel(
            name="线性方程组模型",
            description=f"基于'{topic}'构建的线性方程组模型",
            symbols={"x": x, "y": y},
            equations=[eq1, eq2],
            model_type="equation_system",
            metadata={
                "variables": ["x", "y"],
                "equation_count": 2,
                "topic": topic,
            }
        )
        return model

    def _build_network_flow(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建网络流/最短路径模型。"""
        logger.info("构建网络流模型")

        f_sa, f_sb, f_ac, f_bc, f_ct, f_bt = sp.symbols("f_sa f_sb f_ac f_bc f_ct f_bt", nonnegative=True)

        equations = [
            sp.Eq(f_sa + f_sb, 10),
            sp.Eq(f_sa - f_ac, 0),
            sp.Eq(f_sb - f_bc - f_bt, 0),
            sp.Eq(f_ac + f_bc - f_ct, 0),
            sp.Eq(f_ct + f_bt, 10),
        ]

        edges = [
            {"from": "S", "to": "A", "capacity": 10, "cost": 2},
            {"from": "S", "to": "B", "capacity": 8, "cost": 4},
            {"from": "A", "to": "C", "capacity": 9, "cost": 2},
            {"from": "B", "to": "C", "capacity": 5, "cost": 1},
            {"from": "B", "to": "T", "capacity": 5, "cost": 5},
            {"from": "C", "to": "T", "capacity": 12, "cost": 2},
        ]

        model = MathModel(
            name="物流网络流模型",
            description=f"基于'{topic}'构建的网络流与最短路径模型",
            symbols={
                "f_sa": f_sa,
                "f_sb": f_sb,
                "f_ac": f_ac,
                "f_bc": f_bc,
                "f_ct": f_ct,
                "f_bt": f_bt,
            },
            equations=equations,
            model_type="network_flow",
            metadata={
                "nodes": ["S", "A", "B", "C", "T"],
                "edges": edges,
                "source": "S",
                "sink": "T",
                "demand": 10,
                "topic": topic,
            },
        )
        return model

    def _build_time_series(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建时间序列预测模型。"""
        logger.info("构建时间序列模型")

        np.random.seed(7)
        t = np.arange(24)
        trend = 50 + 1.8 * t
        seasonal = 6 * np.sin(2 * np.pi * t / 6)
        noise = np.random.normal(0, 0.8, len(t))
        y = trend + seasonal + noise

        a0, a1, a2, a3 = sp.symbols("a0 a1 a2 a3", real=True)
        tau = sp.symbols("tau", real=True)
        series_expr = sp.Eq(
            sp.Symbol("y"),
            a0 + a1 * tau + a2 * sp.sin(sp.pi * tau / 3) + a3 * sp.cos(sp.pi * tau / 3),
        )

        model = MathModel(
            name="时间序列预测模型",
            description=f"基于'{topic}'构建的趋势-季节性预测模型",
            symbols={"a0": a0, "a1": a1, "a2": a2, "a3": a3, "tau": tau},
            equations=[series_expr],
            model_type="time_series",
            parameters={"forecast_horizon": 6, "season_period": 6},
            metadata={
                "time_index": t.tolist(),
                "observations": y.tolist(),
                "season_period": 6,
                "forecast_horizon": 6,
                "topic": topic,
            },
        )
        return model

    def _build_optimization(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建优化模型（示例：二次规划）"""
        logger.info("构建优化模型")

        x, y = sp.symbols('x y', real=True)

        # 目标函数: 最小化 x^2 + y^2 + xy - 3x - 2y
        objective = x**2 + y**2 + x*y - 3*x - 2*y

        # 约束条件
        constraints = [
            sp.Ge(x + y, 1),  # x + y >= 1
            sp.Ge(x, 0),      # x >= 0
            sp.Ge(y, 0),      # y >= 0
        ]

        model = MathModel(
            name="二次规划优化模型",
            description=f"基于'{topic}'构建的优化模型",
            symbols={"x": x, "y": y},
            equations=constraints,
            objective=objective,
            objective_type="minimize",
            model_type="optimization",
            metadata={
                "variables": ["x", "y"],
                "constraints": 3,
                "objective_type": "quadratic",
                "topic": topic,
            }
        )
        return model

    def _build_multi_objective(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建多目标优化模型。"""
        logger.info("构建多目标优化模型")

        x, y = sp.symbols('x y', real=True)
        objective_1 = (x - 1) ** 2 + (y - 3) ** 2
        objective_2 = (x - 4) ** 2 + (y - 1) ** 2
        weighted_objective = 0.6 * objective_1 + 0.4 * objective_2

        constraints = [
            sp.Ge(x, 0),
            sp.Ge(y, 0),
            sp.Le(x + y, 6),
        ]

        model = MathModel(
            name="多目标权衡优化模型",
            description=f"基于'{topic}'构建的多目标优化模型",
            symbols={"x": x, "y": y},
            equations=constraints,
            objective=weighted_objective,
            objective_type="minimize",
            model_type="multi_objective",
            metadata={
                "topic": topic,
                "objective_functions": [str(objective_1), str(objective_2)],
                "weights": [0.6, 0.4],
                "variables": ["x", "y"],
            },
        )
        return model

    def _build_differential(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建微分方程模型（示例：简谐振动）"""
        logger.info("构建微分方程模型")

        t = sp.Symbol('t', real=True, positive=True)
        x = sp.Function('x')
        omega, A, phi = sp.symbols('omega A phi', real=True, positive=True)

        # 简谐振动方程: x''(t) + omega^2 * x(t) = 0
        ode = sp.Eq(x(t).diff(t, 2) + omega**2 * x(t), 0)

        model = MathModel(
            name="简谐振动微分方程",
            description=f"基于'{topic}'构建的微分方程模型",
            symbols={"t": t, "omega": omega, "A": A, "phi": phi},
            equations=[ode],
            model_type="differential",
            parameters={"omega": 2.0, "A": 1.0, "phi": 0.0},
            metadata={
                "independent_variable": "t",
                "dependent_variable": "x(t)",
                "order": 2,
                "topic": topic,
            }
        )
        return model

    def _build_pde(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建偏微分方程模型（示例：二维热方程）。"""
        logger.info("构建偏微分方程模型")

        x, y, t = sp.symbols('x y t', real=True, positive=True)
        u = sp.Function('u')
        alpha = sp.symbols('alpha', real=True, positive=True)

        pde = sp.Eq(
            sp.diff(u(x, y, t), t),
            alpha * (sp.diff(u(x, y, t), x, 2) + sp.diff(u(x, y, t), y, 2)),
        )

        model = MathModel(
            name="二维热传导偏微分方程模型",
            description=f"基于'{topic}'构建的二维热传导 PDE 模型",
            symbols={"x": x, "y": y, "t": t, "alpha": alpha},
            equations=[pde],
            model_type="pde",
            parameters={
                "alpha": 0.15,
                "grid_size": 30,
                "time_steps": 18,
                "dt": 0.02,
            },
            metadata={
                "topic": topic,
                "equation_type": "heat_equation_2d",
                "domain": [0.0, 1.0, 0.0, 1.0],
            },
        )
        return model

    def _build_queueing(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建排队系统模型。"""
        logger.info("构建排队系统模型")

        lambd, mu, c = sp.symbols('lambda mu c', positive=True, real=True)
        traffic_intensity = sp.Symbol('rho', positive=True, real=True)
        utilization_eq = sp.Eq(traffic_intensity, lambd / (c * mu))

        model = MathModel(
            name="M/M/c 排队系统模型",
            description=f"基于'{topic}'构建的排队系统模型",
            symbols={"lambda": lambd, "mu": mu, "c": c, "rho": traffic_intensity},
            equations=[utilization_eq],
            model_type="queueing",
            parameters={
                "arrival_rate": 4.5,
                "service_rate": 3.2,
                "servers": 2,
            },
            metadata={
                "queue_type": "M/M/c",
                "topic": topic,
            },
        )
        return model

    def _build_markov_chain(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建马尔可夫链模型。"""
        logger.info("构建马尔可夫链模型")

        p11, p12, p13 = sp.symbols('p11 p12 p13', real=True)
        p21, p22, p23 = sp.symbols('p21 p22 p23', real=True)
        p31, p32, p33 = sp.symbols('p31 p32 p33', real=True)

        equations = [
            sp.Eq(p11 + p12 + p13, 1),
            sp.Eq(p21 + p22 + p23, 1),
            sp.Eq(p31 + p32 + p33, 1),
        ]

        transition_matrix = [
            [0.70, 0.20, 0.10],
            [0.25, 0.55, 0.20],
            [0.15, 0.25, 0.60],
        ]

        model = MathModel(
            name="有限状态马尔可夫链模型",
            description=f"基于'{topic}'构建的状态转移模型",
            symbols={
                "p11": p11, "p12": p12, "p13": p13,
                "p21": p21, "p22": p22, "p23": p23,
                "p31": p31, "p32": p32, "p33": p33,
            },
            equations=equations,
            model_type="markov_chain",
            parameters={"steps": 8},
            metadata={
                "states": ["S1", "S2", "S3"],
                "transition_matrix": transition_matrix,
                "initial_distribution": [0.6, 0.3, 0.1],
                "topic": topic,
            },
        )
        return model

    def _build_statistical(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建统计模型（示例：线性回归）"""
        logger.info("构建统计模型")

        # 生成示例数据
        np.random.seed(42)
        n_samples = 100
        x_data = np.linspace(0, 10, n_samples)
        true_slope = 2.5
        true_intercept = 1.0
        noise = np.random.normal(0, 1, n_samples)
        y_data = true_slope * x_data + true_intercept + noise

        # 符号定义
        beta0, beta1, sigma = sp.symbols('beta0 beta1 sigma', real=True)
        x_sym, y_sym = sp.symbols('x y', real=True)

        # 回归方程
        regression_eq = sp.Eq(y_sym, beta0 + beta1 * x_sym)

        model = MathModel(
            name="线性回归模型",
            description=f"基于'{topic}'构建的统计回归模型",
            symbols={"beta0": beta0, "beta1": beta1, "sigma": sigma, "x": x_sym, "y": y_sym},
            equations=[regression_eq],
            model_type="statistical",
            parameters={
                "n_samples": n_samples,
                "true_slope": true_slope,
                "true_intercept": true_intercept,
            },
            metadata={
                "data_x": x_data.tolist(),
                "data_y": y_data.tolist(),
                "model_type": "linear_regression",
                "topic": topic,
            }
        )
        return model

    def _build_game_theory(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建博弈论模型（示例：双人零和博弈与Nash均衡）"""
        logger.info("构建博弈论模型")

        # 双人零和博弈收益矩阵（A的收益）
        payoff_matrix_a = np.array([
            [3.0, 0.0, 4.0],
            [2.0, 4.0, 1.0],
            [0.0, 3.0, 2.0],
        ])

        # 符号定义：混合策略概率
        p1, p2, p3 = sp.symbols('p1 p2 p3', real=True)
        q1, q2, q3 = sp.symbols('q1 q2 q3', real=True)

        # 策略概率归一化约束
        strategy_sum_a = sp.Eq(p1 + p2 + p3, 1)
        strategy_sum_b = sp.Eq(q1 + q2 + q3, 1)

        # 期望收益函数符号化
        expected_payoff = (
            p1 * q1 * payoff_matrix_a[0, 0] +
            p1 * q2 * payoff_matrix_a[0, 1] +
            p1 * q3 * payoff_matrix_a[0, 2] +
            p2 * q1 * payoff_matrix_a[1, 0] +
            p2 * q2 * payoff_matrix_a[1, 1] +
            p2 * q3 * payoff_matrix_a[1, 2] +
            p3 * q1 * payoff_matrix_a[2, 0] +
            p3 * q2 * payoff_matrix_a[2, 1] +
            p3 * q3 * payoff_matrix_a[2, 2]
        )

        model = MathModel(
            name="双人零和博弈Nash均衡模型",
            description=f"基于'{topic}'构建的博弈论与Nash均衡模型",
            symbols={"p1": p1, "p2": p2, "p3": p3, "q1": q1, "q2": q2, "q3": q3},
            equations=[strategy_sum_a, strategy_sum_b],
            objective=expected_payoff,
            objective_type="maximize",
            model_type="game_theory",
            parameters={"players": 2, "strategy_size": 3, "game_type": "zero_sum"},
            metadata={
                "payoff_matrix": payoff_matrix_a.tolist(),
                "player_names": ["A", "B"],
                "topic": topic,
            }
        )
        return model

    def _build_control_theory(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建控制理论模型（示例：PID控制器）"""
        logger.info("构建控制理论模型")

        # PID 参数符号
        Kp, Ki, Kd = sp.symbols('Kp Ki Kd', real=True)
        # 系统参数
        a, b = sp.symbols('a b', real=True, positive=True)
        # 参考信号
        r_t = sp.Function('r')
        y_t = sp.Function('y')
        e_t = sp.Function('e')

        # 简化PID闭环特征方程（示例：二阶系统）
        # 传递函数特征方程: s^2 + (1+Kp)*s + Ki = 0
        s = sp.symbols('s')
        characteristic_eq = sp.Eq(s**2 + (1 + Kp) * s + Ki, 0)

        # 微分方程形式的系统模型
        # d^2y/dt^2 + a*dy/dt + b*y = Kp*e + Ki*∫e + Kd*de/dt
        t = sp.symbols('t')
        e = sp.Function('e')(t)
        y = sp.Function('y')(t)
        system_eq = sp.Eq(
            sp.Derivative(sp.Derivative(y, t), t) + a * sp.Derivative(y, t) + b * y,
            Kp * e + Ki * sp.Integral(e, (t, 0, t)) + Kd * sp.Derivative(e, t)
        )

        model = MathModel(
            name="PID控制系统模型",
            description=f"基于'{topic}'构建的PID控制理论与系统稳定性分析模型",
            symbols={"Kp": Kp, "Ki": Ki, "Kd": Kd, "a": a, "b": b},
            equations=[system_eq, characteristic_eq],
            model_type="control_theory",
            parameters={"a": 2.0, "b": 1.0, "system_order": 2},
            metadata={
                "controller_type": "PID",
                "system_type": "second_order_linear",
                "topic": topic,
            }
        )
        return model

    def _build_clustering(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建聚类分析模型（示例：K-means）"""
        logger.info("构建聚类分析模型")

        # 生成示例二维数据点（3个簇）
        np.random.seed(42)
        cluster1 = np.random.randn(20, 2) + [2, 2]
        cluster2 = np.random.randn(20, 2) + [-2, 1]
        cluster3 = np.random.randn(20, 2) + [0, -3]
        data = np.vstack([cluster1, cluster2, cluster3])

        # 簇数 K
        K = sp.symbols('K', integer=True, positive=True)
        # 聚类中心
        mu_x, mu_y = sp.symbols('mu_x mu_y', real=True)

        # 距离度量：欧氏距离平方
        x_i = sp.symbols('x_i y_i', real=True)
        dist_sq = (x_i[0] - mu_x)**2 + (x_i[1] - mu_y)**2

        model = MathModel(
            name="K-means聚类分析模型",
            description=f"基于'{topic}'构建的聚类分析模型",
            symbols={"K": K, "mu_x": mu_x, "mu_y": mu_y},
            equations=[],
            model_type="clustering",
            parameters={"n_clusters": 3, "n_samples": 60, "n_features": 2},
            metadata={
                "data": data.tolist(),
                "clustering_method": "kmeans",
                "distance_metric": "euclidean",
                "topic": topic,
            },
        )
        return model

    def _build_bayesian(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建贝叶斯推断模型。"""
        logger.info("构建贝叶斯推断模型")

        alpha_prior, beta_prior = sp.symbols('alpha beta', positive=True)
        theta = sp.symbols('theta', real=True)

        posterior_eq = sp.Eq(
            sp.Symbol('P_theta_given_data'),
            sp.Symbol('Beta') * (alpha_prior + sp.Symbol('successes'))
            / (alpha_prior + beta_prior + sp.Symbol('n_trials'))
        )

        np.random.seed(42)
        true_theta = 0.65
        n_trials = 50
        successes = int(np.random.binomial(n_trials, true_theta))

        model = MathModel(
            name="贝叶斯推断模型",
            description=f"基于'{topic}'构建的贝叶斯参数估计模型",
            symbols={"alpha": alpha_prior, "beta": beta_prior, "theta": theta},
            equations=[posterior_eq],
            model_type="bayesian",
            parameters={
                "alpha_prior": 2.0, "beta_prior": 2.0,
                "n_trials": n_trials, "successes": successes,
            },
            metadata={
                "topic": topic, "prior": "Beta(2, 2)",
                "likelihood": "Binomial",
                "posterior": f"Beta({2 + successes}, {2 + n_trials - successes})",
            },
        )
        return model

    def _build_graph_theory(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建图论模型。"""
        logger.info("构建图论模型")

        n = 6
        np.random.seed(42)
        adj = np.random.randint(1, 20, size=(n, n))
        adj = (adj + adj.T) // 2
        np.fill_diagonal(adj, 0)

        x_vars = sp.symbols(f'x_0:{n}', nonneg=True)

        model = MathModel(
            name="图论最小生成树模型",
            description=f"基于'{topic}'构建的图论与网络优化模型",
            symbols={f"x_{i}": x_vars[i] for i in range(n)},
            equations=[],
            model_type="graph_theory",
            parameters={"n_nodes": n},
            metadata={
                "topic": topic,
                "adjacency_matrix": adj.tolist(),
                "nodes": [f"V{i}" for i in range(n)],
                "algorithm": "kruskal",
            },
        )
        return model

    def _build_fuzzy_logic(self, topic: str, plan: dict[str, Any]) -> MathModel:
        """构建模糊逻辑模型。"""
        logger.info("构建模糊逻辑模型")

        x = sp.Symbol('x', real=True)
        y = sp.Symbol('y', real=True)

        mf_params = {
            "low": {"a": 0, "b": 0, "c": 5},
            "medium": {"a": 3, "b": 5, "c": 7},
            "high": {"a": 5, "b": 10, "c": 10},
        }

        rules = [
            {"antecedent": ("x", "low"), "consequent": "low", "weight": 1.0},
            {"antecedent": ("x", "medium"), "consequent": "medium", "weight": 1.0},
            {"antecedent": ("x", "high"), "consequent": "high", "weight": 1.0},
        ]

        model = MathModel(
            name="模糊推理系统模型",
            description=f"基于'{topic}'构建的模糊逻辑推理模型",
            symbols={"x": x, "y": y},
            equations=[],
            model_type="fuzzy_logic",
            parameters={"n_inputs": 1, "n_outputs": 1, "defuzzification": "centroid"},
            metadata={
                "topic": topic,
                "membership_functions": mf_params,
                "rules": rules,
                "universe": [0, 10],
            },
        )
        return model

    def to_dict(self, model: MathModel) -> dict[str, Any]:
        """将模型转换为字典（用于序列化）"""
        return {
            "name": model.name,
            "description": model.description,
            "model_type": model.model_type,
            "equations": [str(eq) for eq in model.equations],
            "objective": str(model.objective) if model.objective else None,
            "objective_type": model.objective_type,
            "parameters": model.parameters,
            "metadata": model.metadata,
        }
