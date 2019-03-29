import os
import tempfile
from typing import Dict
from consts import HOUSES, IMAGE_PATH

from PIL import Image, ImageDraw, ImageFont


# Tuples of (x1, y1, x2, y2)
BAR_RECTS = {
    "Gryffindor": (62, 70, 204, 513),
    "Hufflepuff": (418, 70, 560, 513),
    "Slytherin": (596, 70, 738, 513),
    "Ravenclaw": (240, 70, 382, 513),
}

# Space below the bottom of the bar to superimpose the scores in text form
BAR_SPACE = 10

# Tuples of (background, fill)
BAR_COLORS = {
    "Gryffindor": ("#fef9ec", "#de5647"),
    "Ravenclaw": ("#f3f9fc", "#0a8bc9"),
    "Hufflepuff": ("#fef9ec", "#f5bf45"),
    "Slytherin": ("#f0efee", "#2c9959"),
}


def calculate_scales(house_points):
    total_points = float(sum(house_points.values())) or 1.0

    return {house: 1.0 if house_points.get(house, 0) == 1200 else (house_points.get(house, 0) / total_points) for house in HOUSES}


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
            fill=BAR_COLORS[house][1], font=font)
    if not imgname:
        imgname = str(abs(hash(str(scores))))
    outfile = os.path.join(tempfile.gettempdir(), imgname + '.png')
    merged.save(outfile, "PNG")
    del overlay
    del bars
    del merged
    return outfile
