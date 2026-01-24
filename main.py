from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from database import get_db, engine
from models import (
    Base, CustomerReceipt, BankLoanReceipt, VendorPayment, EmployeePayment,
    InflowReceiptMaster, Company, CompanyBankAccount,
    InflowForm, InflowFormField,
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
)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
