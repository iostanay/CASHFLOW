from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database import get_db, engine
from models import Base, CustomerReceipt
from schemas import CustomerReceiptCreate, CustomerReceiptResponse

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Customer Receipts API",
    description="API for managing customer receipts",
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
            query = query.filter(CustomerReceipt.customer_name.ilike(f"%{customer_name}%"))
        
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
