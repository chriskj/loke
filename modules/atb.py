# coding=UTF-8
import zeep
from datetime import datetime
import pytz

from loke import LokeEventHandler
import re
import json

class AtBHandler(LokeEventHandler):
    # Handler description

    def handler_version(self):
        # Handler information
        return("AtB")

    def __init__(self, loke):
        # Initiate the handler
        self.loke = loke
        self.loke.register_handler(self)
        print("Loading module: %s" % self.handler_version())

        self.atb = AtB()

    def handle_message(self, event):
        # A message is recieved from Slack
        atbmatch = re.match(r'\.atb (.*)', event['text'], re.I)
        if atbmatch:
            stopname = atbmatch.group(1).lower()
            with open(self.loke.config['atbstops'], 'r') as fil:
                stops = json.load(fil)

            if stopname in stops:
                for stopid in stops[stopname]:
                    trips = self.atb.GetStopStatus(stopid)
                    message = '*%s (id: %s):*\n' % (stopname.title(), stopid)
                    if len(trips) > 0:
                        message += '```'        
                    for trip in trips[:8]:
                        ca = ''
                        if trip['RealTime'] is False:
                            ca = 'Ca '
                        if trip['ArrivalMinutes'] == 0:
                            message += '%snå - %s %s\n' % (ca, trip['LineNumber'], trip['LineDestination'])
                        elif trip['ArrivalMinutes'] < 10:
                            message += '%s%s min - %s %s\n' % (ca, trip['ArrivalMinutes'], trip['LineNumber'], trip['LineDestination'])
                        else:
                            message += '%s%s - %s %s\n' % (ca, trip['ArrivalTime'], trip['LineNumber'], trip['LineDestination'])
                    if len(trips) > 0:
                        message += '```'        
                    self.loke.sc.api_call("chat.postMessage", as_user="true:", channel=event['channel'], text=message)


        return

    def handle_presence_change(self, event):
        # A user changes state active/inactive
        return

    def handle_loop(self):
        # handle_loop() is used by handlers to pick up data when it's not triggered by message og presence change (i.e. watch, countdowns++)
        return

class AtB(object):
    def __init__(self):
        wsdlurl = 'http://st.atb.no/SMWS/SMService.svc?wsdl'
        self.client = zeep.Client(wsdl=wsdlurl)

    def GetStopStatus(self, stopid):
        response = self.client.service.GetStopMonitoring(
            ServiceRequestInfo={
                'RequestorRef':'Loke', 
                'RequestTimestamp': datetime.now(), 
            }, 
            Request={
                'version': '1.4',
                'RequestTimestamp': datetime.now(), 
                'MonitoringRef': '%s' % (stopid,)
            },
            RequestExtension={}
        )
        trips = []

        for item in response.Answer.StopMonitoringDelivery[0].MonitoredStopVisit:
            if item.MonitoredVehicleJourney.MonitoredCall.ExpectedDepartureTime is None:
                expectedtime = item.MonitoredVehicleJourney.MonitoredCall.AimedDepartureTime.replace(tzinfo=None)
                real = False
            else:    
                expectedtime = item.MonitoredVehicleJourney.MonitoredCall.ExpectedDepartureTime
                real = True 
            
            time = expectedtime.strftime("%H:%M")
            timediff = int((expectedtime - datetime.now()).seconds/60)

            trip = {}
            trip['ArrivalMinutes'] = timediff
            trip['RealTime'] = real
            trip['ArrivalTime'] = time
            trip['LineNumber'] = item.MonitoredVehicleJourney.LineRef
            trip['LineOrigin'] = item.MonitoredVehicleJourney.OriginName
            trip['LineDestination'] = item.MonitoredVehicleJourney.MonitoredCall.DestinationDisplay

            trips.append(trip)

        return trips 

