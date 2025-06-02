# backend/ai_services/contract_automation/services/contract_service.py

from typing import Dict, Any, List, Optional
import asyncio
from datetime import datetime
import uuid
import json
from models.contract_generator import ContractGenerator
from schemas.contract_schemas import TemplateResponse, ContractType, Jurisdiction
from shared.database import get_db_session, Contract

class ContractService:
    """Main contract service handling all contract operations"""
    
    def __init__(self):
        self.contract_generator = ContractGenerator()
        self.available_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> List[Dict[str, Any]]:
        """Initialize available contract templates"""
        return [
            {
                "template_id": "standard_contract",
                "name": "Standard Influencer Marketing Agreement",
                "description": "Basic influencer marketing contract for single campaign collaborations",
                "required_fields": [
                    "brand_name", "influencer_name", "platform", "campaign_name",
                    "start_date", "end_date", "deliverables", "total_fee"
                ],
                "optional_fields": [
                    "brand_address", "influencer_address", "handle", "payment_schedule",
                    "exclusivity_clause", "usage_rights_duration"
                ],
                "contract_type": ContractType.STANDARD,
                "jurisdictions": [Jurisdiction.US, Jurisdiction.INTERNATIONAL]
            },
            {
                "template_id": "exclusive_contract",
                "name": "Exclusive Brand Partnership Agreement",
                "description": "Long-term exclusive partnership contract with comprehensive terms",
                "required_fields": [
                    "brand_name", "influencer_name", "platform", "exclusivity_period",
                    "minimum_deliverables", "total_fee"
                ],
                "optional_fields": [
                    "performance_bonuses", "renewal_options", "territory_restrictions"
                ],
                "contract_type": ContractType.EXCLUSIVE,
                "jurisdictions": [Jurisdiction.US, Jurisdiction.EU, Jurisdiction.INTERNATIONAL]
            },
            {
                "template_id": "nda_contract",
                "name": "Non-Disclosure Agreement",
                "description": "Confidentiality agreement for sensitive brand collaborations",
                "required_fields": [
                    "brand_name", "influencer_name", "confidential_information_scope",
                    "nda_duration"
                ],
                "optional_fields": [
                    "permitted_disclosures", "return_of_materials"
                ],
                "contract_type": ContractType.NDA,
                "jurisdictions": [Jurisdiction.US, Jurisdiction.EU, Jurisdiction.UK, Jurisdiction.INTERNATIONAL]
            }
        ]
    
    async def generate_contract(self, deal_terms: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete contract from deal terms"""
        try:
            # Validate required fields
            validation_errors = self._validate_deal_terms(deal_terms)
            if validation_errors:
                raise ValueError(f"Invalid deal terms: {', '.join(validation_errors)}")
            
            # Enrich deal terms with defaults
            enriched_terms = self._enrich_deal_terms(deal_terms)
            
            # Generate the contract
            contract_data = await self.contract_generator.generate_contract(enriched_terms)
            
            # Add service metadata
            contract_data["service_metadata"] = {
                "generated_by": "InfluencerFlow Contract Automation",
                "version": "1.0.0",
                "generation_timestamp": datetime.now().isoformat()
            }
            
            session = get_db_session()
            contract = Contract(
                id=str(uuid.uuid4()),
                collaboration_id=deal_terms.get("collaboration_id"),
                contract_text=contract_data["contract_text"],
                terms=deal_terms,
                status="draft"
            )
            session.add(contract)
            session.commit()
            session.close()
            return contract_data
            
        except Exception as e:
            raise Exception(f"Contract generation failed: {str(e)}")
    
    def _validate_deal_terms(self, deal_terms: Dict[str, Any]) -> List[str]:
        """Validate that all required deal terms are present"""
        errors = []
        required_fields = [
            "brand_name", "influencer_name", "platform", "campaign_name",
            "total_fee", "deliverables"
        ]
        
        for field in required_fields:
            if not deal_terms.get(field):
                errors.append(f"Missing required field: {field}")
        
        # Validate deliverables structure
        deliverables = deal_terms.get("deliverables", [])
        if not isinstance(deliverables, list) or not deliverables:
            errors.append("Deliverables must be a non-empty list")
        else:
            for i, deliverable in enumerate(deliverables):
                if not isinstance(deliverable, dict):
                    errors.append(f"Deliverable {i} must be a dictionary")
                    continue
                
                required_deliverable_fields = ["type", "description"]
                for field in required_deliverable_fields:
                    if not deliverable.get(field):
                        errors.append(f"Deliverable {i} missing required field: {field}")
        
        return errors
    
    def _enrich_deal_terms(self, deal_terms: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich deal terms with defaults and computed values"""
        enriched = deal_terms.copy()
        
        # Add default dates if not provided
        if not enriched.get("start_date"):
            enriched["start_date"] = datetime.now().strftime("%Y-%m-%d")
        
        if not enriched.get("end_date"):
            # Default to 30 days from start
            from datetime import timedelta
            start_date = datetime.strptime(enriched["start_date"], "%Y-%m-%d")
            end_date = start_date + timedelta(days=30)
            enriched["end_date"] = end_date.strftime("%Y-%m-%d")
        
        # Generate default payment schedule if not provided
        if not enriched.get("payment_schedule"):
            total_fee = enriched.get("total_fee", 0)
            enriched["payment_schedule"] = [
                {
                    "milestone": "Contract Signing",
                    "amount": total_fee * 0.5,
                    "due_date": enriched["start_date"]
                },
                {
                    "milestone": "Campaign Completion",
                    "amount": total_fee * 0.5,
                    "due_date": enriched["end_date"]
                }
            ]
        
        # Enrich deliverables with defaults
        for deliverable in enriched.get("deliverables", []):
            if not deliverable.get("due_date"):
                deliverable["due_date"] = enriched["end_date"]
            if not deliverable.get("specs"):
                deliverable["specs"] = "Standard platform specifications apply"
        
        return enriched
    
    async def get_available_templates(self) -> List[TemplateResponse]:
        """Get list of available contract templates"""
        try:
            template_responses = []
            for template in self.available_templates:
                template_responses.append(TemplateResponse(
                    template_id=template["template_id"],
                    name=template["name"],
                    description=template["description"],
                    required_fields=template["required_fields"],
                    optional_fields=template["optional_fields"],
                    contract_type=template["contract_type"],
                    jurisdictions=template["jurisdictions"]
                ))
            
            return template_responses
        except Exception as e:
            raise Exception(f"Failed to get templates: {str(e)}")
    
    async def customize_template(
        self, 
        template_id: str, 
        customization_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Customize a specific template with provided data"""
        try:
            # Find the template
            template = next(
                (t for t in self.available_templates if t["template_id"] == template_id), 
                None
            )
            
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            
            # Merge template requirements with customization data
            enriched_data = customization_data.copy()
            enriched_data["template_type"] = template_id
            
            # Generate contract using the specific template
            contract_data = await self.generate_contract(enriched_data)
            
            return contract_data
            
        except Exception as e:
            raise Exception(f"Template customization failed: {str(e)}")
    
    def get_contract_preview(self, template_id: str) -> Dict[str, Any]:
        """Get a preview of what a contract template looks like"""
        try:
            template = next(
                (t for t in self.available_templates if t["template_id"] == template_id), 
                None
            )
            
            if not template:
                raise ValueError(f"Template not found: {template_id}")
            
            # Create sample data for preview
            sample_data = {
                "brand_name": "[Brand Name]",
                "influencer_name": "[Influencer Name]", 
                "platform": "[Platform]",
                "campaign_name": "[Campaign Name]",
                "start_date": "[Start Date]",
                "end_date": "[End Date]",
                "total_fee": "[Total Fee]",
                "deliverables": [
                    {
                        "type": "[Deliverable Type]",
                        "description": "[Deliverable Description]",
                        "due_date": "[Due Date]",
                        "specs": "[Specifications]"
                    }
                ]
            }
            
            return {
                "template_id": template_id,
                "sample_data": sample_data,
                "required_fields": template["required_fields"],
                "optional_fields": template["optional_fields"]
            }
            
        except Exception as e:
            raise Exception(f"Preview generation failed: {str(e)}")
