from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class ReportCreate(BaseModel):
    text: str
    location: Optional[str] = None
    source_type: Optional[str] = "Citizen SMS"
    language: Optional[str] = "Auto"  # 'Hindi', 'English', 'Bengali', 'Tamil', etc.

class Report(BaseModel):
    id: str
    text: str
    language: str
    language_code: str
    normalized_en_text: Optional[str] = None
    timestamp: str
    location: str
    normalized_location_id: str
    source_type: str
    category: str
    needs: List[str]
    severity: str
    extracted_claims: List[str]
    processing_status: str
    provider_used: str
    incident_id: Optional[str] = None

class Incident(BaseModel):
    id: str
    title: str
    location: str
    normalized_location_id: str
    category: str
    severity: str
    status: str  # 'unverified' | 'corroborated' | 'conflicting' | 'human_reviewed'
    report_ids: List[str]
    languages: List[str]
    unified_summary: Optional[str] = None
    has_contradiction: bool
    contradiction_notes: Optional[str] = None
    created_at: str
    updated_at: str
    operator_notes: Optional[str] = None

class TranslationRequest(BaseModel):
    text: str
    target_language: str  # e.g. 'Hindi', 'Bengali', 'Tamil', 'English'

class InventoryItem(BaseModel):
    id: str
    item_name: str
    total_qty: int
    available_qty: int
    unit: str
    depot_name: str
    is_simulated: bool = True

class Recommendation(BaseModel):
    id: str
    incident_id: str
    incident_title: str
    item_name: str
    recommended_qty: int
    unit: str
    depot_name: str
    rationale: str
    route_warning: Optional[str] = None
    status: str = "PROPOSED"
    is_simulated: bool = True

class ActivityLog(BaseModel):
    id: str
    timestamp: str
    event_type: str
    title: str
    description: str
    severity: str = "INFO"
