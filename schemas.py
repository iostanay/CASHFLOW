from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import date, datetime
from models import (
    ReceiptType, ReceiptMode, PaymentPurpose, PaymentType, EmployeePaymentPurpose,
    FlowTypeEnum, InflowModeEnum, FieldTypeEnum,
)


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
    attachment_path: Optional[str]
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


# Company Schemas
class CompanyBankAccountCreateSimple(BaseModel):
    """Simplified bank account schema for request (only bank_name and account_number)"""
    bank_name: str = Field(..., max_length=150, description="Name of the bank")
    account_number: str = Field(..., max_length=50, description="Bank account number")

    class Config:
        from_attributes = True


class CompanyBankAccountCreate(BaseModel):
    """Full bank account schema with all fields"""
    bank_name: str = Field(..., max_length=150, description="Name of the bank")
    account_number: str = Field(..., max_length=50, description="Bank account number")
    # account_holder_name: Optional[str] = Field(None, max_length=200, description="Account holder name")
    # ifsc_code: Optional[str] = Field(None, max_length=20, description="IFSC code")
    # branch_name: Optional[str] = Field(None, max_length=150, description="Branch name")

    class Config:
        from_attributes = True


class CompanyCreate(BaseModel):
    company_name: str = Field(..., max_length=200, description="Name of the company")
    bank_accounts: Optional[List[CompanyBankAccountCreateSimple]] = Field(default=[], description="List of bank accounts for the company (only bank_name and account_number required)")

    class Config:
        from_attributes = True


class CompanyBankAccountUpdate(BaseModel):
    """Bank account update schema - id is optional (if provided, updates existing; if not, creates new)"""
    id: Optional[int] = Field(None, description="Bank account ID (optional - if provided, updates existing account)")
    bank_name: str = Field(..., max_length=150, description="Name of the bank")
    account_number: str = Field(..., max_length=50, description="Bank account number")


class CompanyUpdate(BaseModel):
    company_name: str = Field(..., max_length=200, description="Name of the company")
    bank_accounts: Optional[List[CompanyBankAccountUpdate]] = Field(default=[], description="List of bank accounts (replace all existing with this list)")

    class Config:
        from_attributes = True


class CompanyResponse(BaseModel):
    id: int
    company_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class CompanyBankAccountResponse(BaseModel):
    id: int
    bank_name: str
    account_holder_name: Optional[str]
    account_number: str
    ifsc_code: Optional[str]
    branch_name: Optional[str]

    class Config:
        from_attributes = True


class CompanyWithBankAccounts(BaseModel):
    company: CompanyResponse
    bank_accounts: List[CompanyBankAccountResponse]

    class Config:
        from_attributes = True


class CompanyBankAccountSimpleResponse(BaseModel):
    """Simplified bank account response with only bank_name and account_number"""
    bank_name: str
    account_number: str

    class Config:
        from_attributes = True


class CompanyCreateResponse(BaseModel):
    """Response model for company creation"""
    company: CompanyResponse
    bank_accounts: List[CompanyBankAccountSimpleResponse]

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    success: bool
    message: str
    data: dict

    class Config:
        from_attributes = True


# --- Inflow Forms ---

class CustomFieldCreate(BaseModel):
    """Schema for custom field in the request (uses 'type' and 'required')"""
    field_key: str = Field(..., max_length=100, description="Field key")
    label: str = Field(..., max_length=150, description="Display label")
    type: FieldTypeEnum = Field(..., description="TEXT, NUMBER, DATE, SPINNER, TEXTAREA")
    required: bool = Field(default=False, description="Whether field is required")
    options: Optional[Any] = Field(None, description="JSON options for SPINNER/dropdown")

    class Config:
        use_enum_values = True


class InflowFormCreateWithFields(BaseModel):
    """Create inflow form with fields in one request"""
    flow_type: FlowTypeEnum = Field(..., description="INFLOW or OUTFLOW")
    mode: InflowModeEnum = Field(..., description="BANK, CASH, or UPI")
    source: str = Field(..., max_length=150, description="Source")
    attachment: int = Field(
        default=0,
        ge=0,
        le=1,
        description="0 = no attachment, 1 = attachment enabled"
    )
    custom_fields: List[CustomFieldCreate] = Field(default=[], description="List of custom fields")

    class Config:
        use_enum_values = True


class InflowFormCreate(BaseModel):
    """Create inflow form without fields"""
    flow_type: FlowTypeEnum = Field(..., description="INFLOW or OUTFLOW")
    mode: InflowModeEnum = Field(..., description="BANK, CASH, or UPI")
    source: str = Field(..., max_length=150, description="Source")

    class Config:
        use_enum_values = True


class InflowFormUpdate(BaseModel):
    flow_type: Optional[FlowTypeEnum] = None
    mode: Optional[InflowModeEnum] = None
    source: Optional[str] = Field(None, max_length=150)

    class Config:
        use_enum_values = True


class InflowFormResponse(BaseModel):
    id: int
    flow_type: str
    mode: str
    source: str
    attachment: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InflowFormSourceResponse(BaseModel):
    """Response with id and source (SELECT id, source FROM inflow_forms WHERE ...)"""
    id: int
    source: str


# --- Inflow Form Fields ---

class InflowFormFieldCreate(BaseModel):
    inflow_form_id: int = Field(..., description="Parent inflow form ID")
    field_key: str = Field(..., max_length=100, description="Field key")
    label: str = Field(..., max_length=150, description="Display label")
    field_type: FieldTypeEnum = Field(..., description="TEXT, NUMBER, DATE, SPINNER, TEXTAREA")
    is_required: bool = Field(default=False, description="Whether field is required")
    options: Optional[Any] = Field(None, description="JSON options for SPINNER/dropdown")
    sort_order: int = Field(default=0, description="Sort order")

    class Config:
        use_enum_values = True


class InflowFormFieldUpdate(BaseModel):
    field_key: Optional[str] = Field(None, max_length=100)
    label: Optional[str] = Field(None, max_length=150)
    field_type: Optional[FieldTypeEnum] = None
    is_required: Optional[bool] = None
    options: Optional[Any] = None
    sort_order: Optional[int] = None

    class Config:
        use_enum_values = True


class InflowFormFieldResponse(BaseModel):
    id: int
    inflow_form_id: int
    field_key: str
    label: str
    field_type: str
    is_required: bool
    options: Optional[Any]
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class CustomFieldResponse(BaseModel):
    """Response format matching the request format (uses 'type' and 'required')"""
    field_key: str
    label: str
    type: str
    required: bool
    options: Optional[Any] = None


class InflowFormWithFieldsResponse(InflowFormResponse):
    """Inflow form with nested fields (for GET by id)"""
    custom_fields: List[CustomFieldResponse] = []

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Response model for file upload"""
    success: bool
    message: str
    file_url: Optional[str] = None
    file_name: Optional[str] = None


class PresignedUrlResponse(BaseModel):
    """Response model for presigned URL regeneration"""
    success: bool
    message: str
    file_url: Optional[str] = None
    expires_in_seconds: int = 604800  # 1 week


# --- Inflow Entry Schemas ---

class InflowEntryAttachmentResponse(BaseModel):
    """Response model for inflow entry attachment"""
    id: int
    inflow_entry_id: int
    file_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class InflowEntryPayloadCreate(BaseModel):
    """Schema for creating inflow entry payload"""
    company_id: int = Field(..., description="Company ID")
    inflow_form_id: int = Field(..., description="Inflow form ID")
    payload: dict = Field(..., description="JSON payload with form data")
    files: Optional[List[str]] = Field(default=None, description="Optional list of file URLs (already uploaded to Railway Storage)")

    class Config:
        from_attributes = True


class InflowEntryPayloadResponse(BaseModel):
    """Response model for inflow entry payload"""
    id: int
    company_id: int
    inflow_form_id: int
    payload: dict
    created_at: datetime
    attachments: List[InflowEntryAttachmentResponse] = []

    class Config:
        from_attributes = True


class InflowEntryCreateResponse(BaseModel):
    """Response model for creating inflow entry with attachments"""
    success: bool
    message: str
    entry: InflowEntryPayloadResponse


class InflowEntryEdit(BaseModel):
    """Schema for editing an inflow entry (transaction)"""
    id: int = Field(..., description="Inflow entry ID to edit")
    payload: Optional[dict] = Field(None, description="Updated payload (partial merge supported)")


class InflowEntryDelete(BaseModel):
    """Schema for deleting an inflow entry (transaction)"""
    id: int = Field(..., description="Inflow entry ID to delete")
