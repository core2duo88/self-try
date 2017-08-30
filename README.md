# Start Up ONAP based on VIO 4.0

目录：

  + [环境配置](#环境配置)
  + [ONAP配置](#onap配置)
  + [ENV文件](#env文件)
  + [ONAP中可能出现的问题](#onap可能出现的问题)

    + [sdc服务不可用](#sdc服务不可用)

## 更新日志

  * 2017-8-29

    + 排查SDC中BE启动失败问题，详情如下[SDC服务不可用](#sdc服务不可用)

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

    解决办法：使用`--insecure`选项

    ```
    $ heat --insecure service-list
    ```

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

## ONAP中可能出现的问题

### sdc服务不可用

  错误现象：

  ![SDC_BE_DOWN](Image/sdc_be_down.PNG)

  排查方法：

  第一步：进入SDC所在的主机，查看各CONTAINER是否正常；  
  第二步：利用SDC自身脚本检查SDC中各服务的异常情况；  
  第三步：对SDC中有问题的服务进行单独log检查。

  具体参考如下：

  ```shell
  # 进入SDC所在的主机，Ip地址为10.154.9.75
  $ ssh -i onap_rsa ubuntu@10.154.9.75

  # 查看CONTAINER情况
  $ sudo docker ps -a

  # SDC自身检查脚本 /data/scripts/docker_health.sh
  $ ./docker_health.sh
  # 亦可直接调用health检查方法
  # http://localhost:8181/sdc1/rest/healthCheck
  # http://localhost:8080/sdc2/rest/healthCheck
  $ curl http://localhost:8181/sdc1/rest/healthCheck
  $ curl http://localhost:8080/sdc2/rest/healthCheck

  # 对SDC中各服务(BE, ES, FE等)进行单独排查
  # 其log文件位于 /data/logs/
  # BE的错误日志 /data/logs/BE/SDC/SDC-BE/error.log
  $ cat error.log
  2017-08-29T02:05:36.661Z|||||ES-Health-Check-Thread|||SDC-BE||||||||ERROR||||192.168.15.35||o.o.sdc.be.dao.impl.ESCatalogDAO||ActivityType=<?>, Desc=<Error while trying to connect to elasticsearch. host: [10.154.9.75:9300] | port: 9200 | error: None of the configured nodes are available: [{#transport#-1}{10.154.9.75}{10.154.9.75:9300}]>org.elasticsearch.client.transport.NoNodeAvailableException: None of the configured nodes are available: [{#transport#-1}{10.154.9.75}{10.154.9.75:9300}]
  ```

  错误原因：

  BE不能连接至ES，进一步原因是VIO中不支持VM访问自身的FloatingIp。

  解决办法：清除SDC VM中的FloatingIp信息，然后重启服务。

  具体参考如下：

  ```
  # SDC VM中FloatingIp的信息的位置 /opt/config/public_ip.txt
  $ cd /opt/config/
  $ mv public_ip.txt public_ip.txt.break

  # SDC中各服务通过挂载VOLUME的方式进行工作，因此，重启服务前需注释掉sfdisk相关代码，并清除相关数据
  # sfdisk相关代码位置 文件/opt/asdc_install.sh中84-88行(基于ONAP 2017-8-25 master分支源码)
  # 相关代码如下
  # 84 # sfdisk /dev/$DISK < /opt/asdc_ext_volume_partitions.txt
  # 85 # mkfs -t ext4 /dev/$DISK"1"
  # 86 # mkdir -p /data
  # 87 # mount /dev/$DISK"1" /data
  # 88 # echo "/dev/"$DISK"1  /data           ext4    errors=remount-ro,noatime,barrier=0 0       1" >> /etc/fstab

  # 清空相关数据，位置/data/
  $ rm -rf /data/*

  # 删除所有的CONTAINER，并重启服务，即重新运行脚本/opt/asdc_install.sh
  $ sudo docker rm $(sudo docker ps -a -q)
  $ cd /opt/
  $ sudo ./asdc_install.sh
  ```
