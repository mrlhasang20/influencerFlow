# backend/ai_services/contract_automation/models/contract_generator.py

import google.generativeai as genai
from jinja2 import Template, Environment, FileSystemLoader
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime
import uuid
import os
import sys
import json
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from shared.config import settings

class ContractGenerator:
    """AI-powered contract generation system using Google Gemini"""
    
    def __init__(self):
        self.configure_gemini()
        self.templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
        self.env = Environment(loader=FileSystemLoader(self.templates_dir))
        self.contract_templates = self._load_contract_templates()
        
    def configure_gemini(self):
        """Configure Google Gemini API client"""
        genai.configure(api_key=settings.google_api_key)
        self.model = genai.GenerativeModel(
            model_name="gemini-pro",
            system_instruction="""You are a legal document assistant specializing in influencer marketing contracts.
            Generate precise, comprehensive, and legally sound contract language.
            Focus on clarity, regulatory compliance, and balanced terms for both parties."""
        )
        
    def _load_contract_templates(self) -> Dict[str, str]:
        """Load all contract templates from the templates directory"""
        templates = {}
        try:
            template_files = [f for f in os.listdir(self.templates_dir) if f.endswith('.html')]
            for file_name in template_files:
                template_id = file_name.split('.')[0]
                with open(os.path.join(self.templates_dir, file_name), 'r') as file:
                    templates[template_id] = file.read()
            
            # Add a fallback template if none found
            if not templates:
                templates["standard_contract"] = self._get_fallback_template()
                
            return templates
        except Exception as e:
            print(f"Error loading templates: {e}")
            return {"standard_contract": self._get_fallback_template()}
    
    def _get_fallback_template(self) -> str:
        """Provide a fallback template if file loading fails"""
        return """
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                h1 { text-align: center; }
                .contract-section { margin-bottom: 20px; }
                .signature-block { margin-top: 50px; display: flex; justify-content: space-between; }
                .signature-line { border-top: 1px solid #000; width: 200px; margin-top: 50px; text-align: center; }
            </style>
        </head>
        <body>
            <h1>INFLUENCER MARKETING AGREEMENT</h1>
            
            <div class="contract-section">
                <p>This Agreement is entered into on {{ contract_date }} between:</p>
                
                <p><strong>BRAND:</strong> {{ brand_name }}<br>
                Address: {{ brand_address }}</p>
                
                <p><strong>INFLUENCER:</strong> {{ influencer_name }}<br>
                Platform: {{ platform }}<br>
                Handle: {{ handle }}</p>
            </div>
            
            <div class="contract-section">
                <h2>CAMPAIGN DETAILS:</h2>
                <p>Campaign Name: {{ campaign_name }}<br>
                Campaign Period: {{ start_date }} to {{ end_date }}</p>
            </div>
            
            <div class="contract-section">
                <h2>DELIVERABLES:</h2>
                {% for deliverable in deliverables %}
                <p>- {{ deliverable.type }}: {{ deliverable.description }}<br>
                  Due Date: {{ deliverable.due_date }}<br>
                  Specifications: {{ deliverable.specs }}</p>
                {% endfor %}
            </div>
            
            <div class="contract-section">
                <h2>COMPENSATION:</h2>
                <p>Total Fee: ${{ total_fee }}</p>
                <p>Payment Schedule:</p>
                {% for payment in payment_schedule %}
                <p>- {{ payment.milestone }}: ${{ payment.amount }} (Due: {{ payment.due_date }})</p>
                {% endfor %}
            </div>
            
            <div class="contract-section">
                <h2>TERMS AND CONDITIONS:</h2>
                <p>{{ terms_and_conditions }}</p>
            </div>
            
            <div class="signature-block">
                <div>
                    <div class="signature-line">Brand Representative</div>
                    <p>Date: _________________</p>
                </div>
                <div>
                    <div class="signature-line">Influencer</div>
                    <p>Date: _________________</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def generate_contract(self, deal_terms: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contract from negotiated terms"""
        try:
            # Generate custom terms and conditions using Gemini
            custom_terms = await self._generate_custom_terms(deal_terms)
            
            # Get the appropriate template
            template_type = deal_terms.get("template_type", "standard_contract")
            template_html = self.contract_templates.get(template_type, self.contract_templates["standard_contract"])
            
            # Prepare template variables
            template_vars = {
                "contract_id": str(uuid.uuid4())[:8],
                "contract_date": datetime.now().strftime("%B %d, %Y"),
                "brand_name": deal_terms.get("brand_name", ""),
                "brand_address": deal_terms.get("brand_address", "Address to be provided"),
                "influencer_name": deal_terms.get("influencer_name", ""),
                "platform": deal_terms.get("platform", ""),
                "handle": deal_terms.get("handle", ""),
                "campaign_name": deal_terms.get("campaign_name", ""),
                "start_date": deal_terms.get("start_date", ""),
                "end_date": deal_terms.get("end_date", ""),
                "deliverables": deal_terms.get("deliverables", []),
                "total_fee": deal_terms.get("total_fee", ""),
                "payment_schedule": deal_terms.get("payment_schedule", []),
                "terms_and_conditions": custom_terms
            }
            
            # Render HTML contract
            template = Template(template_html)
            contract_html = template.render(**template_vars)
            
            # Extract plain text version
            contract_text = self._html_to_text(contract_html)
            
            return {
                "contract_id": f"contract_{template_vars['contract_id']}",
                "contract_text": contract_text,
                "contract_html": contract_html,
                "generated_at": datetime.now(),
                "metadata": {
                    "template_type": template_type,
                    "brand": deal_terms.get("brand_name", ""),
                    "influencer": deal_terms.get("influencer_name", ""),
                    "campaign": deal_terms.get("campaign_name", ""),
                    "value": deal_terms.get("total_fee", "")
                }
            }
            
        except Exception as e:
            print(f"Contract generation failed: {str(e)}")
            raise Exception(f"Contract generation failed: {str(e)}")
    
    async def _generate_custom_terms(self, deal_terms: Dict[str, Any]) -> str:
        """Generate custom terms and conditions using Gemini"""
        prompt = f"""
        Generate comprehensive terms and conditions for an influencer marketing contract with these details:
        
        Campaign Type: {deal_terms.get('campaign_type', 'product promotion')}
        Duration: {deal_terms.get('start_date', 'contract_date')} to {deal_terms.get('end_date', '30 days after start')}
        Platform: {deal_terms.get('platform', 'social media')}
        Content Type: {deal_terms.get('content_type', 'promotional content')}
        
        Include these sections:
        1. Content Approval Process
        2. Usage Rights and Licensing
        3. FTC Compliance and Disclosure Requirements
        4. Cancellation and Modification Terms
        5. Intellectual Property Rights
        6. Performance Metrics and Reporting
        7. Confidentiality
        8. Limitation of Liability
        9. Termination Conditions
        10. Dispute Resolution
        
        Format the output as properly formatted contract text with section headings.
        """
        
        try:
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt
            )
            
            terms_and_conditions = response.text
            return terms_and_conditions
        except Exception as e:
            # Fallback to standard terms if AI generation fails
            return self._get_standard_terms()
    
    def _get_standard_terms(self) -> str:
        """Provide standard terms and conditions as fallback"""
        return """
        1. CONTENT APPROVAL PROCESS
        
        1.1 All content must be submitted to Brand for approval at least 48 hours prior to posting.
        1.2 Brand shall have the right to request reasonable revisions.
        1.3 Content may not be published without Brand's written approval.
        
        2. USAGE RIGHTS AND LICENSING
        
        2.1 Brand is granted a non-exclusive, worldwide license to use, reproduce, and distribute the content for marketing purposes.
        2.2 License duration shall be 6 months from the date of posting unless otherwise specified.
        2.3 Influencer retains ownership of content but may not license it to Brand's direct competitors during the exclusivity period.
        
        3. FTC COMPLIANCE AND DISCLOSURE REQUIREMENTS
        
        3.1 Influencer must clearly disclose the sponsored nature of all content according to FTC guidelines.
        3.2 Acceptable disclosures include #ad, #sponsored, or "Paid partnership with [Brand]".
        3.3 Disclosures must be clear, conspicuous, and not buried among other hashtags.
        
        4. CANCELLATION AND MODIFICATION TERMS
        
        4.1 Either party may terminate this Agreement with 14 days written notice.
        4.2 In the event of termination, Influencer shall be entitled to pro-rated compensation for deliverables completed.
        4.3 Brand may request reasonable modifications to the campaign strategy with Influencer's consent.
        
        5. INTELLECTUAL PROPERTY RIGHTS
        
        5.1 Brand grants Influencer limited use of its trademarks and copyrighted materials for the duration of the campaign.
        5.2 Influencer shall not modify Brand's intellectual property without prior written consent.
        5.3 Upon termination, Influencer shall cease using all Brand intellectual property.
        """
    
    def _html_to_text(self, html_content: str) -> str:
        """Convert HTML to plain text for contract"""
        # Remove HTML tags but preserve line breaks and paragraphs
        text = re.sub(r'<head>.*?</head>', '', html_content, flags=re.DOTALL)
        text = re.sub(r'<style>.*?</style>', '', text, flags=re.DOTALL)
        
        # Replace some HTML elements with text formatting
        text = re.sub(r'<h1>(.*?)</h1>', r'\n\n\1\n\n', text)
        text = re.sub(r'<h2>(.*?)</h2>', r'\n\n\1\n', text)
        text = re.sub(r'<p>(.*?)</p>', r'\1\n', text)
        text = re.sub(r'<br>', r'\n', text)
        text = re.sub(r'<br/>', r'\n', text)
        text = re.sub(r'<div.*?>', r'', text)
        text = re.sub(r'</div>', r'\n', text)
        text = re.sub(r'<strong>(.*?)</strong>', r'\1', text)
        
        # Remove remaining HTML tags
        text = re.sub(r'<.*?>', '', text)
        
        # Fix multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()
