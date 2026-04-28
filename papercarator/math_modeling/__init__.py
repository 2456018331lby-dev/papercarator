"""数学建模模块 - 自动建立、求解和验证数学模型"""

from papercarator.math_modeling.matlab_bridge import MATLABBridge
from papercarator.math_modeling.model_builder import ModelBuilder
from papercarator.math_modeling.solver import ModelSolver
from papercarator.math_modeling.validator import ModelValidator

__all__ = ["ModelBuilder", "ModelSolver", "ModelValidator", "MATLABBridge"]
