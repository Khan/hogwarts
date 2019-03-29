#!/usr/local/bin/python
import points_util
import cup_image
from consts import HOUSES, SLACK_TOKEN, PREFECTS, ANNOUNCERS, CHANNEL, POINTS_FILE

from collections import Counter
import google.cloud.storage
import json
import os
import re
from slackclient import SlackClient
import time

nth = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth"
}

BUCKET_NAME = "ka_users"


def get_client():
    return google.cloud.storage.Client()


def get_bucket(client):
    return client.get_bucket(BUCKET_NAME)


class PointCounter(object):
    def __init__(self, prefects=PREFECTS,
                 announcers=ANNOUNCERS, points_file=POINTS_FILE):
        self.client = get_client()
        self.bucket = get_bucket(self.client)
        try:
            self.points = Counter(json.loads(
                self.bucket.get_blob(POINTS_FILE).download_as_string()))
        except Exception as e:
            print("Exception reading points file!\n%s" % e)
            self.points = Counter()
        self.prefects = prefects
        self.announcers = announcers
        self.points_file = points_file
        self.points_dirty = False

    def post_update(self):
        if self.points_dirty:
            self.points_dirty = False
            try:
                self.bucket.blob(self.points_file).upload_from_string(
                    json.dumps(self.points), client=self.client)
            except Exception as e:
                print("Exception writing points file!\n%s" % e)
                pass

    def get_points_from(self, message, awarder):
        amount = points_util.detect_points(message)
        # only prefects can award over one point at a time
        if awarder not in self.prefects:
            amount = max(min(amount, 1), -1)
        return amount

    @staticmethod
    def message_for(house, points):
        if points > 0:
            return "%s gets %s" % (
                house, points_util.pluralized_points(points))
        return "%s loses %s" % (
            house, points_util.pluralized_points(abs(points)))

    def award_points(self, message, awarder):
        points = self.get_points_from(message, awarder)
        houses = points_util.get_houses_from(message)
        messages = []
        if points and houses:
            for house in houses:
                self.points[house] += points
                self.points_dirty = True
                messages.append(self.message_for(house, points))
                if self.points[house] > 1200:
                    self.points[house] = 1200
                    messages.append(
                        "%s already has the maximum number of points!" % house)
        return messages

    def print_status(self):
        for place, (house, points) in enumerate(sorted(self.points.items(), key=lambda x: x[-1])):
            yield "In %s place, %s with %d points" % (
                nth[len(HOUSES) - place], house, points)


def is_hogwarts_related(message):
    return (
        message.get("type", '') == "message" and
        message.get("channel", '') == CHANNEL and
        "text" in message and
        "user" in message and
        "point" in message["text"] and
        points_util.get_houses_from(message["text"]))


def main():
    sc = SlackClient(SLACK_TOKEN)
    p = PointCounter()
    if sc.rtm_connect():
        sc.api_call(
            "chat.postMessage", channel=CHANNEL, username="Hogwarts bot",
            text="I'm alive!")
        while True:
            messages = sc.rtm_read()
            for message in messages:
                print("Message: %s" % message)
                if is_hogwarts_related(message):
                    print('is_hogwarts_related')
                    for m in p.award_points(message['text'], message['user']):
                        sc.api_call(
                            "chat.postMessage", channel=CHANNEL,
                            username="Hogwarts bot", text=m)
                    os.system(
                        "curl -F file=@%s -F title=%s -F channels=%s -F token=%s https://slack.com/api/files.upload"
                        % (cup_image.image_for_scores(p.points), '"House Points"', CHANNEL, SLACK_TOKEN))

                time.sleep(1)
                p.post_update()
    else:
        print("Connection Failed, invalid token?")


if __name__ == "__main__":
    main()
