from copy import deepcopy
from ..models.diff_text import DiffText
from re import sub
from ..utils.helpers import (
    DetailLevel,
    ObjectTypes,
    enumerate_any,
    json_text,
    simple_text,
)


class DiffItemBuilder:
    def __init__(self, src_dict: dict, dynamic_headers: list):
        self.src_dict = src_dict
        self.dynamic_headers = dynamic_headers
        self.diff_item = {}

    def build_action(self):
        """ What type of diff action was performed? """
        self.diff_item["Action"] = simple_text(self.src_dict["action"])

    def build_func(self):
        """ Which logical branch was reached? """
        self.diff_item["func"] = self.src_dict["func"]

    def build_path(self):
        """ Full path of current JSON node """
        self.diff_item["path"] = self.src_dict["path"].path_list()

    def build_attribute_path(self):
        """ Generate Filtered JSON-Path string """
        self.diff_item["Attribute Path"] = simple_text(
            self.src_dict["path"].get_attribute_jsonpath()
        )

    def build_location_path(self):
        """ Generate Unfiltered JSON-Path string """
        self.diff_item["Location Path"] = simple_text(
            self.src_dict["path"].get_location_jsonpath()
        )

    def build_change_level(self):
        pass

    def build_opcodes(self):
        pass

    def build_value_previous(self):
        pass

    def build_value_updated(self):
        pass

    def build_attribute_previous(self):
        pass

    def build_attribute_updated(self):
        pass

    def build_impact(self):
        pass

    def build_dynamic_columns(self):
        pass


class AddDropBuilder(DiffItemBuilder):
    """ Add or Drop - Populate previous if old item dropped or populate updated if new item added """


class UpdateBuilder(DiffItemBuilder):
    """ Value update - Determine string indices for highlighting differences """

    @staticmethod
    def is_minor_change(old: str, new: str) -> bool:
        """
        Take 2 strings. Returns True if the only difference between the two strings is case or non-alphanumeric changes.

        Keyword arguments:
        old -- Old string to compare
        new -- New string to compare
        """
        return sub("[^0-9A-Z]+", "", old.upper()) == sub("[^0-9A-Z]+", "", new.upper())

    def __init__(self, src_dict: dict, dynamic_headers: list):
        super().__init__(src_dict, dynamic_headers)
        self.diff_text = DiffText(self.src_dict["old"], self.src_dict["new"])

    def build_change_level(self):
        self.diff_item["Change Level"] = simple_text(
            "Minor"
            if UpdateBuilder.is_minor_change(self.src_dict["old"], self.src_dict["new"])
            else "Major"
        )

    def build_opcodes(self):
        self.diff_item["opcodes"] = self.diff_text.opcodes

    def build_value_previous(self):
        self.diff_item["Value (previous)"] = json_text(self.diff_text.old_val)

    def build_value_updated(self):
        self.diff_item["Value (updated)"] = json_text(self.diff_text.new_val)

    def build_attribute_previous(self):
        self.diff_item["Attribute (previous)"] = self.diff_text.old_str

    def build_attribute_updated(self):
        self.diff_item["Attribute (updated)"] = self.diff_text.new_str


class BasicBuilder(DiffItemBuilder):
    def build_impact(self):
        """ Impact is the leaf node in the Path """
        self.diff_item["Impact"] = simple_text(
            self.src_dict["path"].get_alias()
            if self.src_dict["path"].get_alias()
            else self.src_dict["path"].get_name()
        )

    def build_dynamic_columns(self):
        """ Generate dynamic columns """
        for dynamic_column in self.src_dict["path"].get_dynamic_column_aliases():
            alias = dynamic_column.get("alias", dynamic_column["name"])
            if alias not in self.dynamic_headers:
                self.dynamic_headers[alias] = {"names": [dynamic_column["name"]]}
            elif dynamic_column["name"] not in self.dynamic_headers[alias]["names"]:
                self.dynamic_headers[alias]["names"].append(dynamic_column["name"])
            if "alias" in dynamic_column:
                self.dynamic_headers[alias]["alias"] = dynamic_column["alias"]
            if "description" in dynamic_column:
                self.dynamic_headers[alias]["description"] = dynamic_column[
                    "description"
                ]
            self.diff_item[alias] = simple_text(dynamic_column["value"])


class AdvancedBuilder(DiffItemBuilder):
    def build_impact(self):
        """ Impact is the leaf node in the Path """
        self.diff_item["Impact"] = simple_text(self.src_dict["path"].get_name())

    def build_dynamic_columns(self):
        """ Generate dynamic columns """
        for dynamic_column in self.src_dict["path"].get_dynamic_column_names():
            alias = dynamic_column.get("alias", dynamic_column["name"])
            if alias not in self.dynamic_headers:
                self.dynamic_headers[alias] = {"names": [dynamic_column["name"]]}
            elif dynamic_column["name"] not in self.dynamic_headers[alias]["names"]:
                self.dynamic_headers[alias]["names"].append(dynamic_column["name"])
            if "alias" in dynamic_column:
                self.dynamic_headers[alias]["alias"] = dynamic_column["alias"]
            if "description" in dynamic_column:
                self.dynamic_headers[alias]["description"] = dynamic_column[
                    "description"
                ]
            self.diff_item[dynamic_column["name"]] = simple_text(
                dynamic_column["value"]
            )


class BasicAddDropBuilder(AddDropBuilder, BasicBuilder):
    def build_recursive_type(self, attr_name: str, attr_value, target_key: str):
        attr_copy = deepcopy(attr_value)
        has_simple_items = False
        for key, value in enumerate_any(attr_copy):
            if ObjectTypes.is_mapping_type(value):
                # dict inside list/dict
                attr_copy[key] = ObjectTypes.MAPPING_TYPES.collapsed()
            elif ObjectTypes.is_sequence_type(value):
                # list inside list/dict
                attr_copy[key] = ObjectTypes.SEQUENCE_TYPES.collapsed()
            else:
                # simple type inside list/dict
                has_simple_items = True
        self.diff_item[target_key] = json_text(
            attr_copy if has_simple_items or not attr_name else attr_name, 4
        )

    def build_simple_type(self, attr_value, target_key: str):
        self.diff_item[target_key] = simple_text(attr_value)

    def build_attribute(self, source_name_key: str, source_key: str, target_key: str):
        attr_name = self.src_dict.get(source_name_key)
        attr_value = self.src_dict.get(source_key)
        if attr_value is not None and ObjectTypes.is_recursive_type(attr_value):
            self.build_recursive_type(attr_name, attr_value, target_key)
        elif attr_value is not None:
            self.build_simple_type(attr_value, target_key)

    def build_attribute_previous(self):
        self.build_attribute(
            "old_name",
            "old",
            "Attribute (previous)",
        )

    def build_attribute_updated(self):
        self.build_attribute(
            "new_name",
            "new",
            "Attribute (updated)",
        )


class AdvancedAddDropBuilder(AddDropBuilder, AdvancedBuilder):
    def build_attribute(self, source_key: str, target_key: str):
        attribute = self.src_dict.get(source_key)
        if attribute is not None and ObjectTypes.is_recursive_type(attribute):
            self.diff_item[target_key] = json_text(attribute, 4)
        elif attribute is not None:
            self.diff_item[target_key] = simple_text(attribute)

    def build_attribute_previous(self):
        self.build_attribute("old", "Attribute (previous)")

    def build_attribute_updated(self):
        self.build_attribute("new", "Attribute (updated)")


class BasicUpdateBuilder(UpdateBuilder, BasicBuilder):
    pass


class AdvancedUpdateBuilder(UpdateBuilder, AdvancedBuilder):
    pass


class DiffItemDirector:
    @staticmethod
    def get_diff_item(
        src_dict: dict, dynamic_headers: list, detail_level: DetailLevel
    ) -> dict:
        diff_item_builder = None
        old = src_dict.get("old", None)
        new = src_dict.get("new", None)
        is_update = (
            old is not None
            and type(old) == str
            and new is not None
            and type(new) == str
        )
        if detail_level == DetailLevel.BASIC and is_update:
            diff_item_builder = BasicUpdateBuilder(src_dict, dynamic_headers)
        elif detail_level == DetailLevel.BASIC and not is_update:
            diff_item_builder = BasicAddDropBuilder(src_dict, dynamic_headers)
        elif detail_level == DetailLevel.ADVANCED and is_update:
            diff_item_builder = AdvancedUpdateBuilder(src_dict, dynamic_headers)
        elif detail_level == DetailLevel.ADVANCED and not is_update:
            diff_item_builder = AdvancedAddDropBuilder(src_dict, dynamic_headers)

        diff_item_builder.build_action()
        diff_item_builder.build_func()
        diff_item_builder.build_path()
        diff_item_builder.build_attribute_path()
        diff_item_builder.build_location_path()
        diff_item_builder.build_change_level()
        diff_item_builder.build_opcodes()
        diff_item_builder.build_value_previous()
        diff_item_builder.build_value_updated()
        diff_item_builder.build_attribute_previous()
        diff_item_builder.build_attribute_updated()
        diff_item_builder.build_impact()
        diff_item_builder.build_dynamic_columns()

        return diff_item_builder.diff_item
