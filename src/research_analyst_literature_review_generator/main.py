#!/usr/bin/env python
# src/research_analyst_literature_generator/main.py
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Fix: Use relative import or correct package name
from .crew import ResearchPaperAnalyzerCrew
# OR
# from research_analyst_literature_generator.crew import ResearchPaperAnalyzerCrew

# Load environment variables
load_dotenv()


def run():
    """Run the Research Paper Analyzer crew."""
    print("\n" + "="*70)
    print("🎓 AI-Powered Research Paper Analysis & Literature Review Generator")
    print("="*70 + "\n")
    
    # Get user input
    topic = input("📌 Enter research topic: ").strip()
    if not topic:
        print("❌ Error: Topic cannot be empty")
        sys.exit(1)
    
    # ✅ HARDCODE NUMBER OF PAPERS
    num_papers = 5
    
    print(f"\n🔍 Starting literature review generation for: '{topic}'")
    print(f"📄 Target papers: {num_papers}")  # ✅ Show user
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "-"*70 + "\n")
    
    # Create output directories
    os.makedirs("outputs", exist_ok=True)
    os.makedirs("papers", exist_ok=True)
    
    # Initialize and run crew
    try:
        inputs = {
            'topic': topic,
            'target_count': num_papers  # ✅ Pass to crew
        }
        
        print("🚀 Initializing crew...")
        crew = ResearchPaperAnalyzerCrew()
        
        print("⚙️ Starting workflow...\n")
        result = crew.crew().kickoff(inputs=inputs)
        
        print("\n" + "="*70)
        print("✅ LITERATURE REVIEW GENERATION COMPLETE!")
        print("="*70 + "\n")
        
        print("📂 Generated Files:")
        print("  ├── outputs/research_strategy.json")
        print("  ├── outputs/paper_metadata.json")
        print("  ├── outputs/extracted_content.json")
        print("  ├── outputs/synthesis.json")
        print("  ├── outputs/evaluation.json")
        print("  └── outputs/literature_review_final.md")
        print("\n  📁 papers/ (Downloaded PDFs)")
        
        print("\n" + "-"*70)
        print("\n📄 Final Report Preview:\n")
        print(str(result)[:500] + "...\n")
        
        print("🎉 Done! Check the outputs/ folder for all generated files.")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def train():
    """
    Train the crew for a given number of iterations (optional).
    """
    inputs = {
        "topic": "Machine Learning in Healthcare"
    }
    try:
        crew = ResearchPaperAnalyzerCrew()
        crew.crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)
    except Exception as e:
        raise Exception(f"Training failed: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        crew = ResearchPaperAnalyzerCrew()
        crew.crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"Replay failed: {e}")


def test():
    """
    Test the crew execution with a sample topic.
    """
    inputs = {
        "topic": "Explainable AI"
    }
    try:
        crew = ResearchPaperAnalyzerCrew()
        crew.crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"Test failed: {e}")
