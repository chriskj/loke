# coding=UTF-8
import time
import json
from slackclient import SlackClient
from difflib import SequenceMatcher as SM
import forecastio
import re

from config import config

class Loke(object):
    def __init__(self):
        self.sc = None
        self.presence_rate_limit = {}
        self.presence_last_seen = {}

    def handle_message(self, event):
        # Capture last activity by user
        self.presence_last_seen[event['user']] = time.time()

        # Ignore own messages by bot
        if event['user'] == config['ownid']:
            return

        # Open file containing auto-responses
        with open(config['auto_response'], mode='r') as infile:
            responses = json.load(infile)

        # Loop through the dictionary from CSV file
        for response in responses:
            # Split the written message into a list (split by space)
            for word in event['text'].split():
                word = word.lower().strip('\r\t\n,.')
                if response['type'] == 'ratio':
                    #print response['key'], word, SM(None, word, response['key']).ratio()
                    match = SM(None, word, response['key']).ratio() > 0.85
                elif response['type'] == 'equal':
                    #print response['key'], word, response['type'] == 'equal'
                    match = response['key'] == word
                else:
                    match = False
                if match:
                    self.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'],
                            text=response['response'].encode('utf-8'))
                    break # Don't repeat same response for multiple hits
        
        # Trigger on call to .weather - Only supports one city
        if event['text'] == '.weather':
            forecast = forecastio.load_forecast(config['weather_apikey'], config['weather_lat'], config['weather_lng'])
            byDay = forecast.daily()
            self.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='%s weather forecast: %s' % (config['weather_city'], byDay.summary.encode('utf-8')))

        # Trigger on call to .seen - requires that the user has been online since the bot was started
        seenmatch = re.match(r'\.seen <@(.*)>', event['text'], re.I)
        if seenmatch:
            userid = seenmatch.group(1)
            self.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='<@%s> was last seen: %s' % (userid, time.strftime('%d %B %Y - %H:%M:%S', time.localtime(self.presence_last_seen[userid]))))

        # Trigger on call to .status - TODO: Move members to config
        if event['text'] == '.status':
            attachment = [{
                "text": "Status on Project Tur 2016",
                "pretext": "Incoming message from the dark side...",
                "author_name": "Darth Vader",
                "author_icon": "http://orig14.deviantart.net/f682/f/2010/331/4/e/darth_vader_icon_64x64_by_geo_almighty-d33pmvd.png",
                #"image_url": "http://students.marshall.usc.edu/undergrad/files/2014/09/berlin.jpg",
                "fields": [
                {
                    "title": "Confirmed",
                    "value": "<@baa>\n<@kjonsvik>\n<@ksolheim>\n<@raiom>\n<@robin>\n ",
                    "short": "false"
                },
                {
                    "title": "Declined",
                    "value": "kriberg\n<@lrok>\nRune\n ",
                    "short": "true"
                },
                {
                    "title": "On hold",
                    "value": "Børge\n<@caird>\n<@robert>\n<@silasilas>",
                    "short": "false"
                }
                ],
                "color": "#F35A00"
            }]
            self.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], attachments=json.dumps(attachment))

    def handle_presence_change(self, event):
        user = event['user']
        # Capture last activity by user
        self.presence_last_seen[user] = time.time()

        # Capture the last time a user got "book tickets"-notification
        if not user in self.presence_rate_limit:
            self.presence_rate_limit[user] = None
        if user in config['list_travelers'] and event['presence'] == "active":
            if self.presence_rate_limit[user] == self._get_today():
                return # Have already nagged today
            self.presence_rate_limit[user] = self._get_today()
            self.sc.api_call("chat.postMessage", as_user="true:", channel=config['chan_general'], text='<@%s> is alive!! Skal han booke fly mon tro?!' % user)

    def _get_today(self):
        now = time.time()
        return now - (now % (60*60*24))

    def init(self):
        self.sc = SlackClient(config['token'])
        if not self.sc.rtm_connect():
            raise SystemExit(1, "Connection Failed, invalid token?")
        return self

    def loop(self):
        while True:
            new_events = self.sc.rtm_read()
            for event in new_events:
                print event
                try:
                    if event['type'] == "message":
                        self.handle_message(event)

                    if event['type'] == "presence_change":
                        self.handle_presence_change(event)
                except KeyError:
                    # TODO(vegawe): When does this happen? Should not be necessary
                    print("Key not found in dict")
            time.sleep(1)

if __name__ == "__main__":
    Loke().init().loop()
