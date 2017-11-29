#!/usr/bin/env python
# -*- coding: utf-8 -*-

from oslo_config import cfg
from oslo_log import log as logging
from i18n import _, _LI
import oslo_messaging
import json
import time
import sys
sys.path.append("..")
from vio.dmaap.dmaap_producer import Producer

LOG = logging.getLogger(__name__)

def prepare():
    product_name = "oslo_server"
    logging.register_options(cfg.CONF)
    logging.setup(cfg.CONF, product_name)

'''
add below items into nova.conf and restart nova services

notification_driver=messaging
notification_topics= notifications_test
notify_on_state_change=vm_and_task_state
notify_on_any_change=True
instance_usage_audit=True
instance_usage_audit_period=hour
'''

class NotificationEndPoint():

    # custom event type you want to receive
    VM_FAILURE_EVENTS = {
        'compute.instance.delete.end': 'DELETE',
        'compute.instance.pause.end': 'PAUSE',
        'compute.instance.power_off.end': 'POWER_OFF',
        'compute.instance.rebuild.error': 'REBUILD',
        'compute.instance.shutdown.end': 'SHUTDOWN',
        'compute.instance.soft_delete.end': 'SOFT_DELETE',
    }
    filter_rule = oslo_messaging.NotificationFilter(
            publisher_id='^compute.*')

    def info(self, ctxt, publisher_id, event_type, payload, metadata):
        status = payload.get('state_description')
        if status != "" and event_type in VM_FAILURE_EVENTS:
            self.action(payload)
            # throw event to dmaap
            producer = Producer()
            producer.produce_without_auth(json.dumps(payload))

    def action(self, data):
        LOG.info(_LI(json.dumps(data)))


class Server(object):

    def __init__(self):
        self.topic = 'notifications_test'
        self.server = None
        prepare()


class NotificationServer(Server):

    def __init__(self):
        super(NotificationServer, self).__init__()
        # environment at 10.154.8.17
        self.transport = oslo_messaging.get_notification_transport(cfg.CONF,  url='rabbit://test:2iu38b1anC989b03c1ss@10.154.9.67:5672/')
        # The exchange must be the same as control_exchange in transport setting in client.
        self.targets = [oslo_messaging.Target(topic=self.topic, exchange='nova')]
        self.endpoints = [NotificationEndPoint()]

    def start(self):
        LOG.info(_LI("Start Notification server..."))
        self.server = oslo_messaging.get_notification_listener(self.transport, self.targets, self.endpoints, executor='threading')
        self.server.start()
        self.server.wait()

    def stop(self, graceful=False):
        if self.server:
            LOG.info(_LI("Stop the Notification server..."))
            self.server.stop()
            if graceful:
                LOG.info(_LI("Notification server stopped successfully. Waiting for final message to be processed..."))
                self.server.wait()

'''
# for local test
if __name__ == '__main__':
    notification_server = NotificationServer()
    notification_server.start()
'''