"""可视化模块测试"""

from pathlib import Path

import pytest

from papercarator.visualization import ChartGenerator, Model3DGenerator


class TestChartGenerator:
    """测试图表生成器"""

    def test_generate_equation_system(self, tmp_path):
        """测试方程组图表生成"""
        gen = ChartGenerator()

        math_model = {
            "model_type": "equation_system",
            "name": "测试方程组",
        }
        solution = {
            "success": True,
            "values": {"x": 1.0, "y": 2.0, "z": 3.0},
            "message": "求解成功",
        }

        files = gen.generate(math_model, solution, tmp_path)
        assert len(files) > 0
        assert all(f.exists() for f in files)

    def test_generate_optimization(self, tmp_path):
        """测试优化图表生成"""
        gen = ChartGenerator()

        math_model = {
            "model_type": "optimization",
            "name": "测试优化",
        }
        solution = {
            "success": True,
            "values": {"x": 1.0, "y": 2.0},
            "statistics": {"optimal_value": 0.5},
        }

        files = gen.generate(math_model, solution, tmp_path)
        assert len(files) > 0

    def test_generate_differential(self, tmp_path):
        """测试微分方程图表生成"""
        gen = ChartGenerator()

        math_model = {
            "model_type": "differential",
            "name": "测试微分方程",
        }
        solution = {
            "success": True,
            "values": {"omega": 2.0},
            "numerical_data": {
                "t": [0, 1, 2],
                "x": [1, 0.5, 0],
                "v": [0, -1, -2],
            },
        }

        files = gen.generate(math_model, solution, tmp_path)
        assert len(files) > 0

    def test_generate_statistical(self, tmp_path):
        """测试统计图表生成"""
        gen = ChartGenerator()

        math_model = {
            "model_type": "statistical",
            "name": "测试回归",
        }
        solution = {
            "success": True,
            "values": {"intercept": 1.0, "slope": 2.5},
            "numerical_data": {
                "x": [1, 2, 3],
                "y": [3, 5, 7],
                "y_pred": [3.5, 6.0, 8.5],
            },
            "statistics": {"r_squared": 0.95},
        }

        files = gen.generate(math_model, solution, tmp_path)
        assert len(files) > 0

    def test_generate_network_flow(self, tmp_path):
        """测试网络流图表生成"""
        gen = ChartGenerator()

        math_model = {
            "model_type": "network_flow",
            "name": "测试网络流",
        }
        solution = {
            "success": True,
            "values": {"path_cost": 6.0},
            "numerical_data": {
                "edges": [
                    {"from": "S", "to": "A", "capacity": 10, "cost": 2},
                    {"from": "A", "to": "T", "capacity": 8, "cost": 4},
                ],
                "path": ["S", "A", "T"],
                "edge_flows": {"S_A": 8.0, "A_T": 8.0},
            },
        }

        files = gen.generate(math_model, solution, tmp_path)
        assert len(files) > 0

    def test_generate_time_series(self, tmp_path):
        """测试时间序列图表生成"""
        gen = ChartGenerator()

        math_model = {
            "model_type": "time_series",
            "name": "测试时间序列",
        }
        solution = {
            "success": True,
            "numerical_data": {
                "t": [0, 1, 2, 3],
                "y": [10, 12, 11, 13],
                "y_pred": [10.2, 11.8, 11.4, 12.9],
                "t_future": [4, 5],
                "forecast": [14.1, 14.8],
            },
            "statistics": {"rmse": 0.42},
        }

        files = gen.generate(math_model, solution, tmp_path)
        assert len(files) > 0

    def test_generate_multi_objective(self, tmp_path):
        """测试多目标优化图表生成"""
        gen = ChartGenerator()

        math_model = {"model_type": "multi_objective", "name": "测试多目标"}
        solution = {
            "success": True,
            "numerical_data": {
                "pareto_front": [
                    {"f1": 1.0, "f2": 4.0},
                    {"f1": 2.0, "f2": 3.0},
                    {"f1": 3.0, "f2": 2.2},
                ],
                "selected_point": {"f1": 2.0, "f2": 3.0},
            },
        }

        files = gen.generate(math_model, solution, tmp_path)
        assert len(files) > 0

    def test_generate_pde(self, tmp_path):
        """测试 PDE 图表生成"""
        gen = ChartGenerator()

        grid = [
            [0.0, 0.1, 0.0],
            [0.1, 0.8, 0.1],
            [0.0, 0.1, 0.0],
        ]
        math_model = {"model_type": "pde", "name": "测试PDE"}
        solution = {
            "success": True,
            "numerical_data": {
                "x": [0.0, 0.5, 1.0],
                "y": [0.0, 0.5, 1.0],
                "u_initial": grid,
                "u_mid": grid,
                "u_final": grid,
            },
        }

        files = gen.generate(math_model, solution, tmp_path)
        assert len(files) > 0

    def test_generate_queueing(self, tmp_path):
        """测试排队系统图表生成"""
        gen = ChartGenerator()

        math_model = {"model_type": "queueing", "name": "测试排队"}
        solution = {
            "success": True,
            "numerical_data": {
                "t": [0, 1, 2, 3],
                "queue_curve": [0.0, 0.8, 1.2, 1.4],
            },
            "statistics": {
                "server_utilization": 0.7,
                "avg_queue_length": 1.4,
                "avg_wait_time": 0.32,
                "avg_system_time": 0.63,
            },
        }

        files = gen.generate(math_model, solution, tmp_path)
        assert len(files) > 0

    def test_generate_markov_chain(self, tmp_path):
        """测试马尔可夫链图表生成"""
        gen = ChartGenerator()

        math_model = {"model_type": "markov_chain", "name": "测试马尔可夫链"}
        solution = {
            "success": True,
            "numerical_data": {
                "steps": [0, 1, 2],
                "distributions": [
                    [0.6, 0.3, 0.1],
                    [0.5, 0.35, 0.15],
                    [0.46, 0.36, 0.18],
                ],
                "stationary_distribution": [0.4, 0.37, 0.23],
            },
        }

        files = gen.generate(math_model, solution, tmp_path)
        assert len(files) > 0


class TestModel3DGenerator:
    """测试3D模型生成器"""

    def test_generate_math_surface(self, tmp_path):
        """测试数学曲面生成"""
        gen = Model3DGenerator()

        files = gen.generate("数学曲面", {"model_type": "equation_system"}, tmp_path)
        assert len(files) > 0
        assert all(f.exists() for f in files)

    def test_generate_flow(self, tmp_path):
        """测试流体可视化生成"""
        gen = Model3DGenerator()

        files = gen.generate("流体仿真", {"model_type": "differential"}, tmp_path)
        assert len(files) > 0

    def test_generate_heat(self, tmp_path):
        """测试热传导可视化生成"""
        gen = Model3DGenerator()

        files = gen.generate("热传导", {"model_type": "differential"}, tmp_path)
        assert len(files) > 0

    def test_generate_network_3d(self, tmp_path):
        """测试网络3D示意生成"""
        gen = Model3DGenerator()

        files = gen.generate("物流网络优化", {"model_type": "network_flow"}, tmp_path)
        assert len(files) > 0

    def test_generate_time_series_surface(self, tmp_path):
        """测试时间序列3D曲面生成"""
        gen = Model3DGenerator()

        files = gen.generate(
            "时间序列预测",
            {"model_type": "time_series", "metadata": {"observations": [10, 12, 11, 13, 15, 14]}},
            tmp_path,
        )
        assert len(files) > 0

    def test_generate_pareto_surface(self, tmp_path):
        """测试多目标3D曲面生成"""
        gen = Model3DGenerator()

        files = gen.generate("多目标优化", {"model_type": "multi_objective"}, tmp_path)
        assert len(files) > 0

    def test_generate_pde_surface(self, tmp_path):
        """测试 PDE 3D曲面生成"""
        gen = Model3DGenerator()

        files = gen.generate("二维热方程偏微分", {"model_type": "pde", "parameters": {"grid_size": 12}}, tmp_path)
        assert len(files) > 0

    def test_generate_queueing_3d(self, tmp_path):
        """测试排队系统 3D 示意生成"""
        gen = Model3DGenerator()

        files = gen.generate("排队系统分析", {"model_type": "queueing", "parameters": {"arrival_rate": 4.5, "service_rate": 3.2, "servers": 2}}, tmp_path)
        assert len(files) > 0

    def test_generate_markov_3d(self, tmp_path):
        """测试马尔可夫链 3D 示意生成"""
        gen = Model3DGenerator()

        files = gen.generate(
            "马尔可夫链状态转移",
            {"model_type": "markov_chain", "metadata": {"transition_matrix": [[0.7, 0.2, 0.1], [0.2, 0.6, 0.2], [0.1, 0.3, 0.6]]}},
            tmp_path,
        )
        assert len(files) > 0
