import unittest
from bb.utils import file_utils
from test.testutils import test_resource


class FileUtilsTest(unittest.TestCase):

    def test_read_yaml_file(self):
        yamlFilePath = test_resource.path("utils", "file_utils", "test.yml")
        yaml = file_utils.read_yaml_file(yamlFilePath)
        self.assertEqual(True, yaml["test"])


if __name__ == '__main__':
    unittest.main()
