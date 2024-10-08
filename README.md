# Blog-Lambda

## Routen

### Blog 

- POST api/blog
- GET api/blog
- GET api/blog-ids
- GET api/blog/<id>
- PUT api/blog/<id>
- DELETE api/blog/<id>


## Umgebungsvariablen
| Name               | Beschreibung                                       |
| ------------------ | -------------------------------------------------- |
| BLOG_TABLE_NAME    | Name der Blog DynamoDB-Table                       |
| BLOG_S3_BUCKET     | Name des S3-Buckets für die Images                 |
| TTL_FEATURE_ACTIVE | Flag, ob TTL für die Blog DynamoDB-Table aktiv ist |