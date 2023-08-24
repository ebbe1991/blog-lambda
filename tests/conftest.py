import os

import boto3
import pytest
from moto import mock_dynamodb, mock_s3

os.environ['BLOG_TABLE_NAME'] = 'BLOG_TABLE'
os.environ['AWS_DEFAULT_REGION'] = 'us-east-1'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['BLOG_S3_BUCKET'] = 'my-test-bucket'


@pytest.fixture(name='lambda_context')
def lambda_context():
    return None


@pytest.fixture(scope='session')
def dynamodb():
    with mock_dynamodb():
        yield boto3.resource('dynamodb')


@mock_s3
@pytest.fixture(scope='function')
def s3_bucket():
    bucket = os.getenv('BLOG_S3_BUCKET')
    conn = boto3.resource("s3", region_name="us-east-1",
                          aws_access_key_id='YOUR_ACCESS_KEY',
                          aws_secret_access_key='YOUR_SECRET_KEY')
    conn.create_bucket(Bucket=bucket)


@pytest.fixture(scope='function')
def dynamodb_table(dynamodb):
    table_name = os.getenv('BLOG_TABLE_NAME')
    table = dynamodb.create_table(
        TableName=table_name,
        BillingMode='PAY_PER_REQUEST',
        KeySchema=[
            {
                'AttributeName': 'tenant-id',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'id',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'tenant-id',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'id',
                'AttributeType': 'S'
            }
        ]
    )
    table.wait_until_exists()
    yield table
    table.delete()
