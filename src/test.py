"""
Test point counter functionality
"""
from main import PointCounter, get_client
import unittest

from google.auth import exceptions

TEST_PREFECTS = ["prefect"]
TEST_POINTS = "dataset/hackathon.test.json"


class TestPointCounter(unittest.TestCase):
    """Initialize a point counter and test response messages"""

    def setUp(self):
        self.p = PointCounter(TEST_PREFECTS, points_file=TEST_POINTS)

    def test_post_update(self):
        try:
            get_client()
        except exceptions.DefaultCredentialsError:
            print("Skipping bucket test - no permission file found!")
            return

        p = PointCounter(TEST_PREFECTS, points_file=TEST_POINTS, reset=True)
        p.award_points("6 points to Gryffindor", TEST_PREFECTS[0])
        p.post_update()

        p2 = PointCounter(TEST_PREFECTS, points_file=TEST_POINTS)
        self.assertEqual(p2.points['Gryffindor'], 6)

    def test_adding_points(self):
        p = PointCounter(TEST_PREFECTS, points_file=TEST_POINTS)
        msg = p.award_points("6 points to Gryffindor", TEST_PREFECTS[0])
        self.assertEqual(msg[0], "Gryffindor gets 6 points")

    def test_adding_points_not_by_prefect(self):
        p = PointCounter(TEST_PREFECTS, points_file=TEST_POINTS)
        msg = p.award_points("6 points to Gryffindor", "harry potter")
        for m in msg:
            self.assertEqual(m, "Gryffindor gets 1 point")

    def test_adding_one_point(self):
        p = PointCounter(TEST_PREFECTS, points_file=TEST_POINTS)
        msg = p.award_points("oNe point to Gryffindor", "harry potter")
        for m in msg:
            self.assertEqual(m, "Gryffindor gets 1 point")

    def test_adding_one_point_to_slytherin(self):
        msg = self.p.award_points(
            "1 point to slytherin for @benkraft making slackbot"
            " listen for '911' mentions in 1s and 0s", "harry potter")
        for m in msg:
            self.assertEqual(m, "Slytherin gets 1 point")

    def test_subtracting_one_point(self):
        for m in self.p.award_points("oNe point from Gryffindor", "harry potter"):
            self.assertEqual(m, "Gryffindor loses 1 point")

    def test_works_with_usernames(self):
        message = "1 point to ravenclaw <@U0NJ1PH1R>"
        for m in self.p.award_points(message, "nymphadora tonks"):
            self.assertEqual(m, "Ravenclaw gets 1 point")

    def test_calculate_standings(self):
        p = PointCounter(TEST_PREFECTS, points_file=TEST_POINTS)
        p.award_points("6 points to Gryffindor", TEST_PREFECTS[0])
        p.award_points("7 points to Ravenclaw", TEST_PREFECTS[0])
        p.award_points("8 points to Hufflepuff", TEST_PREFECTS[0])
        p.award_points("9 points to Slytherin", TEST_PREFECTS[0])
        for m in p.print_status():
            print(m)


if __name__ == "__main__":
    unittest.main()
