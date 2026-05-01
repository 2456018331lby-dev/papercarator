"""模糊逻辑模型构建器。"""

import numpy as np
import sympy as sp
from typing import Any

from papercarator.math_modeling.model_builder import MathModel


def build_fuzzy_logic(topic: str, plan: dict[str, Any]) -> MathModel:
    """构建模糊逻辑/模糊推理模型。"""
    # 模糊变量
    x = sp.Symbol('x', real=True)
    y = sp.Symbol('y', real=True)

    # 三角隶属函数参数
    mf_params = {
        "low": {"a": 0, "b": 0, "c": 5},
        "medium": {"a": 3, "b": 5, "c": 7},
        "high": {"a": 5, "b": 10, "c": 10},
    }

    # 模糊规则
    rules = [
        {"antecedent": ("x", "low"), "consequent": "low", "weight": 1.0},
        {"antecedent": ("x", "medium"), "consequent": "medium", "weight": 1.0},
        {"antecedent": ("x", "high"), "consequent": "high", "weight": 1.0},
    ]

    model = MathModel(
        name="模糊推理系统模型",
        description=f"基于'{topic}'构建的模糊逻辑推理模型",
        symbols={"x": x, "y": y},
        equations=[],
        model_type="fuzzy_logic",
        parameters={
            "n_inputs": 1,
            "n_outputs": 1,
            "defuzzification": "centroid",
        },
        metadata={
            "topic": topic,
            "membership_functions": mf_params,
            "rules": rules,
            "universe": [0, 10],
        },
    )
    return model
