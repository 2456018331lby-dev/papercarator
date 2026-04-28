"""任务规划器 - 将分析结果转换为可执行的任务计划"""

from dataclasses import dataclass, field
from typing import Any

from loguru import logger


@dataclass
class Task:
    """单个任务"""
    id: str
    name: str
    description: str
    module: str  # 执行模块: planner | math_modeling | visualization | paper_writer | github_publisher
    dependencies: list[str] = field(default_factory=list)
    status: str = "pending"  # pending | running | completed | failed
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class TaskPlanner:
    """任务规划器

    根据题目分析结果，生成详细的执行计划。
    """

    def __init__(self):
        self.tasks: list[Task] = []
        logger.info("初始化 TaskPlanner")

    def create_plan(self, analysis: dict[str, Any]) -> dict[str, Any]:
        """创建执行计划

        Args:
            analysis: TopicAnalyzer的分析结果

        Returns:
            执行计划字典
        """
        logger.info("创建执行计划...")
        self.tasks = []

        # 根据分析结果生成任务序列
        task_id = 0

        # 任务1: 数学建模
        task_id += 1
        math_task = Task(
            id=f"T{task_id:03d}",
            name="数学建模",
            description=f"基于题目'{analysis['topic']}'建立数学模型",
            module="math_modeling",
            dependencies=[],
        )
        self.tasks.append(math_task)

        # 任务2: 模型求解
        task_id += 1
        solve_task = Task(
            id=f"T{task_id:03d}",
            name="模型求解",
            description="求解数学模型并验证结果",
            module="math_modeling",
            dependencies=[math_task.id],
        )
        self.tasks.append(solve_task)

        # 任务3: 数据可视化
        task_id += 1
        viz_task = Task(
            id=f"T{task_id:03d}",
            name="数据可视化",
            description="生成图表和可视化结果",
            module="visualization",
            dependencies=[solve_task.id],
        )
        self.tasks.append(viz_task)

        # 任务4: 3D建模（如果需要）
        if "3d_model" in analysis.get("required_visualizations", []):
            task_id += 1
            model3d_task = Task(
                id=f"T{task_id:03d}",
                name="3D模型生成",
                description="生成研究对象的三维模型",
                module="visualization",
                dependencies=[viz_task.id],
            )
            self.tasks.append(model3d_task)

        # 任务5: 论文写作
        task_id += 1
        paper_task = Task(
            id=f"T{task_id:03d}",
            name="论文撰写",
            description="撰写完整论文",
            module="paper_writer",
            dependencies=[t.id for t in self.tasks if t.module in ["math_modeling", "visualization"]],
        )
        self.tasks.append(paper_task)

        # 任务6: GitHub发布
        task_id += 1
        github_task = Task(
            id=f"T{task_id:03d}",
            name="GitHub发布",
            description="发布论文到GitHub",
            module="github_publisher",
            dependencies=[paper_task.id],
        )
        self.tasks.append(github_task)

        plan = {
            "topic": analysis["topic"],
            "paper_type": analysis["paper_type"],
            "difficulty": analysis["difficulty"],
            "tasks": [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "module": t.module,
                    "dependencies": t.dependencies,
                    "status": t.status,
                }
                for t in self.tasks
            ],
            "estimated_sections": analysis.get("suggested_sections", []),
            "required_tools": {
                "math": analysis.get("required_math_tools", []),
                "visualization": analysis.get("required_visualizations", []),
            },
        }

        logger.info(f"计划创建完成 - 共 {len(self.tasks)} 个任务")
        return plan

    def get_ready_tasks(self) -> list[Task]:
        """获取可以执行的任务（依赖已完成）"""
        completed_ids = {t.id for t in self.tasks if t.status == "completed"}
        return [
            t for t in self.tasks
            if t.status == "pending" and all(d in completed_ids for d in t.dependencies)
        ]

    def update_task_status(self, task_id: str, status: str, output: dict[str, Any] | None = None, error: str | None = None) -> None:
        """更新任务状态"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = status
                if output:
                    task.output = output
                if error:
                    task.error = error
                logger.info(f"任务 {task_id} 状态更新为: {status}")
                break
