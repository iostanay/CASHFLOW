from sqlalchemy import Column, BigInteger, Integer, String, Date, Enum, DECIMAL, Text, TIMESTAMP, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class ReceiptType(str, enum.Enum):
    CASH = "Cash"
    CHEQUE = "Cheque"
    BANK_TRANSFER = "Bank Transfer"
    UPI = "UPI"
    CARD = "Card"


class ReceiptMode(str, enum.Enum):
    CASH = "Cash"
    CHEQUE = "Cheque"
    BANK_TRANSFER = "Bank Transfer"
    NEFT = "NEFT"
    RTGS = "RTGS"
    IMPS = "IMPS"


class PaymentPurpose(str, enum.Enum):
    PURCHASE_MATERIAL = "Purchase of Material"
    PURCHASE_ASSETS = "Purchase of Assets"
    SERVICE_ADVISEMENT = "Service Advisement"
    MAINTENANCE = "MAINTENANCE"
    OTHER = "Other"


class PaymentType(str, enum.Enum):
    CASH = "Cash"
    CHEQUE = "Cheque"
    BANK_TRANSFER = "Bank Transfer"
    UPI = "UPI"
    NEFT = "NEFT"
    RTGS = "RTGS"
    IMPS = "IMPS"


class EmployeePaymentPurpose(str, enum.Enum):
    SALARY_PAYMENT = "Salary Payment"
    EXPENSES_REIMBURSEMENT = "Expenses Reimbursement"
    INCENTIVE_PAYMENT = "Incentive Payment"
    COMMISSION_PAYMENT = "Commission Payment"
    BONUS = "Bonus"
    OTHER = "Other"


class CustomerReceipt(Base):
    __tablename__ = "customer_receipts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    customer_name = Column(String(150), nullable=False)
    receipt_nature = Column(String(50), default="Cash Inflow")
    receipt_purpose = Column(String(100), default="Receipt from Customer")
    
    receipt_date = Column(Date, nullable=False)
    receipt_type = Column(String(50), default="Cash Inflow")
    
    amount = Column(DECIMAL(12, 2), nullable=False)
    
    bank_name = Column(String(150), nullable=True)
    project_name = Column(String(150), nullable=True)
    company_name = Column(String(150), nullable=True)
    
    remarks = Column(Text, nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class InflowReceiptMaster(Base):
    __tablename__ = "inflow_receipt_master"

    entity_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(150), nullable=False, unique=True)


class BankLoanReceipt(Base):
    __tablename__ = "bank_loan_receipts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    bank_name = Column(String(150), nullable=False)
    receipt_nature = Column(String(50), default="Cash Inflow")
    receipt_purpose = Column(String(100), default="Loan Receipts")
    
    loan_reference_no = Column(String(100), nullable=True)
    
    receipt_date = Column(Date, nullable=False)
    amount = Column(DECIMAL(14, 2), nullable=False)
    
    # receipt_mode = Column(Enum(ReceiptMode, native_enum=False, length=50), default="Bank Transfer")
    receipt_mode = Column(String(150), nullable=False)

    remarks = Column(Text, nullable=True)
    
    attachment_path = Column(String(255), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class VendorPayment(Base):
    __tablename__ = "vendor_payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    vendor_name = Column(String(150), nullable=False)
    payment_nature = Column(String(50), default="Cash Outflow")
    # payment_purpose = Column(Enum(PaymentPurpose, native_enum=False, length=100), nullable=False)
    payment_purpose = Column(String(150), nullable=False)
    service_or_material_details = Column(String(255), nullable=True)
    
    payment_date = Column(Date, nullable=False)
    payment_type = Column(Enum(PaymentType, native_enum=False, length=50), nullable=False)
    
    amount = Column(DECIMAL(14, 2), nullable=False)
    
    bank_name = Column(String(150), nullable=True)
    
    remarks = Column(Text, nullable=True)
    
    attachment_path = Column(String(255), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class EmployeePayment(Base):
    __tablename__ = "employee_payments"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    employee_name = Column(String(150), nullable=False)
    employee_id = Column(String(50), nullable=True)
    
    payment_nature = Column(String(50), default="Cash Outflow")
    payment_purpose = Column(Enum(EmployeePaymentPurpose, native_enum=False, length=100), nullable=False)
    
    payment_date = Column(Date, nullable=False)
    payment_type = Column(Enum(PaymentType, native_enum=False, length=50), nullable=False)
    
    amount = Column(DECIMAL(14, 2), nullable=False)
    
    bank_name = Column(String(150), nullable=True)
    
    remarks = Column(Text, nullable=True)
    
    attachment_path = Column(String(255), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class Company(Base):
    __tablename__ = "companies"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_name = Column(String(200), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationship to bank accounts
    bank_accounts = relationship("CompanyBankAccount", back_populates="company", cascade="all, delete-orphan")


class CompanyBankAccount(Base):
    __tablename__ = "company_bank_accounts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    
    bank_name = Column(String(150), nullable=False)
    account_number = Column(String(50), nullable=False)
    # account_holder_name = Column(String(200), nullable=True)
    # ifsc_code = Column(String(20), nullable=True)
    # branch_name = Column(String(150), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    
    # Relationship to company
    company = relationship("Company", back_populates="bank_accounts")


# --- Inflow Forms ---

class FlowTypeEnum(str, enum.Enum):
    INFLOW = "INFLOW"
    OUTFLOW = "OUTFLOW"


class InflowModeEnum(str, enum.Enum):
    BANK = "BANK"
    CASH = "CASH"
    UPI = "UPI"


class FieldTypeEnum(str, enum.Enum):
    TEXT = "TEXT"
    NUMBER = "NUMBER"
    DATE = "DATE"
    SPINNER = "SPINNER"
    TEXTAREA = "TEXTAREA"


class InflowForm(Base):
    __tablename__ = "inflow_forms"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    flow_type = Column(Enum(FlowTypeEnum, native_enum=False, length=20), nullable=False)
    mode = Column(Enum(InflowModeEnum, native_enum=False, length=20), nullable=False)
    source = Column(String(150), nullable=False)
    attachment = Column(Integer, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())

    fields = relationship("InflowFormField", back_populates="inflow_form", cascade="all, delete-orphan")


class InflowFormField(Base):
    __tablename__ = "inflow_form_fields"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    inflow_form_id = Column(BigInteger, ForeignKey("inflow_forms.id", ondelete="CASCADE"), nullable=False)

    field_key = Column(String(100), nullable=False)
    label = Column(String(150), nullable=False)
    field_type = Column(Enum(FieldTypeEnum, native_enum=False, length=20), nullable=False)
    is_required = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)  # for SPINNER / dropdown
    sort_order = Column(Integer, default=0)

    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    inflow_form = relationship("InflowForm", back_populates="fields")

    __table_args__ = (
        UniqueConstraint('inflow_form_id', 'field_key', name='uk_form_field'),
    )
