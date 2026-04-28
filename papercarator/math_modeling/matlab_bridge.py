r"""MATLAB桥接模块 - 通过MATLAB Engine进行高级数学建模

用户已有MATLAB R2024b，本模块提供Python到MATLAB的桥接，
利用MATLAB强大的数值计算能力进行复杂数学建模。

安装MATLAB Engine for Python:
    cd "C:\Program Files\MATLAB\R2024b\extern\engines\python"
    python setup.py install
"""

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from loguru import logger


class MATLABBridge:
    """MATLAB桥接器

    通过MATLAB Engine API或命令行调用MATLAB进行数学建模。
    当MATLAB Engine不可用时，自动回退到命令行模式。
    """

    def __init__(self, matlab_path: str | None = None):
        self.matlab_path = matlab_path or self._find_matlab()
        self._engine = None
        self._engine_available = False

        # 尝试启动MATLAB Engine
        self._try_start_engine()

        logger.info(f"MATLABBridge初始化 (路径: {self.matlab_path}, Engine: {self._engine_available})")

    def _find_matlab(self) -> str:
        """自动查找MATLAB安装路径"""
        # 常见安装路径
        common_paths = [
            r"C:\Program Files\MATLAB\R2024b\bin\matlab.exe",
            r"C:\Program Files\MATLAB\R2024a\bin\matlab.exe",
            r"C:\Program Files\MATLAB\R2023b\bin\matlab.exe",
            r"C:\Program Files\MATLAB\R2023a\bin\matlab.exe",
        ]
        for path in common_paths:
            if Path(path).exists():
                return path

        # 尝试从环境变量查找
        import shutil
        matlab_cmd = shutil.which("matlab")
        if matlab_cmd:
            return matlab_cmd

        logger.warning("未找到MATLAB安装路径，请手动指定")
        return "matlab"

    def _try_start_engine(self) -> None:
        """尝试启动MATLAB Engine"""
        try:
            import matlab.engine
            self._engine = matlab.engine.start_matlab()
            self._engine_available = True
            logger.info("MATLAB Engine启动成功")
        except ImportError:
            logger.warning("MATLAB Engine for Python未安装，将使用命令行模式")
            logger.info("安装方法: cd \"MATLAB_PATH\\extern\\engines\\python\" && python setup.py install")
        except Exception as e:
            logger.warning(f"MATLAB Engine启动失败: {e}")

    def is_available(self) -> bool:
        """检查MATLAB是否可用"""
        return self._engine_available or Path(self.matlab_path).exists()

    def execute(self, code: str, workspace: dict[str, Any] | None = None) -> dict[str, Any]:
        """执行MATLAB代码

        Args:
            code: MATLAB代码字符串
            workspace: 输入变量字典

        Returns:
            输出结果字典
        """
        if self._engine_available:
            return self._execute_with_engine(code, workspace)
        else:
            return self._execute_with_cli(code, workspace)

    def _execute_with_engine(self, code: str, workspace: dict[str, Any] | None = None) -> dict[str, Any]:
        """使用MATLAB Engine执行代码"""
        try:
            # 将Python变量传入MATLAB工作区
            if workspace:
                for name, value in workspace.items():
                    if isinstance(value, np.ndarray):
                        self._engine.workspace[name] = matlab.double(value.tolist())
                    elif isinstance(value, (list, tuple)):
                        self._engine.workspace[name] = matlab.double(value)
                    elif isinstance(value, (int, float)):
                        self._engine.workspace[name] = float(value)
                    elif isinstance(value, str):
                        self._engine.workspace[name] = value

            # 执行代码
            result = self._engine.eval(code, nargout=0)

            # 获取工作区变量
            output = {}
            try:
                var_names = self._engine.eval("who", nargout=1)
                for var_name in var_names:
                    try:
                        val = self._engine.workspace[var_name]
                        if hasattr(val, '_data'):
                            output[var_name] = np.array(val._data)
                        else:
                            output[var_name] = val
                    except Exception:
                        pass
            except Exception:
                pass

            return {"success": True, "output": output, "message": "执行成功"}

        except Exception as e:
            logger.error(f"MATLAB Engine执行失败: {e}")
            return {"success": False, "output": {}, "message": str(e)}

    def _execute_with_cli(self, code: str, workspace: dict[str, Any] | None = None) -> dict[str, Any]:
        """使用命令行执行MATLAB代码"""
        try:
            # 创建临时.m文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.m', delete=False, encoding='utf-8') as f:
                # 写入变量
                if workspace:
                    for name, value in workspace.items():
                        if isinstance(value, np.ndarray):
                            f.write(f"{name} = {self._array_to_matlab(value)};\n")
                        elif isinstance(value, (list, tuple)):
                            f.write(f"{name} = {list(value)};\n")
                        elif isinstance(value, (int, float)):
                            f.write(f"{name} = {value};\n")
                        elif isinstance(value, str):
                            f.write(f"{name} = '{value}';\n")

                # 写入主代码
                f.write(code)

                # 保存结果到JSON
                f.write("\n\n% 保存结果\n")
                f.write("result_struct = struct();\n")
                f.write("vars = who;\n")
                f.write("for i = 1:length(vars)\n")
                f.write("    try\n")
                f.write("        result_struct.(vars{i}) = eval(vars{i});\n")
                f.write("    catch\n")
                f.write("        result_struct.(vars{i}) = 'unsupported_type';\n")
                f.write("    end\n")
                f.write("end\n")

                mat_file = f.name.replace('.m', '_result.mat')
                f.write(f"save('{mat_file}', 'result_struct');\n")

            m_file = f.name

            # 执行MATLAB
            cmd = [
                self.matlab_path,
                "-batch",
                f"run('{m_file}')",
                "-nosplash",
                "-nodesktop",
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )

            # 读取结果
            output = {}
            if Path(mat_file).exists():
                try:
                    import scipy.io
                    mat_data = scipy.io.loadmat(mat_file)
                    if 'result_struct' in mat_data:
                        result_struct = mat_data['result_struct']
                        # 转换为Python字典
                        for field_name in result_struct.dtype.names:
                            val = result_struct[field_name][0, 0]
                            if isinstance(val, np.ndarray):
                                output[field_name] = val
                            else:
                                output[field_name] = val
                except Exception as e:
                    logger.warning(f"读取MAT文件失败: {e}")

            # 清理临时文件
            Path(m_file).unlink(missing_ok=True)
            Path(mat_file).unlink(missing_ok=True)

            success = result.returncode == 0
            return {
                "success": success,
                "output": output,
                "message": result.stdout if success else result.stderr,
            }

        except subprocess.TimeoutExpired:
            logger.error("MATLAB执行超时")
            return {"success": False, "output": {}, "message": "执行超时"}
        except Exception as e:
            logger.error(f"MATLAB CLI执行失败: {e}")
            return {"success": False, "output": {}, "message": str(e)}

    def _array_to_matlab(self, arr: np.ndarray) -> str:
        """将numpy数组转换为MATLAB矩阵字符串"""
        if arr.ndim == 1:
            return str(arr.tolist())
        elif arr.ndim == 2:
            rows = [str(row.tolist()) for row in arr]
            return "[" + "; ".join(rows) + "]"
        else:
            return str(arr.tolist())

    def solve_optimization(self, objective: str, constraints: list[str],
                          variables: list[str], options: dict[str, Any] | None = None) -> dict[str, Any]:
        """使用MATLAB求解优化问题

        Args:
            objective: 目标函数字符串 (MATLAB语法)
            constraints: 约束条件列表
            variables: 变量名列表
            options: 求解器选项

        Returns:
            求解结果
        """
        code = f"""
% 定义优化问题
prob = optimproblem;

% 定义变量
"""
        for var in variables:
            code += f"{var} = optimvar('{var}');\n"

        code += f"\n% 目标函数\n"
        code += f"prob.Objective = {objective};\n"

        code += f"\n% 约束条件\n"
        for i, cons in enumerate(constraints):
            code += f"prob.Constraints.cons{i+1} = {cons};\n"

        code += f"""
% 求解
[sol, fval, exitflag, output] = solve(prob);

% 提取结果
result = struct();
result.success = exitflag == 1;
result.objective_value = fval;
"""
        for var in variables:
            code += f"result.{var} = sol.{var};\n"

        code += "result.exitflag = exitflag;\n"
        code += "result.iterations = output.iterations;\n"

        return self.execute(code)

    def solve_ode(self, ode_func: str, tspan: list[float],
                 y0: list[float], options: dict[str, Any] | None = None) -> dict[str, Any]:
        """使用MATLAB求解常微分方程

        Args:
            ode_func: ODE函数 (dy/dt = f(t,y) 的右侧)
            tspan: 时间范围 [t0, tf]
            y0: 初始条件
            options: 求解器选项

        Returns:
            求解结果
        """
        code = f"""
% 定义ODE
odefun = @(t, y) {ode_func};

% 时间范围
tspan = {tspan};

% 初始条件
y0 = {y0};

% 求解
[t, y] = ode45(odefun, tspan, y0);

% 提取结果
result = struct();
result.t = t;
result.y = y;
result.success = true;
"""
        return self.execute(code)

    def solve_pde(self, pde_def: dict[str, Any]) -> dict[str, Any]:
        """使用MATLAB求解偏微分方程 (需要PDE Toolbox)"""
        code = """
% PDE求解 (示例: 热传导方程)
model = createpde();

% 创建几何
gm = multicuboid(1, 1, 1);
model.Geometry = gm;

% 生成网格
generateMesh(model);

% 定义PDE
specifyCoefficients(model, 'm', 0, 'd', 1, 'c', 1, 'a', 0, 'f', 0);

% 边界条件
applyBoundaryCondition(model, 'dirichlet', 'Face', 1, 'u', 0);

% 初始条件
setInitialConditions(model, 1);

% 求解
tlist = 0:0.1:1;
results = solvepde(model, tlist);

% 提取结果
result = struct();
result.success = true;
result.nodes = results.Mesh.Nodes;
result.elements = results.Mesh.Elements;
result.NodalSolution = results.NodalSolution;
"""
        return self.execute(code)

    def generate_figure(self, plot_code: str, output_path: Path,
                       figsize: tuple[int, int] = (800, 600)) -> Path:
        """使用MATLAB生成高质量图表

        Args:
            plot_code: MATLAB绘图代码
            output_path: 输出图片路径
            figsize: 图片尺寸

        Returns:
            输出文件路径
        """
        code = f"""
% 创建图形
fig = figure('Visible', 'off', 'Position', [0, 0, {figsize[0]}, {figsize[1]}]);

% 执行绘图代码
{plot_code}

% 保存
saveas(fig, '{output_path}');
close(fig);
"""
        result = self.execute(code)
        if result["success"] and output_path.exists():
            return output_path
        else:
            logger.error(f"MATLAB图表生成失败: {result['message']}")
            return output_path

    def close(self) -> None:
        """关闭MATLAB Engine"""
        if self._engine:
            try:
                self._engine.quit()
                logger.info("MATLAB Engine已关闭")
            except Exception as e:
                logger.warning(f"关闭MATLAB Engine时出错: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
