# Built-in imports
from collections import Counter, OrderedDict
from copy import copy, deepcopy
from datetime import datetime
import json
from importlib.resources import files

# Installed imports
from jsonschema import validate, ValidationError

# Source imports
from .models.diff_item import DiffItemDirector
from .models.diff_path import DiffPath
from .utils.helpers import create_counter, DetailLevel, simple_text, ObjectTypes
from .utils.json_utils import jsons_to_schema


def simplify_json_schema(schema):
    schema.pop("required", None)
    schema.pop("type", None)
    if "properties" in schema:
        for prop in schema["properties"]:
            simplify_json_schema(schema["properties"][prop])
    if "items" in schema:
        if "properties" in schema["items"] and "key" not in schema["items"]:
            schema["items"]["key"] = [{"": {}}]
        simplify_json_schema(schema["items"])
    return schema


def create_schema_template(jsons):
    return simplify_json_schema(jsons_to_schema(jsons))


def get_doc_id(schema, doc):
    if "doc_id" in schema:
        return doc[schema["doc_id"]]
    elif type(doc) == dict:
        return "".join(
            get_doc_id(schema["properties"][prop], doc[prop]) for prop in sorted(doc)
        )
    elif type(doc) in (list, tuple):
        return "".join(get_doc_id(schema["items"], item) for item in doc)


def get_validation_features(doc_id, issue, details):
    return {
        "Document": simple_text(doc_id),
        "Issue": simple_text(issue),
        "Details": simple_text(details),
    }


def validate_doc_keys_exist(schema_item: dict, doc_dict: dict) -> bool:
    """
    Take a schema item, and document dict and recursively check that all keys in the schema item have a corresponding value in the document dict.
    Returns True if dict has all key values, otherwise returns False

    Keyword arguments:
    schema_item -- Schema item that corresponds to the doc_dict
    doc_dict -- dict in the json document
    """
    valid = True
    for name, value in sorted(schema_item.items()):
        if name in doc_dict:
            if value:
                valid &= validate_doc_keys_exist(schema_item[name], doc_dict[name])
        else:
            valid = False
    return valid


def validate_key_aliases(schema: dict, key: dict, alias_set: set) -> list:
    duplicates = []
    for name, value in sorted(key.items()):
        if value:
            duplicates += validate_key_aliases(
                schema["properties"][name], value, alias_set
            )
        elif "alias" in schema["properties"][name]:
            alias = schema["properties"][name]["alias"]
            if alias in alias_set:
                duplicates += [alias]
            else:
                alias_set.add(alias)
    return duplicates


def custom_json_validate(doc_id: str, schema: dict, doc, alias_set: set) -> list:
    """
    Take a schema and json document, and recursively return a list of validation errors, if any.

    Keyword arguments:
    doc_id -- json document identfier
    schema -- json schema subtree
    doc -- json document subtree
    alias_set -- a set of alias names for dynamic columns along the path to the current node
    """
    exceptions = []
    alias_set = copy(alias_set)
    if type(doc) not in (dict, list, tuple, int, str, float, bool, type(None)):
        exceptions.append(
            get_validation_features(
                doc_id,
                "Invalid JSON type in document",
                f"type={str(type(doc))}, value={str(doc)}",
            )
        )
    if type(doc) == dict:
        for dict_key, dict_value in sorted(doc.items()):
            exceptions += custom_json_validate(
                doc_id,
                schema["properties"][dict_key]
                if schema
                and "properties" in schema
                and dict_key in schema["properties"]
                else None,
                dict_value,
                alias_set,
            )
    elif type(doc) in (list, tuple):
        types = {type(item) for item in doc}
        if len(types) == 1:
            if dict in types:
                if not schema or "items" not in schema:
                    exceptions.append(
                        get_validation_features(
                            doc_id,
                            "Missing schema subtree for list of dicts.",
                            json.dumps(obj=doc, sort_keys=True),
                        )
                    )
                elif "key" not in schema["items"]:
                    exceptions.append(
                        get_validation_features(
                            doc_id,
                            "Missing schema key attribute for list of dicts.",
                            json.dumps(obj=doc, sort_keys=True),
                        )
                    )
                elif not (schema["items"]["key"]):
                    exceptions.append(
                        get_validation_features(
                            doc_id,
                            "Missing schema key attribute value for list of dicts.",
                            json.dumps(obj=doc, sort_keys=True),
                        )
                    )
                else:
                    for key in schema["items"]["key"]:
                        for item in validate_key_aliases(
                            schema["items"], key, alias_set
                        ):
                            exceptions.append(
                                get_validation_features(
                                    doc_id,
                                    "Duplicate key alias.",
                                    f"alias={item}",
                                )
                            )
                    for item in doc:
                        for key in schema["items"]["key"]:
                            if not (validate_doc_keys_exist(key, item)):
                                exceptions.append(
                                    get_validation_features(
                                        doc_id,
                                        "Document list item missing a key value.",
                                        f"key={schema['items']['key']}, item={json.dumps(obj=item, sort_keys=True)}",
                                    )
                                )
            elif len(types & {list, tuple}) == 1:
                exceptions.append(
                    get_validation_features(
                        doc_id,
                        "Diffing does not support multi-dimensional lists.",
                        json.dumps(obj=doc, sort_keys=True),
                    )
                )
        elif len(types) > 1:
            exceptions.append(
                get_validation_features(
                    doc_id,
                    "Diffing does not support lists of items with mixed types.",
                    json.dumps(obj=doc, sort_keys=True),
                )
            )
        for item in doc:
            exceptions += custom_json_validate(
                doc_id,
                schema["items"] if schema and "items" in schema else None,
                item,
                alias_set,
            )
    return exceptions


def json_validate(schema, doc):
    exceptions = []
    doc_id = get_doc_id(schema, doc)
    if not (doc_id):
        exceptions.append(
            get_validation_features("", "doc_id is missing from schema or document.")
        )
    try:
        # Validate json against json schema
        validate(schema=schema, instance=doc)
    except ValidationError as err:
        exceptions.append(
            get_validation_features(doc_id, "Schema Validation Error.", err)
        )
    exceptions += custom_json_validate(doc_id, schema, doc, set())
    return exceptions


def parse_dict(schema, path, old, new, is_excluded):
    # Property in both dicts
    for key in sorted(old.keys() & new.keys()):
        yield from traverse(
            schema.get("properties", {}).get(key, {}),
            DiffPath(path, schema, key),
            old[key],
            new[key],
            is_excluded or key in schema.get("exclusions", {}),
        )
    # Property has been dropped in new dict
    for key in sorted(old.keys() - new.keys()):
        is_sequence_type = ObjectTypes.is_sequence_type(old[key])
        yield {
            "action": "Drop",
            "func": "dict",
            "path": DiffPath(path, schema, key),
            "old_name": key,
            "old": old[key],
            "is_excluded": is_excluded
            or key in schema.get("exclusions", {})
            or is_sequence_type,
        }
        # If a sequence has been dropped, list all values within the sequence
        if is_sequence_type:
            yield from traverse(
                schema.get("properties", {}).get(key, {}),
                DiffPath(path, schema, key),
                old[key],
                [],
                is_excluded or key in schema.get("exclusions", {}),
            )
    # Property has been added in new dict
    for key in sorted(new.keys() - old.keys()):
        is_sequence_type = ObjectTypes.is_sequence_type(new[key])
        yield {
            "action": "Add",
            "func": "dict",
            "path": DiffPath(path, schema, key),
            "new_name": key,
            "new": new[key],
            "is_excluded": is_excluded
            or key in schema.get("exclusions", {})
            or is_sequence_type,
        }
        # If a sequence has been added, list all values within the sequence
        if is_sequence_type:
            yield from traverse(
                schema.get("properties", {}).get(key, {}),
                DiffPath(path, schema, key),
                [],
                new[key],
                is_excluded or key in schema.get("exclusions", {}),
            )


def create_path_dictlist_map(
    schema: dict, path: DiffPath, dict_list: list, key: dict
) -> dict:
    path_dictlist_map = {}
    for item in dict_list:
        filtered_path = deepcopy(path)
        filtered_path.set_filter(schema["items"], key, item)
        path_dictlist_map.setdefault(filtered_path, []).append(item)
    return path_dictlist_map


def compare_old_new_dicts(schema, path, old, new, is_excluded):
    old_difference = copy(old)
    new_difference = copy(new)
    for key_tree in schema["items"]["key"]:
        old_path_dictlist_map = create_path_dictlist_map(
            schema, path, old_difference, key_tree
        )
        new_path_dictlist_map = create_path_dictlist_map(
            schema, path, new_difference, key_tree
        )
        old_counter = create_counter(old_path_dictlist_map)
        new_counter = create_counter(new_path_dictlist_map)
        old_difference = [
            item
            for key in (old_path_dictlist_map.keys() - new_path_dictlist_map.keys())
            for item in old_path_dictlist_map[key]
        ]
        new_difference = [
            item
            for key in (new_path_dictlist_map.keys() - old_path_dictlist_map.keys())
            for item in new_path_dictlist_map[key]
        ]
        # Dict in both lists
        for key in sorted(old_path_dictlist_map.keys() & new_path_dictlist_map.keys()):
            # n^2 complexity, but if we use good keys, n (# of duplicates) should be 1
            for old_item in old_path_dictlist_map[key]:
                for new_item in new_path_dictlist_map[key]:
                    yield from parse_dict(
                        schema["items"],
                        key,
                        old_item,
                        new_item,
                        is_excluded,
                    )
            # Duplicate Dict has been dropped in new list
            if old_counter[key] > new_counter[key]:
                yield {
                    "action": "Drop",
                    "func": "list-dict",
                    "path": key,
                    "old_name": ", ".join(key.get_values_from_key()),
                    "old": old_path_dictlist_map[key][0]
                    if len(old_path_dictlist_map[key]) == 1
                    else old_path_dictlist_map[key],
                    "is_excluded": is_excluded,
                }
            # Duplicate Dict has been added in new list
            if new_counter[key] > old_counter[key]:
                yield {
                    "action": "Add",
                    "func": "list-dict",
                    "path": key,
                    "new_name": ", ".join(key.get_values_from_key()),
                    "new": new_path_dictlist_map[key][0]
                    if len(new_path_dictlist_map[key]) == 1
                    else new_path_dictlist_map[key],
                    "is_excluded": is_excluded,
                }
    old_path_dictlist_map = create_path_dictlist_map(
        schema, path, old_difference, schema["items"]["key"][0]
    )
    new_path_dictlist_map = create_path_dictlist_map(
        schema, path, new_difference, schema["items"]["key"][0]
    )
    old_counter = create_counter(old_path_dictlist_map)
    new_counter = create_counter(new_path_dictlist_map)
    # Dict has been dropped in new list
    for key in sorted((old_counter - new_counter).keys()):
        yield {
            "action": "Drop",
            "func": "list-dict",
            "path": key,
            "old_name": ", ".join(key.get_values_from_key()),
            "old": old_path_dictlist_map[key][0]
            if len(old_path_dictlist_map[key]) == 1
            else old_path_dictlist_map[key],
            "is_excluded": is_excluded,
        }
    # Dict has been added in new list
    for key in sorted((new_counter - old_counter).keys()):
        yield {
            "action": "Add",
            "func": "list-dict",
            "path": key,
            "new_name": ", ".join(key.get_values_from_key()),
            "new": new_path_dictlist_map[key][0]
            if len(new_path_dictlist_map[key]) == 1
            else new_path_dictlist_map[key],
            "is_excluded": is_excluded,
        }


def compare_old_new_values(schema, path, old, new, is_excluded):
    old_counter = Counter(old)
    new_counter = Counter(new)
    # Value has been dropped in new list
    for val in sorted((old_counter - new_counter).elements()):
        yield {
            "action": "Drop",
            "func": "list-nodict",
            "path": path,
            "old": val,
            "is_excluded": is_excluded,
        }
    # Value has been added in new list
    for val in sorted((new_counter - old_counter).elements()):
        yield {
            "action": "Add",
            "func": "list-nodict",
            "path": path,
            "new": val,
            "is_excluded": is_excluded,
        }


def parse_list(schema, path, old, new, is_excluded):
    old_item_type = type(old[0]) if old else None
    new_item_type = type(new[0]) if new else None
    if not old_item_type or not new_item_type or old_item_type == new_item_type:
        if dict in (old_item_type, new_item_type):
            yield from compare_old_new_dicts(schema, path, old, new, is_excluded)
        else:
            yield from compare_old_new_values(schema, path, old, new, is_excluded)
    else:
        # Items in list have a different type in new list
        yield {
            "action": "Type Update",
            "func": "list-unequal",
            "path": path,
            "old": old,
            "new": new,
            "is_excluded": is_excluded,
        }


def parse_value(schema, path, old, new, is_excluded):
    if old != new:
        yield {
            "action": "Value Update",
            "func": "value",
            "path": path,
            "old": old,
            "new": new,
            "is_excluded": is_excluded,
        }


def traverse(schema, path, old, new, is_excluded):
    """Traverse a pair of json files and a corresponding schema and return a list of differences.

    Keyword arguments:
    schema -- json schema
    path -- list of path parts and filters that point to the current path in the json files
    old -- previous json file for comparison
    new -- updated json file for comparison
    is_excluded -- whether or not the diff item should be excluded from the basic view
    """
    if type(old) == type(new):
        if type(old) == dict:
            yield from parse_dict(schema, path, old, new, is_excluded)
        elif type(old) in (list, tuple):
            yield from parse_list(schema, path, old, new, is_excluded)
        else:
            yield from parse_value(schema, path, old, new, is_excluded)
    else:
        yield {
            "action": "Type Update",
            "func": "traverse",
            "path": path,
            "old": old,
            "new": new,
            "is_excluded": is_excluded,
        }


PRE_BASIC_HEADERS = [
    "Updated Version",
    "Previous Version",
    "Action",
    "Impact",
    "Change Level",
]
POST_BASIC_HEADERS = ["Attribute (updated)", "Attribute (previous)"]
PRE_ADVANCED_HEADERS = ["Attribute Path"]
POST_ADVANCED_HEADERS = [
    "Location Path",
    "Action",
    "Impact",
    "Change Level",
    "Attribute (updated)",
    "Attribute (previous)",
    "Value (updated)",
    "Value (previous)",
]
INFO_HEADERS = ["Attribute", "Value"]
VALIDATION_HEADERS = ["Document", "Issue", "Details"]


def set_readme_body(
    readme_tables: list,
    readme_name: str,
    insert_before: str,
    dynamic_body: list,
    diffs: list,
):
    readme_body = next(
        filter(lambda table: table["title"] == readme_name, readme_tables)
    )["body"]
    insert_position = readme_body.index(
        next(
            filter(
                lambda column: column["Column Name"][0]["text"] == insert_before,
                readme_body,
            )
        )
    )
    readme_body[insert_position:insert_position] = dynamic_body
    # Populate "Impact" list
    next(
        filter(lambda column: column["Column Name"][0]["text"] == "Impact", readme_body)
    )["Description"][0]["text"] += ", ".join(
        sorted(set([f'"{diff_item["Impact"][0]["text"]}"' for diff_item in diffs]))
    )


def load_readme_tables(
    dynamic_basic_headers: OrderedDict,
    dynamic_advanced_headers: OrderedDict,
    basic_diffs: list,
    advanced_diffs: list,
) -> list:
    readme_tables = json.loads(
        files(__name__).joinpath("resources", "readme_tables.json").read_bytes()
    )
    # Basic Readme
    dynamic_body = []
    for dynamic_header_alias, dynamic_header_value in dynamic_basic_headers.items():
        dynamic_body.append({"Column Name": simple_text(dynamic_header_alias)})
        if "description" in dynamic_header_value:
            dynamic_body[-1]["Description"] = simple_text(
                dynamic_header_value["description"]
            )
    set_readme_body(
        readme_tables,
        "ReadMe for Basic Tab",
        (POST_BASIC_HEADERS + PRE_BASIC_HEADERS)[0],
        dynamic_body,
        basic_diffs,
    )
    # Advanced Readme
    dynamic_body = []
    for dynamic_header_alias, dynamic_header_value in dynamic_advanced_headers.items():
        for dynamic_header_name in dynamic_header_value["names"]:
            dynamic_body.append(
                {
                    "Column Name": simple_text(dynamic_header_name),
                }
            )
            if "description" in dynamic_header_value:
                dynamic_body[-1]["Description"] = simple_text(
                    dynamic_header_value["description"]
                )
            if "alias" in dynamic_header_value:
                dynamic_body[-1]["Alias"] = simple_text(dynamic_header_value["alias"])
    set_readme_body(
        readme_tables,
        "ReadMe for Advanced Tab",
        (POST_ADVANCED_HEADERS + PRE_ADVANCED_HEADERS)[0],
        dynamic_body,
        advanced_diffs,
    )
    return readme_tables


def json_diff(schema, old, new):
    exceptions = []
    exceptions += json_validate(schema, old)
    exceptions += json_validate(schema, new)
    basic_diffs = []
    advanced_diffs = []
    dynamic_basic_headers = OrderedDict()
    dynamic_advanced_headers = OrderedDict()
    if not exceptions:
        diffs = [
            diff_item for diff_item in traverse(schema, DiffPath(), old, new, False)
        ]
        basic_diffs = [
            DiffItemDirector.get_diff_item(
                diff_item, dynamic_basic_headers, DetailLevel.BASIC
            )
            for diff_item in filter(
                lambda diff_item: not (diff_item["is_excluded"]),
                diffs,
            )
        ]
        advanced_diffs = [
            DiffItemDirector.get_diff_item(
                diff_item, dynamic_advanced_headers, DetailLevel.ADVANCED
            )
            for diff_item in diffs
        ]
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    previous_version = get_doc_id(schema, old)
    updated_version = get_doc_id(schema, new)
    tables = (
        [
            {
                "head": INFO_HEADERS,
                "title": "Info",
                "body": [
                    {
                        "Attribute": simple_text("Generated"),
                        "Value": simple_text(current_time),
                    },
                    {
                        "Attribute": simple_text("Updated Version"),
                        "Value": simple_text(updated_version),
                    },
                    {
                        "Attribute": simple_text("Previous Version"),
                        "Value": simple_text(previous_version),
                    },
                ],
            }
        ]
        + load_readme_tables(
            dynamic_basic_headers, dynamic_advanced_headers, basic_diffs, advanced_diffs
        )
        + [
            {"head": [], "title": "Basic", "body": []},
            {"head": [], "title": "Advanced", "body": []},
            {
                "head": VALIDATION_HEADERS,
                "title": "Validation",
                "body": exceptions
                if exceptions
                else [{"Issue": simple_text("No Validation issues")}],
            },
        ]
    )
    basic = next(filter(lambda item: item["title"] == "Basic", tables))
    advanced = next(filter(lambda item: item["title"] == "Advanced", tables))
    basic["head"] += PRE_BASIC_HEADERS
    advanced["head"] += PRE_ADVANCED_HEADERS
    basic["head"] += dynamic_basic_headers.keys()
    advanced["head"] += [
        header
        for header_group in dynamic_advanced_headers.values()
        for header in header_group["names"]
    ]
    for row in basic_diffs:
        row["Previous Version"] = simple_text(previous_version)
        row["Updated Version"] = simple_text(updated_version)
    basic["body"] = basic_diffs
    advanced["body"] = advanced_diffs
    basic["head"] += POST_BASIC_HEADERS
    advanced["head"] += POST_ADVANCED_HEADERS
    return tables
