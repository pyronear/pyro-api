import logging
import boto3
# from botocore.config import  Config
from app.services.bucket.baseBucketService import BaseBucketService
from botocore.exceptions import ClientError


ACCESS_KEY = "ACCESS_KEY"
SECRET_KEY = "SECRET_KEY"


class S3Service(BaseBucketService):
    def __init__(self):
        self.s3_client = boto3.client('s3',
                                      aws_access_key_id=ACCESS_KEY,
                                      aws_secret_access_key=SECRET_KEY)

    async def create_bucket(self, bucket_name, region=None):
        """Create an S3 bucket in a specified region

        If a region is not specified, the bucket is created in the S3 default
        region (us-east-1).

        :param bucket_name: Bucket to create
        :param region: String region to create bucket in, e.g., 'us-west-2'
        :return: True if bucket created, else False
        """

        # Create bucket
        try:
            if region is None:
                self.s3_client.create_bucket(Bucket=bucket_name)
            else:
                location = {'LocationConstraint': region}
                self.s3_client.create_bucket(Bucket=bucket_name,
                                             CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False
        return True

    async def upload_file(self, bucket_name: str, bucket_key: str, file_binary: bin):
        """Upload a file to an S3 bucket

        :param file_name: File to upload
        :param bucket: Bucket to upload to
        :param object_name: S3 object name. If not specified then file_name is used
        :return: True if file was uploaded, else False
        """

        # Upload the file
        try:
            self.s3_client.upload_fileobj(file_binary, bucket_name, bucket_key)

        except ClientError as e:
            logging.error(e)
            return False
        return True

    async def get_uploaded_file(self, bucket_name: str, object_name: str, target_location: str):
        with open(target_location, 'wb') as f:
            self.s3_client.download_fileobj(bucket_name, object_name, f)

    async def fetch_buckets(self):
        # Retrieve the list of existing buckets
        response = self.s3_client.list_buckets()

        # Output the bucket names
        print('Existing buckets:')
        for bucket in response['Buckets']:
            print(f'  {bucket["Name"]}')

    async def fetch_bucket_files(self, bucket_name: str):
        pass
