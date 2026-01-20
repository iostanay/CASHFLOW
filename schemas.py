from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from models import ReceiptType, ReceiptMode, PaymentPurpose, PaymentType, EmployeePaymentPurpose


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


class BankLoanReceiptCreate(BaseModel):
    bank_name: str = Field(..., max_length=150, description="Name of the bank")
    receipt_nature: Optional[str] = Field(default="Cash Inflow", max_length=50)
    receipt_purpose: Optional[str] = Field(default="Loan Receipts", max_length=100)
    loan_reference_no: Optional[str] = Field(None, max_length=100)
    receipt_date: date = Field(..., description="Date of the receipt")
    amount: float = Field(..., gt=0, description="Receipt amount")
    receipt_mode: ReceiptMode = Field(default="Bank Transfer", description="Mode of receipt")
    remarks: Optional[str] = None

    class Config:
        use_enum_values = True


class BankLoanReceiptResponse(BaseModel):
    id: int
    bank_name: str
    receipt_nature: str
    receipt_purpose: str
    loan_reference_no: Optional[str]
    receipt_date: date
    amount: float
    receipt_mode: str
    remarks: Optional[str]
    attachment_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VendorPaymentCreate(BaseModel):
    vendor_name: str = Field(..., max_length=150, description="Name of the vendor")
    payment_nature: Optional[str] = Field(default="Cash Outflow", max_length=50)
    payment_purpose: PaymentPurpose = Field(..., description="Purpose of payment-tanay")
    service_or_material_details: Optional[str] = Field(None, max_length=255)
    payment_date: date = Field(..., description="Date of the payment")
    payment_type: PaymentType = Field(..., description="Type of payment")
    amount: float = Field(..., gt=0, description="Payment amount")
    bank_name: Optional[str] = Field(None, max_length=150)
    remarks: Optional[str] = None
    attachment_path: Optional[str] = Field(None, max_length=255)

    class Config:
        use_enum_values = True


class VendorPaymentResponse(BaseModel):
    id: int
    vendor_name: str
    payment_nature: str
    payment_purpose: str
    service_or_material_details: Optional[str]
    payment_date: date
    payment_type: str
    amount: float
    bank_name: Optional[str]
    remarks: Optional[str]
    attachment_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmployeePaymentCreate(BaseModel):
    employee_name: str = Field(..., max_length=150, description="Name of the employee")
    employee_id: Optional[str] = Field(None, max_length=50)
    payment_nature: Optional[str] = Field(default="Cash Outflow", max_length=50)
    payment_purpose: EmployeePaymentPurpose = Field(..., description="Purpose of payment")
    payment_date: date = Field(..., description="Date of the payment")
    payment_type: PaymentType = Field(..., description="Type of payment")
    amount: float = Field(..., gt=0, description="Payment amount")
    bank_name: Optional[str] = Field(None, max_length=150)
    remarks: Optional[str] = None
    attachment_path: Optional[str] = Field(None, max_length=255)

    class Config:
        use_enum_values = True


class EmployeePaymentResponse(BaseModel):
    id: int
    employee_name: str
    employee_id: Optional[str]
    payment_nature: str
    payment_purpose: str
    payment_date: date
    payment_type: str
    amount: float
    bank_name: Optional[str]
    remarks: Optional[str]
    attachment_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InflowReceiptMasterResponse(BaseModel):
    entity_id: int
    name: str

    class Config:
        from_attributes = True
