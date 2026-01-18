from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from models import ReceiptType


class CustomerReceiptCreate(BaseModel):
    customer_name: str = Field(..., max_length=150, description="Name of the customer")
    receipt_nature: Optional[str] = Field(default="Cash Inflow", max_length=50)
    receipt_purpose: Optional[str] = Field(default="Receipt from Customer", max_length=100)
    receipt_date: date = Field(..., description="Date of the receipt")
    receipt_type: ReceiptType = Field(..., description="Type of receipt")
    amount: float = Field(..., gt=0, description="Receipt amount")
    bank_name: Optional[str] = Field(None, max_length=150)
    project_name: Optional[str] = Field(None, max_length=150)
    company_name: Optional[str] = Field(None, max_length=150)
    remarks: Optional[str] = None

    class Config:
        use_enum_values = True


class CustomerReceiptResponse(BaseModel):
    id: int
    customer_name: str
    receipt_nature: str
    receipt_purpose: str
    receipt_date: date
    receipt_type: str
    amount: float
    bank_name: Optional[str]
    project_name: Optional[str]
    company_name: Optional[str]
    remarks: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
