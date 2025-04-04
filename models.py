"""
Data models for the RBC Mortgage & Creditor Insurance Advisor Assistant
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from datetime import date

class CoverageType(str, Enum):
    LIFE = "life"
    DISABILITY = "disability"
    CRITICAL_ILLNESS = "critical_illness"
    JOB_LOSS = "job_loss"

class PaymentFrequency(str, Enum):
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"
    SEMI_MONTHLY = "semi_monthly"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class ScreenType(str, Enum):
    CLIENT_PROFILE = "client_profile"
    MORTGAGE_APPLICATION = "mortgage_application"
    PRODUCT_RECOMMENDATION = "product_recommendation"
    INSURANCE_APPLICATION = "insurance_application"
    PAYMENT_CALCULATOR = "payment_calculator"

class ClientProfile(BaseModel):
    full_name: str
    age: int = Field(..., ge=18, le=100)
    email: Optional[str] = None
    phone: Optional[str] = None
    occupation: Optional[str] = None
    annual_income: float = Field(0, ge=0)
    years_at_current_job: float = Field(0, ge=0)
    mortgage_amount: float = Field(0, ge=0)
    property_value: float = Field(0, ge=0)
    dependents: int = Field(0, ge=0)
    smoker: bool = False
    pre_existing_conditions: bool = False
    risk_tolerance: Optional[str] = "Medium"
    
    @validator('age')
    def validate_age(cls, v):
        if v < 18:
            raise ValueError('Age must be at least 18 years')
        return v

class MortgageDetails(BaseModel):
    principal: float = Field(..., gt=0)
    annual_rate: float = Field(..., ge=0, le=30)
    term_years: int = Field(..., ge=1, le=10)
    amortization_years: int = Field(..., ge=5, le=30)
    payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY
    
    @validator('annual_rate')
    def validate_rate(cls, v):
        if v < 0 or v > 30:
            raise ValueError('Interest rate must be between 0 and 30 percent')
        return v

class InsuranceCoverage(BaseModel):
    coverage_type: CoverageType
    coverage_amount: float = Field(..., ge=0)
    premium: float = Field(..., ge=0)
    term_years: Optional[int] = None
    joint_coverage: bool = False
    
    @validator('coverage_amount')
    def validate_coverage(cls, v):
        if v < 0:
            raise ValueError('Coverage amount cannot be negative')
        return v

class ScenarioSimulation(BaseModel):
    scenario_type: str
    duration_months: int = Field(..., ge=0)
    monthly_impact: float
    total_impact: float
    recommended_coverage: List[InsuranceCoverage] = []

class AdvisorAlert(BaseModel):
    alert_id: str
    screen_type: ScreenType
    title: str
    message: str
    action_required: bool = False
    priority: str = "Medium"  # Low, Medium, High
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ["Low", "Medium", "High"]:
            raise ValueError('Priority must be Low, Medium, or High')
        return v

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str

class ChatSession(BaseModel):
    session_id: str
    messages: List[ChatMessage] = []
    client_id: Optional[str] = None

class InsuranceRecommendation(BaseModel):
    coverage_type: CoverageType
    recommended_amount: float
    monthly_premium: float
    rationale: str
    priority: str  # "Essential", "Recommended", "Optional"
