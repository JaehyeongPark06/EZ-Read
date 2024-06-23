import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from dotenv import load_dotenv
import os

s3_client = boto3.client("s3")
load_dotenv()
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")


def generate_presigned_url(s3_key: str, expiration: int = 3600) -> str:
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": S3_BUCKET_NAME, "Key": s3_key},
            ExpiresIn=expiration,
        )
    except NoCredentialsError:
        print("Credentials not available")
        return None
    except PartialCredentialsError:
        print("Incomplete credentials")
        return None

    return response
