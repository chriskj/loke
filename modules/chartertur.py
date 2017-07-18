# coding=UTF-8
from loke import LokeEventHandler

import requests, re

class restplass(object):
    # Class to look for restplass

    def vis_ving(self):
        # Connect to Ving webpage for Trondheim and look for HTML class-tags to fetch the information required
        match = re.compile('class=\"([^\"]*)\">([^<]*)<')
        url = 'https://www.ving.no/restplasser/DD/A/TRD/-/99/SH/-/-/-/-'

        r = requests.get(url)
        book = r.text

        inttags = [
            'lms-departure-date',
            'lms-price__value',
            'lms-duration-time-long',
            'lms-destination-resort__hotel-name',
            'lms-destination__resort-name',
            'lms-destination__airport-name',
            'lms-destination__country-name',
            'lms-one-seat-left'
        ]

        turdata = []
        turdata_all = []

        for tag, data in match.findall(book):
            if tag == 'lms-trip' and len(turdata) > 0:
                turdata_all.append(turdata)
                turdata = []
            if tag == 'lms-one-seat-left':
                turdata.append('ONE SEAT LEFT')
            elif tag in inttags:
                turdata.append(data)

        return turdata_all

class CharterturHandler(LokeEventHandler):
    # Handler to fetch Restplass-data

    def handler_version(self):
        # Handler information
        return("Chartertur")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

    def handle_message(self, event):
        # A message is recieved from Slack
        if event['text'] == '.chartertur': # Responds to call .chartertur
            tur = restplass()
            turer = tur.vis_ving()
            response = '*Bleik og sur - vi skal på chartertur!*\n```' # Adding ``` to get fixed width font
            for plass in turer:
                response += '%s\n' % (plass)
            response += '```'
            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='%s' % (response))
            return

        return

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return
