from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from constaty_insurance.guardrails import maximum_two_questions
from constaty_insurance.models import ConstatTaskOutput, RiskAnalysisOutput
from constaty_insurance.tools import BaremeTesterTool


@CrewBase
class ConstatyInsuranceCrew:
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def constat_intake_specialist(self) -> Agent:
        return Agent(config=self.agents_config["constat_intake_specialist"])

    @agent
    def claim_structuring_specialist(self) -> Agent:
        return Agent(config=self.agents_config["claim_structuring_specialist"])

    @agent
    def vehicle_damage_assessment_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["vehicle_damage_assessment_specialist"]
        )

    @agent
    def risk_detector_agent(self) -> Agent:
        return Agent(
            config=self.agents_config["risk_detector_agent"],
            tools=[BaremeTesterTool()],
        )

    @agent
    def insurance_decision_support_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config["insurance_decision_support_specialist"]
        )

    @task
    def collect_constat_task(self) -> Task:
        return Task(
            config=self.tasks_config["collect_constat_task"],
            agent=self.constat_intake_specialist(),
            output_json=ConstatTaskOutput,
            guardrail=maximum_two_questions,
        )

    @task
    def structure_claim_task(self) -> Task:
        return Task(
            config=self.tasks_config["structure_claim_task"],
            agent=self.claim_structuring_specialist(),
            context=[self.collect_constat_task()],
        )

    @task
    def assess_vehicle_damage_task(self) -> Task:
        return Task(
            config=self.tasks_config["assess_vehicle_damage_task"],
            agent=self.vehicle_damage_assessment_specialist(),
            context=[self.collect_constat_task(), self.structure_claim_task()],
        )

    @task
    def analyze_claim_risk_task(self) -> Task:
        return Task(
            config=self.tasks_config["analyze_claim_risk_task"],
            agent=self.risk_detector_agent(),
            context=[self.structure_claim_task(), self.assess_vehicle_damage_task()],
            output_json=RiskAnalysisOutput,
        )

    @task
    def create_decision_report_task(self) -> Task:
        return Task(
            config=self.tasks_config["create_decision_report_task"],
            agent=self.insurance_decision_support_specialist(),
            context=[
                self.structure_claim_task(),
                self.assess_vehicle_damage_task(),
                self.analyze_claim_risk_task(),
            ],
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,
        )
