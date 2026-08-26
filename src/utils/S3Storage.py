import uuid
from typing import Optional

import aioboto3
from botocore.exceptions import ClientError
from fastapi import UploadFile


class S3Storage:
    def __init__(self, endpoint_url: str, access_key: str, secret_key: str, bucket_name: str, region_name: Optional[str] = None):
        self._session = aioboto3.Session()

        self.endpoint_url = endpoint_url
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket_name = bucket_name
        self.region_name = region_name

    async def _create_bucket(self):
        async with self._session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name
        ) as s3_client:
            try:
                await s3_client.create_bucket(Bucket=self.bucket_name)
            except ClientError as e:
                if not e.response["Error"]["Code"] in ("BucketAlreadyOwnedByYou", "BucketAlreadyExists"):
                    raise e

    async def connect(self):
        await self._create_bucket()

    async def upload_order_photo(self, order_id: uuid.UUID, file: UploadFile) -> str:
        ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else "jpg"
        key = f"orders/{order_id}/{uuid.uuid4()}.{ext}"

        async with self._session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name
        ) as s3_client:
            await s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=await file.read(),
                ContentType=file.content_type
            )

        return key

    async def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for downloading a photo."""
        async with self._session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name
        ) as s3_client:
            return await s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expires_in
            )

    async def delete_order_photo(self, key: str) -> None:
        """Delete a photo from storage."""
        async with self._session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region_name
        ) as s3_client:
            await s3_client.delete_object(Bucket=self.bucket_name, Key=key)