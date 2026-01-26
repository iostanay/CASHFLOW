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
    "us-east-1"  # Railway Storage typically uses us-east-1
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
    "tsec_PzM+nJh6gE1nmSyIvQk77iHnnBRd7iXzc5-zxLddRvfEgf96VDUB6tjYCScHyhkSHAbux1"
)

# Initialize S3 client for Railway Storage
_railway_s3_client = None
_railway_init_error = None
if BOTO3_AVAILABLE:
    try:
        # Configure S3 client for Railway Storage
        # Railway Storage uses S3-compatible API
        # Use path-style addressing and s3v4 signature
        config = Config(
            signature_version='s3v4',
            s3={
                'addressing_style': 'path'
            }
        )
        
        # Create client - Railway Storage S3-compatible API
        # Note: Make sure credentials don't have extra whitespace
        access_key = RAILWAY_ACCESS_KEY_ID.strip()
        secret_key = RAILWAY_SECRET_ACCESS_KEY.strip()
        
        # Debug: Print first/last chars of keys (for verification, not full keys)
        print(f"Initializing Railway Storage client...")
        print(f"  Access Key ID: {access_key[:10]}...{access_key[-10:]}")
        print(f"  Secret Key: {secret_key[:10]}...{secret_key[-10:]}")
        
        _railway_s3_client = boto3.client(
            's3',
            endpoint_url=RAILWAY_STORAGE_ENDPOINT,
            region_name=RAILWAY_STORAGE_REGION,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
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
        # Try to upload with public-read ACL first
        acl_success = False
        try:
            _railway_s3_client.put_object(
                Bucket=RAILWAY_STORAGE_BUCKET,
                Key=storage_path,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'  # Try with ACL first
            )
            acl_success = True
            print(f"✓ File uploaded with public-read ACL")
        except ClientError as acl_error:
            # If ACL fails, try without ACL
            error_code = acl_error.response.get('Error', {}).get('Code', '')
            if error_code in ['InvalidArgument', 'NotImplemented', 'AccessDenied', 'AccessControlListNotSupported']:
                print(f"ACL not supported in put_object, uploading without ACL: {str(acl_error)}")
                _railway_s3_client.put_object(
                    Bucket=RAILWAY_STORAGE_BUCKET,
                    Key=storage_path,
                    Body=file_content,
                    ContentType=content_type
                )
                # Try to set ACL after upload
                try:
                    _railway_s3_client.put_object_acl(
                        Bucket=RAILWAY_STORAGE_BUCKET,
                        Key=storage_path,
                        ACL='public-read'
                    )
                    acl_success = True
                    print(f"✓ File uploaded and ACL set to public-read after upload")
                except ClientError as acl_error2:
                    print(f"⚠ Could not set ACL to public-read: {str(acl_error2)}")
                    # Continue - will generate presigned URL instead
            else:
                raise
        
        # Verify the upload was successful by checking if object exists
        try:
            _railway_s3_client.head_object(Bucket=RAILWAY_STORAGE_BUCKET, Key=storage_path)
            print(f"✓ File verified in Railway Storage")
        except ClientError as verify_error:
            print(f"Warning: Upload completed but verification failed: {str(verify_error)}")
            # Still return URL as upload might have succeeded
        
        # Construct URL - Railway Storage requires presigned URLs for access
        encoded_path = quote(storage_path, safe='/')
        
        # Generate presigned URL for reliable access (valid for 1 year)
        # Railway Storage buckets are private by default, presigned URLs are required
        print(f"🔍 Generating presigned URL for: {storage_path}")
        try:
            # Generate presigned URL - this is the ONLY way to access files in private Railway Storage buckets
            # Railway Storage limit: presigned URLs can only be valid for max 1 week (604800 seconds)
            presigned_url = _railway_s3_client.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': RAILWAY_STORAGE_BUCKET,
                    'Key': storage_path
                },
                ExpiresIn=604800  # 1 week (604800 seconds = 7 days) - Railway Storage maximum
            )
            
            if presigned_url and len(presigned_url) > 0 and presigned_url.startswith('http'):
                print(f"✓ Successfully generated presigned URL (valid for 1 week - Railway Storage maximum)")
                print(f"  URL preview: {presigned_url[:80]}...")
                return presigned_url
            else:
                raise Exception(f"Invalid presigned URL format: {presigned_url[:50] if presigned_url else 'None'}")
                
        except ClientError as presign_error:
            error_code = presign_error.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = presign_error.response.get('Error', {}).get('Message', str(presign_error))
            print(f"✗ Failed to generate presigned URL")
            print(f"  Error Code: {error_code}")
            print(f"  Error Message: {error_msg}")
            print(f"  Full error: {presign_error}")
            # Don't fallback to public URL - it won't work
            raise Exception(f"Cannot generate accessible URL. Railway Storage error [{error_code}]: {error_msg}. Presigned URLs are required for private buckets.")
            
        except Exception as presign_error:
            print(f"✗ Unexpected error generating presigned URL: {str(presign_error)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Failed to generate presigned URL: {str(presign_error)}")
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
