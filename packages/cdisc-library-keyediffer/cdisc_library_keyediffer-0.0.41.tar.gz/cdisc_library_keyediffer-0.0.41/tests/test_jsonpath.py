from json import dumps
import unittest
from jsonpath_ng.ext import parse
from keyediffer.utils.json_utils import get_json
from tests.helpers import run_diff


class TestJSONPath(unittest.TestCase):
    @staticmethod
    def jsonpath_compare(jsonpath, row, field_name, filename):
        if field_name in row:
            static_data = "".join(part["text"] for part in row[field_name])
            dynamic_data = [
                match.value
                for match in jsonpath.find(get_json(f"tests/data/{filename}.json"))
            ]
            assert (
                len(dynamic_data) == 1 and static_data == dynamic_data[0]
            ), f"\n{dumps(static_data, sort_keys=True)}\n{dumps(dynamic_data, sort_keys=True)}"

    def test_jsonpath(self):
        prefix = "value"
        diffs = run_diff(prefix)
        advanced = next(filter(lambda item: item["title"] == "Advanced", diffs))["body"]
        for row in advanced:
            jsonpath = parse(row["Attribute Path"][0]["text"])
            TestJSONPath.jsonpath_compare(
                jsonpath, row, "Attribute (previous)", f"{prefix}_previous"
            )
            TestJSONPath.jsonpath_compare(
                jsonpath, row, "Attribute (updated)", f"{prefix}_updated"
            )


if __name__ == "__main__":
    unittest.main()
