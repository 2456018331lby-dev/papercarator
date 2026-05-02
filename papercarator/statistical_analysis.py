"""统计分析模块 - 描述统计、假设检验、相关分析、回归分析。

适用于毕业论文和实验论文中的数据分析部分。
"""

import numpy as np
from typing import Any
from loguru import logger


class StatisticalAnalyzer:
    """统计分析器。"""

    def descriptive_stats(self, data: list[float]) -> dict[str, float]:
        """描述统计。"""
        arr = np.array(data, dtype=float)
        arr = arr[~np.isnan(arr)]
        return {
            "n": len(arr),
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr, ddof=1)),
            "median": float(np.median(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "q1": float(np.percentile(arr, 25)),
            "q3": float(np.percentile(arr, 75)),
            "skewness": float(self._skewness(arr)),
            "kurtosis": float(self._kurtosis(arr)),
            "range": float(np.max(arr) - np.min(arr)),
            "iqr": float(np.percentile(arr, 75) - np.percentile(arr, 25)),
            "cv": float(np.std(arr, ddof=1) / np.mean(arr)) if np.mean(arr) != 0 else 0,
        }

    def t_test(self, group1: list[float], group2: list[float],
               paired: bool = False) -> dict[str, Any]:
        """t 检验（独立/配对）。"""
        from scipy import stats
        a1 = np.array(group1, dtype=float)
        a2 = np.array(group2, dtype=float)

        if paired:
            stat, p = stats.ttest_rel(a1, a2)
            test_name = "配对t检验"
        else:
            stat, p = stats.ttest_ind(a1, a2)
            test_name = "独立样本t检验"

        pooled_std = np.sqrt((np.std(a1, ddof=1) ** 2 + np.std(a2, ddof=1) ** 2) / 2)
        cohens_d = float((np.mean(a1) - np.mean(a2)) / pooled_std) if pooled_std > 0 else 0

        return {
            "test": test_name,
            "statistic": float(stat),
            "p_value": float(p),
            "significant_005": p < 0.05,
            "significant_001": p < 0.01,
            "cohens_d": cohens_d,
            "effect_size": self._interpret_d(cohens_d),
            "n1": len(a1),
            "n2": len(a2),
            "mean1": float(np.mean(a1)),
            "mean2": float(np.mean(a2)),
        }

    def correlation(self, x: list[float], y: list[float]) -> dict[str, Any]:
        """相关分析（Pearson）。"""
        from scipy import stats
        a1 = np.array(x, dtype=float)
        a2 = np.array(y, dtype=float)

        r, p = stats.pearsonr(a1, a2)

        return {
            "r": float(r),
            "r_squared": float(r ** 2),
            "p_value": float(p),
            "significant_005": p < 0.05,
            "n": len(a1),
            "strength": self._interpret_r(r),
        }

    def regression(self, x: list[float], y: list[float]) -> dict[str, Any]:
        """简单线性回归。"""
        from scipy import stats
        a1 = np.array(x, dtype=float)
        a2 = np.array(y, dtype=float)

        slope, intercept, r, p, se = stats.linregress(a1, a2)
        y_pred = intercept + slope * a1
        residuals = a2 - y_pred
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((a2 - np.mean(a2)) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0

        return {
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_squared),
            "r": float(r),
            "p_value": float(p),
            "std_error": float(se),
            "equation": "y = {:.4f}x + {:.4f}".format(slope, intercept),
            "significant_005": p < 0.05,
            "n": len(a1),
        }

    def anova(self, *groups) -> dict[str, Any]:
        """单因素方差分析。"""
        from scipy import stats
        clean_groups = [np.array(g, dtype=float) for g in groups]
        stat, p = stats.f_oneway(*clean_groups)

        return {
            "test": "单因素方差分析 (ANOVA)",
            "f_statistic": float(stat),
            "p_value": float(p),
            "significant_005": p < 0.05,
            "n_groups": len(groups),
        }

    def chi_square(self, observed: list[list[int]]) -> dict[str, Any]:
        """卡方检验。"""
        from scipy import stats
        obs = np.array(observed)
        stat, p, dof, expected = stats.chi2_contingency(obs)

        return {
            "test": "卡方检验",
            "chi2": float(stat),
            "p_value": float(p),
            "dof": int(dof),
            "significant_005": p < 0.05,
            "expected_frequencies": expected.tolist(),
        }

    def to_latex_table(self, results: dict, title: str = "统计分析结果") -> str:
        """将统计结果转为 LaTeX 表格。"""
        lines = [
            "\\begin{table}[H]",
            "\\centering",
            "\\caption{{{}}}".format(title),
            "\\begin{tabular}{ll}",
            "\\toprule",
            "\\textbf{指标} & \\textbf{值} \\\\",
            "\\midrule",
        ]

        for key, value in results.items():
            if isinstance(value, float):
                if abs(value) < 0.001:
                    val_str = "{:.2e}".format(value)
                else:
                    val_str = "{:.4f}".format(value)
            elif isinstance(value, bool):
                val_str = "是" if value else "否"
            else:
                val_str = str(value)
            lines.append("{} & {} \\\\".format(self._translate_key(key), val_str))

        lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}"])
        return "\n".join(lines)

    def _skewness(self, arr: np.ndarray) -> float:
        n = len(arr)
        if n < 3:
            return 0.0
        m = np.mean(arr)
        s = np.std(arr, ddof=1)
        return float((n / ((n - 1) * (n - 2))) * np.sum(((arr - m) / s) ** 3))

    def _kurtosis(self, arr: np.ndarray) -> float:
        n = len(arr)
        if n < 4:
            return 0.0
        m = np.mean(arr)
        s = np.std(arr, ddof=1)
        return float(np.sum(((arr - m) / s) ** 4) / n - 3)

    def _interpret_d(self, d: float) -> str:
        ad = abs(d)
        if ad < 0.2:
            return "微小效应"
        elif ad < 0.5:
            return "小效应"
        elif ad < 0.8:
            return "中等效应"
        else:
            return "大效应"

    def _interpret_r(self, r: float) -> str:
        ar = abs(r)
        if ar < 0.2:
            return "极弱相关"
        elif ar < 0.4:
            return "弱相关"
        elif ar < 0.6:
            return "中等相关"
        elif ar < 0.8:
            return "强相关"
        else:
            return "极强相关"

    def _translate_key(self, key: str) -> str:
        translations = {
            "n": "样本量", "mean": "均值", "std": "标准差", "median": "中位数",
            "min": "最小值", "max": "最大值", "q1": "Q1", "q3": "Q3",
            "skewness": "偏度", "kurtosis": "峰度", "range": "极差",
            "iqr": "四分位距", "cv": "变异系数",
            "r": "相关系数", "r_squared": "决定系数", "p_value": "p值",
            "significant_005": "显著(alpha=0.05)", "significant_001": "显著(alpha=0.01)",
            "cohens_d": "Cohen's d", "effect_size": "效应量",
            "slope": "斜率", "intercept": "截距", "std_error": "标准误",
            "equation": "回归方程", "f_statistic": "F统计量",
            "chi2": "卡方值", "dof": "自由度",
            "statistic": "统计量", "test": "检验方法",
            "mean1": "组1均值", "mean2": "组2均值", "n1": "组1样本量", "n2": "组2样本量",
            "strength": "相关强度", "n_groups": "组数",
        }
        return translations.get(key, key)
