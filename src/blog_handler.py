from aws_lambda_powertools.event_handler import APIGatewayHttpResolver
import blog_controller
from blog_controller import BlogDTO
from lambda_utils.response_utils import response, empty_response, to_json_array
from lambda_utils.event_utils import extract_body, extract_tenant, extract_stichtag, extract_count
from lambda_utils.exception import ValidationException
import urllib.parse
app = APIGatewayHttpResolver()


def handle(event: dict, context: dict):
    return app.resolve(event, context)


@app.post('/api/blog')
def post():
    event = app.current_event
    tenant_id = extract_tenant(event)
    body = extract_body(event)
    blog_item = blog_controller.create_blog_item(tenant_id, body)
    return response(201, blog_item.to_json())


@app.put('/api/blog/<id>')
def put(id):
    id = urllib.parse.quote(id)
    event = app.current_event
    tenant_id = extract_tenant(event)
    body = extract_body(event)
    blog_item = blog_controller.update_blog_item(tenant_id, id, body)
    return response(200, blog_item.to_json())


@app.get('/api/blog/<id>')
def get(id):
    id = urllib.parse.quote(id)
    event = app.current_event
    tenant_id = extract_tenant(event)
    blog_item = blog_controller.get_blog_item(tenant_id, id)
    if blog_item:
        return response(200, blog_item.to_json())
    else:
        return empty_response(404)


@app.get('/api/blog')
def getAll():
    event = app.current_event
    tenant_id = extract_tenant(event)
    count = extract_count(event)
    stichtag = extract_stichtag(event)
    blog_items = blog_controller.get_blog_items(tenant_id, stichtag, count)
    body = to_json_array(list(map(BlogDTO.to_json, blog_items)))
    return response(200, body)


@app.delete('/api/blog/<id>')
def delete(id):
    id = urllib.parse.quote(id)
    event = app.current_event
    tenant_id = extract_tenant(event)
    deleted = blog_controller.delete_blog_item(tenant_id, id)
    if deleted:
        return empty_response(204)
    else:
        return empty_response(404)


@app.exception_handler(ValidationException)
def handle_http_exception(exception: ValidationException):
    return response(exception.http_status, exception.to_json())


@app.get('/api/blog/<id>/image')
def request_put_img(id):
    id = urllib.parse.quote(id)
    event = app.current_event
    tenant_id = extract_tenant(event)
    response = blog_controller.request_put_image(tenant_id, id)
    return {
        'statusCode': 201,
        'body': response
    }


@app.delete('/api/blog/<id>/image')
def delete_img(id):
    id = urllib.parse.quote(id)
    event = app.current_event
    tenant_id = extract_tenant(event)
    blog_controller.delete_image(tenant_id, id)
    return empty_response(204)
