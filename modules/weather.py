# coding=UTF-8
import re
import forecastio

from loke import LokeEventHandler

class WeatherHandler(LokeEventHandler):
    def handler_version(self):
        return("Weather")

    def __init__(self, loke):
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

    def handle_message(self, event):
        # Trigger on call to .weather - Only supports one city
        weathermatch = re.match(r'\.weather\ ?(.*)', event['text'], re.I)
        if weathermatch:
            city = weathermatch.group(1).title()
            if city == '':
                city = self.loke.config['weather_default']
            forecast = forecastio.load_forecast(self.loke.config['weather_apikey'], self.loke.config['weather'][city][0], self.loke.config['weather'][city][1])
            byDay = forecast.daily()
            self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text='%s weather forecast: %s' % (city, byDay.summary))
            return


    def handle_presence_change(self, event):
        return

    def handle_loop(self):
        return
