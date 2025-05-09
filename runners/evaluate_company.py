from agents.evaluators import (
    FounderEdgeEvaluator,
    NovelWedgeEvaluator,
    CustomerSignalEvaluator,
    SalesMotionEvaluator,
    MoatPotentialEvaluator,
    InvestorBehaviorEvaluator,
    IncumbentBlindSpotEvaluator
)
import logging
import time
from typing import Dict, Any
from datetime import datetime
import json
import os
from pathlib import Path

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class EvaluationError(Exception):
    """Base exception for evaluation errors"""
    pass

class InputValidationError(EvaluationError):
    """Raised when input data is invalid"""
    pass

class EvaluatorError(EvaluationError):
    """Raised when an evaluator fails"""
    pass

def validate_company_data(company_data: Dict[str, Any]) -> None:
    """
    Validate the company data structure.
    
    Args:
        company_data: Dictionary containing company information
        
    Raises:
        InputValidationError: If required fields are missing or invalid
    """
    # Check if data is nested in a data array
    if "data" in company_data and isinstance(company_data["data"], list) and len(company_data["data"]) > 0:
        company_data = company_data["data"][0]  # Use the first company in the array
    
    required_fields = ["name", "display_name", "summary"]
    missing_fields = [field for field in required_fields if field not in company_data]
    
    if missing_fields:
        raise InputValidationError(
            f"Missing required fields in company data: {', '.join(missing_fields)}"
        )
    
    if not isinstance(company_data, dict):
        raise InputValidationError("Company data must be a dictionary")
    
    logger.info(f"Validating company: {company_data.get('name', 'Unknown')}")

def save_evaluation_log(results: Dict[str, Any], company_name: str) -> None:
    """
    Save evaluation results to a log file.
    
    Args:
        results: Dictionary containing evaluation results
        company_name: Name of the company being evaluated
    """
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"evaluation_{company_name}_{timestamp}.json"
    
    with open(log_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"Evaluation log saved to {log_file}")

def run_evaluation(company_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run evaluation across all dimensions for a company.
    
    Args:
        company_data: Dictionary containing company information
        
    Returns:
        Dictionary containing scores and rationales for each dimension
        
    Raises:
        InputValidationError: If company data is invalid
        EvaluationError: If evaluation fails
    """
    start_time = time.time()
    logger.info(f"Starting evaluation for company: {company_data.get('name', 'Unknown')}")
    
    try:
        # Validate input data
        validate_company_data(company_data)
        
        evaluators = {
            "Founder Edge": FounderEdgeEvaluator(),
            "Novel Wedge": NovelWedgeEvaluator(),
            "Customer Signal": CustomerSignalEvaluator(),
            "Sales Motion": SalesMotionEvaluator(),
            "Moat Potential": MoatPotentialEvaluator(),
            "Investor Behavior": InvestorBehaviorEvaluator(),
            "Incumbent Blind Spot": IncumbentBlindSpotEvaluator()
        }
        
        results = {
            "metadata": {
                "company_name": company_data.get("name") or company_data.get("display_name") or "Unknown Company",
                "evaluation_date": datetime.now().isoformat(),
                "evaluation_version": "1.0"
            }
        }
        total_score = 0
        successful_evaluations = 0
        
        for dimension, evaluator in evaluators.items():
            dimension_start_time = time.time()
            try:
                logger.info(f"Starting {dimension} evaluation...")
                result = evaluator.evaluate(company_data)
                results[dimension] = result
                total_score += result["score"]
                successful_evaluations += 1
                
                dimension_time = time.time() - dimension_start_time
                logger.info(
                    f"{dimension} evaluation completed in {dimension_time:.2f}s. "
                    f"Score: {result['score']}"
                )
                
            except Exception as e:
                logger.error(f"Error in {dimension} evaluation: {str(e)}", exc_info=True)
                results[dimension] = {
                    "score": 0,
                    "rationale": f"Error during evaluation: {str(e)}",
                    "error": str(e)
                }
        
        # Calculate average score only from successful evaluations
        if successful_evaluations > 0:
            results["Overall"] = {
                "score": round(total_score / successful_evaluations, 2),
                "rationale": f"Average score across {successful_evaluations} dimensions",
                "successful_evaluations": successful_evaluations,
                "total_dimensions": len(evaluators)
            }
        else:
            results["Overall"] = {
                "score": 0,
                "rationale": "No successful evaluations",
                "successful_evaluations": 0,
                "total_dimensions": len(evaluators)
            }
        
        # Add timing information
        total_time = time.time() - start_time
        results["metadata"]["total_evaluation_time"] = f"{total_time:.2f}s"
        
        # Save evaluation log
        save_evaluation_log(results, company_data.get("name", "unknown"))
        
        logger.info(
            f"Evaluation completed in {total_time:.2f}s. "
            f"Overall score: {results['Overall']['score']}"
        )
        
        return results
        
    except InputValidationError as e:
        logger.error(f"Input validation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during evaluation: {str(e)}", exc_info=True)
        raise EvaluationError(f"Evaluation failed: {str(e)}")
