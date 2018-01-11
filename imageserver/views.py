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

import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from keystoneauth1 import loading, session
from glanceclient import Client
import random,string

AUTH_URL = 'http://10.154.2.225:5000'
USERNAME = 'admin'
PASSWORD = 'vmware'
PROJECT_ID = '0013cfe6a3874820b41eecb22e0426f4'

logger = logging.getLogger(__name__)

class ImageUpload(APIView):

    parser_classes = (MultiPartParser, FormParser,)

    #curl -F "file=@/Users/bins/Documents/cirros.vmdk" "http://127.0.0.1:9004/api/multicloud-vio/v0/imageupload"

    def post(self, request, format=None):

        my_file = request.FILES['file']

        random_name = ''.join(random.sample(string.ascii_letters + string.digits, 4))
        file_name = my_file.name[:my_file.name.find('.')] + "_" + random_name + my_file.name[my_file.name.find('.'):]

        file_dest = '/Users/bins/Documents/project/' + file_name
        with open(file_dest, 'wb+') as temp_file:
            for chunk in my_file.chunks():
                temp_file.write(chunk)
        temp_file.close()

        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(
            auth_url = AUTH_URL,
            username = USERNAME,
            password = PASSWORD,
            project_id = PROJECT_ID
        )
        try:
            keystone_session = session.Session(auth = auth)
        except Exception as e:
            return Response(data={'error': str(e)}, status=e.http_status)

        try:
            glance = Client('2', session = keystone_session)
            image = glance.images.create(name = file_name[:file_name.find('.')],
                                         is_public='True',
                                         disk_format=file_name[file_name.find('.')+1:],
                                         container_format="bare")
            glance.images.upload(image.id, open('/Users/bins/Documents/project/' + file_name, 'rb'))

        except Exception as e:
            return Response(data={'error': str(e)}, status=e.http_status)
     
        return Response(data={'status': 'OK'}, status=status.HTTP_201_CREATED)


class ImageDownload(APIView):

    def post(self, request, imageid):

        loader = loading.get_plugin_loader('password')
        auth = loader.load_from_options(
            auth_url = AUTH_URL,
            username = USERNAME,
            password = PASSWORD,
            project_id = PROJECT_ID
        )
        
        try:
            keystone_session = session.Session(auth = auth)
        except Exception as e:
            return Response(data={'error': str(e)}, status=e.http_status)

        client = Client('2', session = keystone_session)

        img = client.images.data(imageid)

        image_detail = client.images.get(imageid)

        file_name = "/Users/bins/Documents/project/%s.%s" % (image_detail.name, image_detail.disk_format)
        image_file = open(file_name, 'w+')

        for chunk in img:
            image_file.write(chunk)
        image_file.close()
        
        return Response(data={'status': 'OK'},
                        status=status.HTTP_200_OK)
