"""论文写作模块 - 自动生成学术论文"""

from papercarator.paper_writer.latex_generator import LaTeXGenerator
from papercarator.paper_writer.template_manager import TemplateManager
from papercarator.paper_writer.section_writer import SectionWriter
from papercarator.paper_writer.citation_formatter import CitationFormatter
from papercarator.paper_writer.paper_types import PaperType
from papercarator.paper_writer.thesis_structure import ThesisStructure

__all__ = [
    "LaTeXGenerator", "TemplateManager", "SectionWriter",
    "CitationFormatter", "PaperType", "ThesisStructure",
]