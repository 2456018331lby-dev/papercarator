"""贝叶斯推断模型构建器。"""

import numpy as np
import sympy as sp
from typing import Any

from papercarator.math_modeling.model_builder import MathModel


def build_bayesian(topic: str, plan: dict[str, Any]) -> MathModel:
    """构建贝叶斯推断模型。"""
    # 先验参数
    alpha_prior, beta_prior = sp.symbols('alpha beta', positive=True)
    theta = sp.symbols('theta', real=True)

    # Beta-Binomial 共轭模型
    posterior_eq = sp.Eq(
        sp.Symbol('P_theta_given_data'),
        sp.Symbol('Beta') * (alpha_prior + sp.Symbol('successes'))
        / (alpha_prior + beta_prior + sp.Symbol('n_trials'))
    )

    # 生成观测数据
    np.random.seed(42)
    true_theta = 0.65
    n_trials = 50
    successes = int(np.random.binomial(n_trials, true_theta))
    failures = n_trials - successes

    model = MathModel(
        name="贝叶斯推断模型",
        description=f"基于'{topic}'构建的贝叶斯参数估计模型",
        symbols={"alpha": alpha_prior, "beta": beta_prior, "theta": theta},
        equations=[posterior_eq],
        model_type="bayesian",
        parameters={
            "alpha_prior": 2.0,
            "beta_prior": 2.0,
            "n_trials": n_trials,
            "successes": successes,
            "failures": failures,
            "true_theta": true_theta,
        },
        metadata={
            "topic": topic,
            "prior": "Beta(2, 2)",
            "likelihood": "Binomial",
            "posterior": f"Beta({2 + successes}, {2 + failures})",
        },
    )
    return model
