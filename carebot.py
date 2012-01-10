#!/usr/bin/env python
#
# Searches Twitter for tweets that contain "could care less" and replies with a friendly correction.
# Inspired by http://twitter.com/StealthMountain and MS Office

from time import time
import ConfigParser
import random
import re
import tweepy

config = ConfigParser.RawConfigParser()
config.read("config.ini")

# Make sure you configure the app with read+write permissions
consumer_key = config.get("account", "consumer_key")
consumer_secret = config.get("account", "consumer_secret")
access_token = config.get("account", "access_token")
access_token_secret = config.get("account", "access_token_secret")
password = config.get("account", "password")

oauth = tweepy.OAuthHandler(consumer_key, consumer_secret)
oauth.set_access_token(access_token, access_token_secret)

api = tweepy.API(oauth)
me = api.me()
print("Running as " + me.screen_name)

expression = "could care less"
throttle = 5 * 60
lastTweetAt = 0

greetings = [ "Hello!", "Hi!", "Hiya!", "Hey there!", "Ahoy!", "Howdy!" ]
corrections = [
    "I think you mean \"could not care less\"",
    "Do you mean \"could not care less\"?",
    "Are you sure you don't mean \"could not care less\"?",
    "You probably mean \"could not care less\"",
]

class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        global lastTweetAt # Hrmmm, come on python
        now = time()
        if now - lastTweetAt < throttle:
            # Too soon since the last tweet
            return
        if status.author.id == me.id:
            # Don't correct myself...
            return
        if status.in_reply_to_user_id == me.id or status.text.find(me.screen_name) != -1:
            # It's a conversation with the bot, never reply back
            return
        if status.text.lower().find(expression) == -1:
            # Filter out tweets that don't contain the exact expression
            return
        if re.search("\\bRT\\b", status.text):
            # Ignore old-style retweets
            return

        try:
            # Reply to their tweet
            message = "@" + status.author.screen_name + " " + \
                random.choice(greetings) + " " + random.choice(corrections)
            api.update_status(message, status.id)
            lastTweetAt = now
        except tweepy.TweepError as error:
            print("Tweet error", e.response, e.reason)

    def on_error(self, code):
        print("Error connecting to stream API", code)

# I'm getting HTTP 401 errors when filtering a query with spaces in it, using basic password auth
# seems to work around this...
basicAuth = tweepy.auth.BasicAuthHandler(me.screen_name, password)
listener = StreamListener()
streamer = tweepy.Stream(basicAuth, listener)
streamer.filter(track=[expression])
