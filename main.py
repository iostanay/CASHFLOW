from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database import get_db, engine
from models import Base, CustomerReceipt, BankLoanReceipt
from schemas import CustomerReceiptCreate, CustomerReceiptResponse, BankLoanReceiptCreate, BankLoanReceiptResponse
from firebase_storage import upload_file_to_firebase

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Customer Receipts & Bank Loan Receipts API",
    description="API for managing customer receipts and bank loan receipts",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Customer Receipts API is running"}


@app.post("/api/receipts", response_model=CustomerReceiptResponse, status_code=status.HTTP_201_CREATED)
def create_receipt(receipt: CustomerReceiptCreate, db: Session = Depends(get_db)):
    """
    Create a new customer receipt
    """
    try:
        # Pydantic's use_enum_values=True converts enum to its value (string)
        db_receipt = CustomerReceipt(**receipt.dict())
        db.add(db_receipt)
        db.commit()
        db.refresh(db_receipt)
        return db_receipt
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating receipt: {str(e)}"
        )


@app.get("/api/receipts", response_model=List[CustomerReceiptResponse])
def list_receipts(
    skip: int = 0,
    limit: int = 100,
    customer_name: Optional[str] = None,
    receipt_type: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    List all customer receipts with optional filtering
    """
    try:
        query = db.query(CustomerReceipt)
        
        # Apply filters
        if customer_name:
            query = query.filter(CustomerReceipt.customer_name.like(f"%{customer_name}%"))
        
        if receipt_type:
            query = query.filter(CustomerReceipt.receipt_type == receipt_type)
        
        if start_date:
            query = query.filter(CustomerReceipt.receipt_date >= start_date)
        
        if end_date:
            query = query.filter(CustomerReceipt.receipt_date <= end_date)
        
        # Order by receipt_date descending (newest first)
        receipts = query.order_by(CustomerReceipt.receipt_date.desc()).offset(skip).limit(limit).all()
        return receipts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching receipts: {str(e)}"
        )


@app.get("/api/receipts/{receipt_id}", response_model=CustomerReceiptResponse)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """
    Get a specific receipt by ID
    """
    receipt = db.query(CustomerReceipt).filter(CustomerReceipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Receipt with id {receipt_id} not found"
        )
    return receipt


# Bank Loan Receipts Endpoints

@app.post("/api/bank-loan-receipts", response_model=BankLoanReceiptResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_loan_receipt(
    bank_name: str = Form(...),
    receipt_nature: str = Form(default="Cash Inflow"),
    receipt_purpose: str = Form(default="Loan Receipts"),
    loan_reference_no: Optional[str] = Form(None),
    receipt_date: date = Form(...),
    amount: float = Form(...),
    receipt_mode: str = Form(default="Bank Transfer"),
    remarks: Optional[str] = Form(None),
    attachment: Optional[UploadFile] = File(None),
    attachment_path: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Create a new bank loan receipt with optional file attachment or attachment URL/path
    
    You can either:
    1. Upload a file using 'attachment' (will be uploaded to Firebase)
    2. Provide a URL/path directly using 'attachment_path' (stored as-is)
    """
    try:
        final_attachment_path = None
        
        # # If file is uploaded, upload to Firebase
        # if attachment and attachment.filename:
        #     file_content = await attachment.read()
        #     file_url = upload_file_to_firebase(file_content, attachment.filename)
        #     if file_url:
        #         final_attachment_path = file_url
        #     else:
        #         raise HTTPException(
        #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #             detail="Failed to upload attachment to Firebase"
        #         )
        # # If attachment_path (URL) is provided directly, use it
        # elif attachment_path:
        #     final_attachment_path = attachment_path
        
        # Create receipt data
        receipt_data = {
            "bank_name": bank_name,
            "receipt_nature": receipt_nature,
            "receipt_purpose": receipt_purpose,
            "loan_reference_no": loan_reference_no,
            "receipt_date": receipt_date,
            "amount": amount,
            "receipt_mode": receipt_mode,
            "remarks": remarks,
            # "attachment_path": final_attachment_path
        }
        
        db_receipt = BankLoanReceipt(**receipt_data)
        db.add(db_receipt)
        db.commit()
        db.refresh(db_receipt)
        return db_receipt
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating bank loan receipt: {str(e)}"
        )


@app.get("/api/bank-loan-receipts", response_model=List[BankLoanReceiptResponse])
def list_bank_loan_receipts(
    skip: int = 0,
    limit: int = 100,
    bank_name: Optional[str] = None,
    loan_reference_no: Optional[str] = None,
    receipt_mode: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    List all bank loan receipts with optional filtering
    """
    try:
        query = db.query(BankLoanReceipt)
        
        # Apply filters
        if bank_name:
            query = query.filter(BankLoanReceipt.bank_name.like(f"%{bank_name}%"))
        
        if loan_reference_no:
            query = query.filter(BankLoanReceipt.loan_reference_no.like(f"%{loan_reference_no}%"))
        
        if receipt_mode:
            query = query.filter(BankLoanReceipt.receipt_mode == receipt_mode)
        
        if start_date:
            query = query.filter(BankLoanReceipt.receipt_date >= start_date)
        
        if end_date:
            query = query.filter(BankLoanReceipt.receipt_date <= end_date)
        
        # Order by receipt_date descending (newest first)
        receipts = query.order_by(BankLoanReceipt.receipt_date.desc()).offset(skip).limit(limit).all()
        return receipts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching bank loan receipts: {str(e)}"
        )


@app.get("/api/bank-loan-receipts/{receipt_id}", response_model=BankLoanReceiptResponse)
def get_bank_loan_receipt(receipt_id: int, db: Session = Depends(get_db)):
    """
    Get a specific bank loan receipt by ID
    """
    receipt = db.query(BankLoanReceipt).filter(BankLoanReceipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank loan receipt with id {receipt_id} not found"
        )
    return receipt


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
