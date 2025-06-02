# Legal document service

# backend/ai_services/contract_automation/services/legal_service.py
from google.generativeai import GenerativeModel

class LegalService:
    def __init__(self):
        self.model = GenerativeModel('gemini-pro')
    
    def generate_contract(self, terms: dict) -> str:
        prompt = f"Generate legal contract for: {terms}"
        return self.model.generate_content(prompt).text
