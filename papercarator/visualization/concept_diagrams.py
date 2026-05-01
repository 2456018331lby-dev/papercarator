"""概念图生成器 - 纯matplotlib实现，无需GPU/SD。

为每种模型类型生成专业概念示意图。
当SD不可用时作为备选方案。
"""

from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from loguru import logger


class ConceptDiagramGenerator:
    """用matplotlib生成论文概念示意图。"""

    def generate(self, model_type: str, topic: str, output_dir: Path) -> Path | None:
        """生成指定模型类型的概念图。"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        method = getattr(self, f"_draw_{model_type}", None)
        if not method:
            logger.info(f"概念图: {model_type} 暂无模板")
            return None

        output_path = output_dir / f"{model_type}_concept.png"
        try:
            fig = method(topic)
            fig.savefig(output_path, dpi=200, bbox_inches='tight', facecolor='white')
            plt.close(fig)
            logger.info(f"概念图生成: {output_path}")
            return output_path
        except Exception as e:
            logger.warning(f"概念图生成失败: {e}")
            plt.close('all')
            return None

    def _draw_queueing(self, topic: str):
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 4)
        ax.axis('off')
        ax.set_title(f'排队系统概念图\n{topic}', fontsize=13, fontweight='bold')

        # Arrival
        ax.annotate('', xy=(1.5, 2), xytext=(0, 2), arrowprops=dict(arrowstyle='->', lw=2, color='steelblue'))
        ax.text(0.2, 2.3, '到达流 λ', fontsize=10, color='steelblue')

        # Queue box
        rect = mpatches.FancyBboxPatch((2, 1), 2, 2, boxstyle='round,pad=0.1', facecolor='lightyellow', edgecolor='orange', lw=2)
        ax.add_patch(rect)
        ax.text(3, 2, '等待队列', fontsize=10, ha='center', fontweight='bold')

        # Servers
        for i in range(3):
            y = 0.5 + i * 1.2
            rect = mpatches.FancyBboxPatch((5, y), 1.5, 0.8, boxstyle='round,pad=0.05', facecolor='lightgreen', edgecolor='green', lw=1.5)
            ax.add_patch(rect)
            ax.text(5.75, y + 0.4, f'S{i+1}', fontsize=10, ha='center', fontweight='bold')

        ax.text(5.75, 3.5, '服务台 (μ)', fontsize=10, ha='center', color='green')

        # Arrows
        ax.annotate('', xy=(5, 2), xytext=(4, 2), arrowprops=dict(arrowstyle='->', lw=2, color='orange'))
        ax.annotate('', xy=(7.5, 2), xytext=(6.5, 2), arrowprops=dict(arrowstyle='->', lw=2, color='green'))
        ax.text(8, 2, '离开', fontsize=10, color='green')

        return fig

    def _draw_optimization(self, topic: str):
        fig, ax = plt.subplots(figsize=(8, 6))
        x = np.linspace(-3, 3, 100)
        y = np.linspace(-3, 3, 100)
        X, Y = np.meshgrid(x, y)
        Z = X**2 + Y**2 + X*Y - 2*X - Y

        contour = ax.contour(X, Y, Z, levels=20, cmap='viridis')
        ax.clabel(contour, inline=True, fontsize=8)
        ax.plot(1, 0, 'r*', markersize=20, label='最优解')
        ax.annotate('最优解', xy=(1, 0), xytext=(1.8, 1.5), fontsize=11,
                    arrowprops=dict(arrowstyle='->', color='red'),
                    color='red', fontweight='bold')
        ax.set_xlabel('x₁', fontsize=12)
        ax.set_ylabel('x₂', fontsize=12)
        ax.set_title(f'优化问题等高线图\n{topic}', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        return fig

    def _draw_markov_chain(self, topic: str):
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_xlim(-1, 3)
        ax.set_ylim(-0.5, 2.5)
        ax.axis('off')
        ax.set_title(f'马尔可夫链状态转移图\n{topic}', fontsize=13, fontweight='bold')

        positions = [(0.5, 1), (2.5, 2), (2.5, 0)]
        labels = ['S₁', 'S₂', 'S₃']
        colors = ['steelblue', 'coral', 'seagreen']

        for (x, y), label, color in zip(positions, labels, colors):
            circle = plt.Circle((x, y), 0.3, facecolor=color, edgecolor='black', lw=2, alpha=0.8)
            ax.add_patch(circle)
            ax.text(x, y, label, fontsize=14, ha='center', va='center', fontweight='bold', color='white')

        # Arrows with probabilities
        arrows = [
            ((0.5, 1), (2.5, 2), '0.2'), ((2.5, 2), (2.5, 0), '0.2'),
            ((2.5, 0), (0.5, 1), '0.15'), ((0.5, 1), (0.5, 1), '0.7'),
        ]
        for (x1, y1), (x2, y2), prob in arrows:
            if x1 == x2 and y1 == y2:
                ax.annotate('', xy=(x1-0.2, y1+0.3), xytext=(x1+0.2, y1+0.3),
                           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.5', lw=1.5))
                ax.text(x1, y1+0.55, prob, fontsize=9, ha='center')
            else:
                dx, dy = x2-x1, y2-y1
                ax.annotate('', xy=(x2-dx*0.15, y2-dy*0.15), xytext=(x1+dx*0.15, y1+dy*0.15),
                           arrowprops=dict(arrowstyle='->', lw=1.5, connectionstyle='arc3,rad=0.2'))
                mx, my = (x1+x2)/2, (y1+y2)/2
                ax.text(mx+0.15, my+0.15, prob, fontsize=9, ha='center')

        return fig

    def _draw_bayesian(self, topic: str):
        fig, ax = plt.subplots(figsize=(8, 5))
        from scipy.stats import beta
        x = np.linspace(0, 1, 200)
        ax.plot(x, beta.pdf(x, 2, 2), 'b--', lw=2, label='先验 Beta(2,2)')
        ax.plot(x, beta.pdf(x, 34, 20), 'r-', lw=2.5, label='后验 Beta(34,20)')
        ax.fill_between(x, beta.pdf(x, 34, 20), alpha=0.15, color='red')
        ax.axvline(34/54, color='green', ls=':', lw=2, label=f'后验均值={34/54:.3f}')
        ax.set_xlabel('θ (参数)', fontsize=12)
        ax.set_ylabel('概率密度', fontsize=12)
        ax.set_title(f'贝叶斯推断：先验→后验\n{topic}', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        return fig

    def _draw_clustering(self, topic: str):
        fig, ax = plt.subplots(figsize=(8, 6))
        np.random.seed(42)
        c1 = np.random.randn(20, 2) + [2, 2]
        c2 = np.random.randn(20, 2) + [-2, 1]
        c3 = np.random.randn(20, 2) + [0, -3]
        ax.scatter(c1[:,0], c1[:,1], c='steelblue', s=50, label='簇1', alpha=0.7)
        ax.scatter(c2[:,0], c2[:,1], c='coral', s=50, label='簇2', alpha=0.7)
        ax.scatter(c3[:,0], c3[:,1], c='seagreen', s=50, label='簇3', alpha=0.7)
        centroids = np.array([[2,2], [-2,1], [0,-3]])
        ax.scatter(centroids[:,0], centroids[:,1], c='black', marker='X', s=200, label='聚类中心', zorder=5)
        ax.set_xlabel('特征 1', fontsize=12)
        ax.set_ylabel('特征 2', fontsize=12)
        ax.set_title(f'K-means 聚类结果\n{topic}', fontsize=13, fontweight='bold')
        ax.legend(fontsize=10)
        return fig

    def _draw_control_theory(self, topic: str):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 4)
        ax.axis('off')
        ax.set_title(f'控制系统框图\n{topic}', fontsize=13, fontweight='bold')

        # Blocks
        blocks = [(1, 1.5, '控制器\nGc(s)'), (4.5, 1.5, '被控对象\nGp(s)')]
        for x, y, label in blocks:
            rect = mpatches.FancyBboxPatch((x, y), 2, 1, boxstyle='round,pad=0.1', facecolor='lightblue', edgecolor='steelblue', lw=2)
            ax.add_patch(rect)
            ax.text(x+1, y+0.5, label, fontsize=10, ha='center', va='center', fontweight='bold')

        # Arrows
        ax.annotate('', xy=(3, 2), xytext=(2.5, 2), arrowprops=dict(arrowstyle='->', lw=2))
        ax.annotate('', xy=(4.5, 2), xytext=(3.5, 2), arrowprops=dict(arrowstyle='->', lw=2))
        ax.annotate('', xy=(7.5, 2), xytext=(6.5, 2), arrowprops=dict(arrowstyle='->', lw=2))
        ax.annotate('', xy=(8.5, 1.5), xytext=(8.5, 0.5), arrowprops=dict(arrowstyle='->', lw=1.5))
        ax.annotate('', xy=(1, 0.5), xytext=(8.5, 0.5), arrowprops=dict(arrowstyle='->', lw=1.5, connectionstyle='arc3,rad=0'))
        ax.annotate('', xy=(1, 1.5), xytext=(1, 0.5), arrowprops=dict(arrowstyle='->', lw=1.5))

        ax.text(0.3, 2, 'R(s)', fontsize=12, fontweight='bold')
        ax.text(7.8, 2.2, 'Y(s)', fontsize=12, fontweight='bold')
        ax.text(5, 0.2, '反馈回路', fontsize=9, color='gray')

        return fig

    def _draw_game_theory(self, topic: str):
        fig, ax = plt.subplots(figsize=(7, 5))
        matrix = np.array([[3, 0, 4], [2, 4, 1], [0, 3, 2]])
        im = ax.imshow(matrix, cmap='coolwarm', aspect='auto')
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f'{matrix[i,j]}', ha='center', va='center', fontsize=16, fontweight='bold')
        ax.set_xticks([0,1,2])
        ax.set_yticks([0,1,2])
        ax.set_xticklabels(['B1', 'B2', 'B3'], fontsize=12)
        ax.set_yticklabels(['A1', 'A2', 'A3'], fontsize=12)
        ax.set_xlabel('玩家B策略', fontsize=12)
        ax.set_ylabel('玩家A策略', fontsize=12)
        ax.set_title(f'博弈收益矩阵\n{topic}', fontsize=13, fontweight='bold')
        plt.colorbar(im, ax=ax, label='收益')
        return fig

    def _draw_network_flow(self, topic: str):
        fig, ax = plt.subplots(figsize=(10, 5))
        positions = {'S': (0, 2), 'A': (3, 3.5), 'B': (3, 0.5), 'C': (6, 2), 'T': (9, 2)}
        edges = [('S','A',2,10), ('S','B',4,8), ('A','C',2,9), ('B','C',1,5), ('B','T',5,5), ('C','T',2,12)]

        for node, (x, y) in positions.items():
            ax.scatter(x, y, s=800, c='steelblue', edgecolors='black', zorder=3)
            ax.text(x, y, node, fontsize=14, ha='center', va='center', fontweight='bold', color='white')

        for n1, n2, cost, cap in edges:
            x1, y1 = positions[n1]
            x2, y2 = positions[n2]
            ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                       arrowprops=dict(arrowstyle='->', lw=2, color='gray'))
            mx, my = (x1+x2)/2, (y1+y2)/2
            ax.text(mx, my+0.25, f'c={cost}\ncap={cap}', fontsize=8, ha='center', color='gray')

        ax.set_xlim(-1, 10)
        ax.set_ylim(-0.5, 4.5)
        ax.axis('off')
        ax.set_title(f'网络流图\n{topic}', fontsize=13, fontweight='bold')
        return fig
