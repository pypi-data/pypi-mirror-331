from collections import deque


class DiffPath:
    def __init__(self, parent=None, schema: dict = None, name: str = None):
        self.parent = parent
        self.properties = {"name": name} if name else {}
        if schema and schema.get("properties", {}).get(name, {}).get("alias", {}):
            self.properties["alias"] = schema["properties"][name]["alias"]
        if schema and schema.get("properties", {}).get(name, {}).get("description", {}):
            self.properties["description"] = schema["properties"][name]["description"]

    def set_filter(self, schema: dict, key: dict, doc: dict):
        self.properties["filters"] = DiffPath._get_path_filter(schema, key, doc)

    def path_list(self) -> list:
        return (self.parent.path_list() if self.parent else []) + (
            [self.properties] if self.properties else []
        )

    def get_location_jsonpath(self) -> str:
        location = "$"
        for subpath in self.path_list():
            location += DiffPath.jsonpath_field_name(subpath["name"])
        return location

    def get_attribute_jsonpath(self) -> str:
        location = "$"
        for subpath in self.path_list():
            location += DiffPath.jsonpath_field_name(subpath["name"])
            if "filters" in subpath:
                location += DiffPath.get_filter_jsonpath(subpath["filters"])
        return location

    def get_leaf_jsonpath(self) -> str:
        return f"${DiffPath.get_filter_jsonpath(self.properties['filters'])}"

    def get_name(self) -> str:
        return self.properties["name"]

    def get_alias(self) -> str:
        return self.properties.get("alias", None)

    def get_values_from_key(self) -> list:
        return [
            fltr["value"]
            for fltr in DiffPath._filters_bfs_sorted(self.properties["filters"])
            if "value" in fltr
        ]

    def get_dynamic_column_names(self) -> list:
        return self._get_dynamic_columns(
            lambda fltr, dynamic_path: dynamic_path
            + DiffPath._get_jsonpath_to_trunk(fltr)
        )

    def get_dynamic_column_aliases(self) -> list:
        return self._get_dynamic_columns(
            lambda fltr, dynamic_path: fltr["alias"]
            if "alias" in fltr
            else dynamic_path + DiffPath._get_jsonpath_to_trunk(fltr)
        )

    def __lt__(self, other) -> bool:
        return self.get_leaf_jsonpath() < other.get_leaf_jsonpath()

    def __eq__(self, other) -> bool:
        return self.get_leaf_jsonpath() == other.get_leaf_jsonpath()

    def __hash__(self) -> int:
        return hash(self.get_leaf_jsonpath())

    @staticmethod
    def escape_jsonpath_field(field: str) -> str:
        field = field.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{field}'"

    @staticmethod
    def jsonpath_field_name(name: str) -> str:
        return f"[{DiffPath.escape_jsonpath_field(name)}]"

    @staticmethod
    def get_filter_jsonpath(fltr: dict) -> str:
        return f"[?(@{'&@'.join(DiffPath._get_filter_jsonpath(fltr))})]"

    @staticmethod
    def _filters_bfs_sorted(fltrs: dict):
        # Uses a queue to return key filters in BFS order.
        # Uses sorting to return keys in alpha order at each level
        filter_queue = deque([{"filters": fltrs}])
        while filter_queue:
            head = filter_queue.popleft()
            for _, filter_value in sorted(head["filters"].items()):
                if "parent" in head:
                    filter_value["parent"] = head["parent"]
                yield filter_value
                if "filters" in filter_value:
                    filter_queue.append(
                        {"parent": filter_value, "filters": filter_value["filters"]}
                    )

    @staticmethod
    def _get_path_filter(schema: dict, key: dict, doc: dict) -> dict:
        path = {}
        for name, value in key.items():
            path[name] = {"name": name}
            if schema.get("properties", {}).get(name, {}).get("alias", {}):
                path[name]["alias"] = schema["properties"][name]["alias"]
            if schema.get("properties", {}).get(name, {}).get("description", {}):
                path[name]["description"] = schema["properties"][name]["description"]
            if value:
                path[name]["filters"] = DiffPath._get_path_filter(
                    schema.get("properties", {}).get(name, {}),
                    value,
                    doc[name],
                )
            else:
                path[name]["value"] = doc[name]
        return path

    @staticmethod
    def _get_filtered_jsonpath_to_trunk(fltr: dict) -> str:
        return (
            (
                DiffPath._get_filtered_jsonpath_to_trunk(fltr["parent"])
                if "parent" in fltr
                else ""
            )
            + DiffPath.jsonpath_field_name(fltr["name"])
            + (
                f"={DiffPath.escape_jsonpath_field(fltr['value'])}"
                if "value" in fltr
                else ""
            )
        )

    @staticmethod
    def _get_filter_jsonpath(fltrs: dict) -> list:
        return [
            DiffPath._get_filtered_jsonpath_to_trunk(fltr)
            for fltr in DiffPath._filters_bfs_sorted(fltrs)
            if "filters" not in fltr and "value" in fltr
        ]

    @staticmethod
    def _get_jsonpath_to_trunk(fltr: dict) -> str:
        return (
            DiffPath._get_jsonpath_to_trunk(fltr["parent"]) if "parent" in fltr else ""
        ) + DiffPath.jsonpath_field_name(fltr["name"])

    def _get_dynamic_columns(self, get_column_path) -> list:
        dynamic_columns = []
        dynamic_path = "$"
        for subpath in self.path_list():
            dynamic_path += DiffPath.jsonpath_field_name(subpath["name"])
            if "filters" in subpath and subpath["filters"]:
                for fltr in DiffPath._filters_bfs_sorted(subpath["filters"]):
                    if "filters" not in fltr and "value" in fltr:
                        dynamic_columns.append(
                            {
                                "name": get_column_path(fltr, dynamic_path),
                                "value": fltr["value"],
                            }
                        )
                        if "alias" in fltr:
                            dynamic_columns[-1]["alias"] = fltr["alias"]
                        if "description" in fltr:
                            dynamic_columns[-1]["description"] = fltr["description"]
        return dynamic_columns
