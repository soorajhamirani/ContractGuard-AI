"""
Backend orchestration module for ContractGuard AI - Intelligent Contract Risk Scoring System.

This module handles the core logic for contract analysis, including:
- Utilizing the AI pipeline for extraction and analysis.
- Validating the structure of AI responses.
- Computing analytics and risk scores.
- Returning a structured result dictionary.
"""

import logging
from typing import Dict, Any, List
import ai_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Required keys for validation of AI response
REQUIRED_KEYS = [
    "clause",
    "risk_type",
    "risk_score",
    "reasoning",
    "suggested_revision",
    "confidence"
]

def validate_ai_response(data: List[Any]) -> List[Dict[str, Any]]:
    """
    Validate the structure and content of the AI pipeline response.

    Ensures the response is a list of dictionaries containing all REQUIRED_KEYS
    with appropriate data types.

    Args:
        data (List[Any]): The raw response data from the AI pipeline.

    Returns:
        List[Dict[str, Any]]: The validated list of clause dictionaries.

    Raises:
        ValueError: If the data structure is invalid or keys are missing/incorrect.
    """
    if not isinstance(data, list):
        raise ValueError("AI response must be a list of clauses.")

    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"Item at index {index} is not a dictionary.")

        # Check for missing keys
        missing_keys = [key for key in REQUIRED_KEYS if key not in item]
        if missing_keys:
            raise ValueError(f"Item at index {index} missing keys: {missing_keys}")

        # Validate types
        if not isinstance(item.get("risk_score"), (int, float)):
             raise ValueError(f"Item at index {index}: 'risk_score' must be int or float.")
        
        # 'confidence' might be int (0 or 1) or float
        if not isinstance(item.get("confidence"), (int, float)):
             raise ValueError(f"Item at index {index}: 'confidence' must be a number.")

    return data

def compute_overall_risk(clauses: List[Dict[str, Any]]) -> float:
    """
    Compute the average risk score across all clauses.

    Args:
        clauses (List[Dict[str, Any]]): Validated list of clauses.

    Returns:
        float: The average risk score rounded to 2 decimal places.
    """
    if not clauses:
        return 0.0
    
    total_score = sum(clause.get("risk_score", 0) for clause in clauses)
    average_score = total_score / len(clauses)
    return round(average_score, 2)

def compute_highest_risk_clause(clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Identify and return the clause with the highest risk score.

    Args:
        clauses (List[Dict[str, Any]]): Validated list of clauses.

    Returns:
        Dict[str, Any]: The clause dictionary with the highest risk score, or None if empty.
    """
    if not clauses:
        return {}
    
    # Sort by risk_score in descending order
    sorted_clauses = sorted(clauses, key=lambda x: x.get("risk_score", 0), reverse=True)
    return sorted_clauses[0]

def compute_risk_distribution(clauses: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculate the distribution of clauses by risk type.

    Args:
        clauses (List[Dict[str, Any]]): Validated list of clauses.

    Returns:
        Dict[str, int]: A dictionary mapping risk types to their count.
    """
    distribution = {}
    for clause in clauses:
        risk_type = clause.get("risk_type", "Unknown")
        distribution[risk_type] = distribution.get(risk_type, 0) + 1
    
    return distribution

def analyze_contract(contract_text: str) -> Dict[str, Any]:
    """
    Analyze the provided contract text to determine risk scores and extracting clauses.

    This function orchestrates the analysis process by:
    1. Calling the AI pipeline to extract and analyze clauses.
    2. Validating the AI response against REQUIRED_KEYS.
    3. Computing overall risk metrics and distributions.
    4. returning a structured dictionary with the results.

    Args:
        contract_text (str): The full text of the contract to be analyzed.

    Returns:
        Dict[str, Any]: A dictionary containing:
            - overall_risk_score (float): The aggregate risk score.
            - highest_risk_clause (dict): The clause with the highest risk score.
            - risk_distribution (dict): A breakdown of risk categories.
            - clauses (list): A list of analyzed clause dictionaries.

    Raises:
        ValueError: If the contract text is empty or invalid.
        RuntimeError: If the AI pipeline fails or returns invalid data.
    """
    logger.info("Starting contract analysis...")

    # Step 1: Call AI Pipeline
    try:
        raw_result = ai_pipeline.extract_and_analyze(contract_text)
        logger.info(f"AI pipeline returned {len(raw_result)} clauses.")
    except Exception as e:
        logger.error(f"AI pipeline failed: {str(e)}")
        raise RuntimeError(f"AI pipeline execution failed: {str(e)}") from e
    
    # Step 2: Validate AI response
    try:
        validated_clauses = validate_ai_response(raw_result)
        logger.info("AI response validated successfully.")
    except ValueError as ve:
        logger.error(f"Validation failed: {str(ve)}")
        raise ValueError(f"AI response validation failed: {str(ve)}") from ve

    # Step 3: Compute analytics
    try:
        overall_risk_score = compute_overall_risk(validated_clauses)
        highest_risk_clause = compute_highest_risk_clause(validated_clauses)
        risk_distribution = compute_risk_distribution(validated_clauses)
        logger.info(f"Analytics computed. Overall Score: {overall_risk_score}")
    except Exception as e:
        logger.error(f"Analytics computation failed: {str(e)}")
        raise RuntimeError(f"Failed to compute analytics: {str(e)}") from e

    # Step 4: Return final structured dictionary
    result = {
        "overall_risk_score": overall_risk_score,
        "highest_risk_clause": highest_risk_clause,
        "risk_distribution": risk_distribution,
        "clauses": validated_clauses
    }
    
    return result
