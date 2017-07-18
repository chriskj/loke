# coding=UTF-8
from loke import LokeEventHandler

import requests, re

class restplass(object):
    def vis_ving(self):
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
    def handler_version(self):
        return("Chartertur")

    def __init__(self, loke):
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: Chartertur")

    def handle_message(self, event):
        if event['text'] == '.chartertur':
            tur = restplass()
            turer = tur.vis_ving()
            response = '*Bleik og sur - vi skal på chartertur!*\n```'
            for plass in turer:
                response += '%s\n' % (plass)
            response += '```'
            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='%s' % (response))
            return

        return

    def handle_presence_change(self, event):
        return

