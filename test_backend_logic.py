import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Add the current directory to sys.path to import backend
sys.path.append(os.getcwd())

from backend import orchestrator

class TestBackendOrchestration(unittest.TestCase):
    
    def setUp(self):
        self.sample_contract = "This is a sample contract text."
        self.mock_ai_response = [
            {
                "clause": "Clause 1 text",
                "risk_type": "Liability",
                "risk_score": 8,
                "reasoning": "High liability risk",
                "suggested_revision": "Limit liability",
                "confidence": 0.95
            },
            {
                "clause": "Clause 2 text",
                "risk_type": "Financial",
                "risk_score": 4,
                "reasoning": "Moderate financial risk",
                "suggested_revision": "Review terms",
                "confidence": 0.85
            }
        ]

    # Mock the extract_and_analyze function directly to avoid mocking internal Gemini calls
    @patch('backend.ai_pipeline.extract_and_analyze')
    def test_analyze_contract_success(self, mock_extract):
        # Setup mock
        mock_extract.return_value = self.mock_ai_response
        
        # Run analysis
        result = orchestrator.analyze_contract_text(self.sample_contract)
        
        # Verify AI pipeline was called
        mock_extract.assert_called_once_with(self.sample_contract)
        
        # Verify structure of result
        self.assertIn("overall_risk_score", result)
        self.assertIn("highest_risk_clause", result)
        self.assertIn("risk_distribution", result)
        self.assertIn("clauses", result)
        
        # Verify analytics computation
        self.assertEqual(result["overall_risk_score"], 6.0)
        self.assertEqual(result["highest_risk_clause"]["risk_score"], 8)
        self.assertEqual(result["risk_distribution"]["Liability"], 1)
        self.assertEqual(result["risk_distribution"]["Financial"], 1)

    @patch('backend.ai_pipeline.extract_and_analyze')
    def test_analyze_contract_empty_response(self, mock_extract):
        mock_extract.return_value = []
        
        result = orchestrator.analyze_contract_text(self.sample_contract)
        
        self.assertEqual(result["overall_risk_score"], 0.0)
        self.assertEqual(result["highest_risk_clause"], {})
        self.assertEqual(result["risk_distribution"], {})
        self.assertEqual(result["clauses"], [])

    @patch('backend.ai_pipeline.extract_and_analyze')
    def test_validation_failure(self, mock_extract):
        # Return invalid data (missing keys)
        mock_extract.return_value = [{"clause": "bad clause"}] 
        
        with self.assertRaises(ValueError) as context:
            orchestrator.analyze_contract_text(self.sample_contract)
        
        self.assertIn("AI response validation failed", str(context.exception))

if __name__ == '__main__':
    unittest.main()
