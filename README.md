# Start Up ONAP based on VIO 4.0

目录：

  + [环境准备](#环境准备)
  + [ONAP配置](#onap配置)
  + [ONAP环境信息](#onap环境信息)
  + [ENV文件](#env文件)
  + [TroubleShooting](troubleshooting_guide.md)

## 更新日志

  * 2017-9-20

    * 增加portal中vid获取service data失败的解决办法，详情见[TroubleShooting](troubleshooting_guide.md#vid_failed_to_fetch_service_instance_data_form_aai_response_code_404)

  * 2017-9-18

    * vid healthCheck失败及解决办法，详见[https://wiki.onap.org/questions/15996123/vid-throws-error-javax.servlet.servletexception-init-failed-to-find-or-instantiate-class-org.openecomp.portalsdk.core.onboarding.client.onboardingapiserviceimpl#](https://wiki.onap.org/questions/15996123/vid-throws-error-javax.servlet.servletexception-init-failed-to-find-or-instantiate-class-org.openecomp.portalsdk.core.onboarding.client.onboardingapiserviceimpl#)

    * 增加robot中demo init failure的解决办法，详情见[TroubleShooting](troubleshooting_guide.md#demo_init_failure)

  * 2017-9-15

    * AAI VM的错误排查及解决办法，详见[AAI-INST1](#aai-inst1的resource问题)
    * 增加ONAP系统中各VM的状态异常排查方法(更新中)，详见[ONAP系统中各VM的排查方法](onap_troubleshooting.md)

  * 2017-9-12

    * 添加policy VM的错误异常排查及解决办法[ONAP系统中各VM的排查方法](onap_troubleshooting.md)

  * 2017-9-6

    * 添加[基于VIO部署ONAP的技巧](onap_based_on_vio.md)(主要是为了应对vio环境的不稳定性)

  * 2017-9-5

    * 更新robot中container的ssl问题，详情见[TroubleShooting](troubleshooting_guide.md)

      + 主要文件

        + [keystone-proxy.conf](ConfigFile/keystone-proxy.conf)
        + [keystone.conf](ConfigFile/keystone.conf)

  * 2017-9-1

    * 解决robot中container的ssl问题，详情见[TroubleShooting](troubleshooting_guide.md)

        + 主要文件

          + [haproxy.cfy](ConfigFile/haproxy.cfg)
          + [local_setting.py](ConfigFile/local_setting.py)
          + [keystone.txt](keystone.txt)

  * 2017-8-29

    + 排查SDC中BE启动失败问题，详情如下[TroubleShooting](troubleshooting_guide.md)

  * 2017-8-25

    + 添加ONAP搭建过程，详情见[环境准备](#环境准备)、[ONAP配置](#ONAP配置)、[ENV文件](#ENV文件)
    + 添加基本VIO的ONAP的配置文件

      + 源文件

        + [onap_openstack_float.env](ConfigFile/onap_openstack_float.env)
        + [onap_openstack_float.yaml](ConfigFile/onap_openstack_float.yaml)

      + 修改后的文件

        + [onap_vio.env](ConfigFile/onap_vio.env)
        + [onap_vio.yaml](ConfigFile/onap_vio.yaml)

## 环境准备

  1. Linux VM，作为Heatclient的工具

  * 安装python环境、OpenstackClient、HeatClinet，并配置相应的环境变量

    参考如下：
    ```
    $ apt install python, python-pip
    $ pip install virtualenv, virtualenvwrapper
    $ pip install python-openstackclient, python-heatclient

    # 下载VIO的OpenStack RC文件，并进行配置
    $ source admin-openrc.sh
    ```

    参考链接：

    [https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux_OpenStack_Platform/5/html/End_User_Guide/install_clients.html](https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux_OpenStack_Platform/5/html/End_User_Guide/install_clients.html)

    [https://developer.rackspace.com/docs/cloud-orchestration/v1/getting-started/send-request-ovw/](https://developer.rackspace.com/docs/cloud-orchestration/v1/getting-started/send-request-ovw/)

    [https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux_OpenStack_Platform/5/html/End_User_Guide/cli_openrc.html](https://access.redhat.com/documentation/en-US/Red_Hat_Enterprise_Linux_OpenStack_Platform/5/html/End_User_Guide/cli_openrc.html)

  * 可能出现的问题

    + heatclient不能正常访问heatservice服务，出现SSL问题

    解决办法一：使用`--insecure`选项

    ```
    $ heat --insecure service-list
    ```

    解决办法二：使用vio.pem文件

    ```
    # 进入到VIO所在主机，将/etc/ssl/vio.pem 拷贝至heatclient所在主机的/etc/ssl/vio.pem
    # 向admin-openrc.sh添加OS_CACERT环境变量
    # export OS_CACERT=/etc/ssl/vio.pem
    $ source admin-openrc.sh
    $ openstack server list
    ```

    Ref:

    [https://blogs.vmware.com/openstack/prepare-a-linux-vm-for-managing-openstack/](https://blogs.vmware.com/openstack/prepare-a-linux-vm-for-managing-openstack/)

  2. Linux VM信息，用于登录ONAP中的VMs

  Linux_VM_IP : 10.110.141.221  
  User/Passwd: subond/123

  ```
  $ ssh subond@10.110.141.221
  ```

  3. Linux VM中ONAP相关的信息

  ```
  # VIO的rc文件地址为 /home/subond/heatclient/admin-openrc.sh
  $ source admin-openrc.sh

  # ONAP源码路径为 /home/subond/ONAP825/demo
  # Heat Template文件 /home/subond/ONAP825/demo/heat/ONAP/onap_vio.yaml
  # Heat Template 环境配置文件 /home/subond/ONAP825/demo/heat/ONAP825/onap_vio.env

  # 登录ONAP VMs的私钥路径为 /home/subond/heatclient/onap_rsa
  $ ssh -i onap_rsa ubuntu@OANP_VM_FloatingIP

  # 查看各VMs的ip地址
  $ openstack --insecure server list
  ```

## ONAP配置

  * Network

    public: 10.154.9.0/24网段：用于VM的FloatingIp

    Internal: 192.168.15.0/24网段：用于VM私网地址

  * Image

    ubuntu-14.04-server-cloudimg-amd64
    ubuntu-16.04-server-cloudimg-amd64

    Ref:

    [https://cloud-images.ubuntu.com/releases/](https://cloud-images.ubuntu.com/releases/)

  * Flavor

    |Flavor Name|vCPUs|RAM|Root Disk|
    |:--|:--|:--|:--|
    |onap.tiny|1|512MB|4GB|
    |onap.small|1|1GB|10GB|
    |onap.medium|2|2GB|20GB|
    |onap.large|4|4GB|50GB|
    |onap.xlarge|8|16GB|50GB|

## onap环境信息

  * horizon  
    https://10.154.2.225
  * OpenstackClient & HeatClinet  
    ip: 10.110.141.221  
    user/passwd: subond/123  
  * ONAP系统中各VM的信息  

    |server name|floating ip|os info|
    |:--|:--|:--|
    |aai-inst1|10.154.9.87|ubuntu-14.04|
    |aai-inst2|10.154.9.88|ubuntu-14.04|
    |sdc|10.154.9.84|ubuntu-16.04|
    |mso|10.154.9.89|ubuntu-16.04|
    |vid|10.154.9.76|ubuntu-14.04|
    |policy|10.154.9.81|ubuntu-14.04|
    |portal|10.154.9.83|ubuntu-14.04|
    |clamp|10.154.9.77|ubuntu-16.04|
    |robot|10.154.9.78|ubuntu-16.04|
    |appc|10.154.9.61|ubuntu-14.04|
    |dcae|10.154.9.62|ubuntu-14.04|
    |dns|10.154.9.68|ubuntu-14.04|
    |mr|10.154.9.89|ubuntu-14.04|
    |sdnc|10.154.9.85|ubuntu-14.04|

  * 登录ONAP系统各vm的方法

    ```
    # 先登录至OpenstackClient机(里面包含登录各VM私钥)
    # username: subond; password: 123
    $ ssh subond@10.110.141.221
    # 然后再登录至onap系统的各个vm，相应的Ip如上所示
    # username: ubuntu; no password
    $ ssh ubuntu@<vm_floatingip>
    ```

## ENV文件

  * ONAP REPO的时间及分支：25/Aug/2017, master

  * ENV文件：参照VIO系统环境，设定ONAP环境变量

    * router_gateway_ip: 用于ONAP系统的Router ip的设定，选VIO环境中可用的public IP即可

    * dns_list, external_dns: dns的设定需使用VIO外部环境可用的DNS服务，即10.142.7.21(VIO环境中)

  * 源文件

    + [onap_openstack_float.env](ConfigFile/onap_openstack_float.env)
    + [onap_openstack_float.yaml](ConfigFile/onap_openstack_float.yaml)

  * 修改后的文件

    + [onap_vio.env](ConfigFile/onap_vio.env)
    + [onap_vio.yaml](ConfigFile/onap_vio.yaml)
