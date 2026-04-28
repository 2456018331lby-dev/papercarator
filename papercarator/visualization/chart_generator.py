"""图表生成器 - 生成数据可视化图表"""

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
import numpy as np
from loguru import logger


class ChartGenerator:
    """图表生成器

    根据数学模型和求解结果生成各种图表。
    """

    def __init__(self, dpi: int = 300, figsize: tuple[int, int] = (10, 6)):
        self.dpi = dpi
        self.figsize = figsize
        plt.rcParams['font.size'] = 12
        plt.rcParams['axes.unicode_minus'] = False
        logger.info(f"初始化 ChartGenerator (dpi={dpi})")

    def generate(self, math_model: dict[str, Any], solution: dict[str, Any],
                 output_dir: Path) -> list[Path]:
        """生成所有相关图表

        Args:
            math_model: 数学模型字典
            solution: 求解结果字典
            output_dir: 输出目录

        Returns:
            生成的图表文件路径列表
        """
        logger.info("开始生成图表...")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []
        model_type = math_model.get("model_type", "")

        # 根据模型类型生成对应图表
        if model_type == "equation_system":
            files = self._plot_equation_system(math_model, solution, output_dir)
            generated_files.extend(files)

        elif model_type == "optimization":
            files = self._plot_optimization(math_model, solution, output_dir)
            generated_files.extend(files)

        elif model_type == "differential":
            files = self._plot_differential(math_model, solution, output_dir)
            generated_files.extend(files)

        elif model_type == "statistical":
            files = self._plot_statistical(math_model, solution, output_dir)
            generated_files.extend(files)

        elif model_type == "network_flow":
            files = self._plot_network_flow(math_model, solution, output_dir)
            generated_files.extend(files)

        elif model_type == "time_series":
            files = self._plot_time_series(math_model, solution, output_dir)
            generated_files.extend(files)

        elif model_type == "multi_objective":
            files = self._plot_multi_objective(math_model, solution, output_dir)
            generated_files.extend(files)

        elif model_type == "pde":
            files = self._plot_pde(math_model, solution, output_dir)
            generated_files.extend(files)

        elif model_type == "queueing":
            files = self._plot_queueing(math_model, solution, output_dir)
            generated_files.extend(files)

        elif model_type == "markov_chain":
            files = self._plot_markov_chain(math_model, solution, output_dir)
            generated_files.extend(files)

        logger.info(f"图表生成完成 - 共 {len(generated_files)} 个文件")
        return generated_files

    def _plot_equation_system(self, math_model: dict[str, Any],
                              solution: dict[str, Any], output_dir: Path) -> list[Path]:
        """绘制方程组相关图表"""
        files = []

        # 如果有数值解，绘制变量关系
        values = solution.get("values", {})
        if values:
            fig, ax = plt.subplots(figsize=self.figsize)
            vars_list = [k for k, v in values.items() if isinstance(v, (int, float))]
            vals_list = [values[v] for v in vars_list]

            colors = plt.cm.viridis(np.linspace(0, 1, len(vars_list)))
            bars = ax.bar(vars_list, vals_list, color=colors, edgecolor='black', linewidth=1.2)
            ax.set_xlabel('Variable', fontsize=13)
            ax.set_ylabel('Value', fontsize=13)
            ax.set_title('Solution of Equation System', fontsize=15, fontweight='bold')
            ax.grid(axis='y', alpha=0.3)

            # 在柱子上标注数值
            for bar, val in zip(bars, vals_list):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(),
                       f'{val:.4f}', ha='center', va='bottom', fontsize=10)

            filepath = output_dir / "equation_solution.png"
            fig.tight_layout()
            fig.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
            plt.close(fig)
            files.append(filepath)

        return files

    def _plot_optimization(self, math_model: dict[str, Any],
                           solution: dict[str, Any], output_dir: Path) -> list[Path]:
        """绘制优化问题相关图表"""
        files = []
        values = solution.get("values", {})

        if values and len(values) >= 2:
            # 提取两个主要变量
            var_names = list(values.keys())[:2]
            x_opt = values.get(var_names[0], 0)
            y_opt = values.get(var_names[1], 0)

            # 绘制等高线图
            fig, ax = plt.subplots(figsize=self.figsize)

            # 创建网格
            x_range = np.linspace(x_opt - 3, x_opt + 3, 100)
            y_range = np.linspace(y_opt - 3, y_opt + 3, 100)
            X, Y = np.meshgrid(x_range, y_range)

            # 示例目标函数: x^2 + y^2 + xy
            Z = X**2 + Y**2 + X*Y

            contour = ax.contour(X, Y, Z, levels=20, cmap='viridis')
            ax.clabel(contour, inline=True, fontsize=8)
            ax.plot(x_opt, y_opt, 'r*', markersize=15, label='Optimal Point')
            ax.set_xlabel(var_names[0], fontsize=13)
            ax.set_ylabel(var_names[1], fontsize=13)
            ax.set_title('Optimization Landscape', fontsize=15, fontweight='bold')
            ax.legend()
            ax.grid(alpha=0.3)

            filepath = output_dir / "optimization_landscape.png"
            fig.tight_layout()
            fig.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
            plt.close(fig)
            files.append(filepath)

        # 绘制收敛信息
        stats = solution.get("statistics", {})
        if stats:
            fig, ax = plt.subplots(figsize=(8, 5))
            info_text = "\n".join([f"{k}: {v}" for k, v in stats.items()])
            ax.text(0.1, 0.5, info_text, fontsize=12, family='monospace',
                   verticalalignment='center')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title('Optimization Statistics', fontsize=15, fontweight='bold')

            filepath = output_dir / "optimization_stats.png"
            fig.tight_layout()
            fig.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
            plt.close(fig)
            files.append(filepath)

        return files

    def _plot_differential(self, math_model: dict[str, Any],
                           solution: dict[str, Any], output_dir: Path) -> list[Path]:
        """绘制微分方程相关图表"""
        files = []
        numerical = solution.get("numerical_data", {})

        if numerical and "t" in numerical and "x" in numerical:
            t = np.array(numerical["t"])
            x = np.array(numerical["x"])

            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

            # 位移-时间图
            ax1.plot(t, x, 'b-', linewidth=1.5, label='x(t)')
            ax1.set_xlabel('Time (t)', fontsize=13)
            ax1.set_ylabel('Displacement', fontsize=13)
            ax1.set_title('Displacement vs Time', fontsize=14, fontweight='bold')
            ax1.grid(alpha=0.3)
            ax1.legend()

            # 相空间图
            if "v" in numerical:
                v = np.array(numerical["v"])
                ax2.plot(x, v, 'g-', linewidth=1.5)
                ax2.set_xlabel('Displacement (x)', fontsize=13)
                ax2.set_ylabel('Velocity (v)', fontsize=13)
                ax2.set_title('Phase Space Portrait', fontsize=14, fontweight='bold')
                ax2.grid(alpha=0.3)
            else:
                ax2.plot(t[:-1], np.diff(x)/np.diff(t), 'g-', linewidth=1.5)
                ax2.set_xlabel('Time (t)', fontsize=13)
                ax2.set_ylabel('Velocity', fontsize=13)
                ax2.set_title('Velocity vs Time', fontsize=14, fontweight='bold')
                ax2.grid(alpha=0.3)

            filepath = output_dir / "differential_solution.png"
            fig.tight_layout()
            fig.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
            plt.close(fig)
            files.append(filepath)

        return files

    def _plot_statistical(self, math_model: dict[str, Any],
                          solution: dict[str, Any], output_dir: Path) -> list[Path]:
        """绘制统计模型相关图表"""
        files = []
        numerical = solution.get("numerical_data", {})
        stats = solution.get("statistics", {})

        if numerical and "x" in numerical and "y" in numerical:
            x = np.array(numerical["x"])
            y = np.array(numerical["y"])
            y_pred = np.array(numerical.get("y_pred", []))

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

            # 散点图 + 回归线
            ax1.scatter(x, y, alpha=0.5, s=30, label='Data Points', color='steelblue')
            if len(y_pred) > 0:
                ax1.plot(x, y_pred, 'r-', linewidth=2, label='Regression Line')
            ax1.set_xlabel('X', fontsize=13)
            ax1.set_ylabel('Y', fontsize=13)
            ax1.set_title('Linear Regression', fontsize=14, fontweight='bold')
            ax1.legend()
            ax1.grid(alpha=0.3)

            # 残差图
            if len(y_pred) > 0:
                residuals = y - y_pred
                ax2.scatter(y_pred, residuals, alpha=0.5, s=30, color='coral')
                ax2.axhline(y=0, color='black', linestyle='--', linewidth=1)
                ax2.set_xlabel('Predicted Values', fontsize=13)
                ax2.set_ylabel('Residuals', fontsize=13)
                ax2.set_title('Residual Plot', fontsize=14, fontweight='bold')
                ax2.grid(alpha=0.3)

            filepath = output_dir / "regression_analysis.png"
            fig.tight_layout()
            fig.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
            plt.close(fig)
            files.append(filepath)

        # 统计信息图
        if stats:
            fig, ax = plt.subplots(figsize=(8, 5))
            info_lines = []
            for k, v in stats.items():
                if isinstance(v, dict):
                    info_lines.append(f"{k}:")
                    for sk, sv in v.items():
                        info_lines.append(f"  {sk}: {sv:.6f}" if isinstance(sv, float) else f"  {sk}: {sv}")
                else:
                    info_lines.append(f"{k}: {v:.6f}" if isinstance(v, float) else f"{k}: {v}")

            info_text = "\n".join(info_lines)
            ax.text(0.1, 0.5, info_text, fontsize=11, family='monospace',
                   verticalalignment='center')
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            ax.set_title('Statistical Summary', fontsize=15, fontweight='bold')

            filepath = output_dir / "statistical_summary.png"
            fig.tight_layout()
            fig.savefig(filepath, dpi=self.dpi, bbox_inches='tight')
            plt.close(fig)
            files.append(filepath)

        return files

    def _plot_network_flow(self, math_model: dict[str, Any],
                           solution: dict[str, Any], output_dir: Path) -> list[Path]:
        """绘制网络流/最短路径图。"""
        files = []
        numerical = solution.get("numerical_data", {})
        edges = numerical.get("edges", [])
        path = numerical.get("path", [])
        edge_flows = numerical.get("edge_flows", {})

        if not edges:
            return files

        positions = {
            "S": (0.0, 0.5),
            "A": (1.0, 1.0),
            "B": (1.0, 0.0),
            "C": (2.0, 0.5),
            "T": (3.0, 0.5),
        }

        fig, ax = plt.subplots(figsize=(10, 6))
        path_edges = set(zip(path[:-1], path[1:])) if len(path) >= 2 else set()

        for edge in edges:
            start = positions.get(edge["from"], (0, 0))
            end = positions.get(edge["to"], (0, 0))
            is_selected = (edge["from"], edge["to"]) in path_edges
            color = "crimson" if is_selected else "gray"
            width = 3 if is_selected else 1.5
            ax.annotate(
                "",
                xy=end,
                xytext=start,
                arrowprops=dict(arrowstyle="->", color=color, linewidth=width),
            )
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            label = f"c={edge['cost']}, cap={edge['capacity']}"
            ax.text(mid_x, mid_y + 0.08, label, fontsize=9, ha="center", color=color)

        for node, (x, y) in positions.items():
            ax.scatter(x, y, s=600, color="steelblue", edgecolors="black", zorder=3)
            ax.text(x, y, node, fontsize=12, fontweight="bold", color="white", ha="center", va="center")

        ax.set_title("Network Flow / Shortest Path", fontsize=15, fontweight="bold")
        ax.set_xlim(-0.3, 3.3)
        ax.set_ylim(-0.4, 1.4)
        ax.axis("off")

        filepath = output_dir / "network_flow_graph.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        files.append(filepath)

        if edge_flows:
            fig, ax = plt.subplots(figsize=(9, 5))
            labels = list(edge_flows.keys())
            values = [edge_flows[label] for label in labels]
            ax.bar(labels, values, color=plt.cm.cividis(np.linspace(0, 1, len(labels))))
            ax.set_ylabel("Assigned Flow", fontsize=12)
            ax.set_xlabel("Edge", fontsize=12)
            ax.set_title("Edge Flow Allocation", fontsize=14, fontweight="bold")
            ax.grid(axis="y", alpha=0.3)
            plt.xticks(rotation=30)

            filepath = output_dir / "network_flow_allocation.png"
            fig.tight_layout()
            fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
            plt.close(fig)
            files.append(filepath)

        return files

    def _plot_time_series(self, math_model: dict[str, Any],
                          solution: dict[str, Any], output_dir: Path) -> list[Path]:
        """绘制时间序列预测图。"""
        files = []
        numerical = solution.get("numerical_data", {})
        stats = solution.get("statistics", {})

        if not numerical or "t" not in numerical or "y" not in numerical:
            return files

        t = np.array(numerical["t"])
        y = np.array(numerical["y"])
        y_pred = np.array(numerical.get("y_pred", []))
        t_future = np.array(numerical.get("t_future", []))
        forecast = np.array(numerical.get("forecast", []))

        fig, ax = plt.subplots(figsize=(11, 6))
        ax.plot(t, y, "o-", label="Observed", color="steelblue", linewidth=1.8)
        if len(y_pred) > 0:
            ax.plot(t, y_pred, "--", label="Fitted", color="darkorange", linewidth=2)
        if len(t_future) > 0 and len(forecast) > 0:
            ax.plot(t_future, forecast, "s-", label="Forecast", color="crimson", linewidth=2)
        ax.set_xlabel("Time Index", fontsize=12)
        ax.set_ylabel("Value", fontsize=12)
        ax.set_title("Time Series Forecast", fontsize=15, fontweight="bold")
        ax.grid(alpha=0.3)
        ax.legend()

        filepath = output_dir / "time_series_forecast.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        files.append(filepath)

        if len(y_pred) > 0:
            residuals = y - y_pred
            fig, ax = plt.subplots(figsize=(9, 5))
            ax.bar(t, residuals, color="mediumpurple")
            ax.axhline(0, color="black", linewidth=1)
            ax.set_xlabel("Time Index", fontsize=12)
            ax.set_ylabel("Residual", fontsize=12)
            title = "Forecast Residuals"
            if stats.get("rmse") is not None:
                title += f" (RMSE={stats['rmse']:.3f})"
            ax.set_title(title, fontsize=14, fontweight="bold")
            ax.grid(axis="y", alpha=0.3)

            filepath = output_dir / "time_series_residuals.png"
            fig.tight_layout()
            fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
            plt.close(fig)
            files.append(filepath)

        return files

    def _plot_multi_objective(self, math_model: dict[str, Any],
                              solution: dict[str, Any], output_dir: Path) -> list[Path]:
        """绘制多目标优化帕累托前沿。"""
        files = []
        pareto = solution.get("numerical_data", {}).get("pareto_front", [])
        selected = solution.get("numerical_data", {}).get("selected_point", {})

        if not pareto:
            return files

        f1 = [point["f1"] for point in pareto]
        f2 = [point["f2"] for point in pareto]

        fig, ax = plt.subplots(figsize=self.figsize)
        ax.plot(f1, f2, "o-", color="teal", label="Pareto Samples")
        if selected:
            ax.scatter(
                selected.get("f1", 0),
                selected.get("f2", 0),
                color="crimson",
                s=120,
                marker="*",
                label="Selected Solution",
            )
        ax.set_xlabel("Objective 1", fontsize=12)
        ax.set_ylabel("Objective 2", fontsize=12)
        ax.set_title("Pareto Front Approximation", fontsize=15, fontweight="bold")
        ax.grid(alpha=0.3)
        ax.legend()

        filepath = output_dir / "pareto_front.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        files.append(filepath)

        return files

    def _plot_pde(self, math_model: dict[str, Any],
                  solution: dict[str, Any], output_dir: Path) -> list[Path]:
        """绘制 PDE 数值解。"""
        files = []
        numerical = solution.get("numerical_data", {})
        if not numerical or "u_final" not in numerical:
            return files

        x = np.array(numerical.get("x", []))
        y = np.array(numerical.get("y", []))
        u_initial = np.array(numerical.get("u_initial", []))
        u_mid = np.array(numerical.get("u_mid", []))
        u_final = np.array(numerical.get("u_final", []))

        fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))
        fields = [(u_initial, "Initial Field"), (u_mid, "Mid Field"), (u_final, "Final Field")]
        for ax, (field, title) in zip(axes, fields):
            im = ax.imshow(field, cmap="hot", origin="lower", aspect="auto")
            ax.set_title(title, fontsize=13, fontweight="bold")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            plt.colorbar(im, ax=ax, shrink=0.8)

        filepath = output_dir / "pde_heatmaps.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        files.append(filepath)

        if x.size and y.size:
            X, Y = np.meshgrid(x, y)
            fig = plt.figure(figsize=(9, 6))
            ax = fig.add_subplot(111, projection='3d')
            surf = ax.plot_surface(X, Y, u_final, cmap='inferno', alpha=0.88)
            fig.colorbar(surf, ax=ax, shrink=0.6, aspect=12)
            ax.set_title("PDE Final Surface", fontsize=14, fontweight="bold")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("U")

            filepath = output_dir / "pde_surface.png"
            fig.tight_layout()
            fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
            plt.close(fig)
            files.append(filepath)

        return files

    def _plot_queueing(self, math_model: dict[str, Any],
                       solution: dict[str, Any], output_dir: Path) -> list[Path]:
        """绘制排队系统图表。"""
        files = []
        numerical = solution.get("numerical_data", {})
        stats = solution.get("statistics", {})

        if not numerical:
            return files

        t = np.array(numerical.get("t", []))
        queue_curve = np.array(numerical.get("queue_curve", []))

        fig, ax = plt.subplots(figsize=self.figsize)
        ax.plot(t, queue_curve, "o-", color="steelblue", linewidth=2, label="Queue Length")
        ax.set_xlabel("Time", fontsize=12)
        ax.set_ylabel("Expected Queue Length", fontsize=12)
        ax.set_title("Queue Evolution", fontsize=15, fontweight="bold")
        ax.grid(alpha=0.3)
        ax.legend()

        filepath = output_dir / "queue_curve.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        files.append(filepath)

        if stats:
            fig, ax = plt.subplots(figsize=(8, 5))
            labels = ["utilization", "Lq", "Wq", "W"]
            values = [
                stats.get("server_utilization", 0),
                stats.get("avg_queue_length", 0),
                stats.get("avg_wait_time", 0),
                stats.get("avg_system_time", 0),
            ]
            ax.bar(labels, values, color=plt.cm.Blues(np.linspace(0.4, 0.9, len(labels))))
            ax.set_title("Queueing Metrics", fontsize=14, fontweight="bold")
            ax.grid(axis="y", alpha=0.3)

            filepath = output_dir / "queue_metrics.png"
            fig.tight_layout()
            fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
            plt.close(fig)
            files.append(filepath)

        return files

    def _plot_markov_chain(self, math_model: dict[str, Any],
                           solution: dict[str, Any], output_dir: Path) -> list[Path]:
        """绘制马尔可夫链分布演化。"""
        files = []
        numerical = solution.get("numerical_data", {})
        if not numerical:
            return files

        steps = np.array(numerical.get("steps", []))
        distributions = np.array(numerical.get("distributions", []))
        stationary = np.array(numerical.get("stationary_distribution", []))

        if distributions.size == 0:
            return files

        fig, ax = plt.subplots(figsize=self.figsize)
        for idx in range(distributions.shape[1]):
            ax.plot(steps, distributions[:, idx], marker="o", linewidth=1.8, label=f"State {idx+1}")
            if stationary.size > idx:
                ax.axhline(stationary[idx], linestyle="--", alpha=0.35, color=ax.lines[-1].get_color())
        ax.set_xlabel("Step", fontsize=12)
        ax.set_ylabel("Probability", fontsize=12)
        ax.set_title("Markov State Distribution Evolution", fontsize=15, fontweight="bold")
        ax.grid(alpha=0.3)
        ax.legend()

        filepath = output_dir / "markov_distribution_evolution.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        files.append(filepath)

        fig, ax = plt.subplots(figsize=(7, 5))
        im = ax.imshow(distributions.T, aspect="auto", cmap="viridis", origin="lower")
        ax.set_xlabel("Step", fontsize=12)
        ax.set_ylabel("State", fontsize=12)
        ax.set_title("State Probability Heatmap", fontsize=14, fontweight="bold")
        plt.colorbar(im, ax=ax)

        filepath = output_dir / "markov_probability_heatmap.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=self.dpi, bbox_inches="tight")
        plt.close(fig)
        files.append(filepath)

        return files

    def generate_paper_figure(self, data: dict[str, Any], title: str,
                              output_path: Path, fig_type: str = "line") -> Path:
        """生成论文用图

        Args:
            data: 图表数据
            title: 图表标题
            output_path: 输出路径
            fig_type: 图表类型 (line | bar | scatter | heatmap)

        Returns:
            生成的文件路径
        """
        fig, ax = plt.subplots(figsize=self.figsize)

        if fig_type == "line":
            for label, values in data.items():
                if isinstance(values, dict) and "x" in values and "y" in values:
                    ax.plot(values["x"], values["y"], label=label, linewidth=1.5)
            ax.legend()

        elif fig_type == "bar":
            labels = list(data.keys())
            values = [v if isinstance(v, (int, float)) else sum(v) for v in data.values()]
            ax.bar(labels, values, color=plt.cm.viridis(np.linspace(0, 1, len(labels))))

        elif fig_type == "scatter":
            for label, values in data.items():
                if isinstance(values, dict) and "x" in values and "y" in values:
                    ax.scatter(values["x"], values["y"], label=label, alpha=0.6, s=30)
            ax.legend()

        elif fig_type == "heatmap":
            if isinstance(data, dict) and "matrix" in data:
                im = ax.imshow(data["matrix"], cmap='viridis', aspect='auto')
                plt.colorbar(im, ax=ax)

        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.grid(alpha=0.3)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.tight_layout()
        fig.savefig(output_path, dpi=self.dpi, bbox_inches='tight')
        plt.close(fig)

        return output_path
