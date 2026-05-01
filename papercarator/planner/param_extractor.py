"""Topic Parameter Extractor - 从题目文本中提取数值参数。

当前数学建模使用硬编码参数。本模块尝试从题目描述中提取隐含的
数值参数（如服务台数、到达率等），使模型更贴合具体问题。
"""

import re
from typing import Any

from loguru import logger


class ParamExtractor:
    """从题目和上下文中提取模型参数。"""

    # 中文数字映射
    CN_NUMS = {
        "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
        "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
        "两": 2, "双": 2,
    }

    # 参数提取规则：正则 -> (参数名, 转换函数)
    EXTRACTION_RULES = [
        # 排队系统
        (r"(\d+)\s*个?\s*(?:服务台|窗口|通道)", "servers", int),
        (r"到达率[为是约]?\s*([\d.]+)", "arrival_rate", float),
        (r"服务率[为是约]?\s*([\d.]+)", "service_rate", float),
        (r"平均到达[为是约]?\s*([\d.]+)", "arrival_rate", float),
        # 优化
        (r"(\d+)\s*个?\s*(?:变量|决策变量|未知数)", "n_variables", int),
        (r"(\d+)\s*条?\s*(?:约束|限制条件)", "n_constraints", int),
        # 时间序列
        (r"(\d+)\s*(?:个|期|步)?\s*(?:时间步|预测期|预测步)", "forecast_horizon", int),
        (r"周期[为是约]?\s*(\d+)", "season_period", int),
        # 聚类
        (r"(\d+)\s*(?:个|类)?\s*(?:簇|聚类|类别|分群)", "n_clusters", int),
        (r"K\s*[=＝为]\s*(\d+)", "n_clusters", int),
        # 马尔可夫
        (r"(\d+)\s*(?:个|种)?\s*(?:状态|阶段)", "n_states", int),
        # 博弈
        (r"(\d+)\s*(?:个|名)?\s*(?:参与者|玩家|博弈方)", "n_players", int),
        (r"(\d+)\s*(?:个|种)?\s*(?:策略|纯策略)", "n_strategies", int),
        # 控制
        (r"Kp\s*[=＝为]\s*([\d.]+)", "Kp", float),
        (r"Ki\s*[=＝为]\s*([\d.]+)", "Ki", float),
        (r"Kd\s*[=＝为]\s*([\d.]+)", "Kd", float),
        # PDE
        (r"网格[为是约]?\s*(\d+)\s*[x×]\s*(\d+)", "grid_size", lambda m: int(m)),
        (r"热扩散系数[为是约]?\s*([\d.]+)", "alpha", float),
        # 通用数值
        (r"(\d+(?:\.\d+)?)\s*(?:秒|分钟|小时)", "time_unit", float),
    ]

    def extract(self, topic: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """从题目中提取参数。

        Args:
            topic: 论文题目
            context: 额外上下文（如用户提供的参数描述）

        Returns:
            提取到的参数字典
        """
        params: dict[str, Any] = {}

        # 中文数字预处理
        normalized = topic
        for cn, num in self.CN_NUMS.items():
            normalized = normalized.replace(cn, str(num))

        for pattern, param_name, converter in self.EXTRACTION_RULES:
            match = re.search(pattern, normalized)
            if match:
                try:
                    value = converter(match.group(1))
                    params[param_name] = value
                    logger.info(f"从题目提取参数: {param_name}={value}")
                except (ValueError, IndexError):
                    continue

        # 从上下文补充
        if context:
            for key, value in context.items():
                if key not in params:
                    params[key] = value

        return params

    def apply_to_model(self, model_params: dict[str, float],
                       extracted: dict[str, Any]) -> dict[str, float]:
        """将提取的参数应用到模型参数中（提取值优先于默认值）。

        Args:
            model_params: 模型默认参数
            extracted: 从题目提取的参数

        Returns:
            合并后的参数
        """
        merged = model_params.copy()
        for key, value in extracted.items():
            if key in merged:
                logger.info(f"参数覆盖: {key} {merged[key]} -> {value}")
            merged[key] = value
        return merged
