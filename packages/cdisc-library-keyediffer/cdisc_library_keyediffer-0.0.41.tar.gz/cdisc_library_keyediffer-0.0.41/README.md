# Keyediffer

Keyediffer is a Python library for diffing structured data, like json or xml files, where the two files being diffed share some common structure.

## Prerequisites

[Python](https://www.python.org/downloads/)

[Visual Studio Code](https://code.visualstudio.com/) recommended

Ability to execute from Powershell. (Run Powershell as Administrator and run):

```bash
Set-ExecutionPolicy -ExecutionPolicy Unrestricted
```

## Installation

Follow the steps to [create a virtual environment](https://wiki.cdisc.org/display/NEXGEN/Virtual+Environments)

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Keyediffer [from git.](https://pip.pypa.io/en/stable/reference/pip_install/#vcs-support)

```bash
pip install cdisc-library-keyediffer
```

Use ```--upgrade``` to reinstall regardless of version. 

## Development

Create a virtual environment [venv](https://docs.python.org/3/tutorial/venv.html)

```bash
py -m venv "[path_to_virtual_environment]"
```

Add the following line in the file "[path_to_virtual_environment]\Scripts\Activate.ps1"

```bash
$Env:PYTHONPATH += ";$($pwd.Path)"
```

Switch to the virtual environment

```bash
& "[path_to_virtual_environment]\Scripts\Activate.ps1"
```

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Keyediffer's requirements.

```bash
pip install -r requirements.txt
```

Follow the steps in [this tutorial](https://code.visualstudio.com/docs/python/testing) to execute the tests.

Or run the command `python -m unittest` from the project root

## Usage

### Step 1 - Create a schema template

This first step takes as input the files to be diffed that contain similar structure. 


```python
from keyediffer.utils.excel_utils import save_xlsx
from keyediffer.utils.json_utils import (get_json, save_json)
from keyediffer.json_differ import (create_schema_template, json_diff)

versions = (
    get_json('https://example.com/version1.json'),
    get_json('version2.json'),
    get_json('version3.json')
)
save_json(create_schema_template(versions), 'schema.json')
```

It creates a pruned [schema](https://datatracker.ietf.org/doc/draft-bhutton-json-schema/) subset. Note the following special names:
* `$schema` - JSON Schema identifier
* `properties` - Child properties within a dict/map/element/object structure
* `items` - Child items within a list/array/tuple structure
* `key` - For each list/array/tuple in the structure where the child items are dicts/maps/elements/objects, there is an empty key identifier.

The following properties are removed from the schema since they aren't used by the diff tool: `required`, `type`

```json
{
    "$schema": "https://library.cdisc.org/api/mdr/schema",
    "properties": {
        "_links": {
            "properties": {
...
            }
        },
        "classes": {
            "items": {
                "key": [{"": {}}],
                "properties": {
                    "_links": {
                        "properties": {
...
                            "subclasses": {
                                "items": {
                                    "key": [{"": {}}],
                                    "properties": {
                                        "href": {},
                                        "title": {},
                                        "type": {}
                                    }
                                }
                            }
                        }
                    },
                    "datasets": {
                        "items": {
                            "key": [{"": {}}],
                            "properties": {
                                "_links": {
                                    "properties": {
...
                                    }
                                },
                                "datasetStructure": {},
                                "datasetVariables": {
                                    "items": {
                                        "key": [{"": {}}],
                                        "properties": {
                                            "_links": {
                                                "properties": {
                                                    "codelist": {
                                                        "items": {
                                                            "key": [{"": {}}],
                                                            "properties": {
                                                                "href": {},
                                                                "title": {},
                                                                "type": {}
                                                            }
                                                        }
                                                    },
...
                                                }
                                            },
                                            "core": {},
                                            "describedValueDomain": {},
                                            "description": {},
                                            "label": {},
                                            "name": {},
                                            "ordinal": {},
                                            "role": {},
                                            "simpleDatatype": {},
                                            "valueList": {
                                                "items": {}
                                            }
                                        }
                                    }
                                },
                                "description": {},
                                "label": {},
                                "name": {},
                                "ordinal": {}
                            }
                        }
                    },
                    "description": {},
                    "label": {},
                    "name": {},
                    "ordinal": {}
                }
            }
        },
        "description": {},
        "effectiveDate": {},
        "label": {},
        "name": {},
        "registrationStatus": {},
        "source": {},
        "version": {}
    }
}
```

### Step 2 - Fill in additional attributes in the schema template

The following properties can be created and populated:
* `doc_id` - Name of property that will uniquely identify this document across document versions.
* `key` - A list of key names that should correspond to an attribute/property/key that will uniquely identify the object within the parent list. The key will be used for identifying and comparing common objects across versions. If objects cannot be matched on the first key in the list, it will try to match on the next key in the list.
* `exclusions` - List of child property names that should be excluded from comparison in the "basic" diff output.
* `alias` - Renames properties in the "basic" diff output.



```json
{
    "$schema": "https://library.cdisc.org/api/mdr/schema",
    "exclusions" : ["_links", "name", "version", "effectiveDate", "label"],
    "doc_id" : "name",
    "properties": {
        "_links": {
            "properties": {
...
            }
        },
        "classes": {
            "alias" : "Class",
            "items": {
                "key": [{"name": {}}],
                "exclusions" : ["_links", "ordinal"],
                "properties": {
                    "_links": {
                        "properties": {
...
                            "subclasses": {
                                "items": {
                                    "key": [{"title": {}}],
                                    "properties": {
                                        "href": {},
                                        "title": {},
                                        "type": {}
                                    }
                                }
                            }
                        }
                    },
                    "datasets": {
                        "alias": "Dataset",
                        "items": {
                            "key": [{"name": {}}],
                            "exclusions" : ["_links", "ordinal"],
                            "properties": {
                                "_links": {
                                    "properties": {
...
                                    }
                                },
                                "datasetStructure": {},
                                "datasetVariables": {
                                    "alias": "Variable",
                                    "items": {
                                        "key": [{"name": {}}],
                                        "exclusions" : ["_links", "ordinal"],
                                        "properties": {
                                            "_links": {
                                                "properties": {
                                                    "codelist": {
                                                        "items": {
                                                            "key": [{"href": {}}],
                                                            "properties": {
                                                                "href": {},
                                                                "title": {},
                                                                "type": {}
                                                            }
                                                        }
                                                    },
...
                                                }
                                            },
                                            "core": {
                                                "alias": "Core"
                                            },
                                            "describedValueDomain": {},
                                            "description": {
                                                "alias": "CDISC Notes"
                                            },
                                            "label": {},
                                            "name": {},
                                            "ordinal": {},
                                            "role": {},
                                            "simpleDatatype": {},
                                            "valueList": {
                                                "items": {}
                                            }
                                        }
                                    }
                                },
                                "description": {
                                    "alias": "CDISC Notes"
                                },
                                "label": {},
                                "name": {
                                    "alias": "Variable Name"
                                },
                                "ordinal": {}
                            }
                        }
                    },
                    "description": {
                        "alias": "CDISC Notes"
                    },
                    "label": {},
                    "name": {
                        "alias": "Dataset Name"
                    },
                    "ordinal": {}
                }
            }
        },
        "description": {
            "alias": "CDISC Notes"
        },
        "effectiveDate": {},
        "label": {},
        "name": {
            "alias" : "Class"
        },
        "registrationStatus": {},
        "source": {},
        "version": {}
    }
}
```

### Step 3 - Generate the diff results

```python
save_json(
    json_diff(get_json('schema.json'),
    get_json('version2.json'),
    get_json('version3.json'))
    , 'diff.json')
```

### Step 4 - Save to format of choice

Here is an example to convert to Excel

```python
save_xlsx(get_json('diff.json'), 'diff.xlsx')
```

## Output Columns

### Updated Version

Document ID of new version

### Previous Version

Document ID of old version

### Action

* Type Update
* Drop
* Add
* Value Update

### Impact

Leaf node name in the path. Convenient for filtering.

### Change Level

Only applies to 'Value Update' Category.
* Minor - Non-alphanumeric changes or case changes only
* Major - Alphanumeric changes (other than case)

### <Filter Container*>

These columns are dynamic and are generated for each list's name in the structure.

### Attribute (updated)

New objects / values. Value-level adds and updates are highlighted.

### Attribute (previous)

Old objects / values. Value-level drops and updates are highlighted.

### Attribute Path

JSONPath style path that contains filters. These can be used to identify the exact object.

### Location Path

JSONPath style path without filters. Convenient for filtering.

### Value (updated)

Only applies to 'Value Update' Category. Array containing list of adds and updates for string-level diffs.

### Value (previous)

Only applies to 'Value Update' Category. Array containing list of drops and updates for string-level diffs.
