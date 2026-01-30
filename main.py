from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional, Union
from datetime import date
import json

from database import get_db, engine
from models import (
    Base, CustomerReceipt, BankLoanReceipt, VendorPayment, EmployeePayment,
    InflowReceiptMaster, Company, CompanyBankAccount,
    InflowForm, InflowFormField,
    InflowEntryPayload, InflowEntryAttachment,
)
from schemas import (
    CustomerReceiptCreate, CustomerReceiptResponse, 
    BankLoanReceiptCreate, BankLoanReceiptResponse, 
    VendorPaymentCreate, VendorPaymentResponse, 
    EmployeePaymentCreate, EmployeePaymentResponse, 
    InflowReceiptMasterResponse,
    CompanyCreate, CompanyResponse, CompanyUpdate,
    CompanyBankAccountCreate, CompanyBankAccountResponse,
    CompanyWithBankAccounts, CompanyCreateResponse,
    InflowFormCreateWithFields, InflowFormCreate, InflowFormUpdate, InflowFormResponse, InflowFormWithFieldsResponse, InflowFormSourceResponse,
    InflowFormFieldCreate, InflowFormFieldUpdate, InflowFormFieldResponse, CustomFieldResponse,
    FileUploadResponse, PresignedUrlResponse,
    InflowEntryPayloadCreate, InflowEntryPayloadResponse, InflowEntryCreateResponse,
)
from firebase_storage import upload_file_to_firebase
from railway_storage import upload_file_to_railway, regenerate_presigned_url, generate_presigned_url_from_path

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


# @app.post("/api/receipts", response_model=CustomerReceiptResponse, status_code=status.HTTP_201_CREATED)
# def create_receipt(receipt: CustomerReceiptCreate, db: Session = Depends(get_db)):
#     """
#     Create a new customer receipt
#     """
#     try:
#         # Pydantic's use_enum_values=True converts enum to its value (string)
#         db_receipt = CustomerReceipt(**receipt.dict())
#         db.add(db_receipt)
#         db.commit()
#         db.refresh(db_receipt)
#         return db_receipt
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Error creating receipt: {str(e)}"
#         )


# @app.get("/api/receipts", response_model=List[CustomerReceiptResponse])
# def list_receipts(
#     skip: int = 0,
#     limit: int = 100,
#     customer_name: Optional[str] = None,
#     receipt_type: Optional[str] = None,
#     start_date: Optional[date] = None,
#     end_date: Optional[date] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     List all customer receipts with optional filtering
#     """
#     try:
#         query = db.query(CustomerReceipt)
        
#         # Apply filters
#         if customer_name:
#             query = query.filter(CustomerReceipt.customer_name.like(f"%{customer_name}%"))
        
#         if receipt_type:
#             query = query.filter(CustomerReceipt.receipt_type == receipt_type)
        
#         if start_date:
#             query = query.filter(CustomerReceipt.receipt_date >= start_date)
        
#         if end_date:
#             query = query.filter(CustomerReceipt.receipt_date <= end_date)
        
#         # Order by receipt_date descending (newest first)
#         receipts = query.order_by(CustomerReceipt.receipt_date.desc()).offset(skip).limit(limit).all()
#         return receipts
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching receipts: {str(e)}"
#         )


# @app.get("/api/receipts/{receipt_id}", response_model=CustomerReceiptResponse)
# def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
#     """
#     Get a specific receipt by ID
#     """
#     receipt = db.query(CustomerReceipt).filter(CustomerReceipt.id == receipt_id).first()
#     if not receipt:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Receipt with id {receipt_id} not found"
#         )
#     return receipt


# # Bank Loan Receipts Endpoints

# @app.post("/api/bank-loan-receipts", response_model=BankLoanReceiptResponse, status_code=status.HTTP_201_CREATED)
# async def create_bank_loan_receipt(
#     bank_name: str = Form(...),
#     receipt_nature: str = Form(default="Cash Inflow"),
#     receipt_purpose: str = Form(default="Loan Receipts"),
#     loan_reference_no: Optional[str] = Form(None),
#     receipt_date: date = Form(...),
#     amount: float = Form(...),
#     receipt_mode: str = Form(default="Bank Transfer"),
#     remarks: Optional[str] = Form(None),
#     # attachment: Optional[UploadFile] = File(None),
#     attachment_path: Optional[str] = Form(None),
#     db: Session = Depends(get_db)
# ):
#     """
#     Create a new bank loan receipt with optional file attachment or attachment URL/path
    
#     You can either:
#     1. Upload a file using 'attachment' (will be uploaded to Firebase)
#     2. Provide a URL/path directly using 'attachment_path' (stored as-is)
#     """
#     try:
#         final_attachment_path = None
        
#         # # If file is uploaded, upload to Firebase
#         # if attachment and attachment.filename:
#         #     file_content = await attachment.read()
#         #     file_url = upload_file_to_firebase(file_content, attachment.filename)
#         #     if file_url:
#         #         final_attachment_path = file_url
#         #     else:
#         #         raise HTTPException(
#         #             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         #             detail="Failed to upload attachment to Firebase"
#         #         )
#         # # If attachment_path (URL) is provided directly, use it
#         # elif attachment_path:
#         #     final_attachment_path = attachment_path
        
#         # Create receipt data
#         receipt_data = {
#             "bank_name": bank_name,
#             "receipt_nature": receipt_nature,
#             "receipt_purpose": receipt_purpose,
#             "loan_reference_no": loan_reference_no,
#             "receipt_date": receipt_date,
#             "amount": amount,
#             "receipt_mode": receipt_mode,
#             "remarks": remarks,
#             # "attachment_path": final_attachment_path
#         }
        
#         db_receipt = BankLoanReceipt(**receipt_data)
#         db.add(db_receipt)
#         db.commit()
#         db.refresh(db_receipt)
#         return db_receipt
#     except HTTPException:
#         db.rollback()
#         raise
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Error creating bank loan receipt: {str(e)}"
#         )


# @app.get("/api/bank-loan-receipts", response_model=List[BankLoanReceiptResponse])
# def list_bank_loan_receipts(
#     skip: int = 0,
#     limit: int = 100,
#     bank_name: Optional[str] = None,
#     loan_reference_no: Optional[str] = None,
#     receipt_mode: Optional[str] = None,
#     start_date: Optional[date] = None,
#     end_date: Optional[date] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     List all bank loan receipts with optional filtering
#     """
#     try:
#         query = db.query(BankLoanReceipt)
        
#         # Apply filters
#         if bank_name:
#             query = query.filter(BankLoanReceipt.bank_name.like(f"%{bank_name}%"))
        
#         if loan_reference_no:
#             query = query.filter(BankLoanReceipt.loan_reference_no.like(f"%{loan_reference_no}%"))
        
#         if receipt_mode:
#             query = query.filter(BankLoanReceipt.receipt_mode == receipt_mode)
        
#         if start_date:
#             query = query.filter(BankLoanReceipt.receipt_date >= start_date)
        
#         if end_date:
#             query = query.filter(BankLoanReceipt.receipt_date <= end_date)
        
#         # Order by receipt_date descending (newest first)
#         receipts = query.order_by(BankLoanReceipt.receipt_date.desc()).offset(skip).limit(limit).all()
#         return receipts
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching bank loan receipts: {str(e)}"
#         )


# @app.get("/api/bank-loan-receipts/{receipt_id}", response_model=BankLoanReceiptResponse)
# def get_bank_loan_receipt(receipt_id: int, db: Session = Depends(get_db)):
#     """
#     Get a specific bank loan receipt by ID
#     """
#     receipt = db.query(BankLoanReceipt).filter(BankLoanReceipt.id == receipt_id).first()
#     if not receipt:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Bank loan receipt with id {receipt_id} not found"
#         )
#     return receipt


# # Vendor Payments Endpoints

# @app.post("/api/vendor-payments", response_model=VendorPaymentResponse, status_code=status.HTTP_201_CREATED)
# def create_vendor_payment(payment: VendorPaymentCreate, db: Session = Depends(get_db)):
#     """
#     Create a new vendor payment
#     """
#     try:
#         db_payment = VendorPayment(**payment.dict())
#         db.add(db_payment)
#         db.commit()
#         db.refresh(db_payment)
#         return db_payment
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Error creating vendor payment: {str(e)}"
#         )


# @app.get("/api/vendor-payments", response_model=List[VendorPaymentResponse])
# def list_vendor_payments(
#     skip: int = 0,
#     limit: int = 100,
#     vendor_name: Optional[str] = None,
#     payment_purpose: Optional[str] = None,
#     payment_type: Optional[str] = None,
#     start_date: Optional[date] = None,
#     end_date: Optional[date] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     List all vendor payments with optional filtering
#     """
#     try:
#         query = db.query(VendorPayment)
        
#         # Apply filters
#         if vendor_name:
#             query = query.filter(VendorPayment.vendor_name.like(f"%{vendor_name}%"))
        
#         if payment_purpose:
#             query = query.filter(VendorPayment.payment_purpose == payment_purpose)
        
#         if payment_type:
#             query = query.filter(VendorPayment.payment_type == payment_type)
        
#         if start_date:
#             query = query.filter(VendorPayment.payment_date >= start_date)
        
#         if end_date:
#             query = query.filter(VendorPayment.payment_date <= end_date)
        
#         # Order by payment_date descending (newest first)
#         payments = query.order_by(VendorPayment.payment_date.desc()).offset(skip).limit(limit).all()
#         return payments
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching vendor payments: {str(e)}"
#         )


# @app.get("/api/vendor-payments/{payment_id}", response_model=VendorPaymentResponse)
# def get_vendor_payment(payment_id: int, db: Session = Depends(get_db)):
#     """
#     Get a specific vendor payment by ID
#     """
#     payment = db.query(VendorPayment).filter(VendorPayment.id == payment_id).first()
#     if not payment:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Vendor payment with id {payment_id} not found"
#         )
#     return payment


# # Employee Payments Endpoints

# @app.post("/api/employee-payments", response_model=EmployeePaymentResponse, status_code=status.HTTP_201_CREATED)
# def create_employee_payment(payment: EmployeePaymentCreate, db: Session = Depends(get_db)):
#     """
#     Create a new employee payment
#     """
#     try:
#         db_payment = EmployeePayment(**payment.dict())
#         db.add(db_payment)
#         db.commit()
#         db.refresh(db_payment)
#         return db_payment
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f"Error creating employee payment: {str(e)}"
#         )


# @app.get("/api/employee-payments", response_model=List[EmployeePaymentResponse])
# def list_employee_payments(
#     skip: int = 0,
#     limit: int = 100,
#     employee_name: Optional[str] = None,
#     employee_id: Optional[str] = None,
#     payment_purpose: Optional[str] = None,
#     payment_type: Optional[str] = None,
#     start_date: Optional[date] = None,
#     end_date: Optional[date] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     List all employee payments with optional filtering
#     """
#     try:
#         query = db.query(EmployeePayment)
        
#         # Apply filters
#         if employee_name:
#             query = query.filter(EmployeePayment.employee_name.like(f"%{employee_name}%"))
        
#         if employee_id:
#             query = query.filter(EmployeePayment.employee_id.like(f"%{employee_id}%"))
        
#         if payment_purpose:
#             query = query.filter(EmployeePayment.payment_purpose == payment_purpose)
        
#         if payment_type:
#             query = query.filter(EmployeePayment.payment_type == payment_type)
        
#         if start_date:
#             query = query.filter(EmployeePayment.payment_date >= start_date)
        
#         if end_date:
#             query = query.filter(EmployeePayment.payment_date <= end_date)
        
#         # Order by payment_date descending (newest first)
#         payments = query.order_by(EmployeePayment.payment_date.desc()).offset(skip).limit(limit).all()
#         return payments
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching employee payments: {str(e)}"
#         )


# @app.get("/api/employee-payments/{payment_id}", response_model=EmployeePaymentResponse)
# def get_employee_payment(payment_id: int, db: Session = Depends(get_db)):
#     """
#     Get a specific employee payment by ID
#     """
#     payment = db.query(EmployeePayment).filter(EmployeePayment.id == payment_id).first()
#     if not payment:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"Employee payment with id {payment_id} not found"
#         )
#     return payment


# Inflow Receipt Master Endpoints

@app.get("/api/inflow-receipt-master", response_model=List[InflowReceiptMasterResponse])
def list_inflow_receipt_master(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all inflow receipt master records with optional filtering
    """
    try:
        query = db.query(InflowReceiptMaster)
        
        # Apply filters
        if name:
            query = query.filter(InflowReceiptMaster.name.like(f"%{name}%"))
        
        # Order by name ascending
        records = query.order_by(InflowReceiptMaster.name.asc()).offset(skip).limit(limit).all()
        return records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching inflow receipt master: {str(e)}"
        )


@app.get("/api/inflow-receipt-master/{entity_id}", response_model=InflowReceiptMasterResponse)
def get_inflow_receipt_master(entity_id: int, db: Session = Depends(get_db)):
    """
    Get a specific inflow receipt master record by ID
    """
    record = db.query(InflowReceiptMaster).filter(InflowReceiptMaster.entity_id == entity_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inflow receipt master with id {entity_id} not found"
        )
    return record


# Company Endpoints

@app.post("/api/companies", response_model=CompanyCreateResponse, status_code=status.HTTP_201_CREATED)
def create_company(company: CompanyCreate, db: Session = Depends(get_db)):
    """
    Create a new company with bank accounts in a single API call.
    Request body accepts bank_accounts with only bank_name and account_number.
    Response returns company with all bank account details.
    """
    try:
        company_data = company.dict()
        bank_accounts_data = company_data.pop("bank_accounts", [])
        
        # Create company
        db_company = Company(**company_data)
        db.add(db_company)
        db.flush()  # Flush to get the company ID without committing
        
        # Create bank accounts if provided
        created_bank_accounts = []
        if bank_accounts_data:
            for bank_account_data in bank_accounts_data:
                bank_account_data["company_id"] = db_company.id
                db_bank_account = CompanyBankAccount(**bank_account_data)
                db.add(db_bank_account)
                created_bank_accounts.append(db_bank_account)
        
        db.commit()
        db.refresh(db_company)
        
        # Refresh bank accounts to get their IDs
        for ba in created_bank_accounts:
            db.refresh(ba)
        
        # Format response
        return {
            "company": {
                "id": db_company.id,
                "company_name": db_company.company_name,
                "created_at": db_company.created_at
            },
            "bank_accounts": [
                {
                    "bank_name": ba.bank_name,
                    "account_number": ba.account_number
                }
                for ba in created_bank_accounts
            ]
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating company: {str(e)}"
        )


@app.get("/api/companies")
def list_companies(db: Session = Depends(get_db)):
    """
    List all companies with their bank accounts in the specified format
    """
    try:
        companies = db.query(Company).order_by(Company.created_at.desc()).all()
        
        result = []
        for company in companies:
            # Get bank accounts for this company
            bank_accounts = db.query(CompanyBankAccount).filter(
                CompanyBankAccount.company_id == company.id
            ).all()
            
            # Format bank accounts
            bank_accounts_list = [
                {
                    "id": ba.id,
                    "bank_name": ba.bank_name,
                    # "account_holder_name": ba.account_holder_name,
                    "account_number": ba.account_number,
                    # "ifsc_code": ba.ifsc_code,
                    # "branch_name": ba.branch_name
                }
                for ba in bank_accounts
            ]
            
            # Format company data
            result.append({
                "company": {
                    "id": company.id,
                    "company_name": company.company_name,
                    "created_at": company.created_at.isoformat()
                },
                "bank_accounts": bank_accounts_list
            })
        
        return {
            "success": True,
            "message": "Company list fetched successfully",
            "data": {
                "companies": result
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching companies: {str(e)}"
        )


@app.get("/api/companies/{company_id}")
def get_company(company_id: int, db: Session = Depends(get_db)):
    """
    Get a specific company by ID with its bank accounts
    """
    try:
        # Get company
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found"
            )
        
        # Get bank accounts for this company
        bank_accounts = db.query(CompanyBankAccount).filter(
            CompanyBankAccount.company_id == company.id
        ).all()
        
        # Format bank accounts
        bank_accounts_list = [
            {
                "id": ba.id,
                "bank_name": ba.bank_name,
                "account_number": ba.account_number
            }
            for ba in bank_accounts
        ]
        
        # Format response
        return {
            "success": True,
            "message": "Company fetched successfully",
            "data": {
                "company": {
                    "id": company.id,
                    "company_name": company.company_name,
                    "created_at": company.created_at.isoformat()
                },
                "bank_accounts": bank_accounts_list
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching company: {str(e)}"
        )


@app.put("/api/companies/{company_id}", response_model=CompanyCreateResponse)
def update_company(company_id: int, company_update: CompanyUpdate, db: Session = Depends(get_db)):
    """
    Update a company by ID - updates company name and bank accounts
    Bank accounts are replaced with the provided list
    """
    try:
        # Get company
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found"
            )
        
        # Update company name
        company.company_name = company_update.company_name
        
        # Get existing bank accounts
        existing_bank_accounts = db.query(CompanyBankAccount).filter(
            CompanyBankAccount.company_id == company_id
        ).all()
        
        # Get IDs of bank accounts to keep (those with id in the update request)
        bank_account_ids_to_keep = {
            ba.id for ba in company_update.bank_accounts or [] if ba.id is not None
        }
        
        # Delete bank accounts that are not in the update list
        for existing_ba in existing_bank_accounts:
            if existing_ba.id not in bank_account_ids_to_keep:
                db.delete(existing_ba)
        
        # Update or create bank accounts
        updated_bank_accounts = []
        for bank_account_data in company_update.bank_accounts or []:
            ba_data = bank_account_data.dict()
            ba_id = ba_data.pop("id", None)
            
            if ba_id:
                # Update existing bank account
                existing_ba = db.query(CompanyBankAccount).filter(
                    CompanyBankAccount.id == ba_id,
                    CompanyBankAccount.company_id == company_id
                ).first()
                if existing_ba:
                    existing_ba.bank_name = ba_data["bank_name"]
                    existing_ba.account_number = ba_data["account_number"]
                    updated_bank_accounts.append(existing_ba)
            else:
                # Create new bank account
                ba_data["company_id"] = company_id
                new_ba = CompanyBankAccount(**ba_data)
                db.add(new_ba)
                updated_bank_accounts.append(new_ba)
        
        db.flush()
        
        # Refresh all bank accounts to get their IDs
        for ba in updated_bank_accounts:
            db.refresh(ba)
        
        db.commit()
        db.refresh(company)
        
        # Format response
        return {
            "company": {
                "id": company.id,
                "company_name": company.company_name,
                "created_at": company.created_at
            },
            "bank_accounts": [
                {
                    "bank_name": ba.bank_name,
                    "account_number": ba.account_number
                }
                for ba in updated_bank_accounts
            ]
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating company: {str(e)}"
        )


@app.delete("/api/companies/{company_id}")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    """
    Delete a company by ID (cascades to delete all associated bank accounts)
    """
    try:
        # Get company
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found"
            )
        
        # Delete company (bank accounts will be deleted automatically due to CASCADE)
        db.delete(company)
        db.commit()
        
        return {
            "success": True,
            "message": f"Company with id {company_id} deleted successfully"
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting company: {str(e)}"
        )


# --- Inflow Forms ---

@app.post("/api/inflow-forms", response_model=InflowFormWithFieldsResponse, status_code=status.HTTP_201_CREATED)
def create_inflow_form_with_fields(payload: InflowFormCreateWithFields, db: Session = Depends(get_db)):
    """
    Create a new inflow form with custom fields in one request.
    Accepts: {flow_type, mode, source, custom_fields: [{field_key, label, type, required, options}]}
    """
    try:
        form_data = payload.model_dump(exclude={"custom_fields"})
        db_form = InflowForm(**form_data)
        db.add(db_form)
        db.flush()

        created_fields = []
        for idx, custom_field in enumerate(payload.custom_fields):
            field_data = {
                "inflow_form_id": db_form.id,
                "field_key": custom_field.field_key,
                "label": custom_field.label,
                "field_type": custom_field.type,
                "is_required": custom_field.required,
                "options": custom_field.options,
                "sort_order": idx,
            }
            db_field = InflowFormField(**field_data)
            db.add(db_field)
            created_fields.append(db_field)

        db.commit()
        db.refresh(db_form)
        for field in created_fields:
            db.refresh(field)

        custom_fields_response = [
            CustomFieldResponse(
                field_key=f.field_key,
                label=f.label,
                type=f.field_type,
                required=f.is_required,
                options=f.options,
            )
            for f in sorted(created_fields, key=lambda x: (x.sort_order, x.id))
        ]

        _val = lambda e: e.value if hasattr(e, "value") else e
        return InflowFormWithFieldsResponse(
            id=db_form.id,
            flow_type=_val(db_form.flow_type),
            mode=_val(db_form.mode),
            attachment=_val(db_form.attachment),
            source=db_form.source,
            created_at=db_form.created_at,
            updated_at=db_form.updated_at,
            custom_fields=custom_fields_response,
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating inflow form: {str(e)}"
        )


@app.get("/api/inflow-forms", response_model=List[InflowFormResponse])
def list_inflow_forms(
    flow_type: str,
    mode: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Get inflow forms filtered by flow_type and mode.
    Equivalent to: SELECT * FROM inflow_forms WHERE flow_type = ? AND mode = ?
    """
    try:
        query = (
            db.query(InflowForm)
            .filter(InflowForm.flow_type == flow_type, InflowForm.mode == mode)
            .order_by(InflowForm.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        forms = query.all()
        return forms
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching inflow forms: {str(e)}"
        )


@app.get("/api/inflow-forms/sources", response_model=List[InflowFormSourceResponse])
def list_inflow_form_sources(
    flow_type: str,
    mode: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    Get id and source from inflow_forms filtered by flow_type and mode.
    Equivalent to: SELECT id, source FROM inflow_forms WHERE flow_type = ? AND mode = ?
    """
    try:
        rows = (
            db.query(InflowForm.id, InflowForm.source)
            .filter(InflowForm.flow_type == flow_type, InflowForm.mode == mode)
            .order_by(InflowForm.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [InflowFormSourceResponse(id=r[0], source=r[1]) for r in rows]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching sources: {str(e)}"
        )


@app.get("/api/inflow-forms/{form_id}", response_model=InflowFormWithFieldsResponse)
def get_inflow_form(form_id: int, db: Session = Depends(get_db)):
    """Get an inflow form by ID with its custom fields."""
    form = db.query(InflowForm).filter(InflowForm.id == form_id).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inflow form with id {form_id} not found"
        )
    
    _val = lambda e: e.value if hasattr(e, "value") else e
    fields = sorted(form.fields, key=lambda x: (x.sort_order, x.id))
    custom_fields_response = [
        CustomFieldResponse(
            field_key=f.field_key,
            label=f.label,
            type=f.field_type,
            required=f.is_required,
            options=f.options,
        )
        for f in fields
    ]
    
    return InflowFormWithFieldsResponse(
        id=form.id,
        flow_type=_val(form.flow_type),
        mode=_val(form.mode),
        attachment=bool(_val(form.attachment)),
        source=form.source,
        created_at=form.created_at,
        updated_at=form.updated_at,
        custom_fields=custom_fields_response,
    )


@app.put("/api/inflow-forms/{form_id}", response_model=InflowFormResponse)
def update_inflow_form(form_id: int, payload: InflowFormUpdate, db: Session = Depends(get_db)):
    """Update an inflow form by ID."""
    form = db.query(InflowForm).filter(InflowForm.id == form_id).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inflow form with id {form_id} not found"
        )
    try:
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(form, k, v)
        db.commit()
        db.refresh(form)
        return form
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating inflow form: {str(e)}"
        )


@app.delete("/api/inflow-forms/{form_id}")
def delete_inflow_form(form_id: int, db: Session = Depends(get_db)):
    """Delete an inflow form by ID (cascades to fields)."""
    form = db.query(InflowForm).filter(InflowForm.id == form_id).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inflow form with id {form_id} not found"
        )
    try:
        db.delete(form)
        db.commit()
        return {"success": True, "message": f"Inflow form {form_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting inflow form: {str(e)}"
        )


# --- Inflow Form Fields (Individual CRUD) ---

@app.post("/api/inflow-form-fields", response_model=InflowFormFieldResponse, status_code=status.HTTP_201_CREATED)
def create_inflow_form_field(payload: InflowFormFieldCreate, db: Session = Depends(get_db)):
    """Create a new inflow form field."""
    form = db.query(InflowForm).filter(InflowForm.id == payload.inflow_form_id).first()
    if not form:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inflow form with id {payload.inflow_form_id} not found"
        )
    try:
        db_field = InflowFormField(**payload.model_dump())
        db.add(db_field)
        db.commit()
        db.refresh(db_field)
        return db_field
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating inflow form field: {str(e)}"
        )


# @app.get("/api/inflow-form-fields", response_model=List[InflowFormFieldResponse])
# def list_inflow_form_fields(
#     skip: int = 0,
#     limit: int = 100,
#     inflow_form_id: Optional[int] = None,
#     db: Session = Depends(get_db),
# ):
#     """List inflow form fields, optionally filtered by form."""
#     try:
#         query = db.query(InflowFormField)
#         if inflow_form_id is not None:
#             query = query.filter(InflowFormField.inflow_form_id == inflow_form_id)
#         fields = query.order_by(InflowFormField.sort_order, InflowFormField.id).offset(skip).limit(limit).all()
#         return fields
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error fetching inflow form fields: {str(e)}"
#         )


@app.get("/api/inflow-form-fields/{field_id}", response_model=InflowFormFieldResponse)
def get_inflow_form_field(field_id: int, db: Session = Depends(get_db)):
    """Get an inflow form field by ID."""
    field = db.query(InflowFormField).filter(InflowFormField.id == field_id).first()
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inflow form field with id {field_id} not found"
        )
    return field


@app.put("/api/inflow-form-fields/{field_id}", response_model=InflowFormFieldResponse)
def update_inflow_form_field(field_id: int, payload: InflowFormFieldUpdate, db: Session = Depends(get_db)):
    """Update an inflow form field by ID."""
    field = db.query(InflowFormField).filter(InflowFormField.id == field_id).first()
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inflow form field with id {field_id} not found"
        )
    try:
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(field, k, v)
        db.commit()
        db.refresh(field)
        return field
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating inflow form field: {str(e)}"
        )


@app.delete("/api/inflow-form-fields/{field_id}")
def delete_inflow_form_field(field_id: int, db: Session = Depends(get_db)):
    """Delete an inflow form field by ID."""
    field = db.query(InflowFormField).filter(InflowFormField.id == field_id).first()
    if not field:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Inflow form field with id {field_id} not found"
        )
    try:
        db.delete(field)
        db.commit()
        return {"success": True, "message": f"Inflow form field {field_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting inflow form field: {str(e)}"
        )


# File Upload Endpoint

@app.post("/api/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    folder: Optional[str] = Form(default="attachments", description="Folder path in Railway Storage")
):
    """
    Upload a file to Railway Storage
    
    - **file**: The file to upload (required)
    - **folder**: Optional folder path in Railway Storage (default: "attachments")
    
    Returns the public URL of the uploaded file
    """
    try:
        # Read file content
        file_content = await file.read()
        
        if not file_content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File is empty"
            )
        
        # Upload to Railway Storage
        try:
            file_url = upload_file_to_railway(
                file_content=file_content,
                file_name=file.filename or "unnamed_file",
                folder=folder
            )
            
            if not file_url:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to upload file to Railway Storage: No URL returned"
                )
        except Exception as upload_error:
            error_message = str(upload_error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file to Railway Storage: {error_message}"
            )
        
        return {
            "success": True,
            "message": "File uploaded successfully",
            "file_url": file_url,
            "file_name": file.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )


# Inflow Entry Transaction Endpoint

@app.post("/api/add-transaction", response_model=InflowEntryCreateResponse, status_code=status.HTTP_201_CREATED)
async def add_transaction(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Create a new inflow entry transaction with optional file attachments from device
    
    - **company_id**: ID of the company (required, form field)
    - **inflow_form_id**: ID of the inflow form (required, form field)
    - **payload**: JSON string containing the form data (required, form field)
    - **bank_name**: Optional bank name (form field)
    - **bank_account_number**: Optional bank account number (form field)
    - **files**: Optional list of files to upload as attachments (can upload multiple files from device)
    
    Returns the created entry with all attachments
    
    Example usage with curl:
    curl -X POST "http://localhost:8000/api/add-transaction" \\
      -F "company_id=1" \\
      -F "inflow_form_id=1" \\
      -F "payload={\\"amount\\": 1000}" \\
      -F "bank_name=My Bank" \\
      -F "bank_account_number=1234567890" \\
      -F "files=@/path/to/file1.pdf" \\
      -F "files=@/path/to/file2.jpg"
    """
    try:
        # Parse all form data manually to avoid FastAPI validation issues with files
        form_data = await request.form()
        
        # Extract form fields
        try:
            company_id = int(form_data.get("company_id"))
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="company_id is required and must be a valid integer"
            )
        
        try:
            inflow_form_id = int(form_data.get("inflow_form_id"))
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="inflow_form_id is required and must be a valid integer"
            )
        
        payload = form_data.get("payload")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="payload is required"
            )
        
        # Parse files from form data - DEVICE থেকে files upload handle করবে
        files_list = []
        
        print(f"🔍 DEBUG: Starting file parsing...")
        print(f"🔍 DEBUG: Form data type: {type(form_data)}")
        print(f"🔍 DEBUG: Form data keys: {list(form_data.keys())}")
        
        try:
            # FastAPI's form_data.getlist() should work for multiple files with same name
            if "files" in form_data:
                files_data = form_data.getlist("files")
                print(f"✓ Found 'files' field in form_data, count: {len(files_data)}")
                
                for idx, file_item in enumerate(files_data):
                    print(f"🔍 DEBUG: File item {idx}: type={type(file_item)}")
                    print(f"🔍 DEBUG: Is UploadFile? {isinstance(file_item, UploadFile)}")
                    
                    # Check if it's an UploadFile instance
                    if isinstance(file_item, UploadFile):
                        filename = getattr(file_item, 'filename', None) or getattr(file_item, 'name', None)
                        print(f"🔍 DEBUG: UploadFile filename: {filename}")
                        
                        if filename and str(filename).strip() and filename != 'undefined':
                            files_list.append(file_item)
                            print(f"  ✓ Added device file: {filename}")
                        else:
                            print(f"  ⚠ Skipped file (no valid filename): {file_item}")
                    else:
                        # Try to convert or check if it has file-like attributes
                        print(f"  ⚠ File item is not UploadFile, trying alternative...")
                        # Sometimes FastAPI wraps it differently
                        if hasattr(file_item, 'read') or hasattr(file_item, 'filename'):
                            files_list.append(file_item)
                            print(f"  ✓ Added file-like object")
            
            # Also check all items in case files are stored differently
            print(f"🔍 DEBUG: Checking all form items...")
            for key in form_data.keys():
                if "file" in key.lower():
                    value = form_data.get(key)
                    print(f"🔍 DEBUG: Found file-related key '{key}': type={type(value)}")
                    if isinstance(value, UploadFile) and value not in files_list:
                        filename = getattr(value, 'filename', None)
                        if filename:
                            files_list.append(value)
                            print(f"  ✓ Added file from key '{key}': {filename}")
        
        except Exception as e:
            print(f"⚠ Error parsing files from device: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print(f"✓ Total files from device ready for Railway Storage upload: {len(files_list)}")
        if len(files_list) == 0:
            print(f"⚠ WARNING: No files were parsed! Files might not be in form_data.")
            print(f"🔍 DEBUG: Try checking request directly or use different parsing method.")
        
        # Validate company exists
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {company_id} not found"
            )
        
        # Validate inflow form exists
        inflow_form = db.query(InflowForm).filter(InflowForm.id == inflow_form_id).first()
        if not inflow_form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inflow form with id {inflow_form_id} not found"
            )
        
        # Parse JSON payload - handle both string and already parsed JSON
        try:
            # If payload is already a dict (shouldn't happen with Form, but handle it)
            if isinstance(payload, dict):
                payload_dict = payload
            elif isinstance(payload, str):
                # Strip whitespace and try to parse as JSON string
                payload = payload.strip()
                if not payload:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Payload cannot be empty"
                    )
                # Try to parse as JSON string
                payload_dict = json.loads(payload)
            else:
                # Try to convert to dict
                payload_dict = dict(payload) if hasattr(payload, '__dict__') else {"data": payload}
        except json.JSONDecodeError as e:
            error_detail = f"Invalid JSON payload: {str(e)}"
            if "Expecting value" in str(e) or "Invalid" in str(e):
                error_detail += f". Received: {payload[:100]}..." if len(payload) > 100 else f". Received: {payload}"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error parsing payload: {str(e)}"
            )
        
        # Validate payload is a dict/object (not a list or primitive)
        if not isinstance(payload_dict, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Payload must be a JSON object/dict, got {type(payload_dict).__name__}. Example: {{\"key\": \"value\"}}"
            )
        
        # Merge optional bank fields from form into payload (so they are stored with the entry)
        bank_name = form_data.get("bank_name")
        bank_account_number = form_data.get("bank_account_number")
        if bank_name is not None and str(bank_name).strip():
            payload_dict["bank_name"] = str(bank_name).strip()
        if bank_account_number is not None and str(bank_account_number).strip():
            payload_dict["bank_account_number"] = str(bank_account_number).strip()
        
        # Create inflow entry payload
        db_entry = InflowEntryPayload(
            company_id=company_id,
            inflow_form_id=inflow_form_id,
            payload=payload_dict
        )
        db.add(db_entry)
        db.flush()  # Flush to get the entry ID without committing
        
        # Handle file uploads from device if provided
        # Support both single file and multiple files
        attachment_urls = []
        uploaded_files_count = 0
        failed_files = []
        
        # Also check if file_upload URLs are provided in the payload
        file_urls_from_payload = []
        if isinstance(payload_dict, dict) and "file_upload" in payload_dict:
            file_upload_data = payload_dict.get("file_upload")
            if isinstance(file_upload_data, list):
                # Extract file URLs from payload
                file_urls_from_payload = [url for url in file_upload_data if isinstance(url, str) and url.strip()]
            elif isinstance(file_upload_data, str):
                # Single file URL
                file_urls_from_payload = [file_upload_data] if file_upload_data.strip() else []
        
        # files_list is already parsed from form_data above
        
        # Handle files uploaded from device - UPLOAD TO RAILWAY STORAGE
        print(f"🔍 DEBUG: files_list length: {len(files_list) if files_list else 0}")
        if files_list and len(files_list) > 0:
            print(f"✓ Processing {len(files_list)} file(s) from device for Railway Storage upload...")
            for idx, file in enumerate(files_list):
                filename = getattr(file, 'filename', 'No filename')
                print(f"🔍 DEBUG: Processing file {idx + 1}/{len(files_list)}: {filename}")
                print(f"🔍 DEBUG: File object: {file}, type: {type(file)}")
                # Check if file has a filename (file was actually uploaded from device)
                if hasattr(file, 'filename') and file.filename and file.filename.strip():
                    try:
                        # Read file content from device
                        file_content = await file.read()
                        file_size = len(file_content)
                        
                        if file_content and file_size > 0:
                            print(f"Uploading file from device to Railway Storage: {file.filename} ({file_size} bytes)")
                            
                            # Upload to Railway Storage - DEVICE FILE TO RAILWAY
                            file_url = upload_file_to_railway(
                                file_content=file_content,
                                file_name=file.filename,
                                folder=f"inflow/{company_id}/{inflow_form_id}"  # Organized folder structure
                            )
                            
                            if file_url:
                                print(f"✓ Successfully uploaded {file.filename} to Railway Storage: {file_url}")
                                
                                # Create attachment record with Railway Storage URL
                                db_attachment = InflowEntryAttachment(
                                    inflow_entry_id=db_entry.id,
                                    file_url=file_url  # Railway Storage URL stored here
                                )
                                db.add(db_attachment)
                                attachment_urls.append(file_url)
                                uploaded_files_count += 1
                            else:
                                failed_files.append(file.filename)
                                print(f"✗ Failed to upload file {file.filename} to Railway Storage - no URL returned")
                        else:
                            failed_files.append(file.filename)
                            print(f"✗ File {file.filename} is empty (0 bytes)")
                    except Exception as upload_error:
                        failed_files.append(file.filename)
                        error_msg = str(upload_error)
                        print(f"✗ Error uploading file {file.filename} to Railway Storage: {error_msg}")
                        # Continue with other files even if one fails
                else:
                    print(f"Warning: Skipping file with no filename")
        
        # Handle file URLs from payload (already uploaded files - these are already Railway Storage URLs)
        if file_urls_from_payload:
            print(f"Processing {len(file_urls_from_payload)} file URL(s) from payload (already in Railway Storage)...")
            for file_url in file_urls_from_payload:
                try:
                    # Create attachment record for already uploaded Railway Storage URL
                    db_attachment = InflowEntryAttachment(
                        inflow_entry_id=db_entry.id,
                        file_url=file_url  # Railway Storage URL from payload
                    )
                    db.add(db_attachment)
                    attachment_urls.append(file_url)
                    uploaded_files_count += 1
                    print(f"✓ Added Railway Storage URL to attachments: {file_url}")
                except Exception as url_error:
                    failed_files.append(file_url)
                    print(f"✗ Error creating attachment for Railway Storage URL {file_url}: {str(url_error)}")
        
        # Commit all changes
        db.commit()
        db.refresh(db_entry)
        
        # Get all attachments for this entry
        attachments = db.query(InflowEntryAttachment).filter(
            InflowEntryAttachment.inflow_entry_id == db_entry.id
        ).all()
        
        print(f"🔍 DEBUG: Total attachments in database: {len(attachments)}")
        print(f"🔍 DEBUG: uploaded_files_count: {uploaded_files_count}")
        print(f"🔍 DEBUG: failed_files: {failed_files}")
        print(f"🔍 DEBUG: attachment_urls: {attachment_urls}")
        
        # Build success message
        message = f"Inflow entry created successfully"
        if uploaded_files_count > 0:
            message += f" with {uploaded_files_count} file(s) uploaded to Railway Storage"
        if failed_files:
            message += f". {len(failed_files)} file(s) failed to upload: {', '.join(failed_files[:5])}"  # Limit to first 5
        if len(files_list) > 0 and uploaded_files_count == 0:
            message += f". Warning: {len(files_list)} file(s) were received but none were uploaded successfully."
        
        # Build attachments list for response
        attachments_list = []
        for att in attachments:
            attachments_list.append({
                "id": att.id,
                "inflow_entry_id": att.inflow_entry_id,
                "file_url": att.file_url,
                "created_at": att.created_at
            })
        
        print(f"🔍 DEBUG: Response attachments count: {len(attachments_list)}")
        print(f"🔍 DEBUG: Response attachments: {attachments_list}")
        
        return {
            "success": True,
            "message": message,
            "entry": {
                "id": db_entry.id,
                "company_id": db_entry.company_id,
                "inflow_form_id": db_entry.inflow_form_id,
                "payload": db_entry.payload,
                "created_at": db_entry.created_at,
                "attachments": attachments_list
            }
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating inflow entry: {str(e)}"
        )


# JSON Endpoint for add-transaction (alternative to form-data endpoint)

@app.post("/api/add-transaction-json", response_model=InflowEntryCreateResponse, status_code=status.HTTP_201_CREATED)
async def add_transaction_json(
    transaction_data: InflowEntryPayloadCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new inflow entry transaction with file URLs (JSON endpoint)
    
    This endpoint accepts JSON body instead of form-data.
    Use this when files are already uploaded to Railway Storage and you have the URLs.
    
    - **company_id**: ID of the company (required)
    - **inflow_form_id**: ID of the inflow form (required)
    - **payload**: JSON object with form data (required)
    - **files**: Optional list of file URLs (already uploaded to Railway Storage)
    
    Example:
    {
      "company_id": 1,
      "inflow_form_id": 10,
      "payload": {
        "transaction_id": "TXN123",
        "amount": 5000
      },
      "files": [
        "inflow/1/10/receipt1.pdf",
        "inflow/1/10/receipt2.jpg"
      ]
    }
    """
    try:
        # Validate company exists
        company = db.query(Company).filter(Company.id == transaction_data.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company with id {transaction_data.company_id} not found"
            )
        
        # Validate inflow form exists
        inflow_form = db.query(InflowForm).filter(InflowForm.id == transaction_data.inflow_form_id).first()
        if not inflow_form:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Inflow form with id {transaction_data.inflow_form_id} not found"
            )
        
        # Create inflow entry payload
        db_entry = InflowEntryPayload(
            company_id=transaction_data.company_id,
            inflow_form_id=transaction_data.inflow_form_id,
            payload=transaction_data.payload
        )
        db.add(db_entry)
        db.flush()  # Flush to get the entry ID without committing
        
        # Handle file URLs from request
        attachment_urls = []
        uploaded_files_count = 0
        failed_files = []
        
        if transaction_data.files:
            print(f"Processing {len(transaction_data.files)} file URL(s) from JSON request...")
            for file_url in transaction_data.files:
                if file_url and file_url.strip():
                    try:
                        # Create attachment record for Railway Storage URL
                        db_attachment = InflowEntryAttachment(
                            inflow_entry_id=db_entry.id,
                            file_url=file_url.strip()
                        )
                        db.add(db_attachment)
                        attachment_urls.append(file_url)
                        uploaded_files_count += 1
                        print(f"✓ Added Railway Storage URL to attachments: {file_url}")
                    except Exception as url_error:
                        failed_files.append(file_url)
                        print(f"✗ Error creating attachment for Railway Storage URL {file_url}: {str(url_error)}")
        
        # Commit all changes
        db.commit()
        db.refresh(db_entry)
        
        # Get all attachments for this entry
        attachments = db.query(InflowEntryAttachment).filter(
            InflowEntryAttachment.inflow_entry_id == db_entry.id
        ).all()
        
        # Build success message
        message = f"Inflow entry created successfully"
        if uploaded_files_count > 0:
            message += f" with {uploaded_files_count} file URL(s) linked"
        if failed_files:
            message += f". {len(failed_files)} file URL(s) failed: {', '.join(failed_files[:5])}"
        
        return {
            "success": True,
            "message": message,
            "entry": {
                "id": db_entry.id,
                "company_id": db_entry.company_id,
                "inflow_form_id": db_entry.inflow_form_id,
                "payload": db_entry.payload,
                "created_at": db_entry.created_at,
                "attachments": [
                    {
                        "id": att.id,
                        "inflow_entry_id": att.inflow_entry_id,
                        "file_url": att.file_url,
                        "created_at": att.created_at
                    }
                    for att in attachments
                ]
            }
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating inflow entry: {str(e)}"
        )


# Presigned URL Regeneration Endpoint

@app.post("/api/regenerate-presigned-url", response_model=PresignedUrlResponse, status_code=status.HTTP_200_OK)
async def regenerate_presigned_url_endpoint(
    file_url: str = Form(..., description="Existing Railway Storage URL (can be expired)"),
    db: Session = Depends(get_db)
):
    """
    Regenerate presigned URL for an expired or existing Railway Storage file URL
    
    - **file_url**: Existing Railway Storage URL (can be expired presigned URL or direct URL)
    
    Returns a new presigned URL valid for 1 week (Railway Storage maximum)
    
    This endpoint is useful when:
    - Presigned URLs have expired (they expire after 1 week)
    - You need a fresh presigned URL for file access
    - You have a direct URL that needs to be converted to presigned URL
    """
    try:
        if not file_url or not file_url.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="file_url is required"
            )
        
        print(f"🔄 Regenerating presigned URL for: {file_url[:100]}...")
        
        # Regenerate presigned URL
        new_presigned_url = regenerate_presigned_url(file_url.strip())
        
        if not new_presigned_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate presigned URL. Check if the file exists in Railway Storage."
            )
        
        return {
            "success": True,
            "message": "Presigned URL generated successfully (valid for 1 week)",
            "file_url": new_presigned_url,
            "expires_in_seconds": 604800  # 1 week
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error regenerating presigned URL: {str(e)}"
        )


@app.post("/api/regenerate-attachment-url/{attachment_id}", response_model=PresignedUrlResponse, status_code=status.HTTP_200_OK)
async def regenerate_attachment_url(
    attachment_id: int,
    db: Session = Depends(get_db)
):
    """
    Regenerate presigned URL for an attachment by ID and update database
    
    - **attachment_id**: ID of the attachment in database
    
    Returns a new presigned URL and updates the attachment record in database
    """
    try:
        # Get attachment from database
        attachment = db.query(InflowEntryAttachment).filter(
            InflowEntryAttachment.id == attachment_id
        ).first()
        
        if not attachment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Attachment with id {attachment_id} not found"
            )
        
        if not attachment.file_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attachment has no file URL"
            )
        
        print(f"🔄 Regenerating presigned URL for attachment {attachment_id}: {attachment.file_url[:100]}...")
        
        # Regenerate presigned URL
        new_presigned_url = regenerate_presigned_url(attachment.file_url)
        
        if not new_presigned_url:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate presigned URL. Check if the file exists in Railway Storage."
            )
        
        # Update attachment with new URL
        attachment.file_url = new_presigned_url
        db.commit()
        db.refresh(attachment)
        
        return {
            "success": True,
            "message": f"Presigned URL regenerated and updated for attachment {attachment_id} (valid for 1 week)",
            "file_url": new_presigned_url,
            "expires_in_seconds": 604800  # 1 week
        }
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error regenerating attachment URL: {str(e)}"
        )


# List Inflow Entries with Filters

@app.get("/api/inflow-entries", response_model=List[InflowEntryPayloadResponse], status_code=status.HTTP_200_OK)
async def list_inflow_entries(
    company_id: Optional[int] = None,
    inflow_form_id: Optional[int] = None,
    mode: Optional[str] = None,  # mode from payload
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List inflow entries with optional filters
    
    - **company_id**: Filter by company ID (optional)
    - **inflow_form_id**: Filter by inflow form ID (optional)
    - **mode**: Filter by mode from payload JSON (optional, e.g., "BANK", "CASH", "UPI")
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    
    Returns list of inflow entries with their attachments
    """
    try:
        # Start with base query
        query = db.query(InflowEntryPayload)
        
        # Apply filters
        if company_id is not None:
            query = query.filter(InflowEntryPayload.company_id == company_id)
        
        if inflow_form_id is not None:
            query = query.filter(InflowEntryPayload.inflow_form_id == inflow_form_id)
        
        # Filter by mode in payload (JSON field)
        if mode:
            # MySQL JSON field query - check if payload contains mode
            # For MySQL, we need to use JSON_EXTRACT or cast to text
            # Try different approaches based on database type
            try:
                # Method 1: Direct JSON key access (works with SQLAlchemy JSON type)
                query = query.filter(
                    InflowEntryPayload.payload['mode'].astext == mode
                )
            except:
                # Method 2: Use JSON_EXTRACT for MySQL
                # This is a fallback if the above doesn't work
                from sqlalchemy import text
                query = query.filter(
                    text(f"JSON_EXTRACT(payload, '$.mode') = :mode")
                ).params(mode=mode)
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply pagination and ordering
        entries = query.order_by(InflowEntryPayload.created_at.desc()).offset(skip).limit(limit).all()
        
        # Get attachments for each entry
        result = []
        for entry in entries:
            # Get attachments for this entry
            attachments = db.query(InflowEntryAttachment).filter(
                InflowEntryAttachment.inflow_entry_id == entry.id
            ).all()
            
            # Build response
            entry_data = {
                "id": entry.id,
                "company_id": entry.company_id,
                "inflow_form_id": entry.inflow_form_id,
                "payload": entry.payload,
                "created_at": entry.created_at,
                "attachments": [
                    {
                        "id": att.id,
                        "inflow_entry_id": att.inflow_entry_id,
                        "file_url": att.file_url,
                        "created_at": att.created_at
                    }
                    for att in attachments
                ]
            }
            result.append(entry_data)
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching inflow entries: {str(e)}"
        )


# Alternative endpoint with JSON response including metadata

@app.get("/api/inflow-entries-with-meta")
async def list_inflow_entries_with_meta(
    company_id: Optional[int] = None,
    inflow_form_id: Optional[int] = None,
    mode: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List inflow entries with metadata (total count, pagination info)
    
    Same filters as /api/inflow-entries but includes pagination metadata
    """
    try:
        # Start with base query
        query = db.query(InflowEntryPayload)
        
        # Apply filters
        if company_id is not None:
            query = query.filter(InflowEntryPayload.company_id == company_id)
        
        if inflow_form_id is not None:
            query = query.filter(InflowEntryPayload.inflow_form_id == inflow_form_id)
        
        # Filter by mode in payload (JSON field)
        if mode:
            try:
                # Method 1: Direct JSON key access (works with SQLAlchemy JSON type)
                query = query.filter(
                    InflowEntryPayload.payload['mode'].astext == mode
                )
            except:
                # Method 2: Use JSON_EXTRACT for MySQL (fallback)
                from sqlalchemy import text
                query = query.filter(
                    text(f"JSON_EXTRACT(payload, '$.mode') = :mode")
                ).params(mode=mode)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination and ordering
        entries = query.order_by(InflowEntryPayload.created_at.desc()).offset(skip).limit(limit).all()
        
        # Get attachments for each entry
        entries_list = []
        for entry in entries:
            attachments = db.query(InflowEntryAttachment).filter(
                InflowEntryAttachment.inflow_entry_id == entry.id
            ).all()
            
            entries_list.append({
                "id": entry.id,
                "company_id": entry.company_id,
                "inflow_form_id": entry.inflow_form_id,
                "payload": entry.payload,
                "created_at": entry.created_at,
                "attachments": [
                    {
                        "id": att.id,
                        "inflow_entry_id": att.inflow_entry_id,
                        "file_url": att.file_url,
                        "created_at": att.created_at
                    }
                    for att in attachments
                ]
            })
        
        return {
            "success": True,
            "total": total_count,
            "skip": skip,
            "limit": limit,
            "data": entries_list
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching inflow entries: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
