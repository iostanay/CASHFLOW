import firebase_admin
from firebase_admin import credentials, storage
import os
from typing import Optional
import uuid
from datetime import datetime

# Initialize Firebase Admin SDK
FIREBASE_CREDENTIALS_PATH = os.getenv(
    "FIREBASE_CREDENTIALS_PATH",
    os.path.join(os.path.dirname(__file__), "firebase-credentials.json")
)

# Initialize Firebase Admin (only if not already initialized)
if not firebase_admin._apps:
    if os.path.exists(FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'cashflow-9b16c.appspot.com'
        })
    else:
        raise FileNotFoundError(f"Firebase credentials file not found at: {FIREBASE_CREDENTIALS_PATH}")


def upload_file_to_firebase(file_content: bytes, file_name: str, folder: str = "bank_loan_receipts") -> Optional[str]:
    """
    Upload a file to Firebase Storage
    
    Args:
        file_content: Bytes content of the file
        file_name: Original file name
        folder: Folder path in Firebase Storage
        
    Returns:
        Public URL of the uploaded file or None if upload fails
    """
    try:
        # Generate unique filename with timestamp and UUID
        file_extension = os.path.splitext(file_name)[1]
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
        
        # Create storage path
        storage_path = f"{folder}/{unique_filename}"
        
        # Get bucket reference
        bucket = storage.bucket()
        
        # Create blob and upload
        blob = bucket.blob(storage_path)
        blob.upload_from_string(file_content, content_type='application/octet-stream')
        
        # Make the file publicly accessible (optional, or use signed URLs)
        blob.make_public()
        
        # Return public URL
        return blob.public_url
    except Exception as e:
        print(f"Error uploading file to Firebase: {str(e)}")
        return None


def delete_file_from_firebase(file_url: str) -> bool:
    """
    Delete a file from Firebase Storage using its URL
    
    Args:
        file_url: Public URL of the file
        
    Returns:
        True if deletion successful, False otherwise
    """
    try:
        # Extract blob name from URL
        bucket = storage.bucket()
        
        # Parse URL to get blob path
        # Format: https://storage.googleapis.com/bucket-name/path/to/file
        if "storage.googleapis.com" in file_url:
            blob_path = file_url.split("/o/")[-1].split("?")[0] if "/o/" in file_url else file_url.split(bucket.name + "/")[-1].split("?")[0]
        else:
            # Try to extract from different URL formats
            blob_path = file_url.split(f"{bucket.name}/")[-1].split("?")[0] if bucket.name in file_url else None
        
        if blob_path:
            blob = bucket.blob(blob_path)
            blob.delete()
            return True
        return False
    except Exception as e:
        print(f"Error deleting file from Firebase: {str(e)}")
        return False
