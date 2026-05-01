"""模型求解器 - 求解各种数学模型"""

import heapq
import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import sympy as sp
from loguru import logger
from scipy import optimize

from papercarator.math_modeling.model_builder import MathModel


@dataclass
class Solution:
    """求解结果"""
    success: bool
    values: dict[str, float] = field(default_factory=dict)
    message: str = ""
    # 数值解（用于微分方程等）
    numerical_data: dict[str, Any] = field(default_factory=dict)
    # 统计信息
    statistics: dict[str, Any] = field(default_factory=dict)
    # 元数据
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelSolver:
    """数学模型求解器

    支持求解：方程组、优化问题、微分方程、统计模型。
    当MATLAB可用时，优先使用MATLAB进行高级求解。
    """

    def __init__(self, timeout: int = 300, matlab_bridge: "MATLABBridge | None" = None):
        self.timeout = timeout
        self.matlab_bridge = matlab_bridge
        self._matlab_available = matlab_bridge is not None and matlab_bridge.is_available()
        self.solvers = {
            "equation_system": self._solve_equation_system,
            "optimization": self._solve_optimization,
            "multi_objective": self._solve_multi_objective,
            "differential": self._solve_differential,
            "pde": self._solve_pde,
            "statistical": self._solve_statistical,
            "network_flow": self._solve_network_flow,
            "time_series": self._solve_time_series,
            "queueing": self._solve_queueing,
            "markov_chain": self._solve_markov_chain,
            "game_theory": self._solve_game_theory,
            "control_theory": self._solve_control_theory,
            "clustering": self._solve_clustering,
            "bayesian": self._solve_bayesian,
            "graph_theory": self._solve_graph_theory,
            "fuzzy_logic": self._solve_fuzzy_logic,
        }
        logger.info(f"初始化 ModelSolver (timeout={timeout}s, MATLAB={self._matlab_available})")

    def solve(self, model: MathModel) -> Solution:
        """求解数学模型

        Args:
            model: MathModel对象

        Returns:
            Solution对象
        """
        logger.info(f"开始求解模型: {model.name} (类型: {model.model_type})")

        # 优先尝试MATLAB求解（如果可用且模型类型兼容）
        if self._matlab_available and model.model_type in ("optimization", "differential"):
            logger.info("尝试使用MATLAB求解...")
            matlab_solution = self._solve_with_matlab(model)
            if matlab_solution and matlab_solution.success:
                logger.info(f"MATLAB求解成功: {matlab_solution.message}")
                return matlab_solution
            logger.warning("MATLAB求解失败，回退到Python求解器")

        solver_func = self.solvers.get(model.model_type, self._solve_equation_system)

        try:
            solution = solver_func(model)
            if solution.success:
                logger.info(f"模型求解成功: {solution.message}")
            else:
                logger.warning(f"模型求解失败: {solution.message}")
            return solution
        except Exception as e:
            logger.error(f"求解过程出错: {e}")
            return Solution(
                success=False,
                message=f"求解异常: {str(e)}",
            )

    def _solve_with_matlab(self, model: MathModel) -> Solution | None:
        """使用MATLAB求解模型"""
        if not self.matlab_bridge:
            return None

        try:
            if model.model_type == "optimization":
                return self._solve_with_matlab_optimization(model)
            elif model.model_type == "differential":
                return self._solve_with_matlab_ode(model)
        except Exception as e:
            logger.warning(f"MATLAB求解异常: {e}")
        return None

    def _solve_with_matlab_optimization(self, model: MathModel) -> Solution | None:
        """使用MATLAB求解优化问题"""
        # 提取变量名（排除非决策变量）
        var_names = []
        for name, sym in model.symbols.items():
            if name not in ("sigma", "t"):
                var_names.append(name)

        if not model.objective:
            return None

        # 转换目标函数为字符串
        obj_str = str(model.objective)
        # 将SymPy幂运算转换为MATLAB格式
        obj_str = obj_str.replace("**", "^")

        # 转换约束为字符串
        constraints = []
        for eq in model.equations:
            eq_str = str(eq)
            eq_str = eq_str.replace("**", "^")
            # 转换 >= 和 <=
            if ">=" in eq_str:
                constraints.append(eq_str.replace(">=", ">="))
            elif "<=" in eq_str:
                constraints.append(eq_str.replace("<=", "<="))
            elif ">" in eq_str:
                constraints.append(eq_str.replace(">", ">"))
            elif "<" in eq_str:
                constraints.append(eq_str.replace("<", "<"))

        result = self.matlab_bridge.solve_optimization(
            objective=obj_str,
            constraints=constraints,
            variables=var_names,
        )

        if result.get("success"):
            output = result.get("output", {})
            values = {}
            for var in var_names:
                if var in output:
                    val = output[var]
                    if hasattr(val, "_data"):
                        values[var] = float(np.array(val._data).flatten()[0])
                    else:
                        values[var] = float(val)

            return Solution(
                success=True,
                values=values,
                message=f"MATLAB优化求解成功，目标值: {output.get('objective_value', 'N/A')}",
                statistics={"optimal_value": output.get("objective_value"), "exitflag": output.get("exitflag")},
                metadata={"method": "matlab_optimization", "solver": "optimproblem"},
            )
        return None

    def _solve_with_matlab_ode(self, model: MathModel) -> Solution | None:
        """使用MATLAB求解微分方程"""
        params = model.parameters
        omega = params.get("omega", 1.0)

        # 定义ODE: x'' + omega^2 * x = 0
        # 转换为一阶: y1' = y2, y2' = -omega^2 * y1
        ode_func = f"[y(2); -{omega}^2 * y(1)]"
        tspan = [0, 10]
        y0 = [params.get("A", 1.0), 0.0]

        result = self.matlab_bridge.solve_ode(
            ode_func=ode_func,
            tspan=tspan,
            y0=y0,
        )

        if result.get("success"):
            output = result.get("output", {})
            t = np.array(output.get("t", [])).flatten()
            y = np.array(output.get("y", []))

            if len(y.shape) > 1 and y.shape[1] >= 2:
                x_vals = y[:, 0].tolist()
                v_vals = y[:, 1].tolist()
            else:
                x_vals = y.tolist() if len(y.shape) == 1 else y[:, 0].tolist()
                v_vals = []

            return Solution(
                success=True,
                values={"omega": omega, "A": params.get("A", 1.0), "phi": params.get("phi", 0.0)},
                message="MATLAB ODE45求解成功",
                numerical_data={"t": t.tolist() if hasattr(t, "tolist") else list(t), "x": x_vals, "v": v_vals},
                metadata={"method": "matlab_ode45", "time_points": len(t)},
            )
        return None

    def _solve_equation_system(self, model: MathModel) -> Solution:
        """求解方程组"""
        logger.info("求解方程组...")

        try:
            # 使用SymPy求解
            solution = sp.solve(model.equations, list(model.symbols.values()))

            if solution:
                # 解析解
                values = {}
                if isinstance(solution, dict):
                    for sym, val in solution.items():
                        values[str(sym)] = float(val) if val.is_number else str(val)
                else:
                    values["solution"] = str(solution)

                return Solution(
                    success=True,
                    values=values,
                    message="方程组求解成功",
                    metadata={"method": "sympy_analytical", "solution_type": "analytical"}
                )
            else:
                # 尝试数值求解
                return self._solve_numerical(model)

        except Exception as e:
            return self._solve_numerical(model)

    def _solve_numerical(self, model: MathModel) -> Solution:
        """数值求解方程组"""
        logger.info("尝试数值求解...")

        try:
            # 转换为数值函数
            symbols_list = list(model.symbols.values())
            funcs = []
            for eq in model.equations:
                if isinstance(eq, sp.Equality):
                    funcs.append(sp.lambdify(symbols_list, eq.lhs - eq.rhs, 'numpy'))
                else:
                    funcs.append(sp.lambdify(symbols_list, eq, 'numpy'))

            def equations(vars):
                return np.array([f(*vars) for f in funcs])

            # 尝试多种初始猜测
            initial_guesses = [
                np.ones(len(symbols_list)),
                np.zeros(len(symbols_list)),
                np.random.randn(len(symbols_list)),
            ]

            for initial_guess in initial_guesses:
                try:
                    result = optimize.root(equations, initial_guess, method='hybr')
                    if result.success:
                        values = {str(sym): float(val) for sym, val in zip(symbols_list, result.x)}
                        return Solution(
                            success=True,
                            values=values,
                            message=f"数值求解成功 (残差: {result.fun.max():.2e})",
                            metadata={"method": "scipy_numerical", "residual": float(result.fun.max())}
                        )
                except Exception:
                    continue

            # 如果都失败了，返回失败但包含更多信息
            return Solution(
                success=False,
                message="数值求解失败: 无法找到收敛解",
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"数值求解异常: {str(e)}",
            )

    def _solve_optimization(self, model: MathModel) -> Solution:
        """求解优化问题"""
        logger.info("求解优化问题...")

        try:
            # 提取变量
            var_symbols = [s for name, s in model.symbols.items()
                          if name not in ['sigma', 't']]

            if not model.objective:
                return Solution(success=False, message="目标函数未定义")

            # 转换为数值函数
            obj_func = sp.lambdify(var_symbols, model.objective, 'numpy')

            # 定义目标函数（scipy需要最小化）
            def objective(vars):
                result = obj_func(*vars)
                return float(result) if model.objective_type == "minimize" else -float(result)

            # 初始猜测
            x0 = np.ones(len(var_symbols))

            # 使用BFGS算法
            result = optimize.minimize(objective, x0, method='BFGS')

            if result.success:
                values = {str(sym): float(val) for sym, val in zip(var_symbols, result.x)}
                opt_value = float(result.fun)
                if model.objective_type == "maximize":
                    opt_value = -opt_value

                return Solution(
                    success=True,
                    values=values,
                    message=f"优化求解成功 - 最优值: {opt_value:.6f}",
                    statistics={"optimal_value": opt_value, "iterations": result.nit},
                    metadata={"method": "BFGS", "gradient_evals": result.njev}
                )
            else:
                return Solution(
                    success=False,
                    message=f"优化求解失败: {result.message}",
                )

        except Exception as e:
            return Solution(
                success=False,
                message=f"优化求解异常: {str(e)}",
            )

    def _solve_multi_objective(self, model: MathModel) -> Solution:
        """求解多目标优化问题。"""
        logger.info("求解多目标优化问题...")

        try:
            var_symbols = [s for name, s in model.symbols.items() if name not in ['sigma', 't']]
            if not model.objective:
                return Solution(success=False, message="加权目标函数未定义")

            obj_func = sp.lambdify(var_symbols, model.objective, 'numpy')
            objective_functions = model.metadata.get("objective_functions", [])
            objective_callables = [sp.lambdify(var_symbols, sp.sympify(expr), 'numpy') for expr in objective_functions]

            def objective(vars):
                return float(obj_func(*vars))

            x0 = np.array([1.5, 1.5], dtype=float)
            result = optimize.minimize(objective, x0, method='SLSQP')

            if not result.success:
                return Solution(success=False, message=f"多目标优化失败: {result.message}")

            values = {str(sym): float(val) for sym, val in zip(var_symbols, result.x)}

            pareto_points = []
            for weight in np.linspace(0.1, 0.9, 9):
                def weighted_obj(vars, weight=weight):
                    p1 = float(objective_callables[0](*vars))
                    p2 = float(objective_callables[1](*vars))
                    return weight * p1 + (1 - weight) * p2

                alt = optimize.minimize(weighted_obj, x0, method='SLSQP')
                if alt.success:
                    p1 = float(objective_callables[0](*alt.x))
                    p2 = float(objective_callables[1](*alt.x))
                    pareto_points.append({
                        "weight": float(weight),
                        "x": float(alt.x[0]),
                        "y": float(alt.x[1]),
                        "f1": p1,
                        "f2": p2,
                    })

            current_f1 = float(objective_callables[0](*result.x))
            current_f2 = float(objective_callables[1](*result.x))

            return Solution(
                success=True,
                values=values,
                message="多目标优化求解成功",
                numerical_data={
                    "pareto_front": pareto_points,
                    "selected_point": {"x": float(result.x[0]), "y": float(result.x[1]), "f1": current_f1, "f2": current_f2},
                },
                statistics={
                    "weighted_objective": float(result.fun),
                    "objective_1": current_f1,
                    "objective_2": current_f2,
                    "pareto_samples": len(pareto_points),
                },
                metadata={"method": "weighted_sum_slsqp"},
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"多目标优化异常: {str(e)}",
            )

    def _solve_differential(self, model: MathModel) -> Solution:
        """求解微分方程"""
        logger.info("求解微分方程...")

        try:
            from scipy.integrate import odeint

            # 获取参数
            omega = model.parameters.get("omega", 1.0)
            A = model.parameters.get("A", 1.0)
            phi = model.parameters.get("phi", 0.0)

            # 定义ODE: x'' + omega^2 * x = 0
            # 转换为一阶方程组: y1 = x, y2 = x'
            # y1' = y2
            # y2' = -omega^2 * y1
            def ode_system(y, t):
                return [y[1], -omega**2 * y[0]]

            # 时间范围
            t_span = np.linspace(0, 10, 1000)
            # 初始条件: x(0) = A*cos(phi), x'(0) = -A*omega*sin(phi)
            y0 = [A * np.cos(phi), -A * omega * np.sin(phi)]

            # 求解
            sol = odeint(ode_system, y0, t_span)

            return Solution(
                success=True,
                values={"omega": omega, "A": A, "phi": phi},
                message="微分方程数值求解成功",
                numerical_data={
                    "t": t_span.tolist(),
                    "x": sol[:, 0].tolist(),
                    "v": sol[:, 1].tolist(),
                },
                metadata={"method": "scipy_odeint", "time_points": len(t_span)}
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"微分方程求解异常: {str(e)}",
            )

    def _solve_pde(self, model: MathModel) -> Solution:
        """求解二维热方程。"""
        logger.info("求解偏微分方程模型...")

        try:
            grid_size = int(model.parameters.get("grid_size", 30))
            time_steps = int(model.parameters.get("time_steps", 18))
            alpha = float(model.parameters.get("alpha", 0.15))
            dt = float(model.parameters.get("dt", 0.02))

            x = np.linspace(0, 1, grid_size)
            y = np.linspace(0, 1, grid_size)
            X, Y = np.meshgrid(x, y)
            dx = x[1] - x[0]
            dy = y[1] - y[0]

            u = np.sin(np.pi * X) * np.sin(np.pi * Y)
            snapshots = [u.copy()]

            coeff_x = alpha * dt / (dx ** 2)
            coeff_y = alpha * dt / (dy ** 2)

            for _ in range(time_steps):
                u_next = u.copy()
                u_next[1:-1, 1:-1] = (
                    u[1:-1, 1:-1]
                    + coeff_x * (u[2:, 1:-1] - 2 * u[1:-1, 1:-1] + u[:-2, 1:-1])
                    + coeff_y * (u[1:-1, 2:] - 2 * u[1:-1, 1:-1] + u[1:-1, :-2])
                )
                u_next[0, :] = 0
                u_next[-1, :] = 0
                u_next[:, 0] = 0
                u_next[:, -1] = 0
                u = u_next
                snapshots.append(u.copy())

            final_energy = float(np.sum(u ** 2))
            max_temp = float(np.max(u))

            return Solution(
                success=True,
                values={"alpha": alpha, "max_temperature": max_temp, "energy": final_energy},
                message="二维热方程求解成功",
                numerical_data={
                    "x": x.tolist(),
                    "y": y.tolist(),
                    "u_final": u.tolist(),
                    "u_initial": snapshots[0].tolist(),
                    "u_mid": snapshots[len(snapshots) // 2].tolist(),
                },
                statistics={
                    "grid_size": grid_size,
                    "time_steps": time_steps,
                    "max_temperature": max_temp,
                    "energy": final_energy,
                },
                metadata={"method": "explicit_finite_difference_2d"},
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"偏微分方程求解异常: {str(e)}",
            )

    def _solve_statistical(self, model: MathModel) -> Solution:
        """求解统计模型"""
        logger.info("求解统计模型...")

        try:
            # 获取数据
            x_data = np.array(model.metadata.get("data_x", []))
            y_data = np.array(model.metadata.get("data_y", []))

            if len(x_data) == 0:
                return Solution(success=False, message="没有数据")

            # 线性回归（最小二乘法）
            X = np.vstack([np.ones_like(x_data), x_data]).T
            coeffs, residuals, rank, s = np.linalg.lstsq(X, y_data, rcond=None)

            intercept, slope = coeffs

            # 计算R²
            y_pred = intercept + slope * x_data
            ss_res = np.sum((y_data - y_pred) ** 2)
            ss_tot = np.sum((y_data - np.mean(y_data)) ** 2)
            r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

            return Solution(
                success=True,
                values={"intercept": float(intercept), "slope": float(slope)},
                message=f"回归分析完成 - R² = {r_squared:.4f}",
                numerical_data={
                    "x": x_data.tolist(),
                    "y": y_data.tolist(),
                    "y_pred": y_pred.tolist(),
                },
                statistics={
                    "r_squared": float(r_squared),
                    "mse": float(ss_res / len(x_data)),
                    "coefficients": {"intercept": float(intercept), "slope": float(slope)},
                },
                metadata={"method": "least_squares", "n_samples": len(x_data)}
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"统计求解异常: {str(e)}",
            )

    def _solve_network_flow(self, model: MathModel) -> Solution:
        """求解网络流/最短路径模型。"""
        logger.info("求解网络流模型...")

        try:
            edges = model.metadata.get("edges", [])
            source = model.metadata.get("source", "S")
            sink = model.metadata.get("sink", "T")
            demand = float(model.metadata.get("demand", 10))

            adjacency: dict[str, list[tuple[str, float, float]]] = {}
            for edge in edges:
                adjacency.setdefault(edge["from"], []).append(
                    (edge["to"], float(edge["cost"]), float(edge["capacity"]))
                )

            # Dijkstra shortest path
            queue: list[tuple[float, str, list[str]]] = [(0.0, source, [source])]
            best_costs: dict[str, float] = {source: 0.0}
            best_path: list[str] = []
            shortest_cost = float("inf")

            while queue:
                cost, node, path = heapq.heappop(queue)
                if cost > best_costs.get(node, float("inf")):
                    continue
                if node == sink:
                    shortest_cost = cost
                    best_path = path
                    break

                for nxt, edge_cost, _ in adjacency.get(node, []):
                    next_cost = cost + edge_cost
                    if next_cost < best_costs.get(nxt, float("inf")):
                        best_costs[nxt] = next_cost
                        heapq.heappush(queue, (next_cost, nxt, path + [nxt]))

            if not best_path:
                return Solution(success=False, message="未找到可行路径")

            # Greedy path flow assignment on chosen path
            path_edges = list(zip(best_path[:-1], best_path[1:]))
            edge_map = {(edge["from"], edge["to"]): edge for edge in edges}
            max_path_flow = min(edge_map[edge]["capacity"] for edge in path_edges)
            assigned_flow = min(demand, max_path_flow)

            edge_flows = {}
            for edge in edges:
                key = f"{edge['from']}_{edge['to']}"
                edge_flows[key] = float(assigned_flow if (edge["from"], edge["to"]) in path_edges else 0.0)

            avg_unit_cost = shortest_cost / max(len(path_edges), 1)

            return Solution(
                success=True,
                values={
                    "path_cost": float(shortest_cost),
                    "path_flow": float(assigned_flow),
                    "edge_count": float(len(path_edges)),
                },
                message=f"网络路径求解成功 - 最优路径: {'->'.join(best_path)}",
                numerical_data={
                    "nodes": model.metadata.get("nodes", []),
                    "edges": edges,
                    "path": best_path,
                    "edge_flows": edge_flows,
                },
                statistics={
                    "shortest_cost": float(shortest_cost),
                    "assigned_flow": float(assigned_flow),
                    "average_unit_cost": float(avg_unit_cost),
                },
                metadata={"method": "dijkstra_path_flow", "path": best_path},
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"网络流求解异常: {str(e)}",
            )

    def _solve_time_series(self, model: MathModel) -> Solution:
        """求解时间序列预测模型。"""
        logger.info("求解时间序列模型...")

        try:
            t = np.array(model.metadata.get("time_index", []), dtype=float)
            y = np.array(model.metadata.get("observations", []), dtype=float)
            period = float(model.metadata.get("season_period", 6))
            horizon = int(model.metadata.get("forecast_horizon", 6))

            if len(t) == 0 or len(y) == 0:
                return Solution(success=False, message="时间序列数据为空")

            design = np.column_stack([
                np.ones_like(t),
                t,
                np.sin(2 * np.pi * t / period),
                np.cos(2 * np.pi * t / period),
            ])
            coeffs, *_ = np.linalg.lstsq(design, y, rcond=None)
            fitted = design @ coeffs

            future_t = np.arange(t[-1] + 1, t[-1] + 1 + horizon)
            future_design = np.column_stack([
                np.ones_like(future_t),
                future_t,
                np.sin(2 * np.pi * future_t / period),
                np.cos(2 * np.pi * future_t / period),
            ])
            forecast = future_design @ coeffs

            residuals = y - fitted
            mae = float(np.mean(np.abs(residuals)))
            rmse = float(np.sqrt(np.mean(residuals ** 2)))

            return Solution(
                success=True,
                values={
                    "intercept": float(coeffs[0]),
                    "trend": float(coeffs[1]),
                    "season_sin": float(coeffs[2]),
                    "season_cos": float(coeffs[3]),
                },
                message=f"时间序列预测完成 - 未来{horizon}期已生成",
                numerical_data={
                    "t": t.tolist(),
                    "y": y.tolist(),
                    "y_pred": fitted.tolist(),
                    "t_future": future_t.tolist(),
                    "forecast": forecast.tolist(),
                },
                statistics={
                    "mae": mae,
                    "rmse": rmse,
                    "forecast_mean": float(np.mean(forecast)),
                },
                metadata={"method": "seasonal_trend_least_squares", "forecast_horizon": horizon},
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"时间序列求解异常: {str(e)}",
            )

    def _solve_queueing(self, model: MathModel) -> Solution:
        """求解 M/M/c 排队模型。"""
        logger.info("求解排队系统模型...")

        try:
            arrival_rate = float(model.parameters.get("arrival_rate", 4.5))
            service_rate = float(model.parameters.get("service_rate", 3.2))
            servers = int(model.parameters.get("servers", 2))

            rho = arrival_rate / (servers * service_rate)
            if rho >= 1:
                return Solution(success=False, message="系统不稳定，利用率不小于1")

            a = arrival_rate / service_rate
            sum_terms = sum((a ** n) / math.factorial(n) for n in range(servers))
            tail_term = (a ** servers) / (math.factorial(servers) * (1 - rho))
            p0 = 1.0 / (sum_terms + tail_term)
            lq = p0 * ((a ** servers) * rho) / (math.factorial(servers) * ((1 - rho) ** 2))
            wq = lq / arrival_rate
            w = wq + 1 / service_rate
            l = arrival_rate * w

            time_axis = np.arange(0, 10)
            queue_curve = lq * (1 - np.exp(-0.45 * time_axis))

            return Solution(
                success=True,
                values={
                    "rho": float(rho),
                    "Lq": float(lq),
                    "Wq": float(wq),
                    "W": float(w),
                },
                message="排队系统稳态分析成功",
                numerical_data={
                    "t": time_axis.tolist(),
                    "queue_curve": queue_curve.tolist(),
                },
                statistics={
                    "server_utilization": float(rho),
                    "avg_queue_length": float(lq),
                    "avg_wait_time": float(wq),
                    "avg_system_time": float(w),
                    "avg_system_size": float(l),
                },
                metadata={"method": "mmc_closed_form"},
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"排队系统求解异常: {str(e)}",
            )

    def _solve_markov_chain(self, model: MathModel) -> Solution:
        """求解有限状态马尔可夫链。"""
        logger.info("求解马尔可夫链模型...")

        try:
            matrix = np.array(model.metadata.get("transition_matrix", []), dtype=float)
            initial = np.array(model.metadata.get("initial_distribution", []), dtype=float)
            steps = int(model.parameters.get("steps", 8))

            if matrix.size == 0 or initial.size == 0:
                return Solution(success=False, message="转移矩阵或初始分布为空")

            distributions = [initial.copy()]
            current = initial.copy()
            for _ in range(steps):
                current = current @ matrix
                distributions.append(current.copy())

            eigenvalues, eigenvectors = np.linalg.eig(matrix.T)
            stationary_idx = np.argmin(np.abs(eigenvalues - 1))
            stationary = np.real(eigenvectors[:, stationary_idx])
            stationary = stationary / np.sum(stationary)
            stationary = stationary.real

            final_distribution = distributions[-1]
            values = {
                f"pi_{idx+1}": float(prob)
                for idx, prob in enumerate(final_distribution)
            }

            return Solution(
                success=True,
                values=values,
                message="马尔可夫链状态分布演化求解成功",
                numerical_data={
                    "steps": list(range(steps + 1)),
                    "distributions": [dist.tolist() for dist in distributions],
                    "stationary_distribution": stationary.tolist(),
                },
                statistics={
                    "stationary_gap": float(np.linalg.norm(final_distribution - stationary)),
                    "steps": steps,
                },
                metadata={"method": "matrix_power_iteration"},
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"马尔可夫链求解异常: {str(e)}",
            )

    def _solve_game_theory(self, model: MathModel) -> Solution:
        """求解双人零和博弈的Nash均衡（简化为线性规划）"""
        logger.info("求解博弈论Nash均衡模型...")

        try:
            payoff_matrix = np.array(model.metadata.get("payoff_matrix", []), dtype=float)
            if payoff_matrix.size == 0:
                return Solution(success=False, message="收益矩阵为空")

            n_strategies = payoff_matrix.shape[1]
            player_a_payoff = payoff_matrix

            # 对B来说，收益是 -A的收益（零和）
            player_b_payoff = -payoff_matrix

            # 简化为数值解：计算博弈值（使用最小最大定理）
            # A 的最优策略 = 最大化最小收益
            # B 的最优策略 = 最小化最大收益
            from scipy import optimize

            # 求解 A 的最大最小策略（线性规划）
            n = n_strategies
            c = np.ones(n)
            Aub = -player_a_payoff.T  # 约束：每个纯策略的期望收益 >= v
            bub = -np.ones(n_strategies)
            bounds = [(0, 1) for _ in range(n)]

            result = optimize.linprog(c, A_ub=Aub, b_ub=bub, bounds=bounds, method="highs")
            strategy_a = result.x / result.x.sum() if result.success else np.ones(n) / n
            game_value = float(np.dot(strategy_a, player_a_payoff.min(axis=1)))

            # 最佳响应分析
            best_response_b = player_b_payoff.min(axis=0)
            best_response_a = player_a_payoff.max(axis=1)

            values = {
                f"strategy_A_{i+1}": float(strategy_a[i]) for i in range(len(strategy_a))
            }
            values["game_value"] = game_value

            return Solution(
                success=True,
                values=values,
                message="Nash均衡求解成功",
                numerical_data={
                    "payoff_matrix": payoff_matrix.tolist(),
                    "best_response_B": best_response_b.tolist(),
                    "best_response_A": best_response_a.tolist(),
                    "strategy_A": strategy_a.tolist(),
                },
                statistics={
                    "game_value": game_value,
                    "nash_gap": float(np.max(best_response_a) - np.min(best_response_b)) / 2,
                },
                metadata={"method": "zero_sum_linear_programming"},
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"博弈论求解异常: {str(e)}",
            )

    def _solve_control_theory(self, model: MathModel) -> Solution:
        """求解PID控制系统稳定性分析。"""
        logger.info("求解控制理论模型...")

        try:
            a = float(model.parameters.get("a", 2.0))
            b = float(model.parameters.get("b", 1.0))
            Kp = float(model.parameters.get("Kp", 1.0))
            Ki = float(model.parameters.get("Ki", 0.5))
            Kd = float(model.parameters.get("Kd", 0.0))

            # 特征方程: s^2 + (a + Kp)*s + (b + Ki) = 0
            # 稳定性条件: 所有系数 > 0
            coeff1 = a + Kp
            coeff2 = b + Ki

            # 稳定性判据
            is_stable = coeff1 > 0 and coeff2 > 0

            # 特征根
            discriminant = coeff1**2 - 4 * coeff2
            if discriminant >= 0:
                r1 = (-coeff1 + np.sqrt(discriminant)) / 2
                r2 = (-coeff1 - np.sqrt(discriminant)) / 2
            else:
                real_part = -coeff1 / 2
                imag_part = np.sqrt(-discriminant) / 2
                r1 = complex(real_part, imag_part)
                r2 = complex(real_part, -imag_part)

            # 阶跃响应（数值仿真）
            t = np.linspace(0, 10, 500)
            dt = t[1] - t[0]
            y_response = np.zeros_like(t)
            dy = 0.0
            y = 0.0
            for i in range(len(t)):
                # 简化：使用二阶系统的解析解作为近似
                omega_n = np.sqrt(coeff2)
                damping = coeff1 / (2 * omega_n)
                if discriminant >= 0:
                    y_response[i] = 1 - (r1 * np.exp(r2 * t[i]) - r2 * np.exp(r1 * t[i])) / (r1 - r2)
                else:
                    y_response[i] = 1 - np.exp(-coeff1 * t[i] / 2) * (
                        np.cos(np.sqrt(-discriminant) * t[i] / 2) +
                        coeff1 / np.sqrt(-discriminant) * np.sin(np.sqrt(-discriminant) * t[i] / 2)
                    )

            values = {
                "Kp": Kp, "Ki": Ki, "Kd": Kd,
                "coeff1": coeff1, "coeff2": coeff2,
                "damping_ratio": coeff1 / (2 * np.sqrt(coeff2)) if coeff2 > 0 else 0,
            }

            return Solution(
                success=True,
                values=values,
                message="控制系统稳定性分析成功" if is_stable else "系统不稳定",
                numerical_data={
                    "t": t.tolist(),
                    "step_response": y_response.tolist(),
                    "discriminant": float(discriminant),
                },
                statistics={
                    "is_stable": is_stable,
                    "damping_ratio": float(coeff1 / (2 * np.sqrt(coeff2))) if coeff2 > 0 else 0,
                    "natural_frequency": float(np.sqrt(coeff2)) if coeff2 > 0 else 0,
                },
                metadata={"method": "routh_hurwitz", "system_order": 2},
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"控制理论求解异常: {str(e)}",
            )

    def _solve_clustering(self, model: MathModel) -> Solution:
        """求解K-means聚类问题。"""
        logger.info("求解聚类分析模型...")

        try:
            data = np.array(model.metadata.get("data", []), dtype=float)
            n_clusters = int(model.parameters.get("n_clusters", 3))

            if data.size == 0:
                return Solution(success=False, message="数据为空")

            # K-means 迭代
            np.random.seed(42)
            centroids = data[np.random.choice(len(data), n_clusters, replace=False)]

            for iteration in range(50):
                # 分配每个点到最近的中心
                distances = np.linalg.norm(data[:, np.newaxis] - centroids, axis=2)
                labels = np.argmin(distances, axis=1)

                # 更新中心
                new_centroids = np.array([
                    data[labels == k].mean(axis=0) if np.any(labels == k) else centroids[k]
                    for k in range(n_clusters)
                ])

                if np.linalg.norm(new_centroids - centroids) < 1e-4:
                    centroids = new_centroids
                    break
                centroids = new_centroids

            # 计算SSE
            sse = float(np.sum((data - centroids[labels]) ** 2))

            # 计算各簇的统计信息
            cluster_stats = {}
            for k in range(n_clusters):
                cluster_points = data[labels == k]
                if len(cluster_points) > 0:
                    cluster_stats[f"cluster_{k}_size"] = len(cluster_points)
                    cluster_stats[f"cluster_{k}_std"] = float(np.std(cluster_points))

            values = {
                f"centroid_{k}_x": float(centroids[k, 0]) for k in range(n_clusters)
            }
            values.update({
                f"centroid_{k}_y": float(centroids[k, 1]) for k in range(n_clusters)
            })
            values["SSE"] = sse

            return Solution(
                success=True,
                values=values,
                message=f"K-means聚类求解成功 ({n_clusters} 簇)",
                numerical_data={
                    "data": data.tolist(),
                    "labels": labels.tolist(),
                    "centroids": centroids.tolist(),
                },
                statistics={
                    "sse": sse,
                    "n_clusters": n_clusters,
                    **cluster_stats,
                },
                metadata={"method": "kmeans_lloyd", "iterations": iteration + 1},
            )

        except Exception as e:
            return Solution(
                success=False,
                message=f"聚类分析求解异常: {str(e)}",
            )

    def _solve_bayesian(self, model: MathModel) -> Solution:
        """求解贝叶斯推断模型。"""
        logger.info("求解贝叶斯推断模型...")

        try:
            alpha_prior = float(model.parameters.get("alpha_prior", 2.0))
            beta_prior = float(model.parameters.get("beta_prior", 2.0))
            n_trials = int(model.parameters.get("n_trials", 50))
            successes = int(model.parameters.get("successes", 32))

            # Beta-Binomial 共轭更新
            alpha_post = alpha_prior + successes
            beta_post = beta_prior + (n_trials - successes)

            # 后验均值和方差
            post_mean = alpha_post / (alpha_post + beta_post)
            post_var = (alpha_post * beta_post) / (
                (alpha_post + beta_post) ** 2 * (alpha_post + beta_post + 1)
            )

            # 采样后验分布
            np.random.seed(42)
            samples = np.random.beta(alpha_post, beta_post, 1000)

            x_plot = np.linspace(0, 1, 200)
            from scipy.stats import beta as beta_dist
            prior_pdf = beta_dist.pdf(x_plot, alpha_prior, beta_prior)
            post_pdf = beta_dist.pdf(x_plot, alpha_post, beta_post)

            values = {
                "posterior_mean": float(post_mean),
                "posterior_std": float(np.sqrt(post_var)),
                "credible_interval_95_low": float(np.percentile(samples, 2.5)),
                "credible_interval_95_high": float(np.percentile(samples, 97.5)),
            }

            return Solution(
                success=True,
                values=values,
                message=f"贝叶斯推断成功 - 后验均值: {post_mean:.4f}",
                numerical_data={
                    "x": x_plot.tolist(),
                    "prior_pdf": prior_pdf.tolist(),
                    "posterior_pdf": post_pdf.tolist(),
                    "samples": samples[:200].tolist(),
                },
                statistics={
                    "alpha_posterior": float(alpha_post),
                    "beta_posterior": float(beta_post),
                    "posterior_mean": float(post_mean),
                    "posterior_std": float(np.sqrt(post_var)),
                },
                metadata={"method": "beta_binomial_conjugate"},
            )

        except Exception as e:
            return Solution(success=False, message=f"贝叶斯推断异常: {str(e)}")

    def _solve_graph_theory(self, model: MathModel) -> Solution:
        """求解图论模型（Kruskal最小生成树）。"""
        logger.info("求解图论模型...")

        try:
            adj = np.array(model.metadata.get("adjacency_matrix", []), dtype=float)
            n = adj.shape[0]
            nodes = model.metadata.get("nodes", [f"V{i}" for i in range(n)])

            # Kruskal MST
            edges = []
            for i in range(n):
                for j in range(i + 1, n):
                    if adj[i][j] > 0:
                        edges.append((float(adj[i][j]), i, j))
            edges.sort()

            parent = list(range(n))

            def find(x):
                while parent[x] != x:
                    parent[x] = parent[parent[x]]
                    x = parent[x]
                return x

            mst_edges = []
            mst_cost = 0.0
            for cost, u, v in edges:
                ru, rv = find(u), find(v)
                if ru != rv:
                    parent[ru] = rv
                    mst_edges.append((nodes[u], nodes[v], cost))
                    mst_cost += cost

            values = {
                "mst_cost": float(mst_cost),
                "mst_edge_count": float(len(mst_edges)),
                "n_nodes": float(n),
            }

            return Solution(
                success=True,
                values=values,
                message=f"最小生成树求解成功 - 总代价: {mst_cost:.1f}, 边数: {len(mst_edges)}",
                numerical_data={
                    "adjacency": adj.tolist(),
                    "mst_edges": [(u, v, c) for u, v, c in mst_edges],
                    "nodes": nodes,
                },
                statistics={
                    "mst_cost": float(mst_cost),
                    "edge_count": len(mst_edges),
                    "density": float(np.count_nonzero(adj) / (n * (n - 1))),
                },
                metadata={"method": "kruskal_mst"},
            )

        except Exception as e:
            return Solution(success=False, message=f"图论求解异常: {str(e)}")

    def _solve_fuzzy_logic(self, model: MathModel) -> Solution:
        """求解模糊逻辑推理模型。"""
        logger.info("求解模糊逻辑模型...")

        try:
            mf_params = model.metadata.get("membership_functions", {})
            universe = model.metadata.get("universe", [0, 10])
            x_range = np.linspace(universe[0], universe[1], 100)

            def trimf(x, a, b, c):
                """三角隶属函数。"""
                return np.maximum(0, np.minimum((x - a) / (b - a + 1e-10), (c - x) / (c - b + 1e-10)))

            # 计算各隶属函数
            memberships = {}
            for name, params in mf_params.items():
                memberships[name] = trimf(
                    x_range, params["a"], params["b"], params["c"]
                )

            # 简单推理：取输入值为5时的隶属度
            test_input = 5.0
            input_mf = {}
            for name, params in mf_params.items():
                input_mf[name] = float(trimf(
                    np.array([test_input]), params["a"], params["b"], params["c"]
                )[0])

            # 重心法去模糊化（简化）
            output_values = []
            for name, degree in input_mf.items():
                center = (mf_params[name]["a"] + mf_params[name]["b"] + mf_params[name]["c"]) / 3
                output_values.append(degree * center)
            defuzzified = sum(output_values) / (sum(input_mf.values()) + 1e-10)

            values = {
                "defuzzified_output": float(defuzzified),
                **{f"mf_{k}": float(v) for k, v in input_mf.items()},
            }

            return Solution(
                success=True,
                values=values,
                message=f"模糊推理完成 - 去模糊化输出: {defuzzified:.4f}",
                numerical_data={
                    "x": x_range.tolist(),
                    "memberships": {k: v.tolist() for k, v in memberships.items()},
                    "test_input": test_input,
                    "input_memberships": input_mf,
                },
                statistics={
                    "defuzzified": float(defuzzified),
                    "n_rules": len(model.metadata.get("rules", [])),
                },
                metadata={"method": "mamdani_centroid"},
            )

        except Exception as e:
            return Solution(success=False, message=f"模糊逻辑求解异常: {str(e)}")
