import json
from src import blog_controller
from src import blog_handler
from tests.helper import event, lambda_response, DEFAULT_TENANT_ID


def test_get_blog_item_not_found(lambda_context, dynamodb_table):
    pathParameters = {
        "id": "unknown_id"
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'GET', None, pathParameters), lambda_context)

    assert response == lambda_response(404)


def test_get_blog_item_ok(lambda_context, dynamodb_table):
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    createdblog_item = blog_controller.create_blog_item(
        DEFAULT_TENANT_ID, item)

    pathParameters = {
        "id": createdblog_item.id
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'GET', None, pathParameters), lambda_context)

    assert response == lambda_response(200, createdblog_item.to_json())


def test_get_blog_item_with_introtext_ok(lambda_context, dynamodb_table):
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "introtext": "Eine Einleitung",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    createdblog_item = blog_controller.create_blog_item(
        DEFAULT_TENANT_ID, item)

    pathParameters = {
        "id": createdblog_item.id
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'GET', None, pathParameters), lambda_context)

    assert response == lambda_response(200, createdblog_item.to_json())

def test_get_blog_item_without_tenant_id_not_ok(lambda_context, dynamodb_table):
    headers = {
        'Content-Type': 'application/json'
    }
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    createdblog_item = blog_controller.create_blog_item(
        DEFAULT_TENANT_ID, item)

    pathParameters = {
        "id": createdblog_item.id
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'GET', None, pathParameters, headers), lambda_context)

    assert response == lambda_response(400, json.dumps(
        {'error_text': 'tenant not present.'}))
