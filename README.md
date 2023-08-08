# Blog-Lambda

## Routen

### Neuigkeit 

- POST api/blog
- GET api/blog/<id>
- PUT api/blog/<id>
- DELETE api/blog/<id>


## Umgebungsvariablen
| Name                    | Beschreibung                                            |
|-------------------------|---------------------------------------------------------|
| BLOG_TABLE_NAME         | Name der Blog DynamoDB-Table                            |
| TTL_FEATURE_ACTIVE      | Flag, ob TTL für die Blog DynamoDB-Table aktiv ist      |