# tools/citation_tool.py
import json
import os
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class CitationInput(BaseModel):
    """Input schema for CitationTool"""
    metadata_file: str = Field(..., description="Path to paper_metadata.json")
    style: str = Field(default="APA", description="Citation style: APA, IEEE, or MLA")


class CitationFormatterTool(BaseTool):
    name: str = "Citation Formatter Tool"
    description: str = """
    Formats academic citations in APA, IEEE, or MLA style.
    Input: Path to metadata JSON and citation style (APA/IEEE/MLA).
    """
    args_schema: Type[BaseModel] = CitationInput

    def _run(self, metadata_file: str, style: str = "APA") -> str:
        """Format citations"""
        print(f"\n📚 Formatting citations in {style} style")
        
        if not os.path.exists(metadata_file):
            return json.dumps({"error": f"Metadata file not found: {metadata_file}"})
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        
        citations = []
        
        for paper in papers:
            if style.upper() == "APA":
                citation = self._format_apa(paper)
            elif style.upper() == "IEEE":
                citation = self._format_ieee(paper)
            else:
                citation = self._format_mla(paper)
            
            citations.append(citation)
        
        result = {
            "style": style,
            "citation_count": len(citations),
            "citations": citations
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    
    def _format_apa(self, paper: dict) -> str:
        """Format citation in APA style"""
        authors = paper.get("authors", ["Unknown"])
        author_str = ", ".join(authors[:3])
        if len(authors) > 3:
            author_str += ", et al."
        
        title = paper.get("title", "Untitled")
        year = paper.get("year", "n.d.")
        doi = paper.get("doi", "")
        
        citation = f"{author_str} ({year}). {title}."
        if doi:
            citation += f" https://doi.org/{doi.replace('https://doi.org/', '')}"
        
        return citation
    
    def _format_ieee(self, paper: dict) -> str:
        """Format citation in IEEE style"""
        authors = paper.get("authors", ["Unknown"])
        author_str = ", ".join([a.split()[-1] if a else "Unknown" for a in authors[:3]])
        
        title = paper.get("title", "Untitled")
        year = paper.get("year", "n.d.")
        
        return f'{author_str}, "{title}," {year}.'
    
    def _format_mla(self, paper: dict) -> str:
        """Format citation in MLA style"""
        authors = paper.get("authors", ["Unknown"])
        author_str = authors[0] if authors else "Unknown"
        
        title = paper.get("title", "Untitled")
        year = paper.get("year", "n.d.")
        
        return f'{author_str}. "{title}." {year}.'
