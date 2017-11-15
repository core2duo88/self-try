import requests
import time
from datetime import datetime, timedelta
import ConfigParser
import os
import json
 
class Producer(object):

    URL_TEMPLATE = "%s://%s:%s/events/%s"

    def __init__(self, protocol=None, host=None, port=None, topic=None, user=None, password=None):
        self._protocol = protocol if protocol is not None else getConfig('MQ', 'mqprotocol')
        self._host = host if host is not None else getConfig('MQ', 'mqhost')
        self._port = port if port is not None else getConfig('MQ', 'mqport')
        self._topic = topic if topic is not None else getConfig('MQ', 'mqtopic')
        self._user = user if user is not None else getConfig('MQ', 'mquser')
        self._password = password if password is not None else getConfig('MQ', 'mqpassword')

    def produce_without_auth(self, data):
        url = self.URL_TEMPLATE % (self._protocol, self._host, self._port, self._topic)
        headers = {'Content-type': 'application/json'}
        if self._protocol == "http":
            resp = requests.post(url, data, headers=headers)
        else:
            resp = request.post(url, data, headers=headers, verify=False)
        if resp.status_code == 200 and 'serverTimeMs' in resp.text:
            return "Producer OK"
        else:
            return "Producer ERROR"

    def produce_with_auth(self, data):
        url = self.URL_TEMPLATE % (self._protocol, self._host, self._port, self._topic)
        if self._protocol == "http":
            resp = requests.post(url, data, headers=headers, auth=HTTPBasicAuth(self._user, self._password))
        else:
            resp = request.post(url, data, headers=headers, verify=False,auth=HTTPBasicAuth(self._user, self._password))
        if resp.status_code == 200 and 'serverTimeMs' in resp.text:
            return "Producer OK"
        else:
            return "Producer ERROR"

def getConfig(section, key):
    config = ConfigParser.ConfigParser()
    path = os.path.split(os.path.realpath(__file__))[0] + '/config.conf'
    config.read(path)
    return config.get(section, key)


if __name__ == '__main__':
    print('main')
    def main():
      data = {
        "status": "ACTIVE",
        "suspendUntilTimeUTC": 0,
        "alertId": "b483af7b-f6ae-455b-9be7-75a722f23458",
        "resourceId": "ea7e2446-e802-43e5-9425-cd80ef28bd36",
        "startTimeUTC": 1499680611242,
        "controlState": "OPEN",
        "alertDefinitionId": "AlertDefinition-EPOpsAdapter-Alert-system-availability-linux",
        "subType": "19",
        "cancelTimeUTC": 0,
        "updateTimeUTC": 1499680611242,
        "alertDefinitionName": "NodatareceivedforLinuxplatform",
        "type": "15",
        "alertLevel": "CRITICAL"
        }
      p = Producer()
      p.produce_without_auth(json.dumps(data))
      
    main()