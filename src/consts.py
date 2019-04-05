try:
    from secrets import (
        SLACK_TOKEN, PREFECTS, CHANNEL, POINTS_FILE,
        BUCKET_NAME, PUBLIC_CHANNEL,
        ADMIN_CHANNEL, BOT_ID
    )
except ImportError:
    # These will be mocked on tests
    POINTS_FILE = ''
    BUCKET_NAME = ''
    PREFECTS = []
    SLACK_TOKEN = ''
    CHANNEL = ''
    PUBLIC_CHANNEL = ''
    ADMIN_CHANNEL = ''
    BOT_ID = ''

HOUSES = ["Ravenclaw", "Hufflepuff", "Gryffindor", "Slytherin"]
SPECIAL_SUBJECT = {
    "dumbledore": {
        "name": "Professor Dumbledore",
        "emoji": ":dumbledore-face:",
    },
    "filch": {
        "name": "Mr. Filch",
        "emoji": ":filch:",
    }
}
# Announcers will be able to make the bot print the current standing
ANNOUNCERS = PREFECTS
IMAGE_PATH = "house_points.png"

# 2018 - 🙈🙈🙈
# BUCKET_NAME = "ka_users"
# POINTS_FILE = 'hogwarts_bot/HackathonFeb2018Points.json'

MAX_POINTS = 1200
