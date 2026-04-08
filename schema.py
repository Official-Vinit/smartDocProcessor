from pydantic import BaseModel, Field
from typing import List, Optional

class StructuredAddress(BaseModel):
    street: Optional[str] = Field(default=None, description="Street address or PO Box")
    city: Optional[str] = Field(default=None, description="City or locality")
    state_province: Optional[str] = Field(default=None, description="State, province, or region")
    postal_code: Optional[str] = Field(default=None, description="Postal or ZIP code")
    country: Optional[str] = Field(default=None, description="Country name")

class MonetaryAmount(BaseModel):
    amount: float
    currency: str
    context: str = Field(description="What this amount represents (e.g., 'Total Due', 'Rent', 'Tax')")

# Create specific extraction models to avoid the ambiguous 'Any' type
class StringField(BaseModel):
    value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score 0.0-1.0")
    source_text: str = Field(description="Raw text from document")

class AddressField(BaseModel):
    value: Optional[StructuredAddress] = None
    confidence: float = Field(ge=0.0, le=1.0)
    source_text: str

class MonetaryListField(BaseModel):
    value: Optional[List[MonetaryAmount]] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    source_text: str

# Explicitly define the exact fields we want to extract
class DocumentFields(BaseModel):
    primary_party_name: Optional[StringField] = None
    address: Optional[AddressField] = None
    issue_date: Optional[StringField] = None
    expiry_date: Optional[StringField] = None
    monetary_amounts: Optional[MonetaryListField] = None

class DocumentResponse(BaseModel):
    document_id: str
    category: str = Field(description="High-level category (e.g., 'Financial', 'Legal')")
    type: str = Field(description="Specific document type (e.g., 'Lease Agreement')")
    language: str = Field(description="ISO 639-1 code")
    confidence: float = Field(ge=0.0, le=1.0, description="Overall confidence")
    fields: DocumentFields
    flags: List[str] = Field(default_factory=list)
    processing_errors: List[str] = Field(default_factory=list)