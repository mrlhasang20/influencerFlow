# backend/ai_services/contract_automation/schemas/contract_schemas.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ContractType(str, Enum):
    STANDARD = "standard"
    EXCLUSIVE = "exclusive"
    ONE_TIME = "one_time"
    ONGOING = "ongoing"
    NDA = "nda"
    CUSTOM = "custom"

class Jurisdiction(str, Enum):
    US = "united_states"
    EU = "european_union"
    UK = "united_kingdom"
    INTERNATIONAL = "international"

class ContractGenerationRequest(BaseModel):
    deal_terms: Dict[str, Any] = Field(..., description="Terms negotiated for the contract")
    template_type: ContractType = Field(default=ContractType.STANDARD, description="Type of contract template to use")
    jurisdiction: Jurisdiction = Field(default=Jurisdiction.US, description="Legal jurisdiction for the contract")
    custom_clauses: Optional[List[str]] = Field(default=None, description="Any custom clauses to include")
    generate_html: bool = Field(default=True, description="Whether to generate HTML version")
    
    class Config:
        schema_extra = {
            "example": {
                "deal_terms": {
                    "brand_name": "FitLife Co.",
                    "brand_address": "123 Business St, San Francisco, CA",
                    "influencer_name": "FitnessGuru",
                    "influencer_address": "456 Creator Ave, Los Angeles, CA",
                    "platform": "Instagram",
                    "handle": "@fitnessGuru",
                    "campaign_name": "Summer Fitness Challenge",
                    "campaign_type": "product_promotion",
                    "content_type": "lifestyle_fitness",
                    "start_date": "2023-06-01",
                    "end_date": "2023-07-31",
                    "deliverables": [
                        {
                            "type": "Instagram Post",
                            "description": "Product showcase with workout routine",
                            "due_date": "2023-06-15",
                            "specs": "High-resolution image, product prominently displayed"
                        },
                        {
                            "type": "Instagram Story",
                            "description": "Product unboxing and first impression",
                            "due_date": "2023-06-10",
                            "specs": "Minimum 3 story frames, including swipe-up link"
                        }
                    ],
                    "total_fee": 5000,
                    "payment_schedule": [
                        {
                            "milestone": "Contract Signing",
                            "amount": 2500,
                            "due_date": "2023-06-01"
                        },
                        {
                            "milestone": "Content Delivery",
                            "amount": 2500,
                            "due_date": "2023-07-15"
                        }
                    ]
                },
                "template_type": "standard",
                "jurisdiction": "united_states",
                "generate_html": True
            }
        }

class ContractResponse(BaseModel):
    contract_id: str = Field(..., description="Unique identifier for the contract")
    contract_text: str = Field(..., description="Plain text version of the contract")
    contract_html: Optional[str] = Field(None, description="HTML formatted version of the contract")
    generated_at: datetime = Field(..., description="Timestamp when contract was generated")
    status: str = Field(..., description="Status of the contract generation")
    metadata: Dict[str, Any] = Field(default={}, description="Additional metadata about the contract")

class ComplianceIssue(BaseModel):
    issue_type: str = Field(..., description="Type of compliance issue")
    description: str = Field(..., description="Description of the issue")
    severity: str = Field(..., description="Severity of the issue: high, medium, low")
    location: Optional[str] = Field(None, description="Location in the contract where issue occurs")
    recommendation: str = Field(..., description="Recommended fix for the issue")

class ComplianceCheckRequest(BaseModel):
    contract_text: str = Field(..., description="Contract text to check for compliance")
    jurisdiction: Jurisdiction = Field(..., description="Legal jurisdiction for compliance")
    contract_type: ContractType = Field(..., description="Type of contract for specific regulations")
    
    class Config:
        schema_extra = {
            "example": {
                "contract_text": "This Influencer Marketing Agreement is made between...",
                "jurisdiction": "united_states",
                "contract_type": "standard"
            }
        }

class ComplianceResponse(BaseModel):
    is_compliant: bool = Field(..., description="Whether the contract is compliant")
    compliance_score: float = Field(..., description="Compliance score from 0-100")
    issues: List[ComplianceIssue] = Field(default=[], description="List of compliance issues found")
    recommendations: List[str] = Field(default=[], description="General recommendations")
    required_clauses: List[str] = Field(default=[], description="Required clauses for this contract type")

class ContractTemplateRequest(BaseModel):
    template_id: str = Field(..., description="ID of the template to customize")
    customization_data: Dict[str, Any] = Field(..., description="Data to customize the template")
    
    class Config:
        schema_extra = {
            "example": {
                "template_id": "standard_influencer",
                "customization_data": {
                    "brand_name": "FitLife Co.",
                    "influencer_name": "FitnessGuru",
                    "campaign_name": "Summer Fitness Challenge"
                }
            }
        }

class TemplateResponse(BaseModel):
    template_id: str = Field(..., description="Unique identifier for the template")
    name: str = Field(..., description="Human-readable name of the template")
    description: str = Field(..., description="Description of the template purpose")
    required_fields: List[str] = Field(..., description="Required fields to complete template")
    optional_fields: List[str] = Field(default=[], description="Optional fields for template")
    contract_type: ContractType = Field(..., description="Type of contract this template is for")
    jurisdictions: List[Jurisdiction] = Field(..., description="Supported jurisdictions")
