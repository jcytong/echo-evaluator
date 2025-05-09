from agents.base_evaluator import BaseEvaluator
from agents.rubrics import (
    FOUNDER_EDGE_RUBRIC,
    NOVEL_WEDGE_RUBRIC,
    CUSTOMER_SIGNAL_RUBRIC,
    SALES_MOTION_RUBRIC,
    MOAT_POTENTIAL_RUBRIC,
    INVESTOR_BEHAVIOR_RUBRIC,
    INCUMBENT_BLIND_SPOT_RUBRIC
)
from typing import Dict, Any, List
from langchain.chat_models import ChatOpenAI

class FounderEdgeEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__("Founder Edge", FOUNDER_EDGE_RUBRIC)
    
    def get_search_queries(self, company_data: Dict[str, Any]) -> List[str]:
        company_name = company_data.get("name", "")
        return [
            f"{company_name} founders background experience",
            f"{company_name} founding team",
            f"{company_name} CEO linkedin",
            f"{company_name} founders previous startups"
        ]
    
    def trim_company_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        if not company_data:
            return None
            
        return {
            "name": company_data.get("name"),
            "summary": company_data.get("summary"),
            "employee_count": company_data.get("employee_count"),
            "employee_count_by_role": company_data.get("employee_count_by_role"),
            "average_tenure_by_level": company_data.get("average_tenure_by_level"),
            "funding_details": company_data.get("funding_details"),
            "linkedin_url": company_data.get("linkedin_url"),
            "twitter_url": company_data.get("twitter_url")
        }

class NovelWedgeEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__("Novel Wedge", NOVEL_WEDGE_RUBRIC)
    
    def get_search_queries(self, company_data: Dict[str, Any]) -> List[str]:
        company_name = company_data.get("name", "")
        industry = company_data.get("industry", "")
        return [
            f"{company_name} unique value proposition",
            f"{company_name} competitive advantage {industry}",
            f"{company_name} market positioning",
            f"{company_name} product differentiation"
        ]
    
    def trim_company_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        if not company_data:
            return None
            
        return {
            "name": company_data.get("name"),
            "summary": company_data.get("summary"),
            "founded": company_data.get("founded"),
            "industry": company_data.get("industry"),
            "headline": company_data.get("headline"),
            "website": company_data.get("website"),
            "linkedin_url": company_data.get("linkedin_url")
        }

class CustomerSignalEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__("Customer Signal", CUSTOMER_SIGNAL_RUBRIC)
    
    def get_search_queries(self, company_data: Dict[str, Any]) -> List[str]:
        company_name = company_data.get("name", "")
        return [
            f"{company_name} customer reviews",
            f"{company_name} customer growth",
            f"{company_name} client testimonials",
            f"{company_name} market traction"
        ]
    
    def trim_company_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        if not company_data:
            return None
            
        return {
            "name": company_data.get("name"),
            "summary": company_data.get("summary"),
            "employee_count": company_data.get("employee_count"),
            "employee_count_by_month": company_data.get("employee_count_by_month"),
            "inferred_revenue": company_data.get("inferred_revenue"),
            "employee_growth_rate": company_data.get("employee_growth_rate"),
            "linkedin_follower_count": company_data.get("linkedin_follower_count")
        }

class SalesMotionEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__("Sales Motion", SALES_MOTION_RUBRIC)
    
    def get_search_queries(self, company_data: Dict[str, Any]) -> List[str]:
        company_name = company_data.get("name", "")
        return [
            f"{company_name} sales strategy",
            f"{company_name} go to market",
            f"{company_name} customer acquisition",
            f"{company_name} sales team structure"
        ]
    
    def trim_company_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        if not company_data:
            return None
            
        return {
            "name": company_data.get("name"),
            "summary": company_data.get("summary"),
            "employee_count_by_role": company_data.get("employee_count_by_role"),
            "size": company_data.get("size"),
            "employee_count": company_data.get("employee_count"),
            "inferred_revenue": company_data.get("inferred_revenue")
        }

class MoatPotentialEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__("Moat Potential", MOAT_POTENTIAL_RUBRIC)
    
    def get_search_queries(self, company_data: Dict[str, Any]) -> List[str]:
        company_name = company_data.get("name", "")
        industry = company_data.get("industry", "")
        return [
            f"{company_name} competitive moat",
            f"{company_name} technology stack",
            f"{company_name} patents intellectual property",
            f"{company_name} market barriers entry {industry}"
        ]
    
    def trim_company_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        if not company_data:
            return None
            
        return {
            "name": company_data.get("name"),
            "summary": company_data.get("summary"),
            "industry": company_data.get("industry"),
            "technologies": company_data.get("technologies", []),
            "employee_count_by_role": company_data.get("employee_count_by_role"),
            "average_employee_tenure": company_data.get("average_employee_tenure")
        }

class InvestorBehaviorEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__("Investor Behavior", INVESTOR_BEHAVIOR_RUBRIC)
    
    def get_search_queries(self, company_data: Dict[str, Any]) -> List[str]:
        company_name = company_data.get("name", "")
        return [
            f"{company_name} funding rounds",
            f"{company_name} investors",
            f"{company_name} venture capital",
            f"{company_name} investment news"
        ]
    
    def trim_company_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        if not company_data:
            return None
            
        return {
            "name": company_data.get("name"),
            "funding_details": company_data.get("funding_details", []),
            "latest_funding_stage": company_data.get("latest_funding_stage"),
            "total_funding_raised": company_data.get("total_funding_raised"),
            "last_funding_date": company_data.get("last_funding_date"),
            "number_funding_rounds": company_data.get("number_funding_rounds")
        }

class IncumbentBlindSpotEvaluator(BaseEvaluator):
    def __init__(self):
        super().__init__("Incumbent Blind Spot", INCUMBENT_BLIND_SPOT_RUBRIC)
    
    def get_search_queries(self, company_data: Dict[str, Any]) -> List[str]:
        company_name = company_data.get("name", "")
        industry = company_data.get("industry", "")
        return [
            f"{company_name} market disruption",
            f"{company_name} competitive landscape {industry}",
            f"{company_name} industry innovation",
            f"{company_name} market opportunity"
        ]
    
    def trim_company_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        if not company_data:
            return None
            
        return {
            "name": company_data.get("name"),
            "summary": company_data.get("summary"),
            "industry": company_data.get("industry"),
            "competitors": company_data.get("competitors", []),
            "employee_count": company_data.get("employee_count"),
            "inferred_revenue": company_data.get("inferred_revenue"),
            "size": company_data.get("size")
        } 