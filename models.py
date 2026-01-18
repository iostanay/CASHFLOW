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
