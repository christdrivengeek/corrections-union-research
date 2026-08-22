from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Any, Union

def to_str(v: Any) -> str:
    if v is None:
        return "N/A"
    return str(v)

class StateCompensation(BaseModel):
    cadet_starting_hourly: Optional[Union[str, int, float]] = "N/A"
    cadet_starting_annual: Optional[Union[str, int, float]] = "N/A"
    certified_officer_starting: Optional[Union[str, int, float]] = "N/A"
    top_step_annual: Optional[Union[str, int, float]] = "N/A"
    years_to_top_step: Optional[Union[str, int, float]] = "N/A"
    step_system_description: Optional[Union[str, int, float]] = "N/A"
    salary_evidence_quote: Optional[Union[str, int, float]] = "N/A"

    @field_validator('*', mode='before')
    def coerce_to_string(cls, v):
        return to_str(v)

class BenefitsAndPension(BaseModel):
    pension_system_name: Optional[Union[str, int, float]] = "N/A"
    pension_type: Optional[Union[str, int, float]] = "N/A"
    pension_formula_multiplier: Optional[Union[str, int, float]] = "N/A"
    vesting_years: Optional[Union[str, int, float]] = "N/A"
    employee_pension_contribution: Optional[Union[str, int, float]] = "N/A"
    health_insurance_summary: Optional[Union[str, int, float]] = "N/A"
    hazardous_duty_differentials: Optional[Union[str, int, float]] = "N/A"
    pension_evidence_quote: Optional[Union[str, int, float]] = "N/A"

    @field_validator('*', mode='before')
    def coerce_to_string(cls, v):
        return to_str(v)

class StateCorrectionsReport(BaseModel):
    state_code: str
    state_name: str
    official_agency_name: str
    union_status: str = "Non-Union"
    union_name: Optional[str] = "None"
    right_to_work: bool = False
    union_evidence_quote: Optional[str] = "N/A"
    verification_confidence: str = "High (Official Government/Union Document)"
    compensation: StateCompensation
    benefits: BenefitsAndPension
    official_sources: List[str] = Field(default_factory=list)
    key_findings_summary: str = "Summary pending"

    @field_validator('union_status', 'union_name', 'key_findings_summary', 'union_evidence_quote', 'verification_confidence', mode='before')
    def coerce_strings(cls, v):
        return to_str(v)
    
    @field_validator('right_to_work', mode='before')
    def coerce_bool(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "yes", "1")
        return bool(v)
