import os
import sys

os.environ.update({
    "SUPERADMIN_LOGIN": "benchmark",
    "SUPERADMIN_PWD": "benchmark-only",
    "SUPERADMIN_ORG": "benchmark",
    "POSTGRES_URL": "postgresql+asyncpg://benchmark:benchmark-only@127.0.0.1:55435/benchmark",
    "S3_ACCESS_KEY": "benchmark",
    "S3_SECRET_KEY": "benchmark",
    "S3_REGION": "eu-west-3",
    "S3_ENDPOINT_URL": "http://127.0.0.1:5567",
    "S3_PROXY_URL": "",
    "JWT_SECRET": "benchmark-only",
    "SENTRY_DSN": "",
    "POSTHOG_KEY": "",
    "TEMPORAL_API_URL": "",
    "RISK_API_URL": "",
    "SLACK_HOOK": "",
})
sys.path.insert(0, os.path.join(sys.argv[1], "src"))
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT_URL"],
    aws_access_key_id="benchmark",
    aws_secret_access_key="benchmark",
    region_name="eu-west-3",
)
try:
    s3.head_bucket(Bucket="admin")
except ClientError:
    s3.create_bucket(Bucket="admin", CreateBucketConfiguration={"LocationConstraint": "eu-west-3"})
import pytest

raise SystemExit(
    pytest.main([os.path.join(sys.argv[1], "src/tests") if len(sys.argv) == 2 else sys.argv[2], "-q", "--tb=short"])
)
