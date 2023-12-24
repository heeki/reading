import json
import unittest
from lib.domain.group import Group
from lib.domain.user import User
from lib.domain.plan import Plan

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

    def test_user(self):
        # baseline
        user = User()
        baseline_user_list = user.list_users()
        baseline_user_count = len(baseline_user_list)

        # create user
        new_user_name = "test"
        new_user_email = "test@example.com"
        response = user.create_user(new_user_name, new_user_email)
        uid = response["Item"]["uid"]
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        updated_user_count = len(user.list_users())
        self.assertEqual(updated_user_count, baseline_user_count+1)
        print(f"created user with uid={uid}")

        # get user
        response = user.get_user(uid)
        self.assertEqual(uid, response[0]["uid"]["S"])

        # get group with name
        response = user.get_user_with_description(new_user_name)
        print(json.dumps(response))
        self.assertEqual(new_user_name, response[0]["description"]["S"])

        # delete user
        response = user.delete_user(uid)
        updated_user_count = len(user.list_users())
        self.assertEqual(updated_user_count, baseline_user_count)
        print(f"deleted user with uid={uid}")

    def test_plan(self):
        # baseline
        plan = Plan()
        baseline_plan_list = plan.list_plans()
        baseline_plan_count = len(baseline_plan_list)

        # create plan
        new_plan_name = "testing"
        response = plan.create_plan(new_plan_name)
        uid = response["Item"]["uid"]
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        updated_plan_count = len(plan.list_plans())
        self.assertEqual(updated_plan_count, baseline_plan_count+1)
        print(f"created plan with uid={uid}")

        # get plan
        response = plan.get_plan(uid)
        self.assertEqual(uid, response[0]["uid"]["S"])

        # get plan with name
        response = plan.get_plan_with_description(new_plan_name)
        print(json.dumps(response))
        self.assertEqual(new_plan_name, response[0]["description"]["S"])

        # delete plan
        response = plan.delete_plan(uid)
        updated_plan_count = len(plan.list_plans())
        self.assertEqual(updated_plan_count, baseline_plan_count)
        print(f"deleted plan with uid={uid}")

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(Tests("test_group"))
    suite.addTest(Tests("test_user"))
    suite.addTest(Tests("test_plan"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
