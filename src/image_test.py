import unittest

from consts import HOUSES
from cup_image import image_for_scores


class TestImageRender(unittest.TestCase):

    def test_generate_image(self):
        output_image = image_for_scores({
            HOUSES[0]: 1,
            HOUSES[1]: 1200,
            HOUSES[2]: 1,
            HOUSES[3]: 1200,
        })
        print(output_image)


if __name__ == "__main__":
    unittest.main()
