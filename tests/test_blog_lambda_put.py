import json
from datetime import date
from src import blog_handler
from src import blog_controller
from blog_dto import BlogDTO
from tests.helper import event, lambda_response, DEFAULT_TENANT_ID


def test_update_blog_item_ok(lambda_context, dynamodb_table):
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    createdblog_item = blog_controller.create_blog_item(
        DEFAULT_TENANT_ID, item
    )

    pathParameters = {
        "id": createdblog_item.id
    }
    itemUpdate = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht (aktualisiert)",
        "introtext": "Eine Einleitung (aktualisiert)",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'PUT', json.dumps(itemUpdate), pathParameters), lambda_context)

    assert response == lambda_response(200, BlogDTO(
        "Test", "Eine Testnachricht (aktualisiert)", "Eine Einleitung (aktualisiert)", date.fromisoformat("2022-01-01"), date.fromisoformat("2022-02-01"), createdblog_item.id).to_json())


def test_update_blog_item_required_field_to_null_not_ok(lambda_context, dynamodb_table):
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    createdblog_item = blog_controller.create_blog_item(
        DEFAULT_TENANT_ID, item
    )

    pathParameters = {
        "id": createdblog_item.id
    }
    itemUpdate = {
        'betreff': "",
        "nachricht": "Eine Testnachricht (aktualisiert)",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'PUT', json.dumps(itemUpdate), pathParameters), lambda_context)

    assert response == lambda_response(
        400, json.dumps({'error_text': "'betreff' not present."}))


def test_update_blog_item_with_unknown_id_not_ok(lambda_context, dynamodb_table):
    pathParameters = {
        "id": 'unknown'
    }
    itemUpdate = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht (aktualisiert)",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'PUT', json.dumps(itemUpdate), pathParameters), lambda_context)

    assert response == lambda_response(
        400, json.dumps({'error_text': "unknown id 'unknown' (tenant='mytenant1')."}))


def test_update_blog_item_set_null_value(lambda_context, dynamodb_table):
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

    itemUpdate = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht (aktualisiert)",
        "gueltigVon": "2022-01-01"
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'PUT', json.dumps(itemUpdate), pathParameters), lambda_context)

    assert response == lambda_response(200, BlogDTO(
        "Test", "Eine Testnachricht (aktualisiert)", None, date.fromisoformat("2022-01-01"), None, createdblog_item.id).to_json())


def test_update_blog_item_without_body_not_ok(lambda_context, dynamodb_table):
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

    response = blog_handler.handle(
        event('/api/blog/{id}', 'PUT', None, pathParameters), lambda_context)

    assert response == lambda_response(400, json.dumps(
        {'error_text': 'body not present.'}))


def test_update_blog_item_without_tenant_id_not_ok(lambda_context, dynamodb_table):
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
    itemUpdate = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht (aktualisiert)",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    response = blog_handler.handle(event(
        '/api/blog/{id}', 'PUT', json.dumps(itemUpdate), pathParameters, headers), lambda_context)

    assert response == lambda_response(400, json.dumps(
        {'error_text': 'tenant not present.'}))
