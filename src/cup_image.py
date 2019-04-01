import os
import tempfile
from typing import Dict

from PIL import Image, ImageDraw, ImageFont

from consts import HOUSES, IMAGE_PATH, MAX_POINTS

# Tuples of (x1, y1, x2, y2)
BAR_RECTS = {
    "Gryffindor": (210, 57, 346, 514),
    "Ravenclaw": (400, 57, 536, 514),
    "Hufflepuff": (585, 57, 721, 514),
    "Slytherin": (769, 57, 913, 514),
}

# Space below the bottom of the bar to superimpose the scores in text form
BAR_SPACE = 10

# Tuples of (background, fill)
BAR_COLORS = {
    "Gryffindor": ("#ffffff", "#d7282e"),
    "Ravenclaw": ("#ffffff", "#0071b9"),
    "Hufflepuff": ("#ffffff", "#fdb714"),
    "Slytherin": ("#ffffff", "#008345"),
}


def calculate_scales(house_points, base_ratio=0.6, interpolate_ratio=0.3):
    max_points = max(house_points.values())
    min_points = min(house_points.values()) if len(
        house_points) == len(HOUSES) else 0

    # The base 50% is based on basic score
    base = (max_points / MAX_POINTS) * base_ratio

    # The reset is difference in the max / min
    return {
        house: base + interpolate_ratio * (
            (house_points.get(house, 0) - min_points) /
            max(max_points - min_points, 1)
        )
        for house in HOUSES
    }


def draw_bar_for_house(im, house, scale):
    draw = ImageDraw.Draw(im)

    # Background rectangle
    draw.rectangle(BAR_RECTS[house], fill=BAR_COLORS[house][0])
    bar_y = BAR_RECTS[house][3] * (1-scale) + BAR_RECTS[house][1] * scale

    # Fill rectangle
    draw.rectangle((BAR_RECTS[house][0], bar_y,
                    BAR_RECTS[house][2], BAR_RECTS[house][3]),
                   fill=BAR_COLORS[house][1])

    del draw


def image_for_scores(scores: Dict[str, int], imgname=None) -> str:
    """Generate a sweet house cup image
   Arguments: a dictionary with house names as keys and scores as values
   Returns: filename containing a house cup image representing the
   scores
    """
    scaled = calculate_scales(scores)

    overlay = Image.open(IMAGE_PATH)

    bars = Image.new(overlay.mode, overlay.size)
    for house in HOUSES:
        draw_bar_for_house(bars, house, scaled[house])

    merged = Image.alpha_composite(bars, overlay)

    font = ImageFont.truetype('BrandonText-Black.otf', 32)
    draw = ImageDraw.Draw(merged)
    for house in HOUSES:
        text = "%d" % scores[house]
        w, _ = font.getsize(text)
        draw.text(
            ((BAR_RECTS[house][0] + BAR_RECTS[house][2] - w) * 0.5,
             BAR_RECTS[house][3] + BAR_SPACE),
            text,
            fill=BAR_COLORS[house][0], font=font)
    if not imgname:
        imgname = str(abs(hash(str(scores))))
    outfile = os.path.join(tempfile.gettempdir(), imgname + '.png')
    merged.save(outfile, "PNG")
    del overlay
    del bars
    del merged
    return outfile
