import requests
import time
from datetime import datetime, timedelta
import ConfigParser
import os
import json
 
class Consumer(object):

    URL_TEMPLATE = "%s://%s:%s/events/%s/bins/1?timeout=120"

    def __init__(self, protocol=None, host=None, port=None, topic=None, user=None, password=None):
        self._protocol = protocol if protocol is not None else getConfig('MQ', 'mqprotocol')
        self._host = host if host is not None else getConfig('MQ', 'mqhost')
        self._port = port if port is not None else getConfig('MQ', 'mqport')
        self._topic = topic if topic is not None else getConfig('MQ', 'mqtopic')
        self._user = user if user is not None else getConfig('MQ', 'mquser')
        self._password = password if password is not None else getConfig('MQ', 'mqpassword')

    def consume_without_auth(self):
        url = self.URL_TEMPLATE % (self._protocol, self._host, self._port, self._topic)
        client=requests.session()
        headers = {'Connection': 'keep-alive'}
        if self._protocol == "http":
            resp = client.get(url, headers=headers)
        else:
            resp = client.get(url, headers=headers, verify=False)
        if resp.status_code == 200 and 'status' in resp.text:
            
            all_target_json = []
            for source_json in eval(resp.text):
                target_json = data_format(source_json)
                all_target_json.append(target_json)
            return all_target_json
        else:
            return "No Response"

    def consume_with_auth(self):
        url = self.URL_TEMPLATE % (self._protocol, self._host, self._port, self._topic)
        client=requests.session()
        headers = {'Connection': 'keep-alive'}
        if self._protocol == "http":
            resp = client.get(url, headers=headers, auth=HTTPBasicAuth(self._user, self._password))
        else:
            resp = client.get(url, headers=headers, verify=False, auth=HTTPBasicAuth(self._user, self._password))
        if resp.status_code == 200 and 'status' in resp.text:
            
            all_target_json = []
            for source_json in eval(resp.text):
                target_json = data_format(source_json)
                all_target_json.append(target_json)
            return all_target_json
        else:
            return "No Response"


def data_format(source_json):

    source = json.loads(source_json)
    # do some checks
    if not 'status' in source.keys() and not 'alert' in source.keys():
        raise KeyError('fields are missing')

    try:

        alarmAdditionalInformation = []

        for i in range(1,3): 
            alarmAdditionalInformation.append({'name': 'name8','value': 'value9'})
        
        target = {
                'event': {
                    'commonEventHeader': {
                        'domain': 'fault',
                        'eventId': '122',
                        'functionalRole': 'UNIT TEST',
                        'lastEpochMicrosec': source['updateTimeUTC'],
                        'priority': 'Normal',
                        'reportingEntityName': 'Dummy VM name - No Metadata available',
                        'sequence': 122,
                        'sourceName': 'Dummy VM name - No Metadata available',
                        'startEpochMicrosec': source['updateTimeUTC'],
                        'version': 1.2,
                        'eventType': 'Bad things happen...',
                        'reportingEntityId': 'Dummy VM UUID - No Metadata available',
                        'sourceId': source['resourceId']
                    },
                    'faultFields': {
                        'alarmCondition': 'My alarm condition',
                        'eventSeverity': 'MAJOR',
                        'eventSourceType': 'other',
                        'specificProblem': 'It broke very badly',
                        'eventCategory': 'link',
                        'vfStatus': source['status'],
                        'faultFieldsVersion': 1.1,
 
                        'alarmInterfaceA': 'My Interface Card'
                    }
                }
            }
        target['event']['faultFields']['alarmAdditionalInformation'] = alarmAdditionalInformation

        return json.dumps(target)
    except Exception as e:
        print('ERROR: %s'% e.message)



def getConfig(section, key):
    config = ConfigParser.ConfigParser()
    path = os.path.split(os.path.realpath(__file__))[0] + '/config.conf'
    config.read(path)
    return config.get(section, key)
