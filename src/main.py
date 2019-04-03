#!/usr/local/bin/python
from collections import Counter
import json
import os
import re
import time

from google.auth import exceptions
from slackclient import SlackClient
import google.cloud.storage

import points_util
import cup_image
from consts import HOUSES, SLACK_TOKEN, PREFECTS, ANNOUNCERS, CHANNEL

try:
    from secrets import POINTS_FILE, BUCKET_NAME
except ImportError:
    # These will be mocked on tests
    POINTS_FILE = ''
    BUCKET_NAME = ''


nth = {
    1: "first",
    2: "second",
    3: "third",
    4: "fourth"
}


def get_client():
    return google.cloud.storage.Client()


def get_bucket(client):
    return client.get_bucket(BUCKET_NAME)


class PointCounter(object):
    def __init__(self, prefects=PREFECTS,
                 announcers=ANNOUNCERS, points_file=POINTS_FILE,
                 reset=False):
        self.client = None
        self.bucket = None
        try:
            self.client = get_client()
            self.bucket = get_bucket(self.client)
            data = json.loads(
                self.bucket.get_blob(points_file).download_as_string())
            self.points = Counter(data[0])
        except (exceptions.DefaultCredentialsError, AttributeError) as e:
            print("Exception reading points file!\n%s" % e)
            self.points = Counter()
        if reset:
            self.points = Counter()
        self.prefects = prefects
        self.announcers = announcers
        self.points_file = points_file
        self.points_dirty = False

    def post_update(self):
        if self.points_dirty:
            self.points_dirty = False
            if self.bucket:
                self.bucket.blob(self.points_file).upload_from_string(
                    # NOTE: we post as array in format for KPI datatset
                    json.dumps([self.points]), client=self.client)
            else:
                print("No bucket setting found - not updating.")

    def get_points_from(self, message, awarder):
        amount = points_util.detect_points(message)
        # only prefects can award over one point at a time
        if awarder not in self.prefects:
            amount = max(min(amount, 1), -1)
        return amount

    @staticmethod
    def message_for(house, points, awarder=None):
        user_awared = f"<@{awarder}>" if awarder else ""
        if points > 0:
            return "%s %s gets %s" % (
                user_awared, house, points_util.pluralized_points(points))
        return "%s %s loses %s" % (
            user_awared, house, points_util.pluralized_points(abs(points)))

    def award_points(self, message, awarder):
        points = self.get_points_from(message, awarder)
        houses = points_util.get_houses_from(message)
        messages = []
        if points and houses:
            for house in houses:
                self.points[house] += points
                self.points_dirty = True
                messages.append(self.message_for(house, points, awarder))
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


def convert_name_to_id(sc, channel, prefect_names):
    """Convert the given username into ids"""
    prefect_ids = []

    prefect_name_set = set(prefect_names)
    channel_info = sc.api_call("channels.info", channel=channel)
    user_list = channel_info['channel']['members']

    for user_id in user_list:
        profile = sc.api_call("users.info", user=user_id)
        user_name = profile.get('user', {}).get('name')
        if user_name in prefect_name_set:
            prefect_ids.append(user_id)

    print("Got prefect ids: {}".format(prefect_ids))
    sc.api_call(
        "chat.postMessage", channel=CHANNEL,
        as_user=True, text="Your prefects will be: {}".format(
            ",".join([f"<@{u}>" for u in prefect_ids])
        ))

    return prefect_ids


def main():
    sc = SlackClient(SLACK_TOKEN)
    if sc.rtm_connect():
        sc.api_call(
            "chat.postMessage", channel=CHANNEL,
            as_user=True,
            text="I'm alive!")
        p = PointCounter(prefects=convert_name_to_id(sc, CHANNEL, PREFECTS))
        while True:
            messages = sc.rtm_read()
            seen_messages = False
            for message in messages:
                print("Message: %s" % message)
                if is_hogwarts_related(message):
                    print('is_hogwarts_related')
                    for m in p.award_points(message['text'], message['user']):
                        sc.api_call(
                            "chat.postMessage", channel=CHANNEL,
                            as_user=True, text=m)
                        seen_messages = True
            # NOTE: the following rendering is slow, try to limit it's use
            if seen_messages:
                os.system(
                    "curl -F file=@%s -F title=%s -F channels=%s -F token=%s https://slack.com/api/files.upload"
                    % (cup_image.image_for_scores(p.points), '"House Points"', CHANNEL, SLACK_TOKEN))
            time.sleep(1)
            p.post_update()
    else:
        print("Connection Failed, invalid token?")


if __name__ == "__main__":
    main()
