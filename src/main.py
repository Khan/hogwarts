#!/usr/local/bin/python
from collections import Counter
import json
import os
import re
import time
from typing import Union, Tuple, Optional

from google.auth import exceptions
from slackclient import SlackClient
import google.cloud.storage

import points_util
import cup_image
from consts import (
    HOUSES, SLACK_TOKEN, PREFECTS, ANNOUNCERS, CHANNEL, ADMIN_CHANNEL,
    POINTS_FILE, BUCKET_NAME, PUBLIC_CHANNEL, MAX_POINTS, BOT_ID,
    SPECIAL_SUBJECT
)


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
            amount = max(min(amount, 1), 0)
        return amount

    @staticmethod
    def get_house_party_emoji(h):
        return f":party_{h.lower()}:"

    @staticmethod
    def get_house_emoji(h):
        return f":{h.lower()}:"

    @classmethod
    def message_for(cls, house, points, awarder=None, special_user=None,
                    reason=None) -> Union[str, Tuple[str, str]]:
        """ Convert house and points into message

        :return:  str or tuple (if special character)
        """
        user_awared = f"<@{awarder}>" if awarder else ""
        up_icon = ":small_green_triangle_up:"
        down_icon = ":small_red_triangle_down:"
        if special_user:
            reason = f"for {reason} " if reason else ""
            if points > 0:
                return (
                    f"awards "
                    f"{points_util.pluralized_points(points)} to {house} "
                    f"{reason} "
                    f"{cls.get_house_emoji(house)} {up_icon}",
                    special_user)
            return (f"takes away "
                    f"{points_util.pluralized_points(abs(points))} from {house} "
                    f"{reason} "
                    f"{cls.get_house_emoji(house)} {down_icon}",
                    special_user)

        if points > 0:
            return f"{user_awared} {house} gets " \
                f"{points_util.pluralized_points(points)} " \
                f"{cls.get_house_emoji(house)} {up_icon}"
        return f"{user_awared} {house} loses " \
            f"{points_util.pluralized_points(abs(points))} " \
            f"{cls.get_house_emoji(house)} {down_icon}"

    def award_points(self, message, awarder) -> Union[str, Tuple[str, str]]:
        points = self.get_points_from(message, awarder)
        houses = points_util.get_houses_from(message)
        special_user: Optional[str] = None
        reason = ''
        says = ''
        if awarder in self.prefects:
            special_user = points_util.get_subject_from(message)
            reason = points_util.get_reason(message)
            says = points_util.get_says(message)
        messages = []
        if points and houses:
            for house in houses:
                self.points[house] += points
                self.points_dirty = True
                messages.append(self.message_for(house, points, awarder,
                                                 special_user=special_user,
                                                 reason=reason))
                if self.points[house] > MAX_POINTS:
                    self.points[house] = MAX_POINTS
                    messages.append(
                        "%s already has the maximum number of points!" % house)
                elif self.points[house] < 0:
                    self.points[house] = 0
                    messages.append(
                        "%s already at zero points!" % house)
        elif special_user and says:
            messages.append((says, special_user))

        return messages

    def print_status(self):
        for place, (house, points) in enumerate(sorted(self.points.items(), key=lambda x: x[-1])):
            yield "In %s place, %s with %d points" % (
                nth[len(HOUSES) - place], house, points)


def is_hogwarts_related(message):
    return (
        message.get("type", '') == "message" and
        message.get("channel", '') in {CHANNEL, ADMIN_CHANNEL} and
        "text" in message and
        ("user" in message and message["user"] != BOT_ID) and
        (
            # Points message
            ("point" in message["text"].lower() and
                points_util.get_houses_from(message["text"])) or
            # Simple says
            ("say" in message["text"].lower() and
                points_util.get_subject_from(message["text"]))
        )
    )


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
    # sc.api_call(
    #     "chat.postMessage", channel=CHANNEL,
    #     as_user=True, text="Your prefects will be: {}".format(
    #         ",".join([f"<@{u}>" for u in prefect_ids])
    #     ))

    return prefect_ids


def main():
    sc = SlackClient(SLACK_TOKEN)
    if sc.rtm_connect():
        p = PointCounter(prefects=convert_name_to_id(sc, PUBLIC_CHANNEL,
                                                     PREFECTS))
        sc.api_call(
            "chat.postMessage", channel=CHANNEL,
            as_user=True,
            text="I'm alive!")
        while True:
            messages = sc.rtm_read()
            seen_point_messages = False
            for message in messages:
                print("Message: %s" % message)
                if is_hogwarts_related(message):
                    print('is_hogwarts_related')
                    for m in p.award_points(message['text'], message['user']):
                        if isinstance(m, tuple):
                            m, special_char = m
                            slack_info = SPECIAL_SUBJECT.get(special_char, {})
                            sc.api_call(
                                "chat.postMessage",
                                channel=CHANNEL,
                                as_user=False,
                                username=slack_info.get('name'),
                                icon_emoji=slack_info.get('emoji'),
                                text=m)
                        else:
                            sc.api_call("chat.postMessage", channel=CHANNEL,
                                        as_user=True,
                                        text=m)
                        # HACK: Avoid seeing "says" messages
                        seen_point_messages = ('point' in m)
            # NOTE: the following rendering is slow, try to limit it's use
            if seen_point_messages:
                os.system(
                    "curl -F file=@%s -F title=%s -F channels=%s -F token=%s https://slack.com/api/files.upload"
                    % (cup_image.image_for_scores(p.points), '"House Points"', CHANNEL, SLACK_TOKEN))
            time.sleep(1)
            p.post_update()
    else:
        print("Connection Failed, invalid token?")


if __name__ == "__main__":
    main()
