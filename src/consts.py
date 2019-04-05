try:
    from secrets import (
        SLACK_TOKEN, PREFECTS, CHANNEL, POINTS_FILE,
        BUCKET_NAME, PUBLIC_CHANNEL
    )
except ImportError:
    # These will be mocked on tests
    POINTS_FILE = ''
    BUCKET_NAME = ''
    PREFECTS = []
    SLACK_TOKEN = ''
    CHANNEL = ''
    PUBLIC_CHANNEL = ''

HOUSES = ["Ravenclaw", "Hufflepuff", "Gryffindor", "Slytherin"]
SPECIAL_SUBJECT = ["Dumbledore", "Mr Filch", "Mr. Filch"]
# Announcers will be able to make the bot print the current standing
ANNOUNCERS = PREFECTS
IMAGE_PATH = "house_points.png"

# 2018 - 🙈🙈🙈
# BUCKET_NAME = "ka_users"
# POINTS_FILE = 'hogwarts_bot/HackathonFeb2018Points.json'

MAX_POINTS = 1200
