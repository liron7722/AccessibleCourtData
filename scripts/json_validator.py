import jsonschema
import json
from relative_path import *

DEFAULT_SCHEMA = get_path('json_schema/json_schema.json')


def validate_v1(dataFile, schemaFile=DEFAULT_SCHEMA):
    with open(dataFile, encoding='utf-8') as dataToElastic:
        elasticData = json.load(dataToElastic)
    with open(schemaFile, encoding='utf-8') as jsonSchema:
        schema = json.load(jsonSchema)
    if jsonschema.validate(elasticData, schema) is None:
        return True
    else:
        return False


def validate_v2(dataObject, schemaFile=DEFAULT_SCHEMA):
    with open(schemaFile, encoding='utf-8') as jsonSchema:
        schema = json.load(jsonSchema)
    if jsonschema.validate(dataObject, schema) is None:
        return True
    else:
        return False
