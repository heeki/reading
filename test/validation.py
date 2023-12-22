import json
import unittest
from lib.domain.group import Group

class Tests(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_group(self):
        # baseline
        group = Group()
        baseline_group_list = group.list_groups()
        baseline_group_count = len(baseline_group_list)

        # create group
        new_group_name = "testing"
        response = group.create_group(new_group_name)
        uid = response["Item"]["uid"]
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        updated_group_count = len(group.list_groups())
        self.assertEqual(updated_group_count, baseline_group_count+1)
        print(f"created group with uid={uid}")

        # get group
        response = group.get_group(uid)
        self.assertEqual(uid, response[0]["uid"]["S"])

        # get group with name
        response = group.get_group_with_description(new_group_name)
        print(json.dumps(response))
        self.assertEqual(new_group_name, response[0]["description"]["S"])

        # delete group
        response = group.delete_group(uid)
        updated_group_count = len(group.list_groups())
        self.assertEqual(updated_group_count, baseline_group_count)
        print(f"deleted group with uid={uid}")

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(Tests("test_group"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
