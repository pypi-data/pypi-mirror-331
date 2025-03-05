from genson import SchemaBuilder
from json import dump, load
from jsonschema import validate
import requests


def get_json_from_url(url):
    return requests.get(
        url=url, params={}, headers={"Cache-Control": "no-cache"}
    ).json()


def get_json_from_file(filename):
    with open(filename) as f:
        return load(f)


def get_json(uri):
    return (
        get_json_from_url(uri)
        if uri.lower().startswith("http://") or uri.lower().startswith("https://")
        else get_json_from_file(uri)
    )


def save_json(data, filename):
    with open(filename, "w") as f:
        dump(data, f, indent=4, sort_keys=True)


def download_json(url, filename):
    save_json(get_json_from_url(url), filename)


def jsons_to_schema(jsons, dollar_schema="https://library.cdisc.org/api/mdr/schema"):
    builder = SchemaBuilder(dollar_schema)
    for version in jsons:
        builder.add_object(version)
    schema = builder.to_schema()
    for version in jsons:
        validate(instance=version, schema=schema)
    return schema


def merge_jsons_to_schema(schema, jsons):
    """
    Take a schema and list of json documents and return a new schema with additional items

    Keyword arguments:
    schema -- json schema
    jsons -- list of new json data
    """
    builder = SchemaBuilder()
    builder.add_schema(schema)
    for version in jsons:
        builder.add_object(version)
    return builder.to_schema()