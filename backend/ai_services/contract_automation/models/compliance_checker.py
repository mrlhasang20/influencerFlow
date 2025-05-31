# Legal compliance AI

# backend/ai_services/contract_automation/models/compliance_checker.py
from google.generativeai import GenerativeModel

class ComplianceChecker:
    def __init__(self):
        self.model = GenerativeModel('gemini-pro')
    
    def check_compliance(self, text: str) -> dict:
        response = self.model.generate_content(
            f"Check legal compliance for: {text}"
        )
        return {"compliance_check": response.text}
