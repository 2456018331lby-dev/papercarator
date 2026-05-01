"""论文模板系统。

支持多种学术论文模板：标准article、IEEE、ACM、中文期刊、Springer LNCS、中文学位论文。
"""

from loguru import logger


class PaperTemplate:
    """论文模板管理器。"""

    TEMPLATES = {
        "standard": {
            "name": "标准学术论文",
            "preamble": "\\documentclass[a4paper,12pt]{article}\n\\usepackage{ctex}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{graphicx}\n\\usepackage{booktabs}\n\\usepackage{geometry}\n\\usepackage{hyperref}\n\\usepackage{xcolor}\n\\usepackage{float}\n\\usepackage{algorithm}\n\\usepackage{algorithmic}\n\\usepackage{listings}\n\\usepackage{subcaption}\n\\usepackage{multirow}\n\\usepackage{longtable}\n\\geometry{margin=2.5cm}\n\\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}\n",
        },
        "ieee": {
            "name": "IEEE双栏论文",
            "preamble": "\\documentclass[conference]{IEEEtran}\n\\usepackage{ctex}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{graphicx}\n\\usepackage{booktabs}\n\\usepackage{hyperref}\n\\usepackage{xcolor}\n\\usepackage{float}\n\\usepackage{algorithm}\n\\usepackage{algorithmic}\n\\usepackage{cite}\n\\usepackage{listings}\n\\usepackage{subcaption}\n\\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}\n",
        },
        "acm": {
            "name": "ACM会议论文",
            "preamble": "\\documentclass[sigconf]{acmart}\n\\usepackage{ctex}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{graphicx}\n\\usepackage{booktabs}\n\\usepackage{hyperref}\n\\usepackage{xcolor}\n\\usepackage{float}\n\\usepackage{algorithm}\n\\usepackage{algorithmic}\n\\usepackage{listings}\n\\usepackage{subcaption}\n",
        },
        "cjm": {
            "name": "中文期刊论文",
            "preamble": "\\documentclass[a4paper,11pt]{article}\n\\usepackage{ctex}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{graphicx}\n\\usepackage{booktabs}\n\\usepackage{geometry}\n\\usepackage{hyperref}\n\\usepackage{xcolor}\n\\usepackage{float}\n\\usepackage{algorithm}\n\\usepackage{algorithmic}\n\\usepackage{fancyhdr}\n\\usepackage{listings}\n\\usepackage{subcaption}\n\\usepackage{multirow}\n\\geometry{left=2.5cm, right=2.5cm, top=2.5cm, bottom=2.5cm}\n\\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}\n\\pagestyle{fancy}\n\\fancyhf{}\n\\fancyfoot[C]{\\thepage}\n",
        },
        "springer_lncs": {
            "name": "Springer LNCS",
            "preamble": "\\documentclass[runningheads]{llncs}\n\\usepackage{ctex}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{graphicx}\n\\usepackage{booktabs}\n\\usepackage{hyperref}\n\\usepackage{xcolor}\n\\usepackage{float}\n\\usepackage{algorithm}\n\\usepackage{algorithmic}\n\\usepackage{listings}\n\\usepackage{subcaption}\n",
        },
        "thesis": {
            "name": "中文学位论文",
            "preamble": "\\documentclass[a4paper,12pt]{ctexbook}\n\\usepackage{amsmath}\n\\usepackage{amssymb}\n\\usepackage{graphicx}\n\\usepackage{booktabs}\n\\usepackage{geometry}\n\\usepackage{hyperref}\n\\usepackage{xcolor}\n\\usepackage{float}\n\\usepackage{algorithm}\n\\usepackage{algorithmic}\n\\usepackage{fancyhdr}\n\\usepackage{listings}\n\\usepackage{subcaption}\n\\usepackage{multirow}\n\\usepackage{longtable}\n\\geometry{left=3cm, right=2.5cm, top=2.5cm, bottom=2.5cm}\n\\hypersetup{colorlinks=true, linkcolor=blue, citecolor=blue, urlcolor=blue}\n\\pagestyle{fancy}\n\\fancyhf{}\n\\fancyfoot[C]{\\thepage}\n",
        },
    }

    @classmethod
    def get_preamble(cls, template_name: str) -> str:
        """获取模板导言区。"""
        template = cls.TEMPLATES.get(template_name, cls.TEMPLATES["standard"])
        logger.info(f"使用模板: {template['name']}")
        return template["preamble"]

    @classmethod
    def list_templates(cls) -> list[str]:
        """列出所有可用模板。"""
        return list(cls.TEMPLATES.keys())

    @classmethod
    def get_template_info(cls, template_name: str) -> dict[str, str]:
        """获取模板信息。"""
        template = cls.TEMPLATES.get(template_name, cls.TEMPLATES["standard"])
        return {"name": template["name"], "id": template_name}
