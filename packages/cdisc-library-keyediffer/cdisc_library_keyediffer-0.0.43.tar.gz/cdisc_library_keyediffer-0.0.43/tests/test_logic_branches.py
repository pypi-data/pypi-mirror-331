import unittest
from tests.helpers import compare_with_file


class TestLogicBranches(unittest.TestCase):
    def test_composite_key(self):
        compare_with_file("composite_key")

    def test_dict_drop_str(self):
        compare_with_file("dict_drop_str")

    def test_dict_add_str(self):
        compare_with_file("dict_add_str")

    def test_dict_drop_list(self):
        compare_with_file("dict_drop_list")

    def test_dict_add_list(self):
        compare_with_file("dict_add_list")

    def test_duplicates(self):
        compare_with_file("duplicates")

    def test_list_drop_dict(self):
        compare_with_file("list_drop_dict")

    def test_list_add_dict(self):
        compare_with_file("list_add_dict")

    def test_list_drop_item(self):
        compare_with_file("list_drop_item")

    def test_list_add_item(self):
        compare_with_file("list_add_item")

    def test_list_item_type(self):
        compare_with_file("list_item_type")

    def test_minor_major(self):
        compare_with_file("minor_major")

    def test_multikey(self):
        compare_with_file("multikey")

    def test_text(self):
        compare_with_file("text")

    def test_value(self):
        compare_with_file("value")


if __name__ == "__main__":
    unittest.main()
