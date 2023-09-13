from blog_dto import BlogDTO, create
from lambda_utils.exception import UnknownIdException
from datetime import date
import dynamo_db_service
import os
import json
import boto3
from lambda_utils.exception import ValidationException

s3_bucket_name = os.getenv('BLOG_S3_BUCKET')
s3 = boto3.client('s3')


def create_blog_item(tenant_id: str, dto: dict) -> BlogDTO:
    blog_item = create(dto)
    dynamo_db_service.put_blog_item(tenant_id, blog_item)
    return blog_item


def update_blog_item(tenant_id: str, id: str, dto: dict) -> BlogDTO:
    dto.update({'id': id})
    blog_item = create(dto)
    to_update = get_blog_item(tenant_id, id)
    if to_update:
        dynamo_db_service.put_blog_item(tenant_id, blog_item)
        return blog_item
    else:
        raise UnknownIdException(id, tenant_id)


def get_blog_item(tenant_id: str, id: str) -> BlogDTO:
    item = dynamo_db_service.get_blog_item(tenant_id, id)
    if item:
        blog_item = create(item)
        return blog_item
    else:
        return None


def get_blog_items(tenant_id: str, stichtag: date = None, count: int = None) -> list[BlogDTO]:
    blog_items = []
    items = dynamo_db_service.get_blog_items(tenant_id, count)
    for item in items:
        blog_item = create(item)
        if stichtag is None or blog_item.gueltigBis is None or blog_item.gueltigBis >= stichtag:
            blog_items.append(blog_item)

    sorted_blog_items = sorted(
        blog_items, key=lambda blog_item: blog_item.gueltigVon, reverse=True)
    if count:
        return sorted_blog_items[:count]
    else:
        return sorted_blog_items


def delete_blog_item(tenant_id: str, id: str) -> bool:
    blog_item = get_blog_item(tenant_id, id)
    if blog_item:
        if blog_item.hasPicture:
            delete_image(tenant_id, id)
        dynamo_db_service.delete_blog_item(tenant_id, id)
        return True
    else:
        return False


def request_put_image(tenant_id, id) -> str:
    image_key = get_image_key(tenant_id, id)

    url = s3.generate_presigned_url('put_object', Params={
                                    'Bucket': s3_bucket_name, 'Key': image_key}, ExpiresIn=3600)
    return json.dumps(url)


def put_image(tenant_id, id, body):
    image_key = get_image_key(tenant_id, id)

    max_file_size = 1.5 * 1024 * 1024  # 1,5 MB in Bytes
    binary_size = 0

    binary_size += len(body)
    if binary_size > max_file_size:
        raise ValidationException("Datei ist zu groß.")

    if not is_png(body) and not is_jpg(body):
        raise ValidationException("Datei ist kein PNG oder JPG.")

    s3.put_object(Body=body, Bucket=s3_bucket_name, Key=image_key)
    item = get_blog_item(tenant_id=tenant_id, id=id)
    item.hasPicture = True
    update_blog_item(tenant_id=tenant_id,
                     id=id,
                     dto=json.loads(item.to_json()))


def delete_image(tenant_id, id):
    image_key = get_image_key(tenant_id, id)
    s3.delete_object(Bucket=s3_bucket_name, Key=image_key)
    item = get_blog_item(tenant_id=tenant_id, id=id)
    item.hasPicture = False
    update_blog_item(tenant_id=tenant_id,
                     id=id,
                     dto=json.loads(item.to_json()))


def get_image_key(tenant_id: str, id: str) -> str:
    return f'assets/blog/{tenant_id}/{id}/img.jpg'


def is_png(data):
    png_signature = b'\x89PNG\r\n\x1a\n'
    return data.startswith(png_signature)


def is_jpg(data):
    jpg_signatures = [b'\xFF\xD8\xFF',
                      b'\xFF\xD8\xFF\xE0\x00\x10JFIF', b'\xFF\xD8\xFF\xE1']
    return any(data.startswith(signature) for signature in jpg_signatures)
