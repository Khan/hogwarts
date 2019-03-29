import unittest

from consts import HOUSES
from cup_image import image_for_scores


class TestImageRender(unittest.TestCase):

    def test_generate_image(self):
        cases = {
            "extreme": [1, 1200, 1, 1200],
            "close_early": [1, 10, 1, 20],
            "close_middle": [600, 700, 800, 900],
            "close_late": [1000, 1100, 1000, 1200],
            "leader": [500, 600, 700, 1000],
        }
        for case, scores in cases.items():
            outfile = image_for_scores({
                HOUSES[i]: scores[i] for i, _ in enumerate(HOUSES)
            }, imgname=case)
            print(f"Image outputted to: {outfile}")


if __name__ == "__main__":
    unittest.main()
