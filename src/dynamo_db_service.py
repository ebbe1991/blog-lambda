import os
import boto3
from blog_dto import BlogDTO
from boto3.dynamodb.conditions import Key


def get_blog_items_table():
    dynamodb = boto3.resource('dynamodb')
    table_name = os.getenv('BLOG_TABLE_NAME')
    return dynamodb.Table(table_name)


def put_blog_item(tenant_id: str, blog_item: BlogDTO):
    table = get_blog_items_table()
    table.put_item(
        Item={
            'tenant-id': tenant_id,
            'id': blog_item.id,
            'betreff': blog_item.betreff,
            'nachricht': blog_item.nachricht,
            'introtext': blog_item.introtext,
            'gueltigVon': blog_item.gueltigVon.isoformat() if blog_item.gueltigVon is not None else None,
            'gueltigBis': blog_item.gueltigBis.isoformat() if blog_item.gueltigBis is not None else None,
            'ttl': blog_item.ttl
        }
    )


def get_blog_item(tenant_id: str, id: str):
    table = get_blog_items_table()
    result = table.get_item(
        Key={
            "tenant-id": tenant_id,
            "id": id
        }
    )
    return result.get('Item')


def get_blog_items(tenant_id: str, count: int) -> list:
    table = get_blog_items_table()
    items = []
    response = table.query(
        KeyConditionExpression=Key('tenant-id').eq(tenant_id),
        ScanIndexForward=False
    )
    items.extend(response['Items'])

    if count and len(items) >= count:
        return items

    while 'LastEvaluatedKey' in response:
        response = table.query(
            KeyConditionExpression=Key('tenant-id').eq(tenant_id),
            ScanIndexForward=False,
            ExclusiveStartKey=response['LastEvaluatedKey']
        )
        items.extend(response['Items'])
        if count and len(items) >= count:
            return items


    return items


def delete_blog_item(tenant_id: str, id: str):
    table = get_blog_items_table()
    table.delete_item(
        Key={
            "tenant-id": tenant_id,
            "id": id
        }
    )
