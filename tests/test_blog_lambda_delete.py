import json
from src import blog_controller
from src import blog_handler
from tests.helper import event, lambda_response, DEFAULT_TENANT_ID


def test_delete_blog_item_ok(lambda_context, dynamodb_table):
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    createdblog_item = blog_controller.create_blog_item(
        DEFAULT_TENANT_ID, item)

    blog_items = blog_controller.get_blog_items(DEFAULT_TENANT_ID)
    assert len(blog_items) == 1

    pathParameters = {
        "id": createdblog_item.id
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'DELETE', None, pathParameters), lambda_context)
    
    assert response == lambda_response(204)
    blog_items = blog_controller.get_blog_items(DEFAULT_TENANT_ID)
    assert len(blog_items) == 0


def test_delete_blog_item_not_ok(lambda_context, dynamodb_table):
    pathParameters = {
        "id": "abc123"
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'DELETE', None, pathParameters), lambda_context)
   
    assert response == lambda_response(404)


def test_delete_blog_item_without_tenant_id_not_ok(lambda_context, dynamodb_table):
    pathParameters = {
        "id": "abc123"
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'DELETE', None, pathParameters, headers), lambda_context)
    
    assert response == lambda_response(400, json.dumps(
        {'error_text': 'tenant not present.'}))
