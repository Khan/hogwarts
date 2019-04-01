import unittest

from consts import HOUSES
from cup_image import image_for_scores


class TestImageRender(unittest.TestCase):

    def test_generate_image(self):
        cases = {
            "empty": [0, 0, 0, 0],
            "extreme": [1, 1200, 1, 1200],
            "extreme_empty": [0, 1200, 0, 1200],
            "same_early": [1, 1, 1, 1],
            "close_early": [1, 10, 1, 20],
            "same": [400, 400, 400, 400],
            "close_middle": [610, 620, 580, 600],
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
