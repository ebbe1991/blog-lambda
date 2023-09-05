import os
import json
import boto3
from lambda_utils.exception import ValidationException
from blog_controller import update_blog_item, get_blog_item

s3_bucket_name = os.getenv('BLOG_S3_BUCKET')
s3 = boto3.client('s3')


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
