import json
from datetime import date
from src import blog_handler
from blog_dto import BlogDTO
from tests.helper import event, lambda_response, extract_id


def test_create_blog_item_ok(lambda_context, dynamodb_table):
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    response = blog_handler.handle(
        event('/api/blog', 'POST', json.dumps(item)), lambda_context)

    id = extract_id(response)

    assert id is not None
    assert response == lambda_response(201, BlogDTO(
        "Test", "Eine Testnachricht", None, date.fromisoformat("2022-01-01"), date.fromisoformat("2022-02-01"), id).to_json())


def test_create_blog_item_invalid_dateformat_bad_request(lambda_context, dynamodb_table):
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022.01-01",
        "gueltigBis": "2022-02-01"
    }
    response = blog_handler.handle(
        event('/api/blog', 'POST', json.dumps(item)), lambda_context)

    assert response == lambda_response(400, json.dumps(
        {'error_text': "Invalid isoformat string: '2022.01-01'"}))


def test_create_blog_item_missing_field_betreff_bad_request(lambda_context, dynamodb_table):
    item = {
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    response = blog_handler.handle(
        event('/api/blog', 'POST', json.dumps(item)), lambda_context)

    assert response == lambda_response(
        400, json.dumps({'error_text': "'betreff' not present."}))


def test_create_blog_item_missing_field_nachricht_bad_request(lambda_context, dynamodb_table):
    item = {
        "betreff": "Ein Betreff",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    response = blog_handler.handle(
        event('/api/blog', 'POST', json.dumps(item)), lambda_context)

    assert response == lambda_response(400, json.dumps(
        {'error_text': "'nachricht' not present."}))


def test_create_blog_item_without_optional_parameters_ok(lambda_context, dynamodb_table):
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht"
    }
    response = blog_handler.handle(
        event('/api/blog', 'POST', json.dumps(item)), lambda_context)
    id = extract_id(response)

    assert id is not None
    assert response == lambda_response(201, BlogDTO(
        "Test", "Eine Testnachricht", None, None, None, id).to_json())



def test_create_blog_item_without_body_not_ok(lambda_context, dynamodb_table):
    response = blog_handler.handle(
        event('/api/blog', 'POST'), lambda_context)

    assert response == lambda_response(400, json.dumps(
        {'error_text': 'body not present.'}))

def test_create_blog_item_without_tenant_id_not_ok(lambda_context, dynamodb_table):
    headers = {
        'Content-Type': 'application/json'
    }
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht"
    }
    response = blog_handler.handle(
        event('/api/blog', 'POST', json.dumps(item), None, headers), lambda_context)

    assert response == lambda_response(400, json.dumps(
        {'error_text': 'tenant not present.'}))

def test_create_blog_item_with_optional_introtext_ok(lambda_context, dynamodb_table):
    item = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "introtext": "Eine Einleitung",
        "gueltigVon": "2022-01-01"
    }
    response = blog_handler.handle(
        event('/api/blog', 'POST', json.dumps(item)), lambda_context)
    id = extract_id(response)

    assert id is not None
    assert response == lambda_response(201, BlogDTO(
        "Test", "Eine Testnachricht", "Eine Einleitung", date.fromisoformat("2022-01-01"), None, id).to_json())

