# coding=UTF-8
from loke import LokeEventHandler

import requests, re

class MannenHandler(LokeEventHandler):

    def handler_version(self):
        # Handler information
        return("Har mannen falt?")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

    def handle_message(self, event):
        # A message is recieved from Slack
        if event['text'] == '.harmannenfalt' or event['text'] == '.harveslemannenfalt': # Responds to call .harmannenfalt

            if event['text'] == '.harmannenfalt':
                url = 'http://harmannenfalt.no/'
                response = '*Har Mannen falt?*\n' 
                match = re.compile('<div id=\"yesnomaybe\">\n(.*)')
            elif event['text'] == '.harveslemannenfalt':
                url = 'http://harveslemannenfalt.no/'
                response = '*Har Vesle-Mannen falt?*\n' 
                match = re.compile('<div class=\"janeikanskje\">\n(.*)')
            else:
                return

            r = requests.get(url)
            sitedata = r.text


            svar = match.findall(sitedata)[0].strip().capitalize()

            response += svar

            self.loke.sc.chat_postMessage(as_user="true:", channel=event['channel'], text='%s' % (response))
            return

        return

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return
