import datetime
import json
import time
import unittest
import uuid
from lib.encoders import DateTimeEncoder
from lib.domain.group import Group
from lib.domain.user import User
from lib.domain.plan import Plan
from lib.domain.reading import Reading

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
        print()

        # create group
        new_group_name = "test group"
        response = group.create_group(new_group_name)
        uid = response["uid"]
        self.assertIsNotNone(uid)
        updated_group_count = len(group.list_groups())
        self.assertEqual(updated_group_count, baseline_group_count+1)
        print(f"created group with uid={uid}, base_count={baseline_group_count}, updated_count={updated_group_count}")

        # get group
        response = group.get_group(uid)
        self.assertEqual(uid, response["uid"])

        # get group with name
        response = group.get_group_with_description(new_group_name)
        print(json.dumps(response))
        self.assertEqual(new_group_name, response["description"])

        # update group
        updated_group_name = "updated group"
        response = group.update_group(uid, updated_group_name)
        # print(json.dumps(response, cls=DateTimeEncoder))
        self.assertEqual(updated_group_name, response["description"])
        print(f"updated group with uid={uid}")

        # delete group
        response = group.delete_group(uid)
        updated_group_count = len(group.list_groups())
        self.assertEqual(updated_group_count, baseline_group_count)
        print(f"deleted group with uid={uid}, base_count={baseline_group_count}, final_count={updated_group_count}")

    def test_user(self):
        # baseline
        user = User()
        baseline_user_list = user.list_users()
        baseline_user_count = len(baseline_user_list)
        print()

        # create user
        new_user_name = "test user"
        new_user_email = "test@example.com"
        response = user.create_user(new_user_name, new_user_email)
        uid = response["Item"]["uid"]
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        updated_user_count = len(user.list_users())
        self.assertEqual(updated_user_count, baseline_user_count+1)
        print(f"created user with uid={uid}, base_count={baseline_user_count}, updated_count={updated_user_count}")

        # get user
        response = user.get_user(uid)
        self.assertEqual(uid, response[0]["uid"]["S"])

        # get group with name
        response = user.get_user_with_description(new_user_name)
        print(json.dumps(response))
        self.assertEqual(new_user_name, response[0]["description"]["S"])

        # update user
        updated_user_name = "updated user"
        updated_user_email = "updated@example.com"
        response = user.update_user(uid, updated_user_name, updated_user_email)
        self.assertEqual(updated_user_name, response["Attributes"]["description"]["S"])
        self.assertEqual(updated_user_email, response["Attributes"]["email"]["S"])
        print(f"updated user with uid={uid}")

        # delete user
        response = user.delete_user(uid)
        updated_user_count = len(user.list_users())
        self.assertEqual(updated_user_count, baseline_user_count)
        print(f"deleted user with uid={uid}, base_count={baseline_user_count}, final_count={updated_user_count}")

    def test_plan(self):
        # baseline
        plan = Plan()
        baseline_plan_list = plan.list_plans()
        baseline_plan_count = len(baseline_plan_list)
        print()

        # create plan
        new_plan_name = "test plan"
        response = plan.create_plan(new_plan_name)
        uid = response["Item"]["uid"]
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        updated_plan_count = len(plan.list_plans())
        self.assertEqual(updated_plan_count, baseline_plan_count+1)
        print(f"created plan with uid={uid}, base_count={baseline_plan_count}, updated_count={updated_plan_count}")

        # get plan
        response = plan.get_plan(uid)
        self.assertEqual(uid, response[0]["uid"]["S"])

        # get plan with name
        response = plan.get_plan_with_description(new_plan_name)
        print(json.dumps(response))
        self.assertEqual(new_plan_name, response[0]["description"]["S"])

        # update plan
        updated_plan_name = "updated plan"
        response = plan.update_plan(uid, updated_plan_name)
        self.assertEqual(updated_plan_name, response["Attributes"]["description"]["S"])
        print(f"updated plan with uid={uid}")

        # delete plan
        response = plan.delete_plan(uid)
        updated_plan_count = len(plan.list_plans())
        self.assertEqual(updated_plan_count, baseline_plan_count)
        print(f"deleted plan with uid={uid}, base_count={baseline_plan_count}, final_count={updated_plan_count}")

    def test_reading(self):
        # baseline
        reading = Reading()
        baseline_reading_list = reading.list_readings()
        baseline_reading_count = len(baseline_reading_list)
        print()

        # create reading
        new_reading_name = "test reading"
        new_reading_body = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        new_reading_plan_id = str(uuid.uuid4())
        new_reading_sent_date = datetime.datetime.now().isoformat()
        new_reading_sent_count = "1"
        response = reading.create_reading(new_reading_name, new_reading_body, new_reading_plan_id, new_reading_sent_date, new_reading_sent_count)
        uid = response["Item"]["uid"]
        self.assertEqual(response["ResponseMetadata"]["HTTPStatusCode"], 200)
        updated_reading_count = len(reading.list_readings())
        self.assertEqual(updated_reading_count, baseline_reading_count+1)
        print(f"created reading with uid={uid}, base_count={baseline_reading_count}, updated_count={updated_reading_count}")

        # get reading
        response = reading.get_reading(uid)
        self.assertEqual(uid, response[0]["uid"]["S"])

        # get reading with name
        response = reading.get_reading_with_description(new_reading_name)
        print(json.dumps(response))
        self.assertEqual(new_reading_name, response[0]["description"]["S"])

        # update reading
        updated_reading_name = "updated reading"
        updated_reading_body = "Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem."
        updated_reading_plan_id = str(uuid.uuid4())
        updated_reading_sent_date = datetime.datetime.now().isoformat()
        updated_reading_sent_count = "1"
        response = reading.update_reading(uid, updated_reading_name, updated_reading_body, updated_reading_plan_id, updated_reading_sent_date, updated_reading_sent_count)
        self.assertEqual(updated_reading_name, response["Attributes"]["description"]["S"])
        self.assertEqual(updated_reading_body, response["Attributes"]["body"]["S"])
        self.assertEqual(updated_reading_plan_id, response["Attributes"]["plan_id"]["S"])
        self.assertEqual(updated_reading_sent_date, response["Attributes"]["sent_date"]["S"])
        self.assertEqual(updated_reading_sent_count, response["Attributes"]["sent_count"]["N"])
        print(f"updated reading with uid={uid}")

        # delete reading
        response = reading.delete_reading(uid)
        updated_reading_count = len(reading.list_readings())
        self.assertEqual(updated_reading_count, baseline_reading_count)
        print(f"deleted reading with uid={uid}, base_count={baseline_reading_count}, final_count={updated_reading_count}")

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(Tests("test_group"))
    suite.addTest(Tests("test_user"))
    suite.addTest(Tests("test_plan"))
    suite.addTest(Tests("test_reading"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
