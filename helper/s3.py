import boto3
from botocore.exceptions import NoCredentialsError
from botocore.client import Config
from dotenv import load_dotenv
import os

load_dotenv()

S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET_ACCESS_KEY = os.getenv("S3_SECRET_ACCESS_KEY")
S3_BUCKET_REGION = os.getenv("S3_BUCKET_REGION")

def get_s3_client():
    return boto3.client(
        's3',
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY,
        region_name=S3_BUCKET_REGION,
        config=Config(signature_version='s3v4')
    )

def get_recon_image_from_s3(key, expiry=3600):
    try:
        s3_client = get_s3_client()
        bucket_name = "reconimages"
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': key},
            ExpiresIn=expiry
        )
        return url
    except NoCredentialsError:
        print("Credentials not available")
        return None
