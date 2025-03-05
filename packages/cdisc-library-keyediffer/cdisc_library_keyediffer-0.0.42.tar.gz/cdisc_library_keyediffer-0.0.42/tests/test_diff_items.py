import unittest
from keyediffer.models.diff_item import DiffItemDirector
from keyediffer.utils.helpers import DetailLevel
from keyediffer.models.diff_path import DiffPath
from tests.helpers import compare_objects


class TestDiffItems(unittest.TestCase):
    def test_basic_add(self):
        static_data = {
            "Action": [{"text": "Add"}],
            "func": "Test",
            "path": [{"alias": "Root Alias", "name": "root"}],
            "Attribute Path": [{"text": "$['root']"}],
            "Location Path": [{"text": "$['root']"}],
            "Attribute (updated)": [{"text": "New Value"}],
            "Impact": [{"text": "Root Alias"}],
        }
        dynamic_data = DiffItemDirector.get_diff_item(
            {
                "new": "New Value",
                "action": "Add",
                "func": "Test",
                "path": DiffPath(
                    parent=DiffPath(),
                    schema={"properties": {"root": {"alias": "Root Alias"}}},
                    name="root",
                ),
            },
            (),
            DetailLevel.BASIC,
        )
        compare_objects(
            static_data,
            dynamic_data,
        )

    def test_basic_drop(self):
        static_data = {
            "Action": [{"text": "Drop"}],
            "func": "Test",
            "path": [{"alias": "Root Alias", "name": "root"}],
            "Attribute Path": [{"text": "$['root']"}],
            "Location Path": [{"text": "$['root']"}],
            "Attribute (previous)": [{"text": "Old Value"}],
            "Impact": [{"text": "Root Alias"}],
        }
        dynamic_data = DiffItemDirector.get_diff_item(
            {
                "old": "Old Value",
                "action": "Drop",
                "func": "Test",
                "path": DiffPath(
                    parent=DiffPath(),
                    schema={"properties": {"root": {"alias": "Root Alias"}}},
                    name="root",
                ),
            },
            (),
            DetailLevel.BASIC,
        )
        compare_objects(
            static_data,
            dynamic_data,
        )

    def test_basic_update(self):
        static_data = {
            "Action": [{"text": "Value Update"}],
            "func": "Test",
            "path": [{"alias": "Root Alias", "name": "root"}],
            "Attribute Path": [{"text": "$['root']"}],
            "Location Path": [{"text": "$['root']"}],
            "Change Level": [{"text": "Major"}],
            "opcodes": [("replace", 0, 1, 0, 1)],
            "Value (previous)": [{"text": '["A"]'}],
            "Value (updated)": [{"text": '["B"]'}],
            "Attribute (previous)": [
                {"text": "A", "format": {"bold": True, "color": "#FF3300"}}
            ],
            "Attribute (updated)": [
                {"text": "B", "format": {"bold": True, "color": "#FF3300"}}
            ],
            "Impact": [{"text": "Root Alias"}],
        }
        dynamic_data = DiffItemDirector.get_diff_item(
            {
                "old": "A",
                "new": "B",
                "action": "Value Update",
                "func": "Test",
                "path": DiffPath(
                    parent=DiffPath(),
                    schema={"properties": {"root": {"alias": "Root Alias"}}},
                    name="root",
                ),
            },
            (),
            DetailLevel.BASIC,
        )
        compare_objects(
            static_data,
            dynamic_data,
        )

    def test_advanced_add(self):
        static_data = {
            "Action": [{"text": "Add"}],
            "func": "Test",
            "path": [{"alias": "Root Alias", "name": "root"}],
            "Attribute Path": [{"text": "$['root']"}],
            "Location Path": [{"text": "$['root']"}],
            "Attribute (updated)": [{"text": "New Value"}],
            "Impact": [{"text": "root"}],
        }
        dynamic_data = DiffItemDirector.get_diff_item(
            {
                "new": "New Value",
                "action": "Add",
                "func": "Test",
                "path": DiffPath(
                    parent=DiffPath(),
                    schema={"properties": {"root": {"alias": "Root Alias"}}},
                    name="root",
                ),
            },
            (),
            DetailLevel.ADVANCED,
        )
        compare_objects(
            static_data,
            dynamic_data,
        )

    def test_advanced_drop(self):
        static_data = {
            "Action": [{"text": "Drop"}],
            "func": "Test",
            "path": [{"alias": "Root Alias", "name": "root"}],
            "Attribute Path": [{"text": "$['root']"}],
            "Location Path": [{"text": "$['root']"}],
            "Attribute (previous)": [{"text": "Old Value"}],
            "Impact": [{"text": "root"}],
        }
        dynamic_data = DiffItemDirector.get_diff_item(
            {
                "old": "Old Value",
                "action": "Drop",
                "func": "Test",
                "path": DiffPath(
                    parent=DiffPath(),
                    schema={"properties": {"root": {"alias": "Root Alias"}}},
                    name="root",
                ),
            },
            (),
            DetailLevel.ADVANCED,
        )
        compare_objects(
            static_data,
            dynamic_data,
        )

    def test_advanced_update(self):
        static_data = {
            "Action": [{"text": "Value Update"}],
            "func": "Test",
            "path": [{"alias": "Root Alias", "name": "root"}],
            "Attribute Path": [{"text": "$['root']"}],
            "Location Path": [{"text": "$['root']"}],
            "Change Level": [{"text": "Major"}],
            "opcodes": [("replace", 0, 1, 0, 1)],
            "Value (previous)": [{"text": '["A"]'}],
            "Value (updated)": [{"text": '["B"]'}],
            "Attribute (previous)": [
                {"text": "A", "format": {"bold": True, "color": "#FF3300"}}
            ],
            "Attribute (updated)": [
                {"text": "B", "format": {"bold": True, "color": "#FF3300"}}
            ],
            "Impact": [{"text": "root"}],
        }
        dynamic_data = DiffItemDirector.get_diff_item(
            {
                "old": "A",
                "new": "B",
                "action": "Value Update",
                "func": "Test",
                "path": DiffPath(
                    parent=DiffPath(),
                    schema={"properties": {"root": {"alias": "Root Alias"}}},
                    name="root",
                ),
            },
            (),
            DetailLevel.ADVANCED,
        )
        compare_objects(
            static_data,
            dynamic_data,
        )


if __name__ == "__main__":
    unittest.main()
