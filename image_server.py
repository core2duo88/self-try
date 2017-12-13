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

import paramiko
import os, sys, time
from keystoneauth1 import loading, session
from glanceclient import Client
import random,string

AUTH_URL = 'http://10.154.2.225:5000'
USERNAME = 'admin'
PASSWORD = 'vmware'
PROJECT_ID = '0013cfe6a3874820b41eecb22e0426f4'

def multicloud_transfer(ip, port, user, password, remote_file, local_dest):
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, port, user, password)
        a = ssh.exec_command('date')
        stdin, stdout, stderr = a
        print stdout.read()
        print "start transfering data from %s" % ip
        sftp = paramiko.SFTPClient.from_transport(ssh.get_transport())
        sftp = ssh.open_sftp()
    except Exception as e:
        print "SSH client error"
        raise e

    random_name = ''.join(random.sample(string.ascii_letters + string.digits, 4))
    image_format = remote_file[remote_file.rfind('.') + 1:]
    image_name = remote_file[remote_file.rfind('/'):remote_file.rfind('.')]
    image_file = '%s_%s.%s' % (image_name, random_name, image_format)
    sftp.get(remote_file, '%s%s' % (local_dest, image_file))

    print "start uploading data through keystone server at %s" % AUTH_URL

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
        print "keystone authentication error "
        raise e

    try:
        glance = Client('2', session = keystone_session)
        image = glance.images.create(name = '%s_%s' % (image_name[1:], random_name),
                                     is_public='True',
                                     disk_format='%s' % image_format,
                                     container_format="bare")
        glance.images.upload(image.id, open('%s%s' % (local_dest, image_file), 'rb'))
    except Exception as e:
        print "glance server error"
        raise e

    print "upload to glance server success!"


multicloud_transfer('10.154.9.17',
                    22,
                    'viouser',
                    'vmware',
                    '/home/viouser/cirros-0.3.0-i386-so-disk.vmdk',
                    '/Users/bins/Documents/project')