"""题目分析模块测试"""

import pytest

from papercarator.planner import TopicAnalyzer, TaskPlanner


class TestTopicAnalyzer:
    """测试题目分析器"""

    def test_analyze_basic(self):
        """测试基本分析功能"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("基于深度学习的图像分类方法研究")

        assert result["topic"] == "基于深度学习的图像分类方法研究"
        assert "keywords" in result
        assert "paper_type" in result
        assert result["paper_type"] == "modeling"

    def test_analyze_optimization(self):
        """测试优化类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("资源配置优化问题研究")

        assert result["paper_type"] == "optimization"
        assert "optimization" in result["research_methods"]

    def test_analyze_differential(self):
        """测试微分方程类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("热传导方程的数值解法")

        assert result["paper_type"] == "differential"

    def test_analyze_mixed_optimization_priority(self):
        """测试混合关键词题目的类型优先级"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("基于优化理论的资源配置问题研究")

        assert result["paper_type"] == "optimization"
        assert "optimization" in result["research_methods"]

    def test_analyze_review(self):
        """测试综述类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("深度学习综述")

        assert result["paper_type"] == "review"

    def test_analyze_network_flow(self):
        """测试网络流类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("城市配送网络最短路径优化研究")

        assert result["paper_type"] == "network_flow"
        assert "network_graph" in result["required_visualizations"]

    def test_analyze_time_series(self):
        """测试时间序列类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("电力负荷时间序列预测研究")

        assert result["paper_type"] == "time_series"
        assert "forecasting" in result["research_methods"]

    def test_analyze_multi_objective(self):
        """测试多目标优化类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("多目标资源调度与帕累托优化研究")

        assert result["paper_type"] == "multi_objective"
        assert "pareto_front" in result["required_visualizations"]

    def test_analyze_pde(self):
        """测试偏微分方程类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("二维热方程偏微分建模与数值求解")

        assert result["paper_type"] == "pde"
        assert "surface_plot" in result["required_visualizations"]

    def test_analyze_queueing(self):
        """测试排队系统类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("多服务台排队系统性能分析")

        assert result["paper_type"] == "queueing"
        assert "queue_curve" in result["required_visualizations"]

    def test_analyze_markov_chain(self):
        """测试马尔可夫链类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("设备状态转移的马尔可夫链建模")

        assert result["paper_type"] == "markov_chain"
        assert "state_graph" in result["required_visualizations"]

    def test_analyze_game_theory(self):
        """测试博弈论类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("双人零和博弈的纳什均衡建模分析")

        assert result["paper_type"] == "game_theory"
        assert "payoff_heatmap" in result["required_visualizations"]

    def test_analyze_control_theory(self):
        """测试控制理论类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("PID控制系统稳定性分析与参数整定")

        assert result["paper_type"] == "control_theory"
        assert "step_response" in result["required_visualizations"]

    def test_analyze_clustering(self):
        """测试聚类分析类题目"""
        analyzer = TopicAnalyzer()
        result = analyzer.analyze("基于K-means的客户聚类分析")

        assert result["paper_type"] == "clustering"
        assert "cluster_scatter" in result["required_visualizations"]


class TestTaskPlanner:
    """测试任务规划器"""

    def test_create_plan(self):
        """测试计划创建"""
        planner = TaskPlanner()
        analysis = {
            "topic": "测试题目",
            "paper_type": "modeling",
            "difficulty": "medium",
            "suggested_sections": ["abstract", "introduction", "methodology"],
            "required_visualizations": ["line_chart", "3d_model"],
            "required_math_tools": ["sympy"],
        }

        plan = planner.create_plan(analysis)

        assert plan["topic"] == "测试题目"
        assert len(plan["tasks"]) > 0
        assert plan["tasks"][0]["module"] == "math_modeling"

    def test_task_dependencies(self):
        """测试任务依赖关系"""
        planner = TaskPlanner()
        analysis = {
            "topic": "测试",
            "paper_type": "modeling",
            "difficulty": "easy",
            "suggested_sections": [],
            "required_visualizations": [],
            "required_math_tools": [],
        }

        plan = planner.create_plan(analysis)
        tasks = plan["tasks"]

        # 检查依赖关系
        for task in tasks:
            for dep in task["dependencies"]:
                assert any(t["id"] == dep for t in tasks)
