import jsonschema
import json

DEFAULT_SCHEMA = 'C:/Users/Administrator/Documents/AccessibleCourtData/json_schema/json_schema'

def validate_v1(dataFile, schemaFile=DEFAULT_SCHEMA):
    with open(dataFile, encoding='utf-8') as dataToElastic:
        elasticData = json.load(dataToElastic)
    with open(schemaFile, encoding='utf-8') as jsonSchema:
        schema = json.load(jsonSchema)
    if jsonschema.validate(elasticData, schema) is None:
        return "Ok"
    else:
        return "Error"


def validate_v2(dataObject, schemaFile=DEFAULT_SCHEMA):
    with open(schemaFile, encoding='utf-8') as jsonSchema:
        schema = json.load(jsonSchema)
    if jsonschema.validate(dataObject, schema) is None:
        return "Ok"
    else:
        return "Error"
