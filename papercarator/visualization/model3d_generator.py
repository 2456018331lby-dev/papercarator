"""3D模型生成器 - 生成三维模型和可视化"""

from pathlib import Path
from typing import Any

import numpy as np
from loguru import logger


class Model3DGenerator:
    """3D模型生成器

    使用trimesh、matplotlib或SolidWorks生成3D模型和可视化。
    支持多种几何体生成和自定义模型。
    当SolidWorks可用时，优先用于机械CAD建模。
    """

    def __init__(self, engine: str = "trimesh",
                 solidworks_bridge: "SolidWorksBridge | None" = None):
        self.engine = engine
        self._trimesh_available = self._check_trimesh()
        self.solidworks_bridge = solidworks_bridge
        self._sw_available = solidworks_bridge is not None and solidworks_bridge.is_available()
        logger.info(
            f"初始化 Model3DGenerator (engine={engine}, "
            f"trimesh={self._trimesh_available}, solidworks={self._sw_available})"
        )

    def _check_trimesh(self) -> bool:
        """检查trimesh是否可用"""
        try:
            import trimesh
            return True
        except ImportError:
            logger.warning("trimesh 未安装，将使用matplotlib进行3D可视化")
            return False

    def generate(self, topic: str, math_model: dict[str, Any],
                 output_dir: Path) -> list[Path]:
        """生成3D模型

        Args:
            topic: 论文题目
            math_model: 数学模型数据
            output_dir: 输出目录

        Returns:
            生成的3D文件路径列表
        """
        logger.info("开始生成3D模型...")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []

        # 根据题目和模型类型选择生成的3D模型
        if "机械" in topic or "结构" in topic or "mechanical" in topic.lower():
            # 优先使用SolidWorks进行机械建模
            if self._sw_available and self.solidworks_bridge:
                files = self._generate_with_solidworks(topic, math_model, output_dir)
                if files:
                    generated_files.extend(files)
                else:
                    files = self._generate_mechanical_model(topic, output_dir)
                    generated_files.extend(files)
            else:
                files = self._generate_mechanical_model(topic, output_dir)
                generated_files.extend(files)

        elif "流体" in topic or "flow" in topic.lower():
            files = self._generate_flow_visualization(math_model, output_dir)
            generated_files.extend(files)

        elif "热" in topic or "heat" in topic.lower():
            files = self._generate_heat_visualization(math_model, output_dir)
            generated_files.extend(files)

        elif any(word in topic for word in ["网络", "路径", "物流", "配送"]) or math_model.get("model_type") == "network_flow":
            files = self._generate_network_3d(math_model, output_dir)
            generated_files.extend(files)

        elif any(word in topic for word in ["时间序列", "预测", "时序"]) or math_model.get("model_type") == "time_series":
            files = self._generate_time_series_surface(math_model, output_dir)
            generated_files.extend(files)

        elif any(word in topic for word in ["多目标", "帕累托"]) or math_model.get("model_type") == "multi_objective":
            files = self._generate_pareto_surface(output_dir)
            generated_files.extend(files)

        elif any(word in topic for word in ["偏微分", "热方程", "扩散方程"]) or math_model.get("model_type") == "pde":
            files = self._generate_pde_surface(math_model, output_dir)
            generated_files.extend(files)

        elif any(word in topic for word in ["排队", "服务台"]) or math_model.get("model_type") == "queueing":
            files = self._generate_queueing_3d(math_model, output_dir)
            generated_files.extend(files)

        elif any(word in topic for word in ["马尔可夫", "状态转移"]) or math_model.get("model_type") == "markov_chain":
            files = self._generate_markov_3d(math_model, output_dir)
            generated_files.extend(files)

        else:
            # 默认生成数学曲面
            files = self._generate_math_surface(math_model, output_dir)
            generated_files.extend(files)

        logger.info(f"3D模型生成完成 - 共 {len(generated_files)} 个文件")
        return generated_files

    def _generate_with_solidworks(self, topic: str, math_model: dict[str, Any],
                                  output_dir: Path) -> list[Path]:
        """使用SolidWorks生成机械零件"""
        if not self.solidworks_bridge:
            return []

        try:
            # 从数学模型提取参数，或使用默认值
            params = {
                "name": "mechanical_part",
                "type": "block",
                "width": 50,
                "height": 30,
                "depth": 20,
            }

            # 尝试从math_model中提取尺寸参数
            if "parameters" in math_model:
                mp = math_model["parameters"]
                if "width" in mp:
                    params["width"] = float(mp["width"])
                if "height" in mp:
                    params["height"] = float(mp["height"])
                if "depth" in mp:
                    params["depth"] = float(mp["depth"])
                if "radius" in mp:
                    params["type"] = "cylinder"
                    params["radius"] = float(mp["radius"])
                    params["height"] = float(mp.get("height", 50))

            files = self.solidworks_bridge.create_mechanical_part(params, output_dir)
            if files:
                logger.info(f"SolidWorks生成 {len(files)} 个文件")
            return files

        except Exception as e:
            logger.error(f"SolidWorks生成失败: {e}")
            return []

    def _generate_mechanical_model(self, topic: str, output_dir: Path) -> list[Path]:
        """生成机械结构3D模型"""
        files = []

        if self._trimesh_available:
            try:
                import trimesh

                # 创建一个示例机械零件（立方体+圆柱体组合）
                box = trimesh.creation.box(extents=[2, 1, 0.5])
                cylinder = trimesh.creation.cylinder(radius=0.3, height=1.5)
                cylinder.apply_translation([0, 0, 0.5])

                # 合并
                combined = trimesh.util.concatenate([box, cylinder])

                # 保存为STL
                filepath = output_dir / "mechanical_part.stl"
                combined.export(str(filepath))
                files.append(filepath)

                # 保存为OBJ
                filepath_obj = output_dir / "mechanical_part.obj"
                combined.export(str(filepath_obj))
                files.append(filepath_obj)

                logger.info("已生成机械3D模型 (STL+OBJ)")

            except Exception as e:
                logger.error(f"trimesh生成失败: {e}")
                # 回退到matplotlib
                files = self._generate_mechanical_matplotlib(topic, output_dir)
        else:
            files = self._generate_mechanical_matplotlib(topic, output_dir)

        return files

    def _generate_mechanical_matplotlib(self, topic: str, output_dir: Path) -> list[Path]:
        """使用matplotlib生成机械模型可视化"""
        import matplotlib
        matplotlib.use('Agg')
        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        # 绘制立方体
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection

        # 立方体顶点
        vertices = np.array([
            [-1, -0.5, -0.25], [1, -0.5, -0.25], [1, 0.5, -0.25], [-1, 0.5, -0.25],
            [-1, -0.5, 0.25], [1, -0.5, 0.25], [1, 0.5, 0.25], [-1, 0.5, 0.25]
        ])

        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],
            [vertices[4], vertices[5], vertices[6], vertices[7]],
            [vertices[0], vertices[1], vertices[5], vertices[4]],
            [vertices[2], vertices[3], vertices[7], vertices[6]],
            [vertices[1], vertices[2], vertices[6], vertices[5]],
            [vertices[0], vertices[3], vertices[7], vertices[4]],
        ]

        ax.add_collection3d(Poly3DCollection(faces, alpha=0.5, facecolor='lightblue', edgecolor='black'))

        # 绘制圆柱体
        theta = np.linspace(0, 2*np.pi, 50)
        z_cyl = np.linspace(-0.25, 1.25, 20)
        theta, z_cyl = np.meshgrid(theta, z_cyl)
        x_cyl = 0.3 * np.cos(theta)
        y_cyl = 0.3 * np.sin(theta)
        ax.plot_surface(x_cyl, y_cyl, z_cyl, alpha=0.6, color='coral')

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        ax.set_title('Mechanical Part 3D Model', fontsize=14, fontweight='bold')

        filepath = output_dir / "mechanical_part_3d.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)
        files = [filepath]

        return files

    def _generate_flow_visualization(self, math_model: dict[str, Any], output_dir: Path) -> list[Path]:
        """生成流体可视化"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 速度场
        x = np.linspace(-2, 2, 20)
        y = np.linspace(-2, 2, 20)
        X, Y = np.meshgrid(x, y)
        U = -Y
        V = X

        ax1.quiver(X, Y, U, V, np.sqrt(U**2 + V**2), cmap='viridis', scale=30)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_title('Velocity Field', fontsize=14, fontweight='bold')
        ax1.set_aspect('equal')

        # 流线图
        ax2.streamplot(X, Y, U, V, color=np.sqrt(U**2 + V**2), cmap='plasma', density=1.5)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_title('Streamlines', fontsize=14, fontweight='bold')
        ax2.set_aspect('equal')

        filepath = output_dir / "flow_visualization.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)

        return [filepath]

    def _generate_heat_visualization(self, math_model: dict[str, Any], output_dir: Path) -> list[Path]:
        """生成热传导可视化"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # 温度分布
        x = np.linspace(0, 1, 100)
        y = np.linspace(0, 1, 100)
        X, Y = np.meshgrid(x, y)

        # 示例温度场: T = sin(pi*x) * sin(pi*y) * exp(-t)
        T = np.sin(np.pi * X) * np.sin(np.pi * Y)

        im1 = ax1.contourf(X, Y, T, levels=20, cmap='hot')
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_title('Temperature Distribution', fontsize=14, fontweight='bold')
        plt.colorbar(im1, ax=ax1, label='Temperature')

        # 温度梯度
        dTdx, dTdy = np.gradient(T)
        im2 = ax2.quiver(X[::5, ::5], Y[::5, ::5], dTdx[::5, ::5], dTdy[::5, ::5],
                        np.sqrt(dTdx[::5, ::5]**2 + dTdy[::5, ::5]**2), cmap='coolwarm')
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_title('Temperature Gradient', fontsize=14, fontweight='bold')
        plt.colorbar(im2, ax=ax2, label='Gradient Magnitude')

        filepath = output_dir / "heat_visualization.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)

        return [filepath]

    def _generate_math_surface(self, math_model: dict[str, Any], output_dir: Path) -> list[Path]:
        """生成数学曲面"""
        import matplotlib
        matplotlib.use('Agg')
        from mpl_toolkits.mplot3d import Axes3D
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(12, 5))

        # 曲面1: z = x^2 + y^2
        ax1 = fig.add_subplot(121, projection='3d')
        x = np.linspace(-3, 3, 100)
        y = np.linspace(-3, 3, 100)
        X, Y = np.meshgrid(x, y)
        Z1 = X**2 + Y**2

        surf1 = ax1.plot_surface(X, Y, Z1, cmap='viridis', alpha=0.8)
        ax1.set_xlabel('X')
        ax1.set_ylabel('Y')
        ax1.set_zlabel('Z')
        ax1.set_title('z = x² + y²', fontsize=13, fontweight='bold')
        fig.colorbar(surf1, ax=ax1, shrink=0.5, aspect=10)

        # 曲面2: z = sin(x) * cos(y)
        ax2 = fig.add_subplot(122, projection='3d')
        Z2 = np.sin(X) * np.cos(Y)
        surf2 = ax2.plot_surface(X, Y, Z2, cmap='plasma', alpha=0.8)
        ax2.set_xlabel('X')
        ax2.set_ylabel('Y')
        ax2.set_zlabel('Z')
        ax2.set_title('z = sin(x) · cos(y)', fontsize=13, fontweight='bold')
        fig.colorbar(surf2, ax=ax2, shrink=0.5, aspect=10)

        filepath = output_dir / "math_surface_3d.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)

        return [filepath]

    def _generate_network_3d(self, math_model: dict[str, Any], output_dir: Path) -> list[Path]:
        """生成网络结构 3D 示意。"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        positions = {
            "S": (0.0, 0.0, 0.6),
            "A": (1.0, 1.0, 0.2),
            "B": (1.0, -0.8, 0.4),
            "C": (2.2, 0.2, 1.0),
            "T": (3.2, 0.0, 0.3),
        }
        edges = math_model.get("metadata", {}).get("edges", [])
        if not edges:
            edges = [
                {"from": "S", "to": "A"},
                {"from": "S", "to": "B"},
                {"from": "A", "to": "C"},
                {"from": "B", "to": "C"},
                {"from": "C", "to": "T"},
            ]

        for edge in edges:
            x1, y1, z1 = positions[edge["from"]]
            x2, y2, z2 = positions[edge["to"]]
            ax.plot([x1, x2], [y1, y2], [z1, z2], color="slateblue", linewidth=2)

        for node, (x, y, z) in positions.items():
            ax.scatter(x, y, z, s=180, color="tomato", edgecolors="black")
            ax.text(x, y, z + 0.08, node, fontsize=11, fontweight="bold")

        ax.set_title("3D Network Structure", fontsize=14, fontweight='bold')
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")

        filepath = output_dir / "network_structure_3d.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)

        return [filepath]

    def _generate_time_series_surface(self, math_model: dict[str, Any], output_dir: Path) -> list[Path]:
        """生成时间序列 3D 曲面示意。"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        observations = np.array(math_model.get("metadata", {}).get("observations", []), dtype=float)
        if observations.size == 0:
            return self._generate_math_surface(math_model, output_dir)

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        horizon = len(observations)
        periods = 6
        x = np.arange(horizon)
        y = np.arange(periods)
        X, Y = np.meshgrid(x, y)
        base = np.tile(observations, (periods, 1))
        Z = base + 0.6 * Y

        surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.85)
        fig.colorbar(surf, ax=ax, shrink=0.6, aspect=12)
        ax.set_title("Time Series Seasonal Surface", fontsize=14, fontweight='bold')
        ax.set_xlabel("Time Index")
        ax.set_ylabel("Season Layer")
        ax.set_zlabel("Value")

        filepath = output_dir / "time_series_surface_3d.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)

        return [filepath]

    def _generate_pareto_surface(self, output_dir: Path) -> list[Path]:
        """生成多目标权衡 3D 示意。"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        x = np.linspace(0, 5, 80)
        y = np.linspace(0, 5, 80)
        X, Y = np.meshgrid(x, y)
        Z = 0.6 * ((X - 1) ** 2 + (Y - 3) ** 2) + 0.4 * ((X - 4) ** 2 + (Y - 1) ** 2)

        surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.88)
        fig.colorbar(surf, ax=ax, shrink=0.6, aspect=12)
        ax.set_title("Multi-objective Tradeoff Surface", fontsize=14, fontweight='bold')
        ax.set_xlabel("Decision Variable x")
        ax.set_ylabel("Decision Variable y")
        ax.set_zlabel("Weighted Objective")

        filepath = output_dir / "pareto_surface_3d.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)

        return [filepath]

    def _generate_pde_surface(self, math_model: dict[str, Any], output_dir: Path) -> list[Path]:
        """生成 PDE 3D 温度场。"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        grid_size = int(math_model.get("parameters", {}).get("grid_size", 30))
        x = np.linspace(0, 1, grid_size)
        y = np.linspace(0, 1, grid_size)
        X, Y = np.meshgrid(x, y)
        Z = np.sin(np.pi * X) * np.sin(np.pi * Y) * np.exp(-0.5 * (X + Y))

        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, Z, cmap='hot', alpha=0.9)
        fig.colorbar(surf, ax=ax, shrink=0.6, aspect=12)
        ax.set_title("PDE Temperature Surface", fontsize=14, fontweight='bold')
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Temperature")

        filepath = output_dir / "pde_temperature_3d.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)

        return [filepath]

    def _generate_queueing_3d(self, math_model: dict[str, Any], output_dir: Path) -> list[Path]:
        """生成排队系统 3D 柱状示意。"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        arrival = float(math_model.get("parameters", {}).get("arrival_rate", 4.5))
        service = float(math_model.get("parameters", {}).get("service_rate", 3.2))
        servers = int(math_model.get("parameters", {}).get("servers", 2))

        fig = plt.figure(figsize=(9, 7))
        ax = fig.add_subplot(111, projection='3d')

        xs = np.array([0, 1, 2])
        ys = np.zeros_like(xs)
        zs = np.zeros_like(xs)
        dx = np.full_like(xs, 0.5, dtype=float)
        dy = np.full_like(xs, 0.5, dtype=float)
        dz = np.array([arrival, service, servers], dtype=float)

        ax.bar3d(xs, ys, zs, dx, dy, dz, color=["royalblue", "darkorange", "seagreen"], alpha=0.8)
        ax.set_xticks(xs + 0.25)
        ax.set_xticklabels(["Arrival", "Service", "Servers"])
        ax.set_title("Queueing System 3D Profile", fontsize=14, fontweight='bold')
        ax.set_zlabel("Magnitude")

        filepath = output_dir / "queueing_3d_profile.png"
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)

        return [filepath]

    def _generate_markov_3d(self, math_model: dict[str, Any], output_dir: Path) -> list[Path]:
        """生成马尔可夫链 3D 概率曲面。"""
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        transition_matrix = np.array(math_model.get("metadata", {}).get("transition_matrix", []), dtype=float)
        if transition_matrix.size == 0:
            return self._generate_math_surface(math_model, output_dir)

        x = np.arange(transition_matrix.shape[1])
        y = np.arange(transition_matrix.shape[0])
        X, Y = np.meshgrid(x, y)

        fig = plt.figure(figsize=(9, 7))
        ax = fig.add_subplot(111, projection='3d')
        surf = ax.plot_surface(X, Y, transition_matrix, cmap='plasma', alpha=0.9)
        fig.colorbar(surf, ax=ax, shrink=0.6, aspect=12)
        ax.set_title("Markov Transition Surface", fontsize=14, fontweight='bold')
        ax.set_xlabel("To State")
        ax.set_ylabel("From State")
        ax.set_zlabel("Probability")

        filepath = output_dir / "markov_transition_3d.png"
        fig.tight_layout()
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close(fig)

        return [filepath]

    def generate_custom_mesh(self, vertices: np.ndarray, faces: np.ndarray,
                            output_path: Path) -> Path:
        """生成自定义网格模型

        Args:
            vertices: 顶点坐标 (N, 3)
            faces: 面索引 (M, 3)
            output_path: 输出路径

        Returns:
            输出文件路径
        """
        if self._trimesh_available:
            try:
                import trimesh
                mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
                mesh.export(str(output_path))
                return output_path
            except Exception as e:
                logger.error(f"自定义网格生成失败: {e}")

        # 回退: 保存为numpy文件
        np_path = output_path.with_suffix('.npz')
        np.savez(np_path, vertices=vertices, faces=faces)
        return np_path
