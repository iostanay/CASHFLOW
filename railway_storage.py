import os
from typing import Optional
import uuid
from datetime import datetime
from urllib.parse import quote

# Optional boto3 imports - handle gracefully if not installed
try:
    import boto3
    from botocore.client import Config
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    Config = None
    print("Warning: boto3 not installed. Railway Storage uploads will be disabled.")

# Railway Storage Configuration
RAILWAY_STORAGE_ENDPOINT = os.getenv(
    "RAILWAY_STORAGE_ENDPOINT",
    "https://storage.railway.app"
)
RAILWAY_STORAGE_REGION = os.getenv(
    "RAILWAY_STORAGE_REGION",
    "auto"
)
RAILWAY_STORAGE_BUCKET = os.getenv(
    "RAILWAY_STORAGE_BUCKET",
    "finance-8wy8egnq1digq7hgk"
)
RAILWAY_ACCESS_KEY_ID = os.getenv(
    "RAILWAY_ACCESS_KEY_ID",
    "tid_epYeZVjDSJTkAjLhVLfyCRkSONPrbKoE_f_AvSNa_qXTN__kSt"
)
RAILWAY_SECRET_ACCESS_KEY = os.getenv(
    "RAILWAY_SECRET_ACCESS_KEY",
    "tsec_PzM+nJh6gE1nmSyIvQk77iHnnBRd7iXzc5-zxLddRvfEgf96VDUB6tjYCScHyhkSHAbux1--"
)

# Initialize S3 client for Railway Storage
_railway_s3_client = None
_railway_init_error = None
if BOTO3_AVAILABLE:
    try:
        # Configure S3 client for Railway Storage
        config = Config(
            signature_version='s3v4',
            s3={
                'addressing_style': 'path'
            }
        )
        _railway_s3_client = boto3.client(
            's3',
            endpoint_url=RAILWAY_STORAGE_ENDPOINT,
            region_name=RAILWAY_STORAGE_REGION,
            aws_access_key_id=RAILWAY_ACCESS_KEY_ID,
            aws_secret_access_key=RAILWAY_SECRET_ACCESS_KEY,
            config=config
        )
        # Test connection by listing buckets (optional check)
        print(f"Railway Storage S3 client initialized successfully")
        print(f"  Endpoint: {RAILWAY_STORAGE_ENDPOINT}")
        print(f"  Bucket: {RAILWAY_STORAGE_BUCKET}")
        print(f"  Region: {RAILWAY_STORAGE_REGION}")
    except Exception as e:
        _railway_init_error = str(e)
        print(f"Warning: Railway Storage initialization failed: {str(e)}. File uploads will be disabled.")
        _railway_s3_client = None
else:
    _railway_init_error = "boto3 is not installed"


def upload_file_to_railway(file_content: bytes, file_name: str, folder: str = "attachments") -> Optional[str]:
    """
    Upload a file to Railway Storage
    
    Args:
        file_content: Bytes content of the file
        file_name: Original file name
        folder: Folder path in Railway Storage bucket
        
    Returns:
        Public URL of the uploaded file or None if upload fails
    """
    if not BOTO3_AVAILABLE:
        error_msg = "boto3 is not installed. Please install it using: pip install boto3"
        print(f"Error: {error_msg}")
        raise Exception(error_msg)
    
    if not _railway_s3_client:
        error_msg = f"Railway Storage S3 client not initialized. {_railway_init_error or 'Check your credentials and configuration.'}"
        print(f"Error: {error_msg}")
        raise Exception(error_msg)
    
    try:
        # Generate unique filename with timestamp and UUID
        file_extension = os.path.splitext(file_name)[1]
        unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}{file_extension}"
        
        # Create storage path
        storage_path = f"{folder}/{unique_filename}" if folder else unique_filename
        
        # Determine content type based on file extension
        content_type = 'application/octet-stream'
        if file_extension.lower() in ['.jpg', '.jpeg']:
            content_type = 'image/jpeg'
        elif file_extension.lower() == '.png':
            content_type = 'image/png'
        elif file_extension.lower() == '.pdf':
            content_type = 'application/pdf'
        elif file_extension.lower() in ['.doc', '.docx']:
            content_type = 'application/msword'
        elif file_extension.lower() == '.txt':
            content_type = 'text/plain'
        
        # Upload file to Railway Storage
        # Note: Railway Storage might not support ACL, so we'll try without it first
        try:
            _railway_s3_client.put_object(
                Bucket=RAILWAY_STORAGE_BUCKET,
                Key=storage_path,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'  # Try with ACL first
            )
        except ClientError as acl_error:
            # If ACL fails, try without ACL (Railway Storage might handle public access differently)
            error_code = acl_error.response.get('Error', {}).get('Code', '')
            if error_code in ['InvalidArgument', 'NotImplemented', 'AccessDenied']:
                print(f"ACL not supported, trying without ACL: {str(acl_error)}")
                _railway_s3_client.put_object(
                    Bucket=RAILWAY_STORAGE_BUCKET,
                    Key=storage_path,
                    Body=file_content,
                    ContentType=content_type
                )
            else:
                raise
        
        # Construct public URL
        # Railway Storage public URL format: https://storage.railway.app/bucket-name/path/to/file
        # URL encode the storage path to handle special characters
        encoded_path = quote(storage_path, safe='/')
        public_url = f"{RAILWAY_STORAGE_ENDPOINT}/{RAILWAY_STORAGE_BUCKET}/{encoded_path}"
        
        # Verify the upload was successful by checking if object exists
        try:
            _railway_s3_client.head_object(Bucket=RAILWAY_STORAGE_BUCKET, Key=storage_path)
        except ClientError as verify_error:
            print(f"Warning: Upload completed but verification failed: {str(verify_error)}")
            # Still return URL as upload might have succeeded
        
        return public_url
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        error_message = e.response.get('Error', {}).get('Message', str(e))
        error_detail = f"Railway Storage ClientError [{error_code}]: {error_message}"
        print(f"Error uploading file to Railway Storage: {error_detail}")
        raise Exception(error_detail) from e
    except Exception as e:
        error_detail = f"Unexpected error uploading file to Railway Storage: {str(e)}"
        print(f"Error: {error_detail}")
        raise Exception(error_detail) from e


def delete_file_from_railway(file_url: str) -> bool:
    """
    Delete a file from Railway Storage using its URL
    
    Args:
        file_url: Public URL of the file
        
    Returns:
        True if deletion successful, False otherwise
    """
    if not _railway_s3_client:
        print("Warning: Railway Storage not initialized. Cannot delete file.")
        return False
    
    try:
        # Extract key from URL
        # Format: https://storage.railway.app/bucket-name/path/to/file
        if RAILWAY_STORAGE_ENDPOINT in file_url and RAILWAY_STORAGE_BUCKET in file_url:
            # Remove endpoint and bucket from URL to get the key
            key = file_url.replace(f"{RAILWAY_STORAGE_ENDPOINT}/{RAILWAY_STORAGE_BUCKET}/", "")
            
            # Delete object
            _railway_s3_client.delete_object(
                Bucket=RAILWAY_STORAGE_BUCKET,
                Key=key
            )
            return True
        return False
    except ClientError as e:
        print(f"Error deleting file from Railway Storage: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error deleting file from Railway Storage: {str(e)}")
        return False
