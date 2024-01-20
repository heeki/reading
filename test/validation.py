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
        self.test_id = str(uuid.uuid4())[-12:]
        self.invalid_uid = "invalid"
        self.test_date = datetime.datetime(2024, 1, 1, 9, 0, 0).isoformat()

        group = Group()
        groups = group.list_groups()
        self.test_group_id = groups[0]["uid"]

    def tearDown(self):
        pass

    def test_group(self):
        # baseline
        group = Group()
        baseline_group_list = group.list_groups()
        baseline_group_count = len(baseline_group_list)
        print()

        # create group
        new_group_name = f"test group {self.test_id}"
        response = group.create_group(new_group_name)
        uid = response["uid"]
        self.assertIsNotNone(uid)
        updated_group_count = len(group.list_groups())
        self.assertEqual(updated_group_count, baseline_group_count+1)
        print(f"created group with uid={uid}, base_count={baseline_group_count}, updated_count={updated_group_count}")

        # get group
        response = group.get_group(uid)
        self.assertEqual(uid, response["uid"])

        # get invalid group
        response = group.get_group(self.invalid_uid)
        self.assertEqual({}, response)

        # get group by name
        response = group.get_group_by_description(new_group_name)
        print(json.dumps(response))
        self.assertEqual(new_group_name, response["description"])

        # get group by invalid name
        response = group.get_group_by_description(self.invalid_uid)
        self.assertEqual({}, response)

        # update group
        updated_group_name = f"updated group {self.test_id}"
        response = group.update_group(uid, updated_group_name)
        self.assertEqual(updated_group_name, response["description"])
        print(f"updated group with uid={uid}")

        # update invalid group
        updated_group_name = f"updated group {self.test_id}"
        response = group.update_group(self.invalid_uid, updated_group_name)
        self.assertEqual("ConditionalCheckFailedException", response["error"])

        # delete group
        response = group.delete_group(uid)
        updated_group_count = len(group.list_groups())
        self.assertEqual(updated_group_count, baseline_group_count)
        print(f"deleted group with uid={uid}, base_count={baseline_group_count}, final_count={updated_group_count}")

        # delete invalid group
        response = group.delete_group(self.invalid_uid)
        self.assertEqual({}, response)

    def test_group_stats(self):
        print()
        group = Group()
        response = group.get_group_stats()
        print(json.dumps(response))

    def test_user(self):
        # baseline
        user = User()
        baseline_user_list = user.list_users()
        baseline_user_count = len(baseline_user_list)
        print()

        # create user
        new_user_name = f"test user {self.test_id}"
        new_user_email = "test@example.com"
        new_user_is_subscribed = True
        new_user_group_ids = ["d3aa4ef7-b938-4d0e-b936-272e32139dce"]
        new_user_plan_ids = ["0369ca53-0374-4869-905d-56c204ff1048"]
        response = user.create_user(new_user_name, new_user_email, new_user_is_subscribed, new_user_group_ids, new_user_plan_ids)
        uid = response["uid"]
        self.assertIsNotNone(uid)
        updated_user_count = len(user.list_users())
        self.assertEqual(updated_user_count, baseline_user_count+1)
        print(f"created user with uid={uid}, base_count={baseline_user_count}, updated_count={updated_user_count}")

        # get user
        response = user.get_user(uid)
        self.assertEqual(uid, response["uid"])

        # get invalid user
        response = user.get_user(self.invalid_uid)
        self.assertEqual({}, response)

        # get user by name
        response = user.get_user_by_description(new_user_name)
        print(json.dumps(response))
        self.assertEqual(new_user_name, response["description"])

        # update user
        updated_user_name = f"updated user {self.test_id}"
        updated_user_email = "updated@example.com"
        updated_user_is_subscribed = True
        updated_user_group_ids = ["22ca8c3d-737e-4571-a9a3-43c2d2c04e62"]
        updated_user_plan_ids = ["928f77fc-e9fd-44b0-8820-61a1746fda84"]
        response = user.update_user(uid, updated_user_name, updated_user_email, updated_user_is_subscribed, updated_user_group_ids, updated_user_plan_ids)
        self.assertEqual(updated_user_name, response["description"])
        self.assertEqual(updated_user_email, response["email"])
        self.assertEqual(updated_user_is_subscribed, response["is_subscribed"])
        self.assertEqual(updated_user_group_ids, response["group_ids"])
        self.assertEqual(updated_user_plan_ids, response["plan_ids"])
        print(f"updated user with uid={uid}")

        # unsubscribe
        response = user.unsubscribe_user(uid)
        self.assertEqual(False, response["is_subscribed"])

        # subscribe
        response = user.subscribe_user(uid)
        self.assertEqual(True, response["is_subscribed"])

        # update invalid user
        updated_user_name = f"updated user {self.test_id}"
        response = user.update_user(self.invalid_uid, updated_user_name, updated_user_email, updated_user_is_subscribed, updated_user_group_ids, updated_user_plan_ids)
        self.assertEqual("ConditionalCheckFailedException", response["error"])

        # delete user
        response = user.delete_user(uid)
        updated_user_count = len(user.list_users())
        self.assertEqual(updated_user_count, baseline_user_count)
        print(f"deleted user with uid={uid}, base_count={baseline_user_count}, final_count={updated_user_count}")

        # delete invalid user
        response = user.delete_user(self.invalid_uid)
        self.assertEqual({}, response)

    def test_user_by_group(self):
        print()
        group = Group()
        groups = group.list_groups()

        user = User()
        for g in groups:
            group_id = g.get("uid")
            is_subscribed = True
            response = user.list_users_by_group(group_id, is_subscribed)
            print(f"group_id={group_id} user_count={len(response)}")
        print("listed users by group_id")

    def test_user_by_plan(self):
        print()
        plan = Plan()
        plans = plan.list_plans()

        user = User()
        for p in plans:
            plan_id = p.get("uid")
            is_subscribed = True
            response = user.list_users_by_plan(plan_id, is_subscribed)
            print(f"plan_id={plan_id} user_count={len(response)} is_subscribed={is_subscribed}")
            is_subscribed = False
            response = user.list_users_by_plan(plan_id, is_subscribed)
            print(f"plan_id={plan_id} user_count={len(response)} is_subscribed={is_subscribed}")
        print("listed users by plan_id")

    def test_user_stats(self):
        print()
        user = User()
        user_id = "f975dc69-b0e9-41f1-bfb4-65fc877c10e9"
        response = user.get_user_stats(user_id)
        print(json.dumps(response))
        print("printed user stats")

    def test_plan(self):
        # baseline
        plan = Plan()
        baseline_plan_list = plan.list_plans()
        baseline_plan_count = len(baseline_plan_list)
        print()

        # create plan
        new_plan_name = f"test plan {self.test_id}"
        response = plan.create_plan(new_plan_name)
        uid = response["uid"]
        self.assertIsNotNone(uid)
        updated_plan_count = len(plan.list_plans())
        self.assertEqual(updated_plan_count, baseline_plan_count+1)
        print(f"created plan with uid={uid}, base_count={baseline_plan_count}, updated_count={updated_plan_count}")

        # get plan
        response = plan.get_plan(uid)
        self.assertEqual(uid, response["uid"])

        # get invalid plan
        response = plan.get_plan(self.invalid_uid)
        self.assertEqual({}, response)

        # get plan by name
        response = plan.get_plan_by_description(new_plan_name)
        print(json.dumps(response))
        self.assertEqual(new_plan_name, response["description"])

        # update plan
        updated_plan_name = f"updated plan {self.test_id}"
        response = plan.update_plan(uid, updated_plan_name)
        self.assertEqual(updated_plan_name, response["description"])
        print(f"updated plan with uid={uid}")

        # update invalid plan
        updated_plan_name = f"updated plan {self.test_id}"
        response = plan.update_plan(self.invalid_uid, updated_plan_name)
        self.assertEqual("ConditionalCheckFailedException", response["error"])

        # delete plan
        response = plan.delete_plan(uid)
        updated_plan_count = len(plan.list_plans())
        self.assertEqual(updated_plan_count, baseline_plan_count)
        print(f"deleted plan with uid={uid}, base_count={baseline_plan_count}, final_count={updated_plan_count}")

        # delete invalid plan
        response = plan.delete_plan(self.invalid_uid)
        self.assertEqual({}, response)

    def test_reading(self):
        # baseline
        reading = Reading()
        baseline_reading_list = reading.list_readings()
        baseline_reading_count = len(baseline_reading_list)
        print()

        # create reading
        new_reading_name = f"test reading {self.test_id}"
        new_reading_body = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        new_reading_plan_id = str(uuid.uuid4())
        new_reading_sent_date = self.test_date
        response = reading.create_reading(new_reading_name, new_reading_body, new_reading_plan_id, new_reading_sent_date)
        uid = response["uid"]
        self.assertIsNotNone(uid)
        updated_reading_count = len(reading.list_readings())
        self.assertEqual(updated_reading_count, baseline_reading_count+1)
        print(f"created reading with uid={uid}, base_count={baseline_reading_count}, updated_count={updated_reading_count}")

        # get reading
        response = reading.get_reading(uid)
        self.assertEqual(uid, response["uid"])

        # get invalid reading
        response = reading.get_reading(self.invalid_uid)
        self.assertEqual({}, response)

        # get reading by name
        response = reading.get_reading_by_description(new_reading_name)
        print(json.dumps(response))
        self.assertEqual(new_reading_name, response["description"])

        # update reading
        updated_reading_name = f"updated reading {self.test_id}"
        updated_reading_body = "Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem."
        updated_reading_plan_id = str(uuid.uuid4())
        updated_reading_sent_date = self.test_date
        response = reading.update_reading(uid, updated_reading_name, updated_reading_body, updated_reading_plan_id, updated_reading_sent_date)
        self.assertEqual(updated_reading_name, response["description"])
        self.assertEqual(updated_reading_body, response["body"])
        self.assertEqual(updated_reading_plan_id, response["plan_id"])
        self.assertEqual(updated_reading_sent_date, response["sent_date"])
        print(f"updated reading with uid={uid}")

        # update invalid reading
        updated_reading_name = f"updated reading {self.test_id}"
        response = reading.update_reading(self.invalid_uid, updated_reading_name, updated_reading_body, updated_reading_plan_id, updated_reading_sent_date)
        self.assertEqual("ConditionalCheckFailedException", response["error"])

        # delete reading
        response = reading.delete_reading(uid)
        updated_reading_count = len(reading.list_readings())
        self.assertEqual(updated_reading_count, baseline_reading_count)
        print(f"deleted reading with uid={uid}, base_count={baseline_reading_count}, final_count={updated_reading_count}")

        # delete invalid reading
        response = reading.delete_reading(self.invalid_uid)
        self.assertEqual({}, response)

    def test_reading_by_date(self):
        print()
        reading = Reading()
        new_reading_name = f"test reading {self.test_id}"
        new_reading_body = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        new_reading_plan_id = str(uuid.uuid4())
        new_reading_sent_date = self.test_date
        response = reading.create_reading(new_reading_name, new_reading_body, new_reading_plan_id, new_reading_sent_date)
        uid = response["uid"]

        response = reading.get_reading_by_date(new_reading_sent_date)
        self.assertEqual(new_reading_sent_date, response["sent_date"])

        shortened_date = new_reading_sent_date.split("T")[0]
        response = reading.get_reading_by_date(shortened_date)
        self.assertEqual(new_reading_sent_date, response["sent_date"])

        response = reading.delete_reading(uid)

    def test_reading_completion(self):
        print()
        reading = Reading()
        new_reading_name = f"test reading {self.test_id}"
        new_reading_body = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        new_reading_plan_id = str(uuid.uuid4())
        new_reading_sent_date = self.test_date
        response = reading.create_reading(new_reading_name, new_reading_body, new_reading_plan_id, new_reading_sent_date)
        uid = response["uid"]

        user_id = "f975dc69-b0e9-41f1-bfb4-65fc877c10e9"
        response = reading.add_user_completion(uid, user_id)
        read_by = json.loads(response["read_by"])
        print(json.dumps(read_by))
        print("added user reading completion")
        self.assertEqual(user_id, read_by[0]["user_id"])

        response = reading.list_readings_by_user(user_id)
        print("user reading count={}".format(len(response)))

        group_id = "84db3228-0174-45bf-8b67-2e9c62b5ecf7"
        response = reading.list_readings_by_group(group_id)
        print("group reading count={}".format(len(response)))

        response = reading.delete_reading(uid)

    def test_reading_update_sent_count(self):
        print()
        reading = Reading()
        new_reading_name = f"test reading {self.test_id}"
        new_reading_body = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        new_reading_plan_id = str(uuid.uuid4())
        new_reading_sent_date = self.test_date
        response = reading.create_reading(new_reading_name, new_reading_body, new_reading_plan_id, new_reading_sent_date)
        uid = response["uid"]

        updated_reading_sent_count = {self.test_group_id: 3}
        response = reading.update_reading_sent_count(uid, updated_reading_sent_count)
        response = reading.get_reading(uid)
        self.assertEqual(json.dumps(updated_reading_sent_count), json.dumps(json.loads(response["sent_count"])))

        response = reading.delete_reading(uid)

    def test_reading_current_sent_count(self):
        print()
        reading = Reading()
        response = reading.get_current_sent_count()
        print(json.dumps(response))

if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTest(Tests("test_group"))
    suite.addTest(Tests("test_group_stats"))
    suite.addTest(Tests("test_user"))
    suite.addTest(Tests("test_user_by_group"))
    suite.addTest(Tests("test_user_by_plan"))
    suite.addTest(Tests("test_user_stats"))
    suite.addTest(Tests("test_plan"))
    suite.addTest(Tests("test_reading"))
    suite.addTest(Tests("test_reading_by_date"))
    suite.addTest(Tests("test_reading_completion"))
    suite.addTest(Tests("test_reading_update_sent_count"))
    suite.addTest(Tests("test_reading_current_sent_count"))
    runner = unittest.TextTestRunner()
    runner.run(suite)
