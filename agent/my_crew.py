from typing import List
from pydantic import BaseModel, Field
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew
from crewai_tools import SerperDevTool, ScrapeWebsiteTool



class HotelInfo(BaseModel):
    hotel_name: str = Field(..., description="Hotel name")
    hotel_location: str = Field(..., description="Location")
    hotel_daily_price: float = Field(..., description="The daily price of the hotel in $ dolar")
    hotel_certificates: List[str] = Field(..., description="Certifications")
    accessibility_features: List[str] = Field(default=[], description="Accessibility features")
    benefits: List[str] = Field(default=[], description="Amenities")
    review_score: float = Field(default=0.0, description="Review score")

class HotelRecommendation(BaseModel):
    recommended_hotels: List[HotelInfo] = Field(..., description="List of recommended hotels")
    search_summary: str = Field(..., description="Summary")


@CrewBase
class AIHotelAdvisor:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    
    @agent
    def hotel_search_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['hotel_search_agent'],
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            verbose=True
        )
    
    @agent
    def review_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['review_analysis_agent'],
            verbose=True
        )
    
    @agent
    def certification_specialist_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['certification_specialist_agent'],
            verbose=True
        )
    
    @agent
    def accessibility_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['accessibility_agent'],
            verbose=True
        )
    
    @agent
    def benefits_analysis_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['benefits_analysis_agent'],
            verbose=True
        )
   
    @task
    def hotel_search_task(self) -> Task:
        return Task(
            config=self.tasks_config['hotel_search_task'],
            agent=self.hotel_search_agent(),
            verbose=True
        )
    
    @task
    def review_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['review_analysis_task'],
            agent=self.review_analysis_agent(),
            verbose=True
        )
    
    @task
    def certification_check_task(self) -> Task:
        return Task(
            config=self.tasks_config['certification_check_task'],
            agent=self.certification_specialist_agent(),
            verbose=True
        )
    
    @task
    def accessibility_check_task(self) -> Task:
        return Task(
            config=self.tasks_config['accessibility_check_task'],
            agent=self.accessibility_agent(),
            verbose=True
        )
    
    @task
    def benefits_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['benefits_analysis_task'],
            agent=self.benefits_analysis_agent(),
            verbose=True,
            output_pydantic=HotelRecommendation,
            output_file="hotel_recommendations.json"

        )
   
    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True,
            process=Process.sequential
        )