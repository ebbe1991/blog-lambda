from src import blog_handler, blog_controller
import pytest
from tests.helper import event, lambda_response, DEFAULT_TENANT_ID
import boto3
from moto import mock_s3
from botocore.exceptions import ClientError


@mock_s3
@pytest.mark.skip(reason="Nur lokal...")
def test_upload_img(lambda_context, dynamodb_table):
    conn = boto3.resource("s3", region_name="us-east-1",
                          aws_access_key_id='YOUR_ACCESS_KEY',
                          aws_secret_access_key='YOUR_SECRET_KEY')
    dto = {
        'betreff': "Test",
        "nachricht": "Eine Testnachricht",
        "gueltigVon": "2022-01-01",
        "gueltigBis": "2022-02-01"
    }
    blogdto = blog_controller.create_blog_item(DEFAULT_TENANT_ID, dto)
    conn.create_bucket(Bucket='my-test-bucket')

    pathParameters = {
        "id": blogdto.id
    }
    file_path = "resources/image.jpg"
    input = ''
    with open(file_path, "rb") as file:
        input = file.read()
        response = blog_handler.handle(event(
            '/api/blog/{id}/image',
            'PUT',
            input,
            pathParameters,
            {'x-tenant-id': DEFAULT_TENANT_ID,
             'Content-Type': 'application/octet-stream'},
        ), lambda_context)

    assert response == lambda_response(204)
    blogdto = blog_controller.get_blog_item(tenant_id=DEFAULT_TENANT_ID, id=blogdto.id)
    assert blogdto.hasPicture == True

    image_data = conn.Object('my-test-bucket', f'assets/blog/{DEFAULT_TENANT_ID}/{blogdto.id}/img.jpg').get()[
        "Body"].read()
    assert image_data == input

    response = blog_handler.handle(event(
        '/api/blog/{id}/image',
        'DELETE',
        input,
        pathParameters,
        {'x-tenant-id': DEFAULT_TENANT_ID},
    ), lambda_context)

    assert response == lambda_response(204)
    blogdto = blog_controller.get_blog_item(tenant_id=DEFAULT_TENANT_ID, id=blogdto.id)
    assert blogdto.hasPicture == False

    deleted = False
    try:
        conn.Object('my-test-bucket', f'assets/blog/{DEFAULT_TENANT_ID}/{blogdto.id}/img.jpg').get()[
            "Body"].read()
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            deleted = True
    assert deleted == True


@mock_s3
@pytest.mark.skip(reason="Nur lokal...")
def test_upload_to_big_img(lambda_context):
    conn = boto3.resource("s3", region_name="us-east-1",
                          aws_access_key_id='YOUR_ACCESS_KEY',
                          aws_secret_access_key='YOUR_SECRET_KEY')
    conn.create_bucket(Bucket='my-test-bucket')

    pathParameters = {
        "id": "test-id"
    }
    file_path = "resources/big.jpg"
    input = ''
    with open(file_path, "rb") as file:
        input = file.read()
        response = blog_handler.handle(event(
            '/api/blog/{id}/image',
            'PUT',
            input,
            pathParameters,
            {'x-tenant-id': DEFAULT_TENANT_ID,
             'Content-Type': 'application/octet-stream'},
        ), lambda_context)

    assert response == lambda_response(
        400, '{"error_text": "Datei ist zu gro\\u00df."}')


@mock_s3
@pytest.mark.skip(reason="Nur lokal...")
def test_upload_no_image(lambda_context):
    conn = boto3.resource("s3", region_name="us-east-1",
                          aws_access_key_id='YOUR_ACCESS_KEY',
                          aws_secret_access_key='YOUR_SECRET_KEY')
    conn.create_bucket(Bucket='my-test-bucket')

    pathParameters = {
        "id": "test-id"
    }
    file_path = "resources/no_image.jpg"
    input = ''
    with open(file_path, "rb") as file:
        input = file.read()
        response = blog_handler.handle(event(
            '/api/blog/{id}/image',
            'PUT',
            input,
            pathParameters,
            {'x-tenant-id': DEFAULT_TENANT_ID,
             'Content-Type': 'application/octet-stream'},
        ), lambda_context)

    assert response == lambda_response(
        400, '{"error_text": "Datei ist kein PNG oder JPG."}')
