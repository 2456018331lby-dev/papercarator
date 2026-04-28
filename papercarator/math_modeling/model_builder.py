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
