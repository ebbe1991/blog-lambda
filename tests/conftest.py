import os

import boto3
import pytest
from moto import mock_dynamodb

os.environ['BLOG_TABLE_NAME'] = 'BLOG_TABLE'
os.environ['AWS_DEFAULT_REGION'] = 'eu-central-1'


@pytest.fixture(name='lambda_context')
def lambda_context():
    return None


@pytest.fixture(scope='session')
def dynamodb():
    with mock_dynamodb():
        yield boto3.resource('dynamodb')


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
