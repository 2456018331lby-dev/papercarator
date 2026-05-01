"""文献检索器 - 从Semantic Scholar / CrossRef自动抓取相关论文。

免费API，无需API key。
"""

import json
from typing import Any, Optional

import httpx
from loguru import logger


class LiteratureSearcher:
    """从学术API检索真实文献。"""

    SEMANTIC_SCHOLAR = "https://api.semanticscholar.org/graph/v1"
    CROSSREF = "https://api.crossref.org/works"

    def search(self, query: str, limit: int = 5, source: str = "semantic_scholar") -> list[dict[str, str]]:
        """搜索相关论文。

        Returns:
            [{"title": "...", "authors": "...", "year": "...", "venue": "...", "doi": "...", "url": "..."}]
        """
        if source == "semantic_scholar":
            return self._search_semantic_scholar(query, limit)
        elif source == "crossref":
            return self._search_crossref(query, limit)
        else:
            results = self._search_semantic_scholar(query, limit)
            if not results:
                results = self._search_crossref(query, limit)
            return results

    def _search_semantic_scholar(self, query: str, limit: int) -> list[dict[str, str]]:
        """Semantic Scholar API检索。"""
        try:
            response = httpx.get(
                f"{self.SEMANTIC_SCHOLAR}/paper/search",
                params={
                    "query": query,
                    "limit": limit,
                    "fields": "title,authors,year,venue,externalIds,url,citationCount",
                },
                timeout=15,
            )

            if response.status_code != 200:
                logger.warning(f"Semantic Scholar返回 {response.status_code}")
                return []

            data = response.json()
            results = []
            for paper in data.get("data", []):
                authors = ", ".join(a.get("name", "") for a in paper.get("authors", [])[:3])
                if len(paper.get("authors", [])) > 3:
                    authors += " et al."
                doi = paper.get("externalIds", {}).get("DOI", "")
                results.append({
                    "title": paper.get("title", ""),
                    "authors": authors,
                    "year": str(paper.get("year", "")),
                    "venue": paper.get("venue", ""),
                    "doi": doi,
                    "url": f"https://doi.org/{doi}" if doi else paper.get("url", ""),
                    "citations": paper.get("citationCount", 0),
                })

            logger.info(f"Semantic Scholar找到 {len(results)} 篇论文")
            return results

        except Exception as e:
            logger.warning(f"Semantic Scholar检索失败: {e}")
            return []

    def _search_crossref(self, query: str, limit: int) -> list[dict[str, str]]:
        """CrossRef API检索。"""
        try:
            response = httpx.get(
                self.CROSSREF,
                params={
                    "query": query,
                    "rows": limit,
                    "sort": "relevance",
                    "select": "title,author,published-print,container-title,DOI",
                },
                timeout=15,
            )

            if response.status_code != 200:
                logger.warning(f"CrossRef返回 {response.status_code}")
                return []

            data = response.json()
            results = []
            for item in data.get("message", {}).get("items", []):
                title = item.get("title", [""])[0] if item.get("title") else ""
                authors_list = item.get("author", [])
                authors = ", ".join(
                    f"{a.get('given', '')} {a.get('family', '')}"
                    for a in authors_list[:3]
                )
                if len(authors_list) > 3:
                    authors += " et al."
                year_info = item.get("published-print", {}).get("date-parts", [[]])
                year = str(year_info[0][0]) if year_info and year_info[0] else ""
                venue = item.get("container-title", [""])[0] if item.get("container-title") else ""
                doi = item.get("DOI", "")

                results.append({
                    "title": title,
                    "authors": authors,
                    "year": year,
                    "venue": venue,
                    "doi": doi,
                    "url": f"https://doi.org/{doi}" if doi else "",
                })

            logger.info(f"CrossRef找到 {len(results)} 篇论文")
            return results

        except Exception as e:
            logger.warning(f"CrossRef检索失败: {e}")
            return []

    def to_latex_bibitems(self, papers: list[dict[str, str]], start_key: int = 1) -> str:
        """将检索结果转为LaTeX \bibitem格式。"""
        lines = []
        for i, paper in enumerate(papers, start=start_key):
            key = f"ref{i}"
            title = paper.get("title", "Unknown")
            authors = paper.get("authors", "Unknown")
            year = paper.get("year", "")
            venue = paper.get("venue", "")
            doi = paper.get("doi", "")

            entry = f"\bibitem{{{key}}} {authors}. {title}."
            if venue:
                entry += f" \textit{{{venue}}},"
            if year:
                entry += f" {year}."
            if doi:
                entry += f" DOI: \href{{https://doi.org/{doi}}}{{{doi}}}"
            lines.append(entry)

        return "\n\n".join(lines)

    def enrich_references(self, topic: str, model_type: str, existing_refs: str) -> str:
        """用真实文献补充现有参考文献。"""
        # 搜索相关论文
        queries = [
            f"{topic} mathematical modeling",
            f"{model_type} analysis optimization",
        ]

        all_papers = []
        seen_titles = set()
        for q in queries:
            papers = self.search(q, limit=3)
            for p in papers:
                if p["title"] and p["title"] not in seen_titles:
                    all_papers.append(p)
                    seen_titles.add(p["title"])

        if not all_papers:
            logger.info("未找到额外文献，使用现有参考文献")
            return existing_refs

        # 生成额外文献
        extra_refs = self.to_latex_bibitems(all_papers, start_key=20)
        logger.info(f"补充了 {len(all_papers)} 篇真实文献")
        return existing_refs + "\n\n" + extra_refs
