# coding=UTF-8
import zeep
from datetime import datetime
from lxml import etree
import pytz

from loke import LokeEventHandler
import re

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
            stop = {}
            stop['key'] = atbmatch.group(1).lower()
            if stop['key'] == 'pl' or stop['key'] == 'persaunet leir':
                stop['id'] = 16011368 
                stop['name'] = 'Persaunet leir mot sentrum'
            if stop['key'] == 'strindheim':
                stop['id'] = 16011472
                stop['name'] = 'Strindheim mot sentrum'
            if stop['key'] == 'solsiden':
                stop['id'] = 16010404
                stop['name'] = 'Solsiden fra sentrum'
            if stop['key'] == 'gryta':
                stop['id'] = 16011152
                stop['name'] = 'Gryta mot sentrum'
            if stop['key'] == 'vs' or stop['key'] == 'voll studentby':
                stop['id'] = 16011553
                stop['name'] = 'Voll studentby mot sentrum'
             
            trips = self.atb.GetStopStatus(stop['id'])
            message = '*%s:*\n' % (stop['name'])
            message += '```'        
            for trip in trips:
                ca = ''
                if trip['RealTime'] is False:
                    ca = 'Ca '
                if trip['ArrivalMinutes'] < 10:
                    message += '%s%s min - %s %s\n' % (ca, trip['ArrivalMinutes'], trip['LineNumber'], trip['LineDestination'])

                else:
                    message += '%s%s - %s %s\n' % (ca, trip['ArrivalTime'], trip['LineNumber'], trip['LineDestination'])
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
                'MonitoringRef': '%d' % (stopid,)
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

