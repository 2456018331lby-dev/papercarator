"""Stable Diffusion 概念图生成器。

为论文生成专业概念示意图、流程图、系统架构图等。
通过 HuggingFace Diffusers 在本地运行，或调用 WebUI API。
"""

import subprocess
from pathlib import Path
from typing import Any, Optional

from loguru import logger


class SDIllustrationGenerator:
    """使用 Stable Diffusion 为论文生成概念插图。"""

    PROMPT_TEMPLATES = {
        "queueing": {
            "concept": "A professional technical diagram of a multi-server queueing system M/M/c, showing customers arriving, waiting in queue, and being served at multiple service counters, clean vector illustration style, white background, academic paper figure",
            "negative": "blurry, low quality, text, watermark, photograph",
        },
        "optimization": {
            "concept": "A 3D surface plot showing an optimization landscape with a clear minimum point marked, contour lines below, gradient descent arrows pointing to optimum, clean mathematical visualization, academic paper style",
            "negative": "blurry, low quality, text, watermark",
        },
        "differential": {
            "concept": "A phase portrait diagram showing trajectories of a dynamical system with equilibrium points marked, vector field arrows, clean mathematical illustration, white background, academic figure style",
            "negative": "blurry, low quality, text, watermark, photograph",
        },
        "network_flow": {
            "concept": "A network flow diagram with nodes and directed edges showing flow values, capacities labeled on edges, source and sink nodes highlighted, clean graph theory illustration, academic paper figure",
            "negative": "blurry, low quality, text, watermark",
        },
        "markov_chain": {
            "concept": "A state transition diagram for a Markov chain with 3 states, transition probabilities labeled on curved arrows between states, circles for states, clean vector illustration, academic paper figure",
            "negative": "blurry, low quality, text, watermark, photograph",
        },
        "game_theory": {
            "concept": "A game theory payoff matrix visualization with two players, strategy spaces shown as axes, Nash equilibrium point highlighted, clean academic illustration, white background",
            "negative": "blurry, low quality, text, watermark",
        },
        "control_theory": {
            "concept": "A control system block diagram showing plant, controller, feedback loop, reference input and output signals, clean engineering diagram style, academic paper figure",
            "negative": "blurry, low quality, text, watermark, photograph",
        },
        "clustering": {
            "concept": "A K-means clustering visualization showing data points colored by cluster assignment with X marks for centroids, 2D scatter plot style, clean academic figure, white background",
            "negative": "blurry, low quality, text, watermark, photograph",
        },
        "bayesian": {
            "concept": "A Bayesian inference diagram showing prior distribution, likelihood, and posterior distribution as overlapping curves, with data updating beliefs, clean statistical illustration, academic paper style",
            "negative": "blurry, low quality, text, watermark",
        },
        "pde": {
            "concept": "A heat equation solution visualization showing temperature distribution on a 2D plate at different time steps, color map from blue cold to red hot, clean scientific visualization",
            "negative": "blurry, low quality, text, watermark",
        },
        "fuzzy_logic": {
            "concept": "A fuzzy logic membership function diagram showing three overlapping triangular membership functions low medium high on a horizontal axis, clean academic illustration",
            "negative": "blurry, low quality, text, watermark, photograph",
        },
        "graph_theory": {
            "concept": "A minimum spanning tree diagram with weighted edges, highlighted MST edges in red, nodes arranged in a network, clean graph theory illustration, academic paper figure",
            "negative": "blurry, low quality, text, watermark",
        },
    }

    def __init__(self, model_id: str = "stabilityai/stable-diffusion-xl-base-1.0",
                 use_api: bool = False, api_url: str = "http://127.0.0.1:7860"):
        self.model_id = model_id
        self.use_api = use_api
        self.api_url = api_url
        logger.info(f"初始化 SDIllustrationGenerator (model={model_id})")

    def generate_concept_diagram(self, model_type: str, topic: str,
                                 output_dir: Path, custom_prompt: str = "") -> Optional[Path]:
        """为指定模型类型生成概念示意图。"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        template = self.PROMPT_TEMPLATES.get(model_type)
        if not template:
            logger.warning(f"模型类型 {model_type} 暂无概念图模板")
            return None

        prompt = custom_prompt or template["concept"]
        negative = template.get("negative", "")
        output_path = output_dir / f"{model_type}_concept.png"

        if self.use_api:
            return self._generate_via_api(prompt, negative, output_path)
        else:
            return self._generate_via_diffusers(prompt, negative, output_path)

    def _generate_via_diffusers(self, prompt: str, negative: str,
                                 output_path: Path) -> Optional[Path]:
        """通过本地 diffusers 生成图像。"""
        try:
            script = (
                "import torch\n"
                "from diffusers import AutoPipelineForText2Image\n"
                f"pipe = AutoPipelineForText2Image.from_pretrained(\n"
                f'    "{self.model_id}",\n'
                "    torch_dtype=torch.float16, variant='fp16'\n"
                ")\n"
                "pipe.to('cuda')\n"
                "pipe.enable_model_cpu_offload()\n"
                f"image = pipe(\n"
                f'    prompt="""{prompt}""",\n'
                f'    negative_prompt="""{negative}""",\n'
                "    num_inference_steps=25, guidance_scale=7.5,\n"
                "    height=768, width=768\n"
                ").images[0]\n"
                f"image.save(r'{output_path}')\n"
                "print('DONE')\n"
            )
            result = subprocess.run(
                ["python", "-c", script],
                capture_output=True, text=True, timeout=300
            )
            if "DONE" in result.stdout and output_path.exists():
                logger.info(f"概念图生成成功: {output_path}")
                return output_path
            else:
                logger.warning(f"SD生成失败: {result.stderr[:200]}")
                return None
        except Exception as e:
            logger.warning(f"SD生成异常: {e}")
            return None

    def _generate_via_api(self, prompt: str, negative: str,
                          output_path: Path) -> Optional[Path]:
        """通过 WebUI API 生成图像。"""
        try:
            import httpx
            import base64

            response = httpx.post(
                f"{self.api_url}/sdapi/v1/txt2img",
                json={
                    "prompt": prompt,
                    "negative_prompt": negative,
                    "steps": 25,
                    "cfg_scale": 7.5,
                    "width": 768,
                    "height": 768,
                },
                timeout=120,
            )

            if response.status_code == 200:
                img_data = base64.b64decode(response.json()["images"][0])
                output_path.write_bytes(img_data)
                logger.info(f"概念图生成成功(API): {output_path}")
                return output_path
            else:
                logger.warning(f"SD API返回 {response.status_code}")
                return None
        except Exception as e:
            logger.warning(f"SD API调用失败: {e}")
            return None

    def generate_all_concepts(self, model_type: str, topic: str,
                              output_dir: Path) -> list[Path]:
        """生成该模型类型的所有概念图。"""
        results = []
        diagram = self.generate_concept_diagram(model_type, topic, output_dir)
        if diagram:
            results.append(diagram)
        return results
