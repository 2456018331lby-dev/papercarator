"""毕业论文结构生成器 - 自动生成符合规范的毕业论文 LaTeX 框架。"""

from typing import Any
from loguru import logger


class ThesisStructure:
    """毕业论文 LaTeX 结构生成器。"""

    def generate_preamble(self, title: str = "", author: str = "", institution: str = "",
                          degree: str = "硕士") -> str:
        """生成毕业论文 LaTeX 导言区。"""
        lines = [
            "\\documentclass[a4paper,12pt]{ctexbook}",
            "",
            "% 基础宏包",
            "\\usepackage{amsmath,amssymb,amsfonts}",
            "\\usepackage{graphicx,subcaption}",
            "\\usepackage{booktabs,multirow,longtable}",
            "\\usepackage{geometry}",
            "\\usepackage{hyperref}",
            "\\usepackage{xcolor}",
            "\\usepackage{float}",
            "\\usepackage{algorithm}",
            "\\usepackage{algorithmic}",
            "\\usepackage{listings}",
            "\\usepackage{fancyhdr}",
            "\\usepackage{titlesec}",
            "\\usepackage{tocloft}",
            "\\usepackage{setspace}",
            "",
            "% 页面设置",
            "\\geometry{left=3cm, right=2.5cm, top=2.5cm, bottom=2.5cm}",
            "\\onehalfspacing",
            "",
            "% 页眉页脚",
            "\\pagestyle{fancy}",
            "\\fancyhf{}",
            "\\fancyhead[C]{\\small\\leftmark}",
            "\\fancyfoot[C]{\\thepage}",
            "",
            "% 章节格式",
            "\\ctexset{",
            "    chapter = {",
            "        format = \\centering\\zihao{3}\\heiti,",
            "        number = \\chinese{chapter},",
            "        name = {第,章},",
            "        aftername = \\quad,",
            "        beforeskip = 20pt,",
            "        afterskip = 20pt,",
            "    },",
            "    section = {format = \\zihao{4}\\heiti, beforeskip = 15pt, afterskip = 10pt},",
            "    subsection = {format = \\zihao{-4}\\heiti, beforeskip = 10pt, afterskip = 8pt},",
            "}",
            "",
            "\\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}",
        ]
        return "\n".join(lines)

    def generate_cover(self, title: str, author: str, student_id: str = "",
                       institution: str = "", college: str = "",
                       major: str = "", advisor: str = "",
                       degree: str = "硕士", date: str = "") -> str:
        """生成封面。"""
        return f"""
\\begin{{titlepage}}
    \\centering
    \\vspace*{{2cm}}
    \\begin{{\\zihao{{1}}\\heiti}}
    {institution}\\\\[1cm]
    \\end{{}}
    \\begin{{\\zihao{{2}}\\heiti}}
    {degree}学位论文\\\\[1.5cm]
    \\end{{}}
    \\begin{{\\zihao{{-2}}\\heiti}}
    {title}\\\\[2cm]
    \\end{{}}
    \\begin{{\\zihao{{4}}}}
    \\begin{{tabular}}{{rl}}
    学院：& {college} \\\\[0.3cm]
    专业：& {major} \\\\[0.3cm]
    学号：& {student_id} \\\\[0.3cm]
    姓名：& {author} \\\\[0.3cm]
    指导教师：& {advisor} \\\\[0.3cm]
    日期：& {date} \\\\
    \\end{{tabular}}
    \\end{{}}
\\end{{titlepage}}
"""

    def generate_abstract_page(self, abstract_zh: str, keywords_zh: list[str],
                                abstract_en: str, keywords_en: list[str]) -> str:
        """生成中英文摘要页。"""
        kw_zh = "；".join(keywords_zh)
        kw_en = "; ".join(keywords_en)
        return f"""
\\chapter*{{摘\\quad 要}}
\\addcontentsline{{toc}}{{chapter}}{{摘要}}
{abstract_zh}

\\noindent\\textbf{{关键词：}}{kw_zh}

\\chapter*{{Abstract}}
\\addcontentsline{{toc}}{{chapter}}{{Abstract}}
{abstract_en}

\\noindent\\textbf{{Keywords:}} {kw_en}
"""

    def generate_toc(self) -> str:
        return "\\tableofcontents\n\\clearpage\n"

    def generate_acknowledgements(self, content: str = "") -> str:
        if not content:
            content = "在此，我要感谢我的导师在研究过程中给予的悉心指导和帮助，感谢实验室的同学们在实验和讨论中提供的宝贵意见，感谢家人和朋友的支持与鼓励。"
        return f"""
\\chapter*{{致\\quad 谢}}
\\addcontentsline{{toc}}{{chapter}}{{致谢}}
{content}
"""

    def generate_full_structure(self, config: dict[str, Any]) -> str:
        """生成完整的毕业论文 LaTeX 框架。"""
        parts = []

        parts.append(self.generate_preamble(
            title=config.get("title", ""),
            author=config.get("author", ""),
            institution=config.get("institution", ""),
            degree=config.get("degree", "硕士"),
        ))

        parts.append("\\begin{document}\n")

        parts.append(self.generate_cover(
            title=config.get("title", ""),
            author=config.get("author", ""),
            student_id=config.get("student_id", ""),
            institution=config.get("institution", ""),
            college=config.get("college", ""),
            major=config.get("major", ""),
            advisor=config.get("advisor", ""),
            degree=config.get("degree", "硕士"),
            date=config.get("date", ""),
        ))

        parts.append(self.generate_abstract_page(
            abstract_zh=config.get("abstract_zh", "（待填写）"),
            keywords_zh=config.get("keywords_zh", ["关键词1", "关键词2"]),
            abstract_en=config.get("abstract_en", "(To be filled)"),
            keywords_en=config.get("keywords_en", ["keyword1", "keyword2"]),
        ))

        parts.append(self.generate_toc())

        chapters = config.get("chapters", [
            ("绪论", "（待填写）"),
            ("文献综述", "（待填写）"),
            ("研究方法", "（待填写）"),
            ("结果与分析", "（待填写）"),
            ("讨论", "（待填写）"),
            ("结论与展望", "（待填写）"),
        ])

        for ch_title, ch_content in chapters:
            parts.append(f"\\chapter{{{ch_title}}}\n{ch_content}\n")

        parts.append("""
\\bibliographystyle{plain}
\\begin{thebibliography}{99}
\\bibitem{ref1} （待填写参考文献）
\\end{thebibliography}
""")

        parts.append(self.generate_acknowledgements(config.get("acknowledgements", "")))

        parts.append("\\end{document}")

        return "\n".join(parts)
