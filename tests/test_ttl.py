import json
import os
from src import dynamo_db_service
from src import blog_handler
from tests.helper import event, extract_id, DEFAULT_TENANT_ID


def test_ttl_in_dynamobo_active(lambda_context, dynamodb_table):
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    response = blog_handler.handle(
        event('/api/blog', 'POST', json.dumps(item)), lambda_context)
    id = extract_id(response)
    item = dynamo_db_service.get_blog_item(DEFAULT_TENANT_ID, id)

    assert item['ttl'] == 1644278400


def test_ttl_in_dynamobo_inactive(lambda_context, dynamodb_table):
    os.environ['TTL_FEATURE_ACTIVE'] = '0'
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    response = blog_handler.handle(
        event('/api/blog', 'POST', json.dumps(item)), lambda_context)
    id = extract_id(response)
    item = dynamo_db_service.get_blog_item(DEFAULT_TENANT_ID, id)

    assert item['ttl'] is None
