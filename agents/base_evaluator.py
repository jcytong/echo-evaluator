from typing import Dict, Any, Optional, List
from langchain.chat_models import ChatOpenAI
from tools.search_tool import search_tool
import logging
import re

# Define calibration examples for each dimension
CALIBRATION_EXAMPLES = {
    "Founder Edge": {
        0: [
            "Team of recent graduates with no industry experience",
            "Solo founder from unrelated industry (e.g., restaurant owner starting a SaaS company)",
            "Consultants with no direct experience in the space"
        ],
        1: [
            "Product manager from adjacent industry",
            "Technical founder with general experience but no domain expertise",
            "Former junior employee at competitor"
        ],
        2: [
            "Former VP of Product at target customer company",
            "Serial founder with success in adjacent space",
            "Domain expert with 10+ years experience"
        ],
        3: [
            "Repeat founder who sold previous company in same space",
            "Former CTO of market leader starting competing product",
            "Founder with unique insight from running target customer company"
        ]
    },
    "Novel Wedge": {
        0: [
            "Direct copy of existing solution",
            "Minor UI improvements to existing product",
            "No clear differentiation from incumbents"
        ],
        1: [
            "Incremental improvement on existing solution",
            "New interface but same underlying approach",
            "Cost advantage but no technical innovation"
        ],
        2: [
            "Novel technical approach to known problem",
            "Unique go-to-market strategy in mature space",
            "New business model that reduces friction"
        ],
        3: [
            "Revolutionary technology enabling new capabilities",
            "First to market with solution made possible by recent change",
            "Unique insight that transforms industry economics"
        ]
    },
    "Customer Signal": {
        0: [
            "No paying customers yet",
            "Only friends and family using product",
            "High churn rate with no retention"
        ],
        1: [
            "Few pilot customers but no expansion",
            "Paying customers but slow growth",
            "Mixed customer feedback"
        ],
        2: [
            "Strong retention metrics",
            "Rapid customer acquisition in target segment",
            "Clear evidence of product-market fit"
        ],
        3: [
            "Viral adoption with negative CAC",
            "Industry leaders as reference customers",
            "Exceptional NPS with rapid expansion"
        ]
    },
    "Sales Motion": {
        0: [
            "No repeatable sales process",
            "Random deals with no pattern",
            "No clear target customer profile"
        ],
        1: [
            "Basic sales process but long cycles",
            "Some deals but high CAC",
            "Inconsistent win rates"
        ],
        2: [
            "Efficient sales process with predictable pipeline",
            "Strong win rates in target segment",
            "Clear ICP with repeatable motion"
        ],
        3: [
            "Viral product-led growth with negative CAC",
            "Highly efficient enterprise sales motion",
            "Perfect channel-market fit with rapid scaling"
        ]
    },
    "Moat Potential": {
        0: [
            "Easily replicable solution",
            "No proprietary technology",
            "No network effects or switching costs"
        ],
        1: [
            "Basic technical barriers",
            "Some data advantage but not unique",
            "Moderate switching costs"
        ],
        2: [
            "Strong network effects emerging",
            "Significant proprietary technology",
            "High switching costs with platform lock-in"
        ],
        3: [
            "Dominant network effect with winner-take-all dynamics",
            "Revolutionary protected technology",
            "Ecosystem lock-in with high data barriers"
        ]
    },
    "Investor Behavior": {
        0: [
            "No institutional investors",
            "Only friends and family funding",
            "Unable to raise follow-on rounds"
        ],
        1: [
            "Some angel investors but no leads",
            "Small seed round from generalist investors",
            "Struggling to raise next round"
        ],
        2: [
            "Strong tier-2 VC backing",
            "Strategic investors in space",
            "Multiple rounds with up-rounds"
        ],
        3: [
            "Top-tier VC leading all rounds",
            "Strategic bidding war for rounds",
            "Exceptional investor social proof"
        ]
    },
    "Incumbent Blind Spot": {
        0: [
            "Incumbents already building similar solution",
            "Easy for large players to copy",
            "No structural barriers to incumbent entry"
        ],
        1: [
            "Incumbents aware but slow to respond",
            "Some organizational barriers",
            "Limited time advantage"
        ],
        2: [
            "Clear structural barriers for incumbents",
            "Strong first-mover advantage in new category",
            "Significant organizational conflicts"
        ],
        3: [
            "Fundamental disruption incumbents cannot pursue",
            "Perfect timing with high barriers to response",
            "Structural inability for incumbents to compete"
        ]
    }
}

class BaseEvaluator:
    def __init__(self, dimension_name: str, rubric: str):
        self.dimension_name = dimension_name
        self.rubric = rubric
        self.llm = ChatOpenAI(
            model="o3",
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
        
        # Get calibration examples for this dimension
        dimension_examples = CALIBRATION_EXAMPLES.get(self.dimension_name, {})
        calibration_examples_text = ""
        if dimension_examples:
            calibration_examples_text = "Calibration Examples:\n"
            for score in range(4):  # 0 to 3
                examples = dimension_examples.get(score, [])
                calibration_examples_text += f"\nScore {score}:\n"
                for example in examples:
                    calibration_examples_text += f"- {example}\n"

        # Create evaluation prompt
        self.logger.info("Creating evaluation prompt")
        prompt = f"""
        You are a critical evaluator assessing {company_data.get('name')} for the {self.dimension_name} dimension, specifically analyzing its potential as a fast follower opportunity. Assume nothing until proven.

        Key Hypothesis to Evaluate:
        1. The company is targeting a proven problem/market where customers will pay
        2. The space has limited incumbents (signaled by competitors being young companies)
        3. Recent technological or market changes enable new solutions
        4. Rapid growth signals strong product-market fit or investor validation
        5. The timing is right for a fast follower strategy
        
        Scoring Guidelines (Adversarial):
        - 0 = No signal of edge. Founders are generalists or unrelated to domain.
        - 1 = Background is adjacent but not clearly strategic.
        - 2 = Domain or network relevance is evident but not unique.
        - 3 = Rare and strategic edge (e.g., repeat founder in same vertical, ex-CxO in target buyer persona).
        
        {calibration_examples_text}
        
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
        1. A concise, informative analysis of the company's potential as a fast follower opportunity for the {self.dimension_name} dimension. Your rationale must be no longer than 500 words (about 2 minutes to read). Avoid repetition and unnecessary detail.
        2. After providing the rationale, determine the appropriate score from 0-3 using the rubric.
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