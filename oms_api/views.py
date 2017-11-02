# Copyright (c) 2017 VMware, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

# OMS API:
#   /j_spring_security_check?j_username={}&j_password=%{}: POST, username、password, login
#   /hello: GET, hello API
#   /version: GET. server version
#   /status: GET, server status
#   /tasks: GET, task list
#   /networks: GET, network list
#   /datastores: GET, datastore list
#   /clusters: GET, deployment list
#   /cluster/{}: GET, name, get specified deployment
#   /cluster/{}: DELETE, name, delete specified deployment
#   /clusters: POST, spec, create deployment
#   /vc: POST, spec, add compute vc
#   /vc-certificate?host={}&port={}: GET, host、port, query vc certificate
#   /vc: GET, vc list
#   /vcinfo: POST, spec, query vc information
#   /clusters/{}/availabilityzones: GET, name, query all AZ
#   /clusters/{}/availabilityzones: PUT, name、spec, Sync AZ according to the spec
#   /cluster/{}/config: PUT, name, add nova datastore
#   /task/{}: GET, taskid, get specified task
#   /clusters/{}/novadatastore: PUT, name、spec, delete nova datastore
#   /clusters/{}/glancedatastore: PUT, name、spec, delete glance datastore
#   /clusters/{}/edit: PUT, name、spec, edit cluster 
#   /clusters/{}/profile: GET, name, retrieve cluster profile
#   /clusters/plan: PUT, spec, create deplyment plan
#   /cluster/{}/nodegroup/{}/plan: PUT, name、nodegroup、node, add nova node plan
#   /cluster/{}/nodegroup/{}/scaleout: PUT, name、nodegroup、spec, add nova node
#   /clusters/{}/nodegroups: POST, name、spec, add nova nodegroup
#   /cluster/{}/nodegroup/{}/node: DELETE, name、nodegroup、node, del nova node
#   /network/{}?action=add: PUT, name、spec, increase IP addresses to a network
#   /network/{}?action=remove: PUT, name、spec, remove IP addresses from a network
#   /network/{}/async: PUT, name、spec, update DNS
#   /conf: GET, get system configuration
#   /conf?syslogserver={}&syslogserverport={}&syslogserverprotocol={}&syslogservertag={}:
#       :PUT, logserver、port、protocol、tag, set system log server
#   /network/{}: GET, name, get network by name
#   /bundles: POST, spec, create support bundle
#   /bundle/{}; GET, dest, get support bundle
#   /validates/{}: POST, type、spec, validate 
#   /clusters/{}/services/{}?action={}:PUT, name、service、action, manage openstack services
#   /clusters/{}/services?action=start:PUT, name、spec, start services
#   /clusters/{}/services?action=stop:PUT, name、spec, stop services
#   /clusters/{}/services?action=restart:PUT, name、spec, restart services
#   /clusters/{}/csr: POST, name、spec, generate csr
#   /clusters/{}/horizon: POST, name、spec, add horizon
#   /clusters/{}/horizon: DELETE, name、title, delete horizon
#   /clusters/{}/horizon: GET, name, horizon list
#   /plugin/status: GET, get plugin status
#   /checkOmsVCConnection: GET, check oms-vc connection
#   /connection/status: GET, get oms-vc connection
#   /plugin/register?addException=true: POST, register plugin
#   /datacollector?enabled={}: POST, false, change datacollector setting
#   /datacollector: GET, get datacollector setting
#   /phauditfile: GET, get audit file
#   /cluster/{}?action=start: PUT, name, start cluster
#   /cluster/{}?action=stop: PUT, name, stop cluster
#   /cluster/{}?action=retry: PUT, name, retry cluster
#   /clusters/{}/upgrade/provision: POST, name、spec, upgrade provisio 
#   /clusters/{}/upgrade/retry: PUT, name、spec, upgrade retry
#   /clusters/{}/upgrade/configure: PUT, name, migrate blue cluster data
#   /clusters/{}/upgrade/switch: PUT, name, switch to green cluster
#   /clusters/{}/keystonebackend: PUT, name、spec, switch keystone backend
#   /deploymenttype?deployment_type={}: POST, type, change deployment type
#   /clusters/{}/unconfigceilometer: PUT, name, unconfig ceilometer
#   /cluster/{}/vcconf: PUT, name、spec, vc configuration



import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import requests
from restclient import RestClient
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json
import re
logger = logging.getLogger(__name__)

rest_client = RestClient("10.154.9.156", "administrator@vsphere.local", "VMware1!")

class Omsnode(APIView):
    def post(self, request, cluster, ng):
        api_url_template = "cluster/{}/nodegroup/{}/scaleout"
        url = api_url_template.format(cluster, ng)
        try:
            resp = rest_client.do_put(url, request.body)    
        except Exception as e:
            return Response(data={'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data={'oms': resp},
                        status=status.HTTP_202_ACCEPTED)


    def delete(self, request, cluster, ng, nd):
        api_url_template = "cluster/{}/nodegroup/{}/node"
        url = api_url_template.format(cluster, ng)
        try:
            resp = rest_client.do_delete(url, nd)
        except Exception as e:
            return Response(data={'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data={'oms': resp},
                        status=status.HTTP_202_ACCEPTED)


class Omsdatastore(APIView):
    def post(self, request):
        try:
            resp = rest_client.do_put("cluster/VIO/config", request.body)
        except Exception as e:
            return Response(data={'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data={'oms': resp},
                        status=status.HTTP_202_ACCEPTED)

    def delete(self, request):
        try:
            resp = rest_client.do_put("clusters/VIO/novadatastore", request.body)
        except Exception as e:
            return Response(data={'error': str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(data={'oms': resp},
                        status=status.HTTP_202_ACCEPTED)