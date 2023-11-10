import os

import boto3


def create_s3_client(
    aws_access_key_id: str, aws_secret_access_key: str
) -> boto3.client:
    client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    return client


def create_polly_client(
    aws_access_key_id: str, aws_secret_access_key: str, region_name: str
) -> boto3.client:
    client = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name,
    ).client("polly")
    return client


def upload_to_aws(
    s3_client: boto3.client, local_file_path: str, bucket_name: str, s3_file_name: str
):
    try:
        s3_client.upload_file(local_file_path, bucket_name, s3_file_name)
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False


def generate_presigned_url(
    s3_client: str,
    object_name: str,
    bucket_name: str,
    expires_in=86400,  # 24 hours
) -> str:
    """expires_in is in seconds"""
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": object_name},
        ExpiresIn=expires_in,
    )
    return url
