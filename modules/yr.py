# coding=UTF-8
from loke import LokeEventHandler
import json
import requests
import xml.etree.ElementTree as ET
import re
from datetime import datetime

# To get Norwegian names for months and days
import locale
locale.setlocale(locale.LC_ALL, 'nb_NO.utf8')

class YrHandler(LokeEventHandler):
    # Handler to show weather information from Yr

    def handler_version(self):
        # Handler information
        return("Yr")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

    def handle_message(self, event):
        # A message is rpecieved from Slack
        yrmatch = re.match(r'\.yr (.*)', event['text'], re.I)
        if yrmatch:
            place = yrmatch.group(1).title()
            if place in self.loke.config['yr_places']:
                url = self.loke.config['yr_places'][place]
            else:
                self.loke.sc.chat_postMessage(as_user="true:", channel=event['channel'], text='I don\'t know the place %s' % place)
                return

            data = requests.get(url).text
            xml = ET.fromstring(data).find('forecast')

            # Fetch credit information
            credit = ET.fromstring(data).find('credit').find('link').attrib['text']
            crediturl = ET.fromstring(data).find('credit').find('link').attrib['url']
            
            data = {}
            datalist = []
            
            if xml.find('text'):
                for item in xml.find('text').find('location').findall('time'):
                    data[item.attrib['from']] = {
                        'date': datetime.strptime(item.attrib['from'], "%Y-%m-%d"),
                        #'text': item.find('body').text.replace('<strong>','').replace('</strong>',''),
                    }
            
            for item in xml.find('tabular').findall('time'):
                if not item.attrib['from'][:10] in data:
                    data[item.attrib['from'][:10]] = {
                        'date': datetime.strptime(item.attrib['from'][:10],  "%Y-%m-%d")
                    }
                data[item.attrib['from'][:10]]['temp%s' % (item.attrib['period'])] = item.find('temperature').attrib['value']
                data[item.attrib['from'][:10]]['windspeed%s' % (item.attrib['period'])] = item.find('windSpeed').attrib['name']
                data[item.attrib['from'][:10]]['winddirection%s' % (item.attrib['period'])] = item.find('windDirection').attrib['name']

            
            for key, value in data.items():
                datalist.append(value)
            
            datalist.sort(key=lambda e: e['date'])

            attachment = [{
                "author_name": credit,
                "author_link": crediturl,
                "author_icon": "https://www.yr.no/assets/images/logo-yr-50.png",
                "fields": [
                ],
                "color": "#00B9F1"
            }]
            for entry in datalist[:6]:
                attachment[0]['fields'].append({
                    'title': datetime.strftime(entry['date'], "%A %d. %B").capitalize(),
                    'value': '%s\n\nTemperatur:\n%s - %s - %s - %s\n\nVind:\n%s, %s, %s, %s' % (entry.get('text', ''), entry.get('temp0', '  '), entry.get('temp1', '  '),entry.get('temp2', '  '),entry.get('temp3', '  '),entry.get('windspeed0', ''),entry.get('windspeed1', ''),entry.get('windspeed2', ''),entry.get('windspeed3', ''),),
                    'short': 'false'
                })
                
            self.loke.sc.chat_postMessage(as_user="true:", channel=event['channel'], attachments=json.dumps(attachment))
            return

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return


