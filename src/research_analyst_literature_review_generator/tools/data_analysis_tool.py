# tools/data_analysis_tool.py
import json
import os
from typing import Type
from collections import Counter
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class DataAnalysisInput(BaseModel):
    """Input schema for DataAnalysisTool"""
    extracted_content_file: str = Field(..., description="Path to extracted_content.json")


class DataAnalysisTool(BaseTool):
    name: str = "Data Analysis Tool"
    description: str = """
    Analyzes extracted paper content to identify themes, patterns, and statistics.
    Groups papers by common topics and generates analytical insights.
    Input: Path to extracted_content.json file.
    """
    args_schema: Type[BaseModel] = DataAnalysisInput

    def _run(self, extracted_content_file: str) -> str:
        """Analyze paper content"""
        print(f"\n📊 Analyzing data from: {extracted_content_file}")
        
        if not os.path.exists(extracted_content_file):
            return json.dumps({"error": f"File not found: {extracted_content_file}"})
        
        with open(extracted_content_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        
        # Perform analysis
        analysis = {
            "total_papers": len(papers),
            "year_distribution": self._analyze_years(papers),
            "keyword_frequency": self._analyze_keywords(papers),
            "themes": self._identify_themes(papers),
            "statistics": self._calculate_stats(papers),
            "paper_groupings": self._group_papers(papers)
        }
        
        # Save analysis
        output_path = os.path.join("outputs", "synthesis.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Analysis complete: {len(analysis['themes'])} themes identified")
        
        return json.dumps(analysis, indent=2, ensure_ascii=False)
    
    def _analyze_years(self, papers: list) -> dict:
        """Analyze publication year distribution"""
        years = [p.get("year") for p in papers if p.get("year")]
        year_counts = Counter(years)
        return dict(sorted(year_counts.items()))
    
    def _analyze_keywords(self, papers: list) -> dict:
        """Analyze keyword frequency across papers"""
        all_keywords = []
        for paper in papers:
            all_keywords.extend(paper.get("keywords", []))
        
        keyword_counts = Counter(all_keywords)
        return dict(keyword_counts.most_common(20))
    
    def _identify_themes(self, papers: list) -> list:
        """Identify common themes in papers"""
        all_keywords = []
        for paper in papers:
            all_keywords.extend(paper.get("keywords", []))
        
        keyword_freq = Counter(all_keywords)
        top_keywords = [k for k, v in keyword_freq.most_common(10)]
        
        themes = []
        for keyword in top_keywords:
            related_papers = []
            for paper in papers:
                if keyword in paper.get("keywords", []):
                    related_papers.append({
                        "title": paper.get("title"),
                        "year": paper.get("year")
                    })
            
            if related_papers:
                themes.append({
                    "theme_name": keyword.capitalize(),
                    "paper_count": len(related_papers),
                    "papers": related_papers[:5]
                })
        
        return themes
    
    def _calculate_stats(self, papers: list) -> dict:
        """Calculate various statistics"""
        return {
            "avg_text_length": sum(p.get("full_text_length", 0) for p in papers) // len(papers) if papers else 0,
            "papers_with_methodology": sum(1 for p in papers if p.get("methodology")),
            "papers_with_conclusion": sum(1 for p in papers if p.get("conclusion")),
            "unique_authors": len(set(author for p in papers for author in p.get("authors", []) if author))
        }
    
    def _group_papers(self, papers: list) -> dict:
        """Group papers by year ranges"""
        recent = [p for p in papers if str(p.get("year", "")).startswith(("2024", "2025"))]
        older = [p for p in papers if str(p.get("year", "")).startswith(("2020", "2021", "2022", "2023"))]
        
        return {
            "recent_papers": len(recent),
            "older_papers": len(older)
        }
