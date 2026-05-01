"""算法伪代码生成器。

根据模型类型自动生成对应的算法伪代码LaTeX环境。
"""

from loguru import logger


class AlgorithmWriter:
    """生成LaTeX算法伪代码。"""

    ALGORITHM_TEMPLATES = {
        "queueing": (
            "\\begin{algorithm}[H]\n"
            "\\caption{M/M/c 排队系统稳态分析}\n"
            "\\begin{algorithmic}[1]\n"
            "\\REQUIRE 到达率 $\\lambda$, 服务率 $\\mu$, 服务台数 $c$\n"
            "\\ENSURE 系统利用率 $\\rho$, 平均队长 $L_q$, 平均等待时间 $W_q$\n"
            "\\STATE $\\rho \\gets \\lambda / (c \\cdot \\mu)$\n"
            "\\IF{$\\rho \\geq 1$}\n"
            "    \\RETURN \\text{系统不稳定}\n"
            "\\ENDIF\n"
            "\\STATE $a \\gets \\lambda / \\mu$\n"
            "\\STATE $S \\gets \\sum_{n=0}^{c-1} \\frac{a^n}{n!}$\n"
            "\\STATE $P_0 \\gets \\left(S + \\frac{a^c}{c!(1-\\rho)}\\right)^{-1}$\n"
            "\\STATE $L_q \\gets \\frac{P_0 \\cdot a^c \\cdot \\rho}{c! \\cdot (1-\\rho)^2}$\n"
            "\\STATE $W_q \\gets L_q / \\lambda$\n"
            "\\STATE $W \\gets W_q + 1/\\mu$\n"
            "\\RETURN $\\rho, L_q, W_q, W$\n"
            "\\end{algorithmic}\n"
            "\\end{algorithm}"
        ),
        "optimization": (
            "\\begin{algorithm}[H]\n"
            "\\caption{梯度下降优化算法}\n"
            "\\begin{algorithmic}[1]\n"
            "\\REQUIRE 目标函数 $f(x)$, 学习率 $\\alpha$, 初始点 $x_0$, 容差 $\\epsilon$\n"
            "\\ENSURE 最优解 $x^*$\n"
            "\\STATE $x \\gets x_0$\n"
            "\\FOR{$k = 1, 2, \\ldots, K_{\\max}$}\n"
            "    \\STATE $g_k \\gets \\nabla f(x)$\n"
            "    \\IF{$\\|g_k\\| < \\epsilon$}\n"
            "        \\RETURN $x$\n"
            "    \\ENDIF\n"
            "    \\STATE $x \\gets x - \\alpha \\cdot g_k$\n"
            "\\ENDFOR\n"
            "\\RETURN $x$\n"
            "\\end{algorithmic}\n"
            "\\end{algorithm}"
        ),
        "clustering": (
            "\\begin{algorithm}[H]\n"
            "\\caption{K-means 聚类算法}\n"
            "\\begin{algorithmic}[1]\n"
            "\\REQUIRE 数据集 $X=\\{x_1,...,x_n\\}$, 簇数 $K$\n"
            "\\ENSURE 聚类中心 $\\{\\mu_1,...,\\mu_K\\}$, 标签 $\\{c_1,...,c_n\\}$\n"
            "\\STATE 随机初始化 $K$ 个聚类中心 $\\mu_1,...,\\mu_K$\n"
            "\\REPEAT\n"
            "    \\FOR{每个样本 $x_i \\in X$}\n"
            "        \\STATE $c_i \\gets \\arg\\min_k \\|x_i - \\mu_k\\|^2$\n"
            "    \\ENDFOR\n"
            "    \\FOR{$k = 1$ to $K$}\n"
            "        \\STATE $\\mu_k \\gets \\frac{1}{|C_k|} \\sum_{x_i \\in C_k} x_i$\n"
            "    \\ENDFOR\n"
            "\\UNTIL{聚类中心不再变化}\n"
            "\\RETURN $\\{\\mu_k\\}, \\{c_i\\}$\n"
            "\\end{algorithmic}\n"
            "\\end{algorithm}"
        ),
        "markov_chain": (
            "\\begin{algorithm}[H]\n"
            "\\caption{马尔可夫链稳态分布求解}\n"
            "\\begin{algorithmic}[1]\n"
            "\\REQUIRE 转移矩阵 $P$, 初始分布 $\\pi_0$, 步数 $T$\n"
            "\\ENSURE 稳态分布 $\\pi^*$\n"
            "\\STATE $\\pi \\gets \\pi_0$\n"
            "\\FOR{$t = 1$ to $T$}\n"
            "    \\STATE $\\pi \\gets \\pi \\cdot P$\n"
            "    \\IF{$\\|\\pi - \\pi_{prev}\\| < 10^{-8}$}\n"
            "        \\RETURN $\\pi$\n"
            "    \\ENDIF\n"
            "    \\STATE $\\pi_{prev} \\gets \\pi$\n"
            "\\ENDFOR\n"
            "\\RETURN $\\pi$\n"
            "\\end{algorithmic}\n"
            "\\end{algorithm}"
        ),
        "game_theory": (
            "\\begin{algorithm}[H]\n"
            "\\caption{Nash 均衡求解（线性规划法）}\n"
            "\\begin{algorithmic}[1]\n"
            "\\REQUIRE 收益矩阵 $A \\in \\mathbb{R}^{m \\times n}$\n"
            "\\ENSURE 最优混合策略 $p^*$, 博弈值 $v^*$\n"
            "\\STATE 构造线性规划: $\\min \\mathbf{1}^T p$ s.t. $A^T p \\geq \\mathbf{1}, p \\geq 0$\n"
            "\\STATE 求解得到 $p_{raw}$\n"
            "\\STATE $v \\gets 1 / (\\mathbf{1}^T p_{raw})$\n"
            "\\STATE $p^* \\gets v \\cdot p_{raw}$\n"
            "\\RETURN $p^*, v$\n"
            "\\end{algorithmic}\n"
            "\\end{algorithm}"
        ),
        "bayesian": (
            "\\begin{algorithm}[H]\n"
            "\\caption{Beta-Binomial 贝叶斯推断}\n"
            "\\begin{algorithmic}[1]\n"
            "\\REQUIRE 先验参数 $\\alpha_0, \\beta_0$, 观测数据 $n$ 次试验中 $s$ 次成功\n"
            "\\ENSURE 后验参数 $\\alpha_n, \\beta_n$, 后验均值 $\\hat{\\theta}$\n"
            "\\STATE $\\alpha_n \\gets \\alpha_0 + s$\n"
            "\\STATE $\\beta_n \\gets \\beta_0 + (n - s)$\n"
            "\\STATE $\\hat{\\theta} \\gets \\alpha_n / (\\alpha_n + \\beta_n)$\n"
            "\\STATE $\\hat{\\sigma} \\gets \\sqrt{\\frac{\\alpha_n \\beta_n}{(\\alpha_n+\\beta_n)^2(\\alpha_n+\\beta_n+1)}}$\n"
            "\\RETURN $\\alpha_n, \\beta_n, \\hat{\\theta}, \\hat{\\sigma}$\n"
            "\\end{algorithmic}\n"
            "\\end{algorithm}"
        ),
        "control_theory": (
            "\\begin{algorithm}[H]\n"
            "\\caption{PID 控制器离散实现}\n"
            "\\begin{algorithmic}[1]\n"
            "\\REQUIRE 参考信号 $r(t)$, PID增益 $K_p, K_i, K_d$, 采样周期 $\\Delta t$\n"
            "\\ENSURE 控制输出 $u(t)$\n"
            "\\STATE $e_{prev} \\gets 0, \\; I \\gets 0$\n"
            "\\FOR{每个采样时刻 $t$}\n"
            "    \\STATE $e \\gets r(t) - y(t)$\n"
            "    \\STATE $I \\gets I + e \\cdot \\Delta t$\n"
            "    \\STATE $D \\gets (e - e_{prev}) / \\Delta t$\n"
            "    \\STATE $u \\gets K_p \\cdot e + K_i \\cdot I + K_d \\cdot D$\n"
            "    \\STATE $e_{prev} \\gets e$\n"
            "    \\STATE 输出 $u$ 到执行器\n"
            "\\ENDFOR\n"
            "\\end{algorithmic}\n"
            "\\end{algorithm}"
        ),
        "fuzzy_logic": (
            "\\begin{algorithm}[H]\n"
            "\\caption{Mamdani 模糊推理系统}\n"
            "\\begin{algorithmic}[1]\n"
            "\\REQUIRE 输入 $x$, 隶属函数集 $\\{A_i\\}$, 规则库 $R$\n"
            "\\ENSURE 去模糊化输出 $y^*$\n"
            "\\FOR{每条规则 $r_k \\in R$}\n"
            "    \\STATE 计算激活度 $\\alpha_k = \\mu_{A_k}(x)$\n"
            "    \\STATE 截断输出隶属函数: $\\mu_{B_k}' = \\min(\\alpha_k, \\mu_{B_k})$\n"
            "\\ENDFOR\n"
            "\\STATE 聚合: $\\mu_{agg}(y) = \\max_k \\mu_{B_k}'(y)$\n"
            "\\STATE 去模糊化: $y^* = \\frac{\\int y \\cdot \\mu_{agg}(y) dy}{\\int \\mu_{agg}(y) dy}$\n"
            "\\RETURN $y^*$\n"
            "\\end{algorithmic}\n"
            "\\end{algorithm}"
        ),
    }

    @classmethod
    def generate(cls, model_type: str) -> str:
        """生成指定模型类型的算法伪代码。"""
        algorithm = cls.ALGORITHM_TEMPLATES.get(model_type, "")
        if algorithm:
            logger.info(f"生成算法伪代码: {model_type}")
        return algorithm

    @classmethod
    def has_algorithm(cls, model_type: str) -> bool:
        """检查是否有该模型类型的算法模板。"""
        return model_type in cls.ALGORITHM_TEMPLATES
