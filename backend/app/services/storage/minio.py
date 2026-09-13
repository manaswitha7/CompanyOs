import boto3

from app.config import settings


s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
    region_name="us-east-1",
)


def create_bucket_if_not_exists():
    buckets = s3_client.list_buckets()["Buckets"]

    bucket_names = [
        bucket["Name"]
        for bucket in buckets
    ]

    if settings.S3_BUCKET not in bucket_names:
        s3_client.create_bucket(
            Bucket=settings.S3_BUCKET
        )


def upload_file(
    file_object,
    object_name: str,
    content_type: str | None = None,
):
    extra_args = {}

    if content_type:
        extra_args["ContentType"] = content_type

    s3_client.upload_fileobj(
        file_object,
        settings.S3_BUCKET,
        object_name,
        ExtraArgs=extra_args,
    )

    return object_name


def download_file(object_name: str):
    return s3_client.get_object(
        Bucket=settings.S3_BUCKET,
        Key=object_name,
    )


def delete_file(object_name: str):
    s3_client.delete_object(
        Bucket=settings.S3_BUCKET,
        Key=object_name,
    )
