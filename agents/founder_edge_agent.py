from langchain.agents import Tool, initialize_agent
from langchain_openai import ChatOpenAI
from tools.search_tool import search_tool
import os
from agents.base_evaluator import BaseEvaluator
from agents.evaluators import FounderEdgeEvaluator

def extract_score(response):
    # crude scoring parser, can improve with regex or LLM
    if "3" in response: return 3
    if "2" in response: return 2
    if "1" in response: return 1
    return 0

def trim_company_data(company_data):
    # Extract only essential fields for founder evaluation
    essential_fields = {
        "name": company_data.get("name"),
        "display_name": company_data.get("display_name"),
        "summary": company_data.get("summary"),
        "headline": company_data.get("headline"),
        "founded": company_data.get("founded"),
        "website": company_data.get("website"),
        "linkedin_url": company_data.get("linkedin_url"),
        "twitter_url": company_data.get("twitter_url"),
        "total_funding_raised": company_data.get("total_funding_raised"),
        "latest_funding_stage": company_data.get("latest_funding_stage"),
        "last_funding_date": company_data.get("last_funding_date")
    }
    return essential_fields

FOUNDER_EDGE_RUBRIC = """Definition:
Founder Edge is the unique combination of factors that give a founder an advantage over other founders in the same space. The following are examples of Founder Edges:
- Deep domain expertise
- Prior startup/operating experience in the same space
- Significant network access to potential customers, investors, talent and partners
- Strong personal brand
- Fundraising credibility
- Unique cultural fit
- Exceptional execution skills
- Unique technical insights
- Unique customer acquisition insights

Use this rubric:
- 0: No clear advantage
- 1: Mild advantage
- 2: Clear domain edge
- 3: Strong & unique edge (repeat founder, elite fit)"""

class FounderEdgeEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__(
            dimension_name="Founder Edge",
            rubric=FOUNDER_EDGE_RUBRIC
        )
    
    def trim_company_data(self, company_data):
        # Add founder-specific fields to the base data
        base_data = super().trim_company_data(company_data)
        base_data.update({
            "employee_count": company_data.get("employee_count"),
            "employee_count_by_role": company_data.get("employee_count_by_role"),
            "average_tenure_by_level": company_data.get("average_tenure_by_level"),
            "funding_details": company_data.get("funding_details")
        })
        return base_data

def evaluate(company_data):
    evaluator = FounderEdgeEvaluator()
    return evaluator.evaluate(company_data)
