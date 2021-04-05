from loguru import logger
import watchtower
import argh
import socket
import boto3
from botocore.exceptions import ClientError


logger.add(
    watchtower.CloudWatchLogHandler(
        log_group="/hatchutils/s3_security", stream_name=socket.gethostname()
    )
)


def fix_public(client=None, bucket_name=None):
    client.put_public_access_block(
        Bucket=bucket_name,
        PublicAccessBlockConfiguration={
            "BlockPublicAcls": True,
            "IgnorePublicAcls": True,
            "BlockPublicPolicy": True,
            "RestrictPublicBuckets": True,
        },
    )


def set_cost_tag(client, bucket_name):
    client.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={
            "TagSet": [
                {
                    "Key": "S3-Bucket-Name",
                    "Value": bucket_name,
                },
            ],
        },
    )


def main(fix_public=False, fix_tags=False):
    s3_client = boto3.client("s3")
    logger.debug("Fixing yo buckets")
    all_buckets = s3_client.list_buckets()
    for bucket in all_buckets["Buckets"]:
        try:
            logger.debug(f'Fixing: {bucket["Name"]}')
            if fix_public:
                logger.debug(f'Removing public access on: {bucket["Name"]}')
                fix_public(client=s3_client, bucket_name=bucket["Name"])
            elif fix_tags:
                logger.debug(f'Fixing Cost Tracking Tags on: {bucket["Name"]}')
                set_cost_tag(client=s3_client, bucket_name=bucket["Name"])
            # fix_public(client=s3_client, bucket_name=bucket["Name"])
            # set_cost_tag(client=s3_client, bucket_name=bucket["Name"])
        except ClientError:
            logger.debug(f'  {bucket["Name"]}: failed')


if __name__ == "__main__":
    argh.dispatch_command(main)
