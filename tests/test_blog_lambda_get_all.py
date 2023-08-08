import json
from src import blog_controller
from src import blog_handler
from tests.helper import event, extract_body, extract_status_code, lambda_response, DEFAULT_TENANT_ID


def test_get_blog_items_ok(lambda_context, dynamodb_table):
    item1 = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    item2 = {
        'betreff': "Test2",
        "nachricht": "Eine Testnachricht",
        "introtext": "Eine Einleitung",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    blog_controller.create_blog_item(DEFAULT_TENANT_ID, item1)
    blog_controller.create_blog_item(DEFAULT_TENANT_ID, item2)

    response = blog_handler.handle(
        event('/api/blog', 'GET'), lambda_context)
    body = extract_body(response)

    assert extract_status_code(response) == 200
    assert len(body) == 2


def test_get_blog_items_with_stichtag_ok(lambda_context, dynamodb_table):
    item1 = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    item2 = {
        'betreff': "Test2",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2023-01-01",
        "gueltigBis": "2023-02-01"
    }
    blog_controller.create_blog_item(DEFAULT_TENANT_ID, item1)
    item2023 = blog_controller.create_blog_item(DEFAULT_TENANT_ID, item2)

    response = blog_handler.handle(
        event('/api/blog', 'GET', queryParameters={"stichtag": "2023-01-25"}), lambda_context)
    body = extract_body(response)

    assert extract_status_code(response) == 200
    assert len(body) == 1
    assert json.dumps(body[0]) == item2023.to_json()


def test_get_blog_items_with_count_ok(lambda_context, dynamodb_table):
    item1 = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    item2 = {
        'betreff': "Test2",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2023-01-01",
        "gueltigBis": "2023-02-01"
    }
    item3 = {
        'betreff': "Test3",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2024-01-01",
        "gueltigBis": "2024-02-01"
    }
    blog_controller.create_blog_item(DEFAULT_TENANT_ID, item1)
    item2023 = blog_controller.create_blog_item(DEFAULT_TENANT_ID, item2)
    item2024 = blog_controller.create_blog_item(DEFAULT_TENANT_ID, item3)

    response = blog_handler.handle(
        event('/api/blog', 'GET', queryParameters={"count": 2}), lambda_context)
    body = extract_body(response)

    assert extract_status_code(response) == 200
    assert len(body) == 2
    assert json.dumps(body[0]) == item2024.to_json()
    assert json.dumps(body[1]) == item2023.to_json()


def test_get_blog_items_empty_ok(lambda_context, dynamodb_table):
    response = blog_handler.handle(
        event('/api/blog', 'GET'), lambda_context)
    body = extract_body(response)

    assert extract_status_code(response) == 200
    assert len(body) == 0


def test_get_blog_items_without_tenant_id_not_ok(lambda_context, dynamodb_table):
    headers = {
        'Content-Type': 'application/json'
    }
    response = blog_handler.handle(
        event('/api/blog', 'GET', None, None, headers), lambda_context)

    assert response == lambda_response(400, json.dumps(
        {'error_text': 'tenant not present.'}))


def test_get_blog_items_with_count_ok(lambda_context, dynamodb_table):
    item1 = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    item2 = {
        'betreff': "Test2",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2023-01-01",
        "gueltigBis": "2023-02-01"
    }
    blog_controller.create_blog_item(DEFAULT_TENANT_ID, item1)
    item2023 = blog_controller.create_blog_item(DEFAULT_TENANT_ID, item2)

    response = blog_handler.handle(
        event('/api/blog', 'GET', queryParameters={"count": "1"}), lambda_context)
    body = extract_body(response)

    assert extract_status_code(response) == 200
    assert len(body) == 1
    assert json.dumps(body[0]) == item2023.to_json()
