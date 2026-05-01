"""图论模型构建器。"""

import numpy as np
import sympy as sp
from typing import Any

from papercarator.math_modeling.model_builder import MathModel


def build_graph_theory(topic: str, plan: dict[str, Any]) -> MathModel:
    """构建图论模型（最小生成树/连通性分析）。"""
    # 邻接矩阵
    n = 6
    np.random.seed(42)
    adj = np.random.randint(1, 20, size=(n, n))
    adj = (adj + adj.T) // 2  # 对称化
    np.fill_diagonal(adj, 0)

    # 符号变量
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
