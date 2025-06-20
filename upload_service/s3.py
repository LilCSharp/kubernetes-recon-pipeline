import boto3
import os

s3 = boto3.client("s3", endpoint_url=os.getenv("S3_ENDPOINT"))

def upload_to_s3(content: bytes, key: str, bucket: str):
    s3.put_object(Bucket=bucket, Key=key, Body=content)

def s3_object_exists(bucket: str, key: str) -> bool:
    try:
        s3.head_object(Bucket=bucket, Key=key)
        return True
    except s3.exceptions.ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
            return False
        raise
