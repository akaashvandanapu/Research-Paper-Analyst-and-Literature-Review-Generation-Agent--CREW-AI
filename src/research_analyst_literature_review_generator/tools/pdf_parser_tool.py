# tools/pdf_parser_tool.py
import json
import os
from typing import Type
import pymupdf  # PyMuPDF
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class PDFParserInput(BaseModel):
    """Input schema for PDFParserTool"""
    metadata_file: str = Field(..., description="Path to paper_metadata.json file")


class PDFParserTool(BaseTool):
    name: str = "PDF Parser Tool"
    description: str = """
    Extracts text content from research paper PDFs. 
    Parses abstract, methodology, findings, and conclusions.
    Input: Path to metadata JSON file containing paper file paths.
    """
    args_schema: Type[BaseModel] = PDFParserInput

    def _run(self, metadata_file: str) -> str:
        """Extract content from PDFs"""
        print(f"\n📖 Parsing PDFs from: {metadata_file}")
        
        if not os.path.exists(metadata_file):
            return json.dumps({"error": f"Metadata file not found: {metadata_file}"})
        
        with open(metadata_file, 'r', encoding='utf-8') as f:
            papers = json.load(f)
        
        extracted_data = []
        
        for paper in papers:
            file_path = paper.get("file_path")
            if not file_path or not os.path.exists(file_path):
                print(f"⚠️ File not found: {file_path}")
                continue
            
            try:
                print(f"📄 Parsing: {os.path.basename(file_path)}")
                
                # Extract text using PyMuPDF
                doc = pymupdf.open(file_path)
                full_text = ""
                for page in doc:
                    full_text += page.get_text()
                doc.close()
                
                # Extract sections (simple heuristic)
                sections = self._extract_sections(full_text)
                
                extracted_data.append({
                    "title": paper.get("title"),
                    "year": paper.get("year"),
                    "doi": paper.get("doi"),
                    "authors": paper.get("authors", []),
                    "full_text_length": len(full_text),
                    "abstract": sections.get("abstract", "")[:1000],
                    "introduction": sections.get("introduction", "")[:1500],
                    "methodology": sections.get("methodology", "")[:1500],
                    "results": sections.get("results", "")[:1500],
                    "conclusion": sections.get("conclusion", "")[:1000],
                    "keywords": self._extract_keywords(full_text)
                })
                
            except Exception as e:
                print(f"❌ Error parsing {file_path}: {e}")
                continue
        
        # Save extracted content
        output_path = os.path.join("outputs", "extracted_content.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Extracted content from {len(extracted_data)} papers")
        
        return json.dumps({
            "extracted_papers": len(extracted_data),
            "output_file": output_path,
            "papers": extracted_data
        }, indent=2, ensure_ascii=False)
    
    def _extract_sections(self, text: str) -> dict:
        """Extract paper sections using keyword matching"""
        text_lower = text.lower()
        sections = {}
        
        # Simple section extraction
        section_keywords = {
            "abstract": ["abstract"],
            "introduction": ["introduction", "1. introduction"],
            "methodology": ["methodology", "methods", "materials and methods"],
            "results": ["results", "findings"],
            "conclusion": ["conclusion", "discussion"]
        }
        
        for section, keywords in section_keywords.items():
            for keyword in keywords:
                idx = text_lower.find(keyword)
                if idx != -1:
                    sections[section] = text[idx:idx+1000]
                    break
        
        return sections
    
    def _extract_keywords(self, text: str) -> list:
        """Extract potential keywords from text"""
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
        words = text.lower().split()
        word_freq = {}
        
        for word in words:
            word_clean = ''.join(c for c in word if c.isalnum())
            if len(word_clean) > 4 and word_clean not in common_words:
                word_freq[word_clean] = word_freq.get(word_clean, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
