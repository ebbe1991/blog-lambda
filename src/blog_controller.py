from blog_dto import BlogDTO, create
from lambda_utils.exception import UnknownIdException
from datetime import date
import dynamo_db_service


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
    
    sorted_blog_items = sorted(blog_items, key=lambda blog_item: blog_item.gueltigVon, reverse=True)    
    if count:
        return sorted_blog_items[:count]
    else:
        return sorted_blog_items


def delete_blog_item(tenant_id: str, id: str) -> bool:
    blog_item = get_blog_item(tenant_id, id)
    if blog_item:
        dynamo_db_service.delete_blog_item(tenant_id, id)
        return True
    else:
        return False
