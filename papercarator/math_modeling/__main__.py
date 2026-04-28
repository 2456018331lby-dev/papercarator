"""数学建模模块测试入口"""

from papercarator.math_modeling.model_builder import ModelBuilder
from papercarator.math_modeling.solver import ModelSolver
from papercarator.math_modeling.validator import ModelValidator


def main():
    """测试数学建模流程"""
    topic = "基于优化理论的资源配置问题研究"
    plan = {"paper_type": "modeling", "difficulty": "medium"}

    # 构建模型
    builder = ModelBuilder()
    model = builder.build(topic, plan)
    print(f"模型: {model.name}")
    print(f"类型: {model.model_type}")
    print(f"方程: {[str(eq) for eq in model.equations]}")

    # 求解
    solver = ModelSolver()
    solution = solver.solve(model)
    print(f"\n求解结果:")
    print(f"成功: {solution.success}")
    print(f"消息: {solution.message}")
    print(f"数值: {solution.values}")

    # 验证
    validator = ModelValidator()
    result = validator.validate(model, solution)
    print(f"\n验证结果:")
    print(f"有效: {result.is_valid}")
    print(f"得分: {result.score:.2f}")


if __name__ == "__main__":
    main()
