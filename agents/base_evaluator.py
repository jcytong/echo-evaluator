from typing import Dict, Any, Optional, List
from langchain.chat_models import ChatOpenAI
from tools.search_tool import search_tool
import logging
import re

class BaseEvaluator:
    def __init__(self, dimension_name: str, rubric: str):
        self.dimension_name = dimension_name
        self.rubric = rubric
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0
        )
        self.search_tool = search_tool
        self.logger = logging.getLogger(__name__)
        
    def get_company_data(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract company data from the nested structure"""
        self.logger.info(f"Received data structure: {type(data)}")
        
        if not data:
            self.logger.warning("Received empty data")
            return None
            
        if not isinstance(data, dict):
            self.logger.warning(f"Expected dict, got {type(data)}")
            return None
            
        self.logger.info(f"Data keys: {data.keys()}")
            
        # Handle nested data structure
        if "data" in data and isinstance(data["data"], list):
            if not data["data"]:  # Empty list
                self.logger.warning("Company data list is empty")
                return None
                
            self.logger.info(f"Found {len(data['data'])} companies in data list")
            return data["data"][0]
            
        # If no nested structure, return the data as is
        return data
        
    def get_search_queries(self, company_data: Dict[str, Any]) -> List[str]:
        """Get dimension-specific search queries. Override in subclasses."""
        company_name = company_data.get("name", "")
        return [f"{company_name} {self.dimension_name}"]
        
    def search_web(self, company_data: Dict[str, Any]) -> str:
        """Perform multiple targeted web searches for the company"""
        try:
            queries = self.get_search_queries(company_data)
            all_results = []
            
            for query in queries:
                try:
                    results = self.search_tool.run(query)
                    all_results.append(f"Search results for '{query}':\n{results}")
                except Exception as e:
                    self.logger.error(f"Error in individual search query '{query}': {str(e)}")
                    
            return "\n\n".join(all_results) if all_results else ""
            
        except Exception as e:
            self.logger.error(f"Error performing web search: {str(e)}")
            return ""
            
    def evaluate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Starting evaluation for {self.dimension_name}")
        
        company_data = self.get_company_data(data)
        if not company_data:
            self.logger.warning("No company data found")
            return {
                "score": 0,
                "rationale": f"Insufficient company information to evaluate {self.dimension_name}"
            }
            
        # Get trimmed company data
        trimmed_data = self.trim_company_data(company_data)
        if not trimmed_data:
            self.logger.warning("No trimmed data available after processing")
            return {
                "score": 0,
                "rationale": f"Insufficient company information to evaluate {self.dimension_name}"
            }
            
        # Perform targeted web searches
        self.logger.info("Starting web search")
        web_results = self.search_web(company_data)
        self.logger.info(f"Web search completed, found {len(web_results.split())} words")
        
        # Create evaluation prompt
        self.logger.info("Creating evaluation prompt")
        prompt = f"""
        You are a critical evaluator assessing {company_data.get('name')} for the {self.dimension_name} dimension, specifically analyzing its potential as a fast follower opportunity. 
        
        Key Hypothesis to Evaluate:
        1. The company is targeting a proven problem/market where customers will pay
        2. The space has limited incumbents (signaled by competitors being young companies)
        3. Recent technological or market changes enable new solutions
        4. Rapid growth signals strong product-market fit or investor validation
        5. The timing is right for a fast follower strategy
        
        Scoring Guidelines:
        - Score 0: No clear evidence of proven market or concerning red flags
        - Score 1: Some evidence of market potential but significant risks or timing concerns
        - Score 2: Strong evidence of proven market with reasonable entry timing
        - Score 3: Exceptional evidence of perfect timing for fast follower strategy (should be rare)
        
        Critical Questions to Address:
        1. Market Validation:
           - Is there clear evidence that customers will pay for this type of solution?
           - Are early movers showing strong growth/traction?
           - What signals validate the market timing?
        
        2. Competitive Landscape:
           - How fragmented is the current market?
           - Are competitors also young/recently funded?
           - What barriers exist for established players?
        
        3. Growth Signals:
           - Is the headcount growth indicative of revenue growth or just funding?
           - Does the hiring pattern suggest product-market fit?
           - Are there signs of sustainable unit economics?
        
        4. Timing Analysis:
           - Why is now the right time for this solution?
           - What recent changes enable new approaches?
           - Is the market mature enough but not too crowded?
        
        Important Instructions:
        1. Use BOTH company data AND web research to inform your evaluation
        2. Be skeptical - distinguish between genuine signals and funding-driven growth
        3. Explicitly identify missing information that would strengthen the evaluation
        4. Challenge assumptions about market readiness and timing
        5. Consider both technical and go-to-market risks
        6. Your response MUST start with either "Score: X" or just the number X (where X is 0-3)
        7. Justify why the company doesn't deserve a higher score
        8. Question the reliability and completeness of available information
        
        Company Data:
        {trimmed_data}
        
        Web Research Results:
        {web_results}
        
        Evaluation Rubric:
        {self.rubric}
        
        Provide:
        1. A score (0-3) at the start of your response
        2. A detailed analysis that:
           - Evaluates market validation evidence
           - Assesses competitive dynamics
           - Analyzes growth signals
           - Questions timing assumptions
           - Identifies potential risks
           - Lists critical missing information
           - Explains why a higher score wasn't given
        3. A balanced conclusion that weighs all factors
        """
        
        try:
            self.logger.info("Sending evaluation prompt to LLM")
            response = self.llm.predict(prompt)
            self.logger.info(f"Raw response from LLM (first 200 chars): {response[:200]}...")
            self.logger.debug(f"Full response: {response}")
            
            # Parse response to extract score and rationale
            score = 0
            rationale = response
            
            # First try to find an explicit score
            self.logger.info("Attempting to parse score")
            if "score:" in response.lower():
                try:
                    score_part = response.lower().split("score:")[1].split("\n")[0].strip()
                    self.logger.debug(f"Found score part: {score_part}")
                    # Extract first number from the score part
                    numbers = re.findall(r'\d+', score_part)
                    if numbers:
                        score = int(numbers[0])
                        self.logger.info(f"Successfully parsed score from 'Score:' prefix: {score}")
                except Exception as e:
                    self.logger.warning(f"Failed to parse score after 'Score:': {str(e)}")
            
            # If no explicit score found, try to find a number at the start
            if score == 0:
                try:
                    self.logger.info("Attempting to find score at start of response")
                    # Look for a single digit at the start of the response
                    match = re.match(r'^\s*(\d)', response)
                    if match:
                        score = int(match.group(1))
                        self.logger.info(f"Successfully parsed score from start of response: {score}")
                except Exception as e:
                    self.logger.warning(f"Failed to parse score from start: {str(e)}")
            
            # Ensure score is in valid range
            original_score = score
            score = max(0, min(3, score))
            if score != original_score:
                self.logger.warning(f"Score adjusted from {original_score} to {score} to stay within valid range")
            
            # Clean up rationale - try multiple patterns
            self.logger.info("Attempting to extract rationale")
            rationale_patterns = [
                r'(?i)rationale:\s*(.*)', # Case-insensitive "rationale:"
                r'(?i)evaluation:\s*(.*)', # Case-insensitive "evaluation:"
                r'^\s*(?:score:?\s*\d+|[0-3])\s*\n+(.*)', # After score
                r'^\s*(?:score:?\s*\d+|[0-3])\s*(.*)' # After score without newline
            ]
            
            original_rationale = rationale
            for i, pattern in enumerate(rationale_patterns):
                self.logger.debug(f"Trying pattern {i + 1}: {pattern}")
                match = re.search(pattern, response, re.DOTALL)
                if match:
                    rationale = match.group(1).strip()
                    self.logger.info(f"Successfully extracted rationale using pattern {i + 1}")
                    self.logger.debug(f"Rationale starts with: {rationale[:100]}...")
                    break
            
            if rationale == original_rationale:
                self.logger.warning("No rationale pattern matched, using full response as rationale")
            
            self.logger.info(f"Evaluation complete. Final score: {score}")
            return {
                "score": score,
                "rationale": rationale
            }
            
        except Exception as e:
            self.logger.error(f"Error during evaluation: {str(e)}", exc_info=True)
            return {
                "score": 0,
                "rationale": f"Error during evaluation: {str(e)}"
            }
            
    def trim_company_data(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Base method to trim company data - should be overridden by subclasses"""
        return {
            "name": company_data.get("name"),
            "summary": company_data.get("summary"),
            "website": company_data.get("website"),
            "linkedin_url": company_data.get("linkedin_url")
        } 