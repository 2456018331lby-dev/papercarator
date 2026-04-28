"""模型验证器 - 验证数学模型的正确性和结果合理性"""

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from loguru import logger

from papercarator.math_modeling.model_builder import MathModel
from papercarator.math_modeling.solver import Solution


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    checks: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    score: float = 0.0  # 0-1之间的验证得分


class ModelValidator:
    """数学模型验证器

    验证模型的正确性、解的合理性等。
    """

    def __init__(self, tolerance: float = 1e-6):
        self.tolerance = tolerance
        logger.info(f"初始化 ModelValidator (tolerance={tolerance})")

    def validate(self, model: MathModel, solution: Solution) -> ValidationResult:
        """验证模型和解

        Args:
            model: MathModel对象
            solution: Solution对象

        Returns:
            ValidationResult对象
        """
        logger.info("开始验证模型...")

        result = ValidationResult(is_valid=True)

        # 1. 验证求解是否成功
        self._check_solution_success(result, solution)

        # 2. 验证解的合理性
        if solution.success:
            self._check_solution_reasonableness(result, model, solution)

        # 3. 验证模型一致性
        self._check_model_consistency(result, model)

        # 4. 计算验证得分
        result.score = self._calculate_score(result)

        # 最终判定
        result.is_valid = len(result.errors) == 0 and result.score >= 0.5

        logger.info(f"验证完成 - 得分: {result.score:.2f}, 有效: {result.is_valid}")
        return result

    def _check_solution_success(self, result: ValidationResult, solution: Solution) -> None:
        """检查求解是否成功"""
        check = {
            "name": "求解成功",
            "passed": solution.success,
            "message": solution.message,
        }
        result.checks.append(check)

        if not solution.success:
            result.errors.append(f"求解失败: {solution.message}")

    def _check_solution_reasonableness(self, result: ValidationResult, model: MathModel, solution: Solution) -> None:
        """检查解的合理性"""
        # 检查数值是否在合理范围内
        for var_name, value in solution.values.items():
            if isinstance(value, (int, float)):
                # 检查是否为NaN或Inf
                if np.isnan(value) or np.isinf(value):
                    result.errors.append(f"变量 {var_name} 的值为非法数值: {value}")
                    check = {
                        "name": f"{var_name} 数值合法",
                        "passed": False,
                        "message": f"值为 {value}",
                    }
                else:
                    # 检查是否过大或过小
                    if abs(value) > 1e10:
                        result.warnings.append(f"变量 {var_name} 的值过大: {value:.2e}")
                    check = {
                        "name": f"{var_name} 数值合理",
                        "passed": True,
                        "message": f"值为 {value:.6f}",
                    }
                result.checks.append(check)

    def _check_model_consistency(self, result: ValidationResult, model: MathModel) -> None:
        """检查模型一致性"""
        # 检查方程数量与变量数量
        if model.model_type == "equation_system":
            n_equations = len(model.equations)
            n_variables = len(model.symbols)

            check = {
                "name": "方程与变量数量匹配",
                "passed": n_equations == n_variables,
                "message": f"方程数: {n_equations}, 变量数: {n_variables}",
            }
            result.checks.append(check)

            if n_equations != n_variables:
                result.warnings.append(
                    f"方程数({n_equations})与变量数({n_variables})不匹配，"
                    f"可能欠定或超定"
                )

        # 检查目标函数（优化问题）
        if model.model_type == "optimization":
            has_objective = model.objective is not None
            check = {
                "name": "目标函数已定义",
                "passed": has_objective,
                "message": "已定义" if has_objective else "未定义",
            }
            result.checks.append(check)

            if not has_objective:
                result.errors.append("优化问题缺少目标函数")

        if model.model_type == "multi_objective":
            objectives = model.metadata.get("objective_functions", [])
            check = {
                "name": "多目标函数已定义",
                "passed": len(objectives) >= 2,
                "message": f"目标数量: {len(objectives)}",
            }
            result.checks.append(check)
            if len(objectives) < 2:
                result.errors.append("多目标优化缺少足够的目标函数")

        if model.model_type == "network_flow":
            has_edges = bool(model.metadata.get("edges"))
            check = {
                "name": "网络边已定义",
                "passed": has_edges,
                "message": f"边数量: {len(model.metadata.get('edges', []))}",
            }
            result.checks.append(check)
            if not has_edges:
                result.errors.append("网络流模型缺少边定义")

        if model.model_type == "time_series":
            observations = model.metadata.get("observations", [])
            check = {
                "name": "时间序列样本充足",
                "passed": len(observations) >= 12,
                "message": f"样本长度: {len(observations)}",
            }
            result.checks.append(check)
            if len(observations) < 12:
                result.warnings.append("时间序列样本较少，预测稳定性有限")

        if model.model_type == "pde":
            grid_size = int(model.parameters.get("grid_size", 0))
            check = {
                "name": "PDE 网格规模有效",
                "passed": grid_size >= 10,
                "message": f"grid_size: {grid_size}",
            }
            result.checks.append(check)
            if grid_size < 10:
                result.warnings.append("PDE 网格较粗，结果仅适合演示")

        if model.model_type == "queueing":
            arrival_rate = float(model.parameters.get("arrival_rate", 0))
            service_rate = float(model.parameters.get("service_rate", 0))
            servers = int(model.parameters.get("servers", 0))
            stable = servers > 0 and service_rate > 0 and arrival_rate < servers * service_rate
            check = {
                "name": "排队系统稳定",
                "passed": stable,
                "message": f"lambda={arrival_rate}, mu={service_rate}, c={servers}",
            }
            result.checks.append(check)
            if not stable:
                result.errors.append("排队系统不稳定或参数非法")

        if model.model_type == "markov_chain":
            matrix = np.array(model.metadata.get("transition_matrix", []), dtype=float)
            rows_ok = matrix.size > 0 and np.allclose(matrix.sum(axis=1), 1.0)
            check = {
                "name": "转移矩阵行归一化",
                "passed": rows_ok,
                "message": "行和接近1" if rows_ok else "存在非法行和",
            }
            result.checks.append(check)
            if not rows_ok:
                result.errors.append("马尔可夫链转移矩阵非法")

    def _calculate_score(self, result: ValidationResult) -> float:
        """计算验证得分"""
        if not result.checks:
            return 0.0

        passed = sum(1 for c in result.checks if c["passed"])
        total = len(result.checks)

        # 基础得分
        score = passed / total if total > 0 else 0.0

        # 根据错误和警告调整
        score -= len(result.errors) * 0.2
        score -= len(result.warnings) * 0.05

        return max(0.0, min(1.0, score))
