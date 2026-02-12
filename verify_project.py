import os
import io
import json
import unittest
from unittest.mock import MagicMock, patch

# Set dummy key for testing imports
os.environ["GOOGLE_API_KEY"] = "TEST_KEY"

# Import modules to test
from backend import ai_pipeline, orchestrator, analyzer

class TestBackendIntegration(unittest.TestCase):
    def test_full_flow(self):
        """Test the entire flow from PDF extraction to result transformation."""
        
        # 1. Mock PyPDF2 in analyzer
        with patch('backend.analyzer.PyPDF2.PdfReader') as MockPdfReader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "This is a sample contract text."
            
            mock_reader = MagicMock()
            mock_reader.pages = [mock_page]
            
            MockPdfReader.return_value = mock_reader
            
            # 2. Mock Gemini API calls in ai_pipeline
            # We need to mock _call_gemini twice: once for extraction, once for analysis
            with patch('backend.ai_pipeline._call_gemini') as mock_gemini:
                
                # Setup return values for the two calls
                # Call 1: Extraction returns a list text
                # Call 2: Analysis returns JSON
                mock_gemini.side_effect = [
                    "1. Clause 1\n2. Clause 2",  # Extraction output
                    json.dumps([                 # Analysis JSON output
                        {
                            "clause": "Clause 1",
                            "risk_type": "Financial",
                            "risk_score": 8,
                            "reasoning": "High risk",
                            "suggested_revision": "Fix it",
                            "confidence": 0.95
                        }
                    ])
                ]
                
                # 3. Simulate File Upload
                mock_file = io.BytesIO(b"fake pdf content")
                mock_file.name = "test.pdf"
                
                # 4. Run the top-level analyzer function
                print("Running analyze_contract...")
                result = analyzer.analyze_contract(mock_file)
                
                # 5. Verify Structure
                print("Verifying result structure...")
                self.assertIn("overall_risk_score", result)
                self.assertIn("clauses", result)
                self.assertEqual(len(result["clauses"]), 1)
                
                clause = result["clauses"][0]
                self.assertEqual(clause["clause_text"], "Clause 1")
                self.assertEqual(clause["risk_score"], 8)
                self.assertEqual(clause["confidence_score"], 0.95)
                
                print("Integration test passed!")

if __name__ == "__main__":
    unittest.main()
