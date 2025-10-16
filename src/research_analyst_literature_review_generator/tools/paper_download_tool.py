# tools/paper_download_tool.py
import os
import json
import time
import requests
import subprocess
import tempfile
import shutil
from typing import Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Session for API requests
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "PaperFetcher/1.1"})

def sanitize_filename(name, max_len=80):
    """Sanitize filename for safe file creation"""
    if not name:
        return "untitled"
    safe = "".join(c for c in name if c.isalnum() or c in " _-").strip()
    return (safe[:max_len]).rstrip(" .")

def normalize_doi(doi: str | None) -> str | None:
    """Normalize DOI format"""
    if not doi:
        return None
    doi = doi.strip()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:", "DOI:"):
        if doi.lower().startswith(prefix):
            return doi[len(prefix):]
    return doi

def get_pdf_url_from_openalex(paper: dict) -> str | None:
    """Extract PDF URL from OpenAlex paper data"""
    loc = paper.get("best_oa_location") or {}
    if loc.get("pdf_url"):
        return loc["pdf_url"]
    
    ploc = paper.get("primary_location") or {}
    if ploc.get("pdf_url"):
        return ploc["pdf_url"]
    
    for l in (paper.get("locations") or []):
        if isinstance(l, dict) and l.get("pdf_url"):
            return l["pdf_url"]
    return None

def get_pdf_url_from_unpaywall(doi: str, email: str) -> str | None:
    """Get PDF URL from Unpaywall API"""
    doi_norm = normalize_doi(doi)
    if not doi_norm:
        return None
    url = f"https://api.unpaywall.org/v2/{doi_norm}?email={email}"
    try:
        r = SESSION.get(url, timeout=20)
        time.sleep(0.4)
        if r.status_code != 200:
            return None
        data = r.json()
        loc = data.get("best_oa_location")
        if loc and loc.get("url_for_pdf"):
            return loc["url_for_pdf"]
    except Exception:
        pass
    return None

def download_from_scihub(doi: str, output_path: str) -> bool:
    """Download PDF from Sci-Hub using scidownl"""
    doi_norm = normalize_doi(doi)
    if not doi_norm:
        return False
    
    print(f"   🔓 Trying Sci-Hub for DOI: {doi_norm}")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # CRITICAL: Add trailing slash
            temp_dir_with_slash = temp_dir + os.sep
            
            result = subprocess.run(
                ["scidownl", "download", "--doi", f"https://doi.org/{doi_norm}", 
                 "--out", temp_dir_with_slash],
                capture_output=True,
                text=True,
                timeout=90
            )
            
            time.sleep(0.5)
            downloaded_files = os.listdir(temp_dir)
            pdf_files = [f for f in downloaded_files if f.lower().endswith('.pdf')]
            
            if pdf_files:
                source_pdf = os.path.join(temp_dir, pdf_files[0])
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                shutil.move(source_pdf, output_path)
                print(f"   ✓ Downloaded from Sci-Hub: {os.path.basename(output_path)}")
                return True
            else:
                print("   ⚠️ Sci-Hub download failed")
                return False
                
        except subprocess.TimeoutExpired:
            print("   ⚠️ Sci-Hub request timed out")
            return False
        except FileNotFoundError:
            print("   ⚠️ scidownl not installed")
            return False
        except Exception as e:
            print(f"   ↪️ Sci-Hub error: {e}")
            return False

def download_pdf(pdf_url, filepath):
    """Download PDF from URL"""
    try:
        with SESSION.get(
            pdf_url,
            headers={"Accept": "application/pdf"},
            timeout=60,
            stream=True,
            allow_redirects=True,
        ) as r:
            if r.status_code != 200:
                return False
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 64):
                    if chunk:
                        f.write(chunk)
        print(f"✅ Downloaded: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def stream_openalex_papers(topic, from_year=None, to_year=None, page_size=25):
    """Stream papers from OpenAlex API"""
    OPENALEX_BASE = "https://api.openalex.org/works"
    OPENALEX_MAILTO = os.getenv("OPENALEX_MAILTO", "research@example.com")
    
    filters = ["is_oa:true"]
    if from_year:
        filters.append(f"from_publication_date:{from_year}-01-01")
    if to_year:
        filters.append(f"to_publication_date:{to_year}-12-31")

    cursor = "*"
    while True:
        params = {
            "search": topic,
            "filter": ",".join(filters),
            "per_page": page_size,
            "cursor": cursor,
            "mailto": OPENALEX_MAILTO,
        }
        try:
            resp = SESSION.get(OPENALEX_BASE, params=params, timeout=20)
            time.sleep(0.5)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"❌ OpenAlex request failed: {e}")
            return

        results = data.get("results", []) or []
        if not results:
            return

        for p in results:
            yield p

        next_cursor = data.get("meta", {}).get("next_cursor")
        if not next_cursor:
            return
        cursor = next_cursor


class PaperDownloadInput(BaseModel):
    """Input schema for PaperDownloadTool"""
    topic: str = Field(..., description="Research topic to search for")
    target_count: int = Field(default=5, description="Number of papers to download")
    from_year: int = Field(default=None, description="Start year for paper search")
    to_year: int = Field(default=None, description="End year for paper search")


class PaperDownloadTool(BaseTool):
    name: str = "Paper Download Tool"
    description: str = """
    Searches for academic papers on OpenAlex and downloads PDFs using 
    Unpaywall and Sci-Hub. Returns paths to downloaded papers and metadata.
    Input: topic (required), target_count (default=5), from_year (optional), to_year (optional)
    """
    args_schema: Type[BaseModel] = PaperDownloadInput

    def _run(self, topic: str, target_count: int = 5, from_year: int = None, to_year: int = None) -> str:
        """Execute paper download"""
        print(f"\n🔎 Searching papers on: '{topic}'")
        
        save_dir = os.path.join("papers", sanitize_filename(topic))
        os.makedirs(save_dir, exist_ok=True)
        
        downloaded = 0
        metadata_list = []
        unpaywall_email = os.getenv("UNPAYWALL_EMAIL", "research@example.com")
        
        for paper in stream_openalex_papers(topic, from_year, to_year):
            if downloaded >= target_count:
                break
                
            title = paper.get("title") or "untitled"
            year = paper.get("publication_year") or "Unknown"
            doi = paper.get("doi")
            
            print(f"\n📄 {title}")
            
            filename = f"{year}-{sanitize_filename(title)}.pdf"
            filepath = os.path.join(save_dir, filename)
            
            # Try OpenAlex → Unpaywall → Sci-Hub
            pdf_url = get_pdf_url_from_openalex(paper)
            success = False
            
            if pdf_url:
                success = download_pdf(pdf_url, filepath)
            
            if not success and doi:
                pdf_url = get_pdf_url_from_unpaywall(doi, unpaywall_email)
                if pdf_url:
                    success = download_pdf(pdf_url, filepath)
            
            if not success and doi:
                success = download_from_scihub(doi, filepath)
            
            if success:
                downloaded += 1
                metadata_list.append({
                    "title": title,
                    "year": year,
                    "doi": doi,
                    "file_path": filepath,
                    "authors": [a.get("author", {}).get("display_name") for a in paper.get("authorships", [])[:3]],
                    "abstract": paper.get("abstract_inverted_index")
                })
                time.sleep(0.8)
        
        # Save metadata
        metadata_path = os.path.join("outputs", "paper_metadata.json")
        os.makedirs("outputs", exist_ok=True)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata_list, f, indent=2, ensure_ascii=False)
        
        result = {
            "downloaded_count": downloaded,
            "papers_directory": save_dir,
            "metadata_file": metadata_path,
            "papers": metadata_list
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
