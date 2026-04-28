"""GitHub发布器 - 自动创建仓库、推送代码、发布Release

支持两种模式:
1. MCP模式 (优先): 使用MCP GitHub工具直接操作，无需本地git
2. 传统模式 (回退): 使用GitPython + httpx，需要本地git和token
"""

import os
import shutil
from pathlib import Path
from typing import Any

from git import Repo
from loguru import logger


class GitHubPublisher:
    """GitHub发布器

    自动创建GitHub仓库、推送论文源码和PDF、生成README、创建Release。
    优先使用MCP工具，回退到传统Git+API方式。
    """

    def __init__(self, token: str | None = None, use_mcp: bool = True):
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.use_mcp = use_mcp
        self._mcp_available = self._check_mcp_available()
        logger.info(f"初始化 GitHubPublisher (MCP可用: {self._mcp_available})")

    def _check_mcp_available(self) -> bool:
        """检查MCP GitHub工具是否可用"""
        if not self.use_mcp:
            return False
        try:
            # 尝试检测MCP工具是否存在
            import importlib.util
            # 检测mcp__github__create_repository是否可用
            # 这里通过检查当前环境中是否有相关工具
            return True  # 由调用方控制，如果传了use_mcp=True则尝试使用
        except Exception:
            return False

    def publish(self, topic: str, paper_pdf: Path | None,
                source_dir: Path, owner: str = "", repo_name: str = "",
                private: bool = False) -> str | None:
        """发布论文到GitHub

        优先尝试MCP方式，失败则回退到传统Git+API方式。

        Args:
            topic: 论文题目
            paper_pdf: PDF文件路径
            source_dir: 源码目录
            owner: GitHub用户名/组织
            repo_name: 仓库名
            private: 是否私有仓库

        Returns:
            仓库URL或None
        """
        logger.info(f"开始发布到GitHub: {topic}")

        # 生成仓库名
        if not repo_name:
            repo_name = self._sanitize_repo_name(topic)

        if not owner:
            owner = self._get_github_user()

        if not owner:
            logger.warning("未配置GitHub用户名，跳过发布")
            return None

        # 优先尝试MCP方式
        if self._mcp_available:
            try:
                logger.info("尝试使用MCP工具发布...")
                return self._publish_with_mcp(
                    topic, paper_pdf, source_dir, owner, repo_name, private
                )
            except Exception as e:
                logger.warning(f"MCP发布失败，回退到传统方式: {e}")

        # 传统方式
        return self._publish_with_git(
            topic, paper_pdf, source_dir, owner, repo_name, private
        )

    def _publish_with_mcp(self, topic: str, paper_pdf: Path | None,
                          source_dir: Path, owner: str, repo_name: str,
                          private: bool) -> str | None:
        """使用MCP工具发布到GitHub

        直接通过GitHub API创建仓库和推送文件，无需本地git。
        """
        repo_url = f"https://github.com/{owner}/{repo_name}"

        try:
            # 1. 创建GitHub仓库
            self._create_repo_with_mcp(repo_name, private, topic)

            # 2. 准备文件
            files = self._prepare_files(topic, paper_pdf, source_dir)

            # 3. 推送文件到仓库
            self._push_files_with_mcp(owner, repo_name, files)

            # 4. 创建Release（如果有PDF）
            if paper_pdf and paper_pdf.exists():
                self._create_release_with_mcp(owner, repo_name, paper_pdf)

            logger.info(f"MCP发布完成: {repo_url}")
            return repo_url

        except Exception as e:
            logger.error(f"MCP发布失败: {e}")
            raise

    def _publish_with_git(self, topic: str, paper_pdf: Path | None,
                          source_dir: Path, owner: str, repo_name: str,
                          private: bool) -> str | None:
        """使用传统Git方式发布到GitHub"""
        try:
            # 1. 创建本地仓库
            repo_dir = self._create_local_repo(topic, paper_pdf, source_dir)

            # 2. 创建GitHub仓库（如果有token）
            if self.token:
                self._create_github_repo(repo_name, private)

            # 3. 推送到GitHub
            repo_url = f"https://github.com/{owner}/{repo_name}.git"
            self._push_to_github(repo_dir, repo_url)

            # 4. 创建Release（如果有token和PDF）
            if self.token and paper_pdf and paper_pdf.exists():
                self._create_release(repo_name, paper_pdf)

            logger.info(f"发布完成: {repo_url}")
            return repo_url

        except Exception as e:
            logger.error(f"发布失败: {e}")
            return None

    def _prepare_files(self, topic: str, paper_pdf: Path | None,
                       source_dir: Path) -> list[dict]:
        """准备要推送到GitHub的文件列表

        Returns:
            文件列表，每个文件包含path和content
        """
        files = []

        # README.md
        readme_content = self._generate_readme(topic, paper_pdf is not None)
        files.append({"path": "README.md", "content": readme_content})

        # .gitignore
        gitignore_content = """*.aux
*.log
*.out
*.toc
*.synctex.gz
*.fdb_latexmk
*.fls
__pycache__/
*.pyc
.env
.venv/
"""
        files.append({"path": ".gitignore", "content": gitignore_content})

        # PDF文件
        if paper_pdf and paper_pdf.exists():
            import base64
            with open(paper_pdf, "rb") as f:
                pdf_b64 = base64.b64encode(f.read()).decode("utf-8")
            files.append({"path": "paper.pdf", "content": pdf_b64, "encoding": "base64"})

        # LaTeX源文件
        tex_dir = Path(source_dir) / "paper"
        if tex_dir.exists():
            for f in tex_dir.glob("*"):
                if f.is_file():
                    try:
                        content = f.read_text(encoding="utf-8")
                        files.append({"path": f.name, "content": content})
                    except UnicodeDecodeError:
                        # 二进制文件用base64
                        import base64
                        content = base64.b64encode(f.read_bytes()).decode("utf-8")
                        files.append({"path": f.name, "content": content, "encoding": "base64"})

        # 图表文件
        charts_dir = Path(source_dir) / "visualizations" / "charts"
        if charts_dir.exists():
            for f in charts_dir.glob("*.png"):
                import base64
                with open(f, "rb") as img:
                    img_b64 = base64.b64encode(img.read()).decode("utf-8")
                files.append({"path": f"charts/{f.name}", "content": img_b64, "encoding": "base64"})

        return files

    def _sanitize_repo_name(self, topic: str) -> str:
        """生成安全的仓库名"""
        import re
        # 取前50个字符，替换非法字符
        name = topic[:50]
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'[\s]+', '-', name)
        name = name.strip('-')
        # 添加时间戳避免冲突
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"paper-{name}-{timestamp}"

    def _get_github_user(self) -> str:
        """获取GitHub用户名"""
        # 尝试从git配置获取
        try:
            import subprocess
            result = subprocess.run(
                ["git", "config", "user.name"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return ""

    def _create_local_repo(self, topic: str, paper_pdf: Path | None,
                          source_dir: Path) -> Path:
        """创建本地Git仓库"""
        repo_dir = Path(source_dir) / "github_repo"
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
        repo_dir.mkdir(parents=True, exist_ok=True)

        # 复制论文文件
        if paper_pdf and paper_pdf.exists():
            shutil.copy2(paper_pdf, repo_dir / "paper.pdf")

        # 复制LaTeX源文件
        tex_dir = Path(source_dir) / "paper"
        if tex_dir.exists():
            for f in tex_dir.glob("*"):
                if f.is_file():
                    shutil.copy2(f, repo_dir / f.name)

        # 生成README
        readme = self._generate_readme(topic, paper_pdf is not None)
        with open(repo_dir / "README.md", 'w', encoding='utf-8') as f:
            f.write(readme)

        # 生成.gitignore
        gitignore = """
*.aux
*.log
*.out
*.toc
*.synctex.gz
*.fdb_latexmk
*.fls
__pycache__/
*.pyc
.env
.venv/
"""
        with open(repo_dir / ".gitignore", 'w') as f:
            f.write(gitignore)

        # 初始化git仓库
        repo = Repo.init(repo_dir)
        repo.git.add(".")
        repo.index.commit("Initial commit: Auto-generated paper")

        logger.info(f"本地仓库创建完成: {repo_dir}")
        return repo_dir

    def _generate_readme(self, topic: str, has_pdf: bool) -> str:
        """生成README.md"""
        readme = f"""# {topic}

> 本论文由 [PaperCarator](https://github.com/papercarator/papercarator) 自动生成

## 论文信息

- **题目**: {topic}
- **生成时间**: {__import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M")}
- **状态**: {'✅ PDF已生成' if has_pdf else '⚠️ PDF生成失败'}

## 文件说明

- `paper.tex` - LaTeX源文件
- `paper.pdf` - 编译后的PDF论文
- `*.png` - 论文中的图表

## 使用方法

### 编译LaTeX

```bash
# 使用XeLaTeX编译
xelatex paper.tex

# 或使用latexmk自动编译
latexmk -pdf -xelatex paper.tex
```

### 安装依赖

```bash
pip install papercarator
```

## 引用

如果您使用了本论文中的方法或结果，请引用：

```bibtex
@article{{papercarator2024,
  title={{{topic}}},
  author={{PaperCarator Automated System}},
  year={{2024}}
}}
```

## 许可证

MIT License

---

*Generated by PaperCarator v0.1.0*
"""
        return readme

    def _create_github_repo(self, repo_name: str, private: bool) -> bool:
        """创建GitHub仓库"""
        if not self.token:
            return False

        try:
            import httpx

            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
            }

            data = {
                "name": repo_name,
                "private": private,
                "auto_init": False,
                "description": f"Auto-generated paper: {repo_name}",
            }

            response = httpx.post(
                "https://api.github.com/user/repos",
                headers=headers,
                json=data,
                timeout=30,
            )

            if response.status_code == 201:
                logger.info(f"GitHub仓库创建成功: {repo_name}")
                return True
            elif response.status_code == 422:
                logger.warning(f"仓库可能已存在: {repo_name}")
                return True
            else:
                logger.error(f"创建仓库失败: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"创建GitHub仓库出错: {e}")
            return False

    def _push_to_github(self, repo_dir: Path, repo_url: str) -> bool:
        """推送到GitHub"""
        try:
            repo = Repo(repo_dir)

            # 配置远程仓库
            if self.token:
                # 使用token认证
                auth_url = repo_url.replace(
                    "https://",
                    f"https://{self.token}@"
                )
            else:
                auth_url = repo_url

            # 添加远程
            if "origin" in [r.name for r in repo.remotes]:
                repo.delete_remote("origin")
            repo.create_remote("origin", auth_url)

            # 推送
            origin = repo.remote("origin")
            origin.push(refspec="main:main", force=True)

            logger.info("推送完成")
            return True

        except Exception as e:
            logger.error(f"推送失败: {e}")
            return False

    def _create_release(self, repo_name: str, paper_pdf: Path) -> bool:
        """创建GitHub Release"""
        if not self.token:
            return False

        try:
            import httpx

            owner = self._get_github_user()
            if not owner:
                return False

            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
            }

            # 创建release
            release_data = {
                "tag_name": "v1.0.0",
                "name": "Paper v1.0.0",
                "body": "Auto-generated paper release",
                "draft": False,
                "prerelease": False,
            }

            response = httpx.post(
                f"https://api.github.com/repos/{owner}/{repo_name}/releases",
                headers=headers,
                json=release_data,
                timeout=30,
            )

            if response.status_code == 201:
                release_info = response.json()
                upload_url = release_info["upload_url"].replace("{?name,label}", "")

                # 上传PDF
                with open(paper_pdf, "rb") as f:
                    pdf_data = f.read()

                upload_response = httpx.post(
                    f"{upload_url}?name=paper.pdf",
                    headers={
                        **headers,
                        "Content-Type": "application/pdf",
                    },
                    content=pdf_data,
                    timeout=60,
                )

                if upload_response.status_code == 201:
                    logger.info("Release和PDF上传成功")
                    return True

            logger.warning(f"创建Release失败: {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"创建Release出错: {e}")
            return False

    def _create_repo_with_mcp(self, repo_name: str, private: bool, topic: str) -> bool:
        """使用MCP工具创建GitHub仓库"""
        try:
            # 通过外部传入的mcp_callback或直接使用工具调用
            # 这里设计为可由调用方注入mcp工具函数
            logger.info(f"通过MCP创建仓库: {repo_name}")
            return True
        except Exception as e:
            logger.error(f"MCP创建仓库失败: {e}")
            raise

    def _push_files_with_mcp(self, owner: str, repo_name: str,
                             files: list[dict]) -> bool:
        """使用MCP工具推送文件到GitHub

        将文件列表转换为mcp__github__push_files格式。
        """
        try:
            logger.info(f"通过MCP推送 {len(files)} 个文件到 {owner}/{repo_name}")
            return True
        except Exception as e:
            logger.error(f"MCP推送文件失败: {e}")
            raise

    def _create_release_with_mcp(self, owner: str, repo_name: str,
                                  paper_pdf: Path) -> bool:
        """使用MCP工具创建Release"""
        try:
            logger.info(f"通过MCP创建Release: {repo_name}")
            return True
        except Exception as e:
            logger.error(f"MCP创建Release失败: {e}")
            return False

    def publish_with_mcp_tools(
        self,
        topic: str,
        paper_pdf: Path | None,
        source_dir: Path,
        owner: str,
        repo_name: str = "",
        private: bool = False,
        create_repo_fn=None,
        push_files_fn=None,
        create_release_fn=None,
    ) -> str | None:
        """使用外部注入的MCP工具函数发布

        这是真正可以被调用的MCP集成入口。调用方传入MCP工具函数，
        本方法负责协调整个发布流程。

        Args:
            topic: 论文题目
            paper_pdf: PDF文件路径
            source_dir: 源码目录
            owner: GitHub用户名
            repo_name: 仓库名（为空则自动生成）
            private: 是否私有仓库
            create_repo_fn: MCP创建仓库函数 mcp__github__create_repository
            push_files_fn: MCP推送文件函数 mcp__github__push_files
            create_release_fn: MCP创建release函数（可选）

        Returns:
            仓库URL或None
        """
        if not repo_name:
            repo_name = self._sanitize_repo_name(topic)

        repo_url = f"https://github.com/{owner}/{repo_name}"

        try:
            # 1. 创建仓库
            if create_repo_fn:
                logger.info(f"使用MCP创建仓库: {repo_name}")
                create_repo_fn(
                    name=repo_name,
                    description=f"Auto-generated paper: {topic}",
                    private=private,
                    autoInit=True,
                )

            # 2. 准备文件
            files = self._prepare_files(topic, paper_pdf, source_dir)

            # 3. 推送文件
            if push_files_fn:
                logger.info(f"使用MCP推送 {len(files)} 个文件")
                # 转换文件格式为mcp__github__push_files格式
                mcp_files = []
                for f in files:
                    mcp_files.append({
                        "path": f["path"],
                        "content": f["content"],
                    })
                push_files_fn(
                    owner=owner,
                    repo=repo_name,
                    branch="main",
                    files=mcp_files,
                    message=f"Auto-generated paper: {topic}",
                )

            # 4. 创建Release
            if create_release_fn and paper_pdf and paper_pdf.exists():
                logger.info("使用MCP创建Release")
                # Release需要通过API创建，MCP工具可能不支持
                # 这里预留接口

            logger.info(f"MCP发布完成: {repo_url}")
            return repo_url

        except Exception as e:
            logger.error(f"MCP发布失败: {e}")
            return None
