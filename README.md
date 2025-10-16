# 🎓 Automated Literature Review Generator

> Multi-agent AI system that automatically generates comprehensive literature reviews from research papers using CrewAI.

## 📋 Overview

This system uses 6 specialized AI agents to automate the entire literature review process - from discovering and downloading papers to generating publication-ready reviews with detailed analysis, comparisons, and citations.

**Input:** Research topic (e.g., "Machine Learning")  
**Output:** 4,000-6,000 word literature review with themes, methodology comparisons, quality assessments, and APA citations  
**Time:** ~10-15 minutes

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone <your-repo-url>
cd research_analyst_literature_generator

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Configuration

Create `.env` file:

```env
OPENAI_API_KEY=sk-your-key-here
OPENALEX_MAILTO=your-email@example.com
UNPAYWALL_EMAIL=your-email@example.com
```

### Run

```bash
crewai run
```

Enter your research topic when prompted, and wait for the system to generate the complete literature review.

## 📁 Project Structure

```
research_analyst_literature_generator/
├── outputs/                          # Generated files
│   ├── research_strategy.json
│   ├── paper_metadata.json
│   ├── extracted_content.json
│   ├── synthesis.json
│   ├── evaluation.json
│   └── literature_review_final.md   # Main output
├── papers/                           # Downloaded PDFs
├── src/research_analyst_literature_generator/
│   ├── main.py                       # Entry point
│   ├── crew.py                       # Agent orchestration
│   ├── tools/                        # Custom tools
│   │   ├── paper_download_tool.py
│   │   ├── pdf_parser_tool.py
│   │   ├── data_analysis_tool.py
│   │   └── citation_tool.py
│   └── config/
│       ├── agents.yaml               # Agent definitions
│       └── tasks.yaml                # Task descriptions
└── .env                              # API keys
```

## 🤖 System Architecture

### Agents

1. **Research Coordinator** - Creates search strategy and keywords
2. **Paper Discovery** - Downloads 5 papers from OpenAlex/Sci-Hub
3. **Content Extractor** - Parses PDFs, extracts methodology and results
4. **Synthesis Analyst** - Identifies themes and patterns
5. **Critical Evaluator** - Assesses quality and identifies gaps
6. **Report Generator** - Writes final literature review

### Workflow

```
User Input (Topic)
    ↓
Agent 1: Strategy → research_strategy.json
    ↓
Agent 2: Download → papers/*.pdf + paper_metadata.json
    ↓
Agent 3: Extract → extracted_content.json
    ↓
┌───────────────┬───────────────┐
Agent 4: Synthesis  Agent 5: Evaluation  (Parallel capable)
└───────────────┴───────────────┘
    ↓
Agent 6: Report → literature_review_final.md
```

### Tools

- **Paper Download Tool** - OpenAlex API, Unpaywall API, scidownl
- **PDF Parser Tool** - PyMuPDF for text extraction
- **Data Analysis Tool** - pandas for synthesis
- **Citation Formatter** - APA citation generation
- **FileReadTool** - CrewAI built-in for file reading

## 📊 Sample Output

The system generates:

- ✅ 5 JSON files with intermediate data
- ✅ 5 downloaded research papers (PDFs)
- ✅ 4,000-6,000 word literature review with:
  - Executive summary
  - Thematic analysis (4-6 themes)
  - Methodology comparison tables
  - Key findings synthesis
  - Quality assessment (scored 1-10)
  - Research gaps (10-15 identified)
  - Future directions (10+ suggestions)
  - APA-formatted references

## 🔧 Troubleshooting

### File not found errors

Ensure paths use `outputs/` prefix in `tasks.yaml`:

```yaml
# Read file: outputs/extracted_content.json
```

### Unicode errors

Use UTF-8 encoding in all tools:

```python
with open(file, 'r', encoding='utf-8') as f:
    data = json.load(f)
```

### API rate limits

- Use GPT-4o-mini (higher limits)
- Or switch to local Ollama

## 📦 Requirements

```
Python 3.10+
crewai[tools]>=0.70.0
python-dotenv>=1.0.0
pymupdf>=1.24.0
pandas>=2.2.0
requests>=2.31.0
scidownl>=1.0.0
```

## 🎯 Assignment Criteria Met

- ✅ 6 agents with role specialization
- ✅ Sequential + parallel execution architecture
- ✅ Role-tailored prompts in YAML configs
- ✅ Context sharing via 5 JSON intermediate files
- ✅ 5 tools integrated (4 custom + 1 prebuilt)
- ✅ Structured outputs (JSON + Markdown)

## 👨‍💻 Author

**Akaash Gupta Vandanapu**  

akaashgupta2005@gmail.com