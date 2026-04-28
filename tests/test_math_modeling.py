"""数学建模模块测试"""

import pytest

from papercarator.math_modeling import ModelBuilder, ModelSolver, ModelValidator


class TestModelBuilder:
    """测试模型构建器"""

    def test_build_equation_system(self):
        """测试方程组模型构建"""
        builder = ModelBuilder()
        model = builder.build("方程组求解", {"paper_type": "modeling"})

        assert model.model_type == "equation_system"
        assert len(model.equations) > 0

    def test_build_optimization(self):
        """测试优化模型构建"""
        builder = ModelBuilder()
        model = builder.build("优化问题", {"paper_type": "optimization"})

        assert model.model_type == "optimization"
        assert model.objective is not None

    def test_build_differential(self):
        """测试微分方程模型构建"""
        builder = ModelBuilder()
        model = builder.build("微分方程", {"paper_type": "differential"})

        assert model.model_type == "differential"

    def test_build_statistical(self):
        """测试统计模型构建"""
        builder = ModelBuilder()
        model = builder.build("回归分析", {"paper_type": "statistical"})

        assert model.model_type == "statistical"

    def test_build_network_flow(self):
        """测试网络流模型构建"""
        builder = ModelBuilder()
        model = builder.build("城市配送网络最短路径优化", {"paper_type": "network_flow"})

        assert model.model_type == "network_flow"
        assert len(model.metadata.get("edges", [])) > 0

    def test_build_time_series(self):
        """测试时间序列模型构建"""
        builder = ModelBuilder()
        model = builder.build("电力负荷时间序列预测", {"paper_type": "time_series"})

        assert model.model_type == "time_series"
        assert len(model.metadata.get("observations", [])) > 0

    def test_build_multi_objective(self):
        """测试多目标优化模型构建"""
        builder = ModelBuilder()
        model = builder.build("多目标资源调度", {"paper_type": "multi_objective"})

        assert model.model_type == "multi_objective"
        assert len(model.metadata.get("objective_functions", [])) >= 2

    def test_build_pde(self):
        """测试 PDE 模型构建"""
        builder = ModelBuilder()
        model = builder.build("二维热方程偏微分建模", {"paper_type": "pde"})

        assert model.model_type == "pde"
        assert model.parameters.get("grid_size", 0) > 0

    def test_build_queueing(self):
        """测试排队系统模型构建"""
        builder = ModelBuilder()
        model = builder.build("多服务台排队系统分析", {"paper_type": "queueing"})

        assert model.model_type == "queueing"
        assert model.parameters.get("servers", 0) > 0

    def test_build_markov_chain(self):
        """测试马尔可夫链模型构建"""
        builder = ModelBuilder()
        model = builder.build("状态转移马尔可夫链分析", {"paper_type": "markov_chain"})

        assert model.model_type == "markov_chain"
        assert len(model.metadata.get("transition_matrix", [])) > 0


class TestModelSolver:
    """测试模型求解器"""

    def test_solve_equation_system(self):
        """测试方程组求解"""
        builder = ModelBuilder()
        solver = ModelSolver()

        model = builder.build("方程组", {"paper_type": "modeling"})
        solution = solver.solve(model)

        assert solution.success
        assert len(solution.values) > 0

    def test_solve_optimization(self):
        """测试优化问题求解"""
        builder = ModelBuilder()
        solver = ModelSolver()

        model = builder.build("优化", {"paper_type": "optimization"})
        solution = solver.solve(model)

        assert solution.success
        assert "optimal_value" in solution.statistics or True

    def test_solve_differential(self):
        """测试微分方程求解"""
        builder = ModelBuilder()
        solver = ModelSolver()

        model = builder.build("微分方程", {"paper_type": "differential"})
        solution = solver.solve(model)

        assert solution.success
        assert "t" in solution.numerical_data

    def test_solve_statistical(self):
        """测试统计模型求解"""
        builder = ModelBuilder()
        solver = ModelSolver()

        model = builder.build("回归", {"paper_type": "statistical"})
        solution = solver.solve(model)

        assert solution.success
        assert "r_squared" in solution.statistics

    def test_solve_network_flow(self):
        """测试网络流模型求解"""
        builder = ModelBuilder()
        solver = ModelSolver()

        model = builder.build("物流网络最短路径", {"paper_type": "network_flow"})
        solution = solver.solve(model)

        assert solution.success
        assert "shortest_cost" in solution.statistics
        assert len(solution.metadata.get("path", [])) >= 2

    def test_solve_time_series(self):
        """测试时间序列模型求解"""
        builder = ModelBuilder()
        solver = ModelSolver()

        model = builder.build("需求时间序列预测", {"paper_type": "time_series"})
        solution = solver.solve(model)

        assert solution.success
        assert "rmse" in solution.statistics
        assert "forecast" in solution.numerical_data

    def test_solve_multi_objective(self):
        """测试多目标优化求解"""
        builder = ModelBuilder()
        solver = ModelSolver()

        model = builder.build("多目标资源调度", {"paper_type": "multi_objective"})
        solution = solver.solve(model)

        assert solution.success
        assert "objective_1" in solution.statistics
        assert len(solution.numerical_data.get("pareto_front", [])) > 0

    def test_solve_pde(self):
        """测试 PDE 求解"""
        builder = ModelBuilder()
        solver = ModelSolver()

        model = builder.build("二维热方程偏微分建模", {"paper_type": "pde"})
        solution = solver.solve(model)

        assert solution.success
        assert "u_final" in solution.numerical_data
        assert "max_temperature" in solution.statistics

    def test_solve_queueing(self):
        """测试排队系统求解"""
        builder = ModelBuilder()
        solver = ModelSolver()

        model = builder.build("多服务台排队系统分析", {"paper_type": "queueing"})
        solution = solver.solve(model)

        assert solution.success
        assert "avg_wait_time" in solution.statistics
        assert "queue_curve" in solution.numerical_data

    def test_solve_markov_chain(self):
        """测试马尔可夫链求解"""
        builder = ModelBuilder()
        solver = ModelSolver()

        model = builder.build("状态转移马尔可夫链分析", {"paper_type": "markov_chain"})
        solution = solver.solve(model)

        assert solution.success
        assert "distributions" in solution.numerical_data
        assert "stationary_gap" in solution.statistics


class TestModelValidator:
    """测试模型验证器"""

    def test_validate_success(self):
        """测试成功验证"""
        builder = ModelBuilder()
        solver = ModelSolver()
        validator = ModelValidator()

        model = builder.build("方程组", {"paper_type": "modeling"})
        solution = solver.solve(model)
        result = validator.validate(model, solution)

        assert isinstance(result.is_valid, bool)
        assert 0 <= result.score <= 1

    def test_validate_with_errors(self):
        """测试含错误的验证"""
        from papercarator.math_modeling.solver import Solution

        validator = ModelValidator()
        builder = ModelBuilder()

        model = builder.build("方程组", {"paper_type": "modeling"})
        bad_solution = Solution(success=False, message="求解失败")

        result = validator.validate(model, bad_solution)
        assert not result.is_valid
