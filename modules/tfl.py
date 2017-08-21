# coding=UTF-8
import requests
import json
from datetime import datetime
import dateutil.parser
import pytz
import re

from loke import LokeEventHandler

class TfLHandler(LokeEventHandler):
    # TfL Data

    def handler_version(self):
        # Handler information
        return("TfL")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

    def handle_message(self, event):
        if 'text' in event:
            if event['text'] == '.tfl status':
                tfl = TfL(self.loke.config)
                data = tfl.GetLinesStatus('tube')

                if len(data) == 0:
                    return
                
                attachment = [{
                    "author_name": 'Transport for London',
                    "author_link": 'http://tfl.gov.uk/',
                    "author_icon": "https://tfl.gov.uk/cdn/static/assets/icons/favicon-196x196.png",
                    "fields": [{
                        'title':    'Tube Line Status',
                        'value':    '\n'.join(['%s %s line - %s' % (str(line['statusid']).replace('10',':white_check_mark:').replace('9',':warning:').replace('6', ':no_entry:').replace('20', ':no_entry:'), line['name'], line['statustext']) for line in data]) 
                    }],
                    "color": "#aaaaaa"
                }]

                self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], attachments=json.dumps(attachment))
                return

            tflmatch = re.match(r'\.tfl (.*)', event['text'], re.I)
            if tflmatch:
                stationname = '%s Underground Station' % tflmatch.group(1).title().strip()

                tfl = TfL(self.loke.config)
                data = tfl.GetArrivals(stationname)

                if data is None:
                    return

                platformlist = []
                for platform in data:
                    platformlist.append(platform)

                attachment = [{
                    "author_name": 'Transport for London',
                    "author_link": 'http://tfl.gov.uk/',
                    "author_icon": "https://tfl.gov.uk/cdn/static/assets/icons/favicon-196x196.png",
                    "fields": [],
                    "color": "#aaaaaa"
                }]
                for platform in sorted(platformlist):
                    values = sorted(data[platform], key=lambda e: e['arrivalMinutes'])
                    attachment[0]['fields'].append({
                        'title': platform,
                        'value': '\n'.join(['%s line to %s - %s minutes' % (train['lineName'], train['destinationName'].replace(' Underground Station',''), train['arrivalMinutes']) for train in values[:4]]),
                        'short': False

                    })

                self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], attachments=json.dumps(attachment))
                return

        # A message is recieved from Slack
        return

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return

class TfL(object):
    def __init__(self, config):
        self.appid = config['tfl_appid']
        self.appkey = config['tfl_appkey']

    def GetLinesStatus(self, mode):
        if mode == 'tube':
            url = 'https://api.tfl.gov.uk/Line/Mode/tube/Status'
        else:
            return

        tfldata = self._FetchData(url)
        
        data = []
        for line in tfldata:
            data.append({
                'id':           line['id'],
                'name':         line['name'],
                'statusid':     line['lineStatuses'][0]['statusSeverity'],
                'statustext':   line['lineStatuses'][0]['statusSeverityDescription']

            })
        
        return data

    def GetArrivals(self, station):
        stationdata = self._GetStation(station)
        if stationdata is None:
            return

        url = 'https://api.tfl.gov.uk/Line/%s/Arrivals?stopPointId=%s' % (','.join(['%s' % (line) for line in stationdata['lines']]) ,stationdata['id'])
        tfldata = self._FetchData(url)

        data = {}
        for line in tfldata:
            if line['platformName'] not in data:
                data[line['platformName']] = []

            expectedtime = dateutil.parser.parse(line['expectedArrival']).replace(tzinfo=pytz.utc)
            timediff = int((expectedtime - datetime.now(pytz.utc)).seconds/60)

            try:
                data[line['platformName']].append({
                    'platformName': line['platformName'],
                    'lineName': line['lineName'],
                    'destinationName': line['destinationName'],
                    'expectedArrival':  line['expectedArrival'],
                    'arrivalMinutes': timediff
                })
            except KeyError:    
                data[line['platformName']].append({
                    'platformName': line['platformName'],
                    'lineName': line['lineName'],
                    'destinationName': 'Unknown',
                    'expectedArrival':  line['expectedArrival'],
                    'arrivalMinutes': timediff
                })

        return data

    def _GetStation(self, station):
        url = 'https://api.tfl.gov.uk/Line/Mode/tube'
        lines = self._FetchData(url)
        lineids = []
        stations = {}
        
        for line in lines:
            lineids.append(line['id'])

        #lineids = ['bakerloo']
        for line in lineids:
            url = 'https://api.tfl.gov.uk/Line/%s/StopPoints' % (line)
            data = self._FetchData(url)
            for stop in data:
                if stop['commonName'] not in stations:
                    stations[stop['commonName']] = {
                        'id': stop['id'],
                        #'fullName': stop['fullName'],
                        'commonName': stop['commonName'],
                        'lines': []
                    }
                    for line in stop['lines']:
                        if line['id'] in lineids:
                            stations[stop['commonName']]['lines'].append(line['id'])
                else:
                    for line in stop['lines']:
                        if line['id'] in lineids and line['id'] not in stations[stop['commonName']]['lines']:
                            stations[stop['commonName']]['lines'].append(line['id'])
        if station not in stations:
            return
        return stations[station]

        
    def _FetchData(self, url):
        if '?' in url:
            fullurl = '%s&app_id=%s&app_key=%s' % (url, self.appid, self.appkey)
        else:
            fullurl = '%s?app_id=%s&app_key=%s' % (url, self.appid, self.appkey)

        r = requests.get(fullurl)    
        
        return json.loads(r.text)


