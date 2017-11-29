#!/usr/bin/env python
# -*- coding: utf-8 -*-


from oslo_config import cfg
from oslo_log import log as logging
from i18n import _, _LI, _LW, _LE
import oslo_messaging


oslo_messaging_opts = [
    cfg.StrOpt('event_stream_topic',
                default="test_notification",
                help=_('topic name for receiving events from a queue')
    )
]

cfg.CONF.register_opts(oslo_messaging_opts, group='oslo_messaging')

#For Notification mode, the control_exchange means the exchange in rabbitmq.
oslo_messaging.set_transport_defaults(control_exchange='notification')

#Init the oslo_log
LOG = logging.getLogger(__name__)

def prepare():
    product_name = 'oslo_client'
    logging.register_options(cfg.CONF)
    logging.setup(cfg.CONF, product_name)

class Client(object):

    def __init__(self):
        """
        Usage for cfg.CONF:
            cfg.CONF.{group_name}.{cfg.StrOpt.name}
        """
        self.topic = cfg.CONF.oslo_messaging.event_stream_topic
        self.client = None
        prepare()



class NotificationClient(Client):

    def __init__(self):
        """
        The method for notification client to send message called info(ctxt, msg, priority, retry).
        :param ctxt: (dict) A request context dict
        :param msg: (dict) Message to be sent
        :param priority: (str) Priority of the message(info, warn, error). It is the same as the function name in
            server's EndPoint.
        :param retry: (int) The num for client to re-send the message when it is failed. It is optional, and the
            default is None or -1(Means do not retry)
        """
        super(NotificationClient, self).__init__()
        self.transport = oslo_messaging.get_notification_transport(cfg.CONF,  url='rabbit://test:2iu38b1anC989b03c1ss@10.154.9.67:5672/')
        self.publisher_id = 'notifications_test'
        self.client = oslo_messaging.Notifier(self.transport, self.publisher_id, driver='messaging', topic=self.topic)

    def emit(self, message):
        """
        Method to send message to listener
        :param message: (dict) a dict object to send
        :return: None
        """
        self.event_type = 'oslo_test_event'
        self.client.info({}, self.event_type, message)
        LOG.info('Send message: %s', message)

if __name__ == '__main__':
    message = {'test':'A Test for oslo_messaging'}
    notification_client = NotificationClient()
    notification_client.emit(message)