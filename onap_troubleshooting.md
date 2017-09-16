## ONAP系统中各VM的异常排查方法

当OANP系统中各个vm出现异常或错误时，有时可能是因为环境造成的，重启服务即可，一般步骤如下：

```
# 删除所有容器
$ sudo docker rm $(sudo docker ps -a -q) --force

# 重启服务，运行/opt/<name>_install.sh文件
$ cd /opt
$ sudo ./<name>_install.sh
```

目录：

  * [aai-inst1](#aai-inst1)
  * [aai-inst2](#aai-inst2)
  * [dns-server](#dns-server)
  * [policy](#policy)

### aai-inst1

  aai-inst1 vm中共有10个container。其异常排除方法主要有：

  1. 查看/var/log/cloud-init-output.log

  2. 查看每个container的log信息。

  ```
  $ sudo docker logs <CONTAINER_NAME>
  or
  $ sudo docker logs <CONTAINER_NAME> -f
  ```

  3. aai-inst1中各服务正常，而与之交互的aai-inst2 vm异常，需进一步排查。

### aai-inst2

  aai-inst2 vm中共有3个container。其异常排查方法主要有：

  1. 查看/var/log/cloud-init-output.log

  2. 查看每个container的log信息。

  ```
  $ sudo docker logs <CONTAINER_NAME>
  or
  $ sudo docker logs <CONTAINER_NAME> -f
  ```

### dns-server

  dns-server vm中的dns服务由bind9提供，其配置文件为/etc/bind/zones/db.simpledemo.openecomp.org。

  检查dns-server是否异常的方法就是：**ONAP系统中各个VM均可通过域名ping各个服务，而不需要单独修改每个VM上的/etc/hosts文件**。

  因此，当某个vm出现异常时，一方面可能由vm本身引起，另一方面可能有域名解析引起。所以，错误的排查需要注意的dns-server的异常，而robot中的healthCheck并没有包含dns-server相关的检查。

  常用的域名有：

  ```
  sdc.api.simpledemo.openecomp.org
  appc.api.simpledemo.openecomp.org
  vid.api.simpledemo.openecomp.org
  ···
  ```

### policy

  policy vm中共有6个container。其异常排查方法主要有：

  1. 查看/var/log/cloud-init-output.log

  2. 查看每个container的log信息。

  ```
  $ sudo docker logs <CONTAINER_NAME>
  or
  $ sudo docker logs <CONTAINER_NAME> -f
  ```
