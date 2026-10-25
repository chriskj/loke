# coding=UTF-8
import re
import requests

from loke import LokeEventHandler

class WeatherHandler(LokeEventHandler):
    # Handler to fetch weather information from Open-Meteo

    def handler_version(self):
        # Handler information
        return("Weather")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

    def handle_message(self, event):
        # A message is recieved from Slack

        # Trigger on call to .weather - Supports citites specified in config
        weathermatch = re.match(r'\.weather\ ?(.*)', event['text'], re.I)
        if weathermatch:
            city = weathermatch.group(1).title()
            if city == '':
                city = self.loke.config['weather_default']
            coordinates = self.loke.config['weather'].get(city)
            if not coordinates:
                self.loke.sc.chat_postMessage(
                    channel=event['channel'],
                    text="I don't know the place %s" % city,
                )
                return

            response = requests.get(
                'https://api.open-meteo.com/v1/forecast',
                params={
                    'latitude': coordinates[0],
                    'longitude': coordinates[1],
                    'daily': (
                        'temperature_2m_max,temperature_2m_min,'
                        'precipitation_probability_max'
                    ),
                    'forecast_days': 3,
                    'timezone': 'auto',
                },
                timeout=15,
            )
            response.raise_for_status()
            daily = response.json()['daily']
            forecast_lines = []
            for date, low, high, precipitation in zip(
                daily['time'],
                daily['temperature_2m_min'],
                daily['temperature_2m_max'],
                daily['precipitation_probability_max'],
            ):
                forecast_lines.append(
                    '%s: %.1f–%.1f °C, precipitation %s%%'
                    % (date, low, high, precipitation)
                )
            self.loke.sc.chat_postMessage(
                channel=event['channel'],
                text='*%s weather forecast*\n%s'
                % (city, '\n'.join(forecast_lines)),
            )
            return


    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return
