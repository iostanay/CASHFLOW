from sqlalchemy import Column, BigInteger, String, Date, Enum, DECIMAL, Text, TIMESTAMP
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


class BankLoanReceipt(Base):
    __tablename__ = "bank_loan_receipts"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    bank_name = Column(String(150), nullable=False)
    receipt_nature = Column(String(50), default="Cash Inflow")
    receipt_purpose = Column(String(100), default="Loan Receipts")
    
    loan_reference_no = Column(String(100), nullable=True)
    
    receipt_date = Column(Date, nullable=False)
    amount = Column(DECIMAL(14, 2), nullable=False)
    
    receipt_mode = Column(Enum(ReceiptMode, native_enum=False, length=50), default="Bank Transfer")
    
    remarks = Column(Text, nullable=True)
    
    attachment_path = Column(String(255), nullable=True)
    
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp())
