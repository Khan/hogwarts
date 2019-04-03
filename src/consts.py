from secrets import SLACK_TOKEN, PREFECTS, CHANNEL
HOUSES = ["Ravenclaw", "Hufflepuff", "Gryffindor", "Slytherin"]
# Announcers will be able to make the bot print the current standing
ANNOUNCERS = PREFECTS
IMAGE_PATH = "house_points.png"

# 2018 - 🙈🙈🙈
# BUCKET_NAME = "ka_users"
# POINTS_FILE = 'hogwarts_bot/HackathonFeb2018Points.json'
try:
    from secrets import POINTS_FILE, BUCKET_NAME
except ImportError:
    # These will be mocked on tests
    POINTS_FILE = ''
    BUCKET_NAME = ''

MAX_POINTS = 1200
