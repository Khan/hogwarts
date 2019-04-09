import re

from consts import SPECIAL_SUBJECT, HOUSES


def clean(message):
    """Standardize spacing and capitalization"""
    return ' '.join(m.lower() for m in message.split() if m)


def pluralized_points(num_points):
    if num_points == 1 or num_points == -1:
        return "%d point" % num_points
    return "%d points" % num_points


def detect_points(message):
    amounts = [amount for amount in re.split(r"\W", clean(message))
               if amount.isdigit()]
    if len(amounts) == 0 and 'one' in clean(message):
        amounts = [1]
    if len(amounts) >= 1:
        return int(amounts[0]) * detect_point_polarity(message)
    else:
        return 0


def detect_point_polarity(message):
    """Discern whether this is a point awarding or deduction"""
    message = clean(message)
    if any(x in message for x in ["points to", "point to", "point for", "points for"]):
        return 1
    elif any(x in message for x in ["points from", "point from"]):
        return -1
    else:
        return 0


def proper_name_for(house):
    """Forgive house misspelling"""
    if "raven" in house:
        return "Ravenclaw"
    if "huff" in house:
        return "Hufflepuff"
    if "gryf" in house:
        return "Gryffindor"
    if "slyt" in house:
        return "Slytherin"


def get_houses_from(message):
    tokenized = clean(message).split()
    if 'everybody' in tokenized:
        return HOUSES
    return list(set(proper_name_for(w) for w in tokenized if proper_name_for(w)))


def get_subject_from(message):
    for s in SPECIAL_SUBJECT.keys():
        # allow "mr. filch", "prof dumbledor, etc."
        for word in message.lower().split()[0:2]:
            if s.lower() == word:
                return s
    return None


def get_reason(message) -> str:
    for s in ['for ', 'because of ']:
        if s in message:
            return message.split(s, 1)[1]
    return ''


def get_says(message) -> str:
    for s in ['says ', 'say ']:
        if s in message:
            return message.split(s, 1)[1]
    return ''
