"""SolidWorks桥接模块 - 通过COM接口自动化3D建模

用户已有SolidWorks，本模块提供Python到SolidWorks的桥接，
利用SolidWorks强大的CAD功能进行工程3D建模。

依赖:
    pip install pywin32

SolidWorks API参考:
    https://help.solidworks.com/2024/english/api/sldworksapi/getting_started_with_solidworks_api.htm
"""

import os
from pathlib import Path
from typing import Any

from loguru import logger


class SolidWorksBridge:
    """SolidWorks桥接器

    通过pywin32 COM接口自动化SolidWorks进行3D建模。
    支持零件建模、装配体、工程图生成。
    """

    def __init__(self, visible: bool = False):
        self.visible = visible
        self._sw_app = None
        self._model = None
        self._available = False

        self._try_connect()
        logger.info(f"SolidWorksBridge初始化 (可见: {visible}, 可用: {self._available})")

    def _try_connect(self) -> None:
        """尝试连接SolidWorks"""
        try:
            import win32com.client

            # 尝试连接到已运行的SolidWorks实例
            try:
                self._sw_app = win32com.client.GetActiveObject("SldWorks.Application")
                logger.info("连接到已运行的SolidWorks实例")
            except Exception:
                # 启动新实例
                self._sw_app = win32com.client.Dispatch("SldWorks.Application")
                logger.info("启动新的SolidWorks实例")

            self._sw_app.Visible = self.visible
            self._available = True

        except ImportError:
            logger.warning("pywin32未安装，SolidWorks桥接不可用")
            logger.info("安装方法: pip install pywin32")
        except Exception as e:
            logger.warning(f"连接SolidWorks失败: {e}")

    def is_available(self) -> bool:
        """检查SolidWorks是否可用"""
        return self._available and self._sw_app is not None

    def create_part(self, part_name: str = "AutoPart") -> Any:
        """创建新零件

        Args:
            part_name: 零件名称

        Returns:
            Model对象
        """
        if not self.is_available():
            logger.error("SolidWorks不可用")
            return None

        try:
            # 创建新零件
            model = self._sw_app.NewPart()
            self._model = model
            logger.info(f"创建零件: {part_name}")
            return model
        except Exception as e:
            logger.error(f"创建零件失败: {e}")
            return None

    def create_sketch(self, plane: str = "Front") -> Any:
        """创建草图

        Args:
            plane: 基准面 (Front/Top/Right)

        Returns:
            Sketch对象
        """
        if not self._model:
            logger.error("没有活动的零件")
            return None

        try:
            # 选择基准面
            plane_names = {
                "Front": "Front Plane",
                "Top": "Top Plane",
                "Right": "Right Plane",
            }
            plane_name = plane_names.get(plane, "Front Plane")

            # 获取特征管理器
            feature_mgr = self._model.FeatureManager

            # 选择基准面并创建草图
            boolstatus = self._model.Extension.SelectByID2(
                plane_name, "PLANE", 0, 0, 0, False, 0, None, 0
            )

            if not boolstatus:
                logger.warning(f"选择基准面失败: {plane_name}")
                return None

            # 插入草图
            self._model.SketchManager.InsertSketch(True)
            sketch = self._model.SketchManager.ActiveSketch

            logger.info(f"在{plane}平面创建草图")
            return sketch

        except Exception as e:
            logger.error(f"创建草图失败: {e}")
            return None

    def draw_rectangle(self, width: float, height: float,
                      center_x: float = 0, center_y: float = 0) -> bool:
        """绘制矩形

        Args:
            width: 宽度
            height: 高度
            center_x: 中心X坐标
            center_y: 中心Y坐标

        Returns:
            是否成功
        """
        try:
            sketch_mgr = self._model.SketchManager

            # 创建矩形
            x1 = center_x - width / 2
            y1 = center_y - height / 2
            x2 = center_x + width / 2
            y2 = center_y + height / 2

            sketch_mgr.CreateCornerRectangle(x1, y1, 0, x2, y2, 0)
            logger.info(f"绘制矩形: {width}x{height}")
            return True

        except Exception as e:
            logger.error(f"绘制矩形失败: {e}")
            return False

    def draw_circle(self, radius: float, center_x: float = 0, center_y: float = 0) -> bool:
        """绘制圆

        Args:
            radius: 半径
            center_x: 中心X坐标
            center_y: 中心Y坐标

        Returns:
            是否成功
        """
        try:
            sketch_mgr = self._model.SketchManager

            # 创建圆
            sketch_mgr.CreateCircleByRadius(center_x, center_y, 0, radius)
            logger.info(f"绘制圆: 半径={radius}")
            return True

        except Exception as e:
            logger.error(f"绘制圆失败: {e}")
            return False

    def extrude(self, depth: float, direction: str = "blind") -> bool:
        """拉伸凸台

        Args:
            depth: 拉伸深度
            direction: 拉伸方向类型

        Returns:
            是否成功
        """
        try:
            # 退出草图
            self._model.SketchManager.InsertSketch(True)

            # 创建拉伸特征
            feature_mgr = self._model.FeatureManager

            # 选择草图
            self._model.ClearSelection2(True)
            self._model.Extension.SelectByID2(
                "Sketch1", "SKETCH", 0, 0, 0, False, 0, None, 0
            )

            # 创建拉伸
            feature = feature_mgr.FeatureExtrusion2(
                True, False, False, 0, 0,
                depth, 0.01, False, False, False, False,
                0.01745329251994, 0.01745329251994, False, False, False, False,
                True, True, True, 0, 0, False
            )

            logger.info(f"拉伸凸台: 深度={depth}")
            return True

        except Exception as e:
            logger.error(f"拉伸失败: {e}")
            return False

    def save_part(self, output_path: Path, format_type: str = "sldprt") -> bool:
        """保存零件

        Args:
            output_path: 输出路径
            format_type: 文件格式 (sldprt/step/iges/stl)

        Returns:
            是否成功
        """
        if not self._model:
            logger.error("没有活动的零件")
            return False

        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 格式映射
            format_map = {
                "sldprt": "",
                "step": ".step",
                "iges": ".igs",
                "stl": ".stl",
            }

            # 保存
            save_path = str(output_path.with_suffix(format_map.get(format_type, "")))

            if format_type == "sldprt":
                self._model.SaveAs3(save_path, 0, 2)
            else:
                # 使用导出功能
                self._model.Extension.SaveAs(
                    save_path, 0, 2, None, 0, 0
                )

            logger.info(f"保存零件: {save_path}")
            return True

        except Exception as e:
            logger.error(f"保存零件失败: {e}")
            return False

    def export_image(self, output_path: Path, width: int = 1920,
                    height: int = 1080) -> bool:
        """导出渲染图片

        Args:
            output_path: 输出路径
            width: 图片宽度
            height: 图片高度

        Returns:
            是否成功
        """
        if not self._model:
            logger.error("没有活动的零件")
            return False

        try:
            # 设置视图
            self._model.ShowNamedView2("*Isometric", 7)
            self._model.ViewZoomtofit2()

            # 保存图片
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            self._model.Extension.SaveAs(
                str(output_path), 0, 2, None, 0, 0
            )

            logger.info(f"导出图片: {output_path}")
            return True

        except Exception as e:
            logger.error(f"导出图片失败: {e}")
            return False

    def create_mechanical_part(self, params: dict[str, Any], output_dir: Path) -> list[Path]:
        """创建机械零件（根据参数）

        Args:
            params: 零件参数
            output_dir: 输出目录

        Returns:
            生成的文件路径列表
        """
        files = []

        if not self.is_available():
            logger.warning("SolidWorks不可用，跳过3D建模")
            return files

        try:
            # 创建零件
            self.create_part(params.get("name", "Part"))

            # 创建草图
            self.create_sketch("Front")

            # 根据类型绘制
            part_type = params.get("type", "block")

            if part_type == "block":
                w = params.get("width", 50)
                h = params.get("height", 30)
                self.draw_rectangle(w, h)
                self.extrude(params.get("depth", 20))

            elif part_type == "cylinder":
                r = params.get("radius", 15)
                self.draw_circle(r)
                self.extrude(params.get("height", 50))

            elif part_type == "plate_with_hole":
                w = params.get("width", 80)
                h = params.get("height", 60)
                hr = params.get("hole_radius", 10)
                self.draw_rectangle(w, h)
                self.draw_circle(hr)
                self.extrude(params.get("depth", 10))

            # 保存多种格式
            base_name = params.get("name", "part")

            # SLDPRT
            sld_path = output_dir / f"{base_name}.sldprt"
            if self.save_part(sld_path, "sldprt"):
                files.append(sld_path)

            # STEP
            step_path = output_dir / f"{base_name}.step"
            if self.save_part(step_path, "step"):
                files.append(step_path)

            # STL
            stl_path = output_dir / f"{base_name}.stl"
            if self.save_part(stl_path, "stl"):
                files.append(stl_path)

            # 图片
            img_path = output_dir / f"{base_name}_3d.png"
            if self.export_image(img_path):
                files.append(img_path)

            logger.info(f"机械零件创建完成: {len(files)} 个文件")

        except Exception as e:
            logger.error(f"创建机械零件失败: {e}")

        return files

    def close(self) -> None:
        """关闭SolidWorks"""
        if self._sw_app:
            try:
                if not self.visible:
                    self._sw_app.ExitApp()
                logger.info("SolidWorks已关闭")
            except Exception as e:
                logger.warning(f"关闭SolidWorks时出错: {e}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
