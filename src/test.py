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
        msg = p.award_points("10 points to Gryffindor", TEST_PREFECTS[0])
        self.assertIn("<@prefect> Gryffindor gets 10 points", msg[0])

    def test_adding_points_not_by_prefect(self):
        p = PointCounter(TEST_PREFECTS, points_file=TEST_POINTS)
        msg = p.award_points("6 points to Gryffindor", "harry potter")
        for m in msg:
            self.assertIn("<@harry potter> Gryffindor gets 1 point", m)

    def test_adding_one_point(self):
        p = PointCounter(TEST_PREFECTS, points_file=TEST_POINTS)
        msg = p.award_points("oNe point to Gryffindor", "harry potter")
        for m in msg:
            self.assertIn("<@harry potter> Gryffindor gets 1 point", m)

    def test_adding_one_point_to_slytherin(self):
        msg = self.p.award_points(
            "1 point to slytherin for @benkraft making slackbot"
            " listen for '911' mentions in 1s and 0s", "harry potter")
        for m in msg:
            self.assertIn("<@harry potter> Slytherin gets 1 point", m)

    def test_subtracting_one_point_not_prefect(self):
        msgs = self.p.award_points("oNe point from Gryffindor", "harry potter")
        self.assertEqual(len(msgs), 0)

    def test_works_with_usernames(self):
        message = "1 point to ravenclaw <@U0NJ1PH1R>"
        for m in self.p.award_points(message, "nymphadora tonks"):
            self.assertIn("<@nymphadora tonks> Ravenclaw gets 1 point", m)

    def test_works_with_dumbledore_with_prefect(self):
        message = "Dumbledore awards 1 point to ravenclaw <@U0NJ1PH1R>"
        for m in self.p.award_points(message, "prefect"):
            self.assertEqual(
                m[0], "Awards 1 point to Ravenclaw  :party_ravenclaw:")
            self.assertEqual(m[1], "dumbledore")

    def test_works_with_dumbledore_with_prefect_with_reason(self):
        message = "Dumbledore awards 1 point to ravenclaw <@U0NJ1PH1R> for making reason works"
        for m in self.p.award_points(message, "prefect"):
            self.assertEqual(
                m[0], "Awards 1 point to Ravenclaw for making reason works  :party_ravenclaw:")
            self.assertEqual(m[1], "dumbledore")

    def test_works_with_dumbledore_takes_away_with_prefect(self):
        self.p.award_points("10 points to Gryffindor", TEST_PREFECTS[0])
        message = "Dumbledore takes away 1 point from Gryffindor <@U0NJ1PH1R> because of breaking reason"
        for m in self.p.award_points(message, "prefect"):
            self.assertEqual(
                m[0], "Takes away 1 point from Gryffindor for breaking reason  "
                ":party_ravenclaw: :party_hufflepuff: :party_slytherin:")
            self.assertEqual(m[1], "dumbledore")

    def test_works_with_dumbledore_normal(self):
        message = "Awards 1 point to ravenclaw <@U0NJ1PH1R> for cheating"
        for m in self.p.award_points(message, "nymphadora tonks"):
            self.assertIn("<@nymphadora tonks> Ravenclaw gets 1 point", m)

    def test_works_with_dumbledore_says_with_prefect(self):
        message = "Dumbledore says ho ho ho :party-khan:"
        msg = self.p.award_points(message, "prefect")
        self.assertIsInstance(msg[0], tuple)
        msg_text, char = msg[0]
        self.assertEqual(msg_text, "ho ho ho :party-khan:")
        self.assertEqual(char, "dumbledore")

    def test_works_with_dumbledore_says_no_prefect(self):
        message = "Dumbledore says ho ho ho :party-khan:"
        msg = self.p.award_points(message, "Harry potter")
        self.assertEqual(len(msg), 0)

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
