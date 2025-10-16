# src/research_analyst_literature_generator/crew.py
import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool
from dotenv import load_dotenv

from .tools import (
    PaperDownloadTool,
    PDFParserTool,
    DataAnalysisTool,
    CitationFormatterTool
)

load_dotenv()

# Configure LLM (OpenAI)
llm = LLM(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.7,
)


@CrewBase
class ResearchPaperAnalyzerCrew():
    """Research Paper Analysis and Literature Review Generator Crew"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    def __init__(self):
        self.file_read_tool = FileReadTool()
        self.paper_download_tool = PaperDownloadTool()
        self.pdf_parser_tool = PDFParserTool()
        self.data_analysis_tool = DataAnalysisTool()
        self.citation_tool = CitationFormatterTool()
    
    # ... all agent definitions stay the same ...
    
    @agent
    def research_coordinator(self) -> Agent:
        return Agent(
            config=self.agents_config['research_coordinator'],
            tools=[],
            llm=llm,
            allow_delegation=False,
            max_iter=10,
            memory=False,
        )
    
    @agent
    def paper_discovery(self) -> Agent:
        return Agent(
            config=self.agents_config['paper_discovery'],
            tools=[self.paper_download_tool],
            llm=llm,
            allow_delegation=False,
            max_iter=10,
            memory=False,
        )
    
    @agent
    def content_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['content_extractor'],
            tools=[self.pdf_parser_tool, self.file_read_tool],
            llm=llm,
            allow_delegation=False,
            max_iter=10,
            memory=False,
        )
    
    @agent
    def synthesis_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['synthesis_analyst'],
            tools=[self.data_analysis_tool, self.file_read_tool],
            llm=llm,
            allow_delegation=False,
            max_iter=10,
            memory=False,
        )
    
    @agent
    def critical_evaluator(self) -> Agent:
        return Agent(
            config=self.agents_config['critical_evaluator'],
            tools=[self.file_read_tool],
            llm=llm,
            allow_delegation=False,
            max_iter=10,
            memory=False,
        )
    
    @agent
    def report_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['report_generator'],
            tools=[self.citation_tool, self.file_read_tool],
            llm=llm,
            allow_delegation=False,
            max_iter=10,
            memory=False,
        )
    
    # ... all task definitions stay the same ...
    
    @task
    def create_research_strategy(self) -> Task:
        return Task(
            config=self.tasks_config['create_research_strategy'],
            output_file='outputs/research_strategy.json'
        )
    
    @task
    def search_and_download_papers(self) -> Task:
        return Task(
            config=self.tasks_config['search_and_download_papers'],
        )
    
    @task
    def extract_paper_content(self) -> Task:
        return Task(
            config=self.tasks_config['extract_paper_content'],
        )
    
    @task
    def synthesize_findings(self) -> Task:
        return Task(
            config=self.tasks_config['synthesize_findings'],
        )
    
    @task
    def evaluate_research_quality(self) -> Task:
        return Task(
            config=self.tasks_config['evaluate_research_quality'],
            output_file='outputs/evaluation.json'
        )
    
    @task
    def generate_literature_review(self) -> Task:
        return Task(
            config=self.tasks_config['generate_literature_review'],
            output_file='outputs/literature_review_final.md'
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Research Paper Analyzer crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,  # ✅ This actually CAN do parallel
            verbose=True,
            memory=False,
        )
