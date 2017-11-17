## 中国移动集成问题汇总

#### **一、华为**
1. 创建volume失败，报错显示资源不足
	- **问题描述**：VIO4.0 cinder bug，在创建volume的时候会check datastore的resource是否满足volume
	的需求，但code实际上check的controller node的硬盘是否满足volume的需求。
	- **解决方案**：注销了cinder中check resource的code。修改文件 /usr/lib/python2.7/dist-packages/cinder/volume/flows/manager/create_volume.py
	
	 ```python
	 806 # Modify by damon-Damon
	 807 #image_utils.check_available_space(CONF.image_conversion_dir,
    808 #                                  image_meta['size'], image_id)
    ```
        
2. 创建block\_device\_mapping失败，
	- **问题描述**：创建block\_device\_mapping 是华为传入参数"disk_bus":"scsi"，该参数在vio中命名规则不一致，对应过来的命名规则是lsiLogic
	- **解决方案**：修改/usr/lib/python2.7/dist-packages/nova/virt/vmwareapi/vmops.py文件，碰到scsi时映射为lsiLogic
	
	```python
	977 # Add by damon-Damon
	978 if adapter_type == 'scsi':
   979  	adapter_type = constants.ADAPTER_TYPE_LSILOGICSAS

   1037 # Modify by damon-Damon
        if (adapter_type is not None and adapter_type not in valid_bus and adapter_type != 'scsi'):
   ```
    
	
3. 部署SBC应用，启动应用报错
	- **问题描述**：应用启动时，需要与网卡进行通信，默认的网卡type是E1000，华为生成不支持，只支持ovs和vmxnet 3。
	- **解决方案**：对华为的镜像添加了一项metadata，hw\_vif\_model=VirtualVmxnet3。以下是修改的镜像列表
		- Huawei\_SuSE\_V500R002C30SPC200\_sbc\_hru
		- Huawei\_SuSE\_V500R002C30SPC200\_sbc\_lbu
		- Huawei\_SuSE\_V500R002C30SPC200\_sbc\_vpu
4. 部署vUGW_OMU失败
	- **问题描述:** 创建虚拟机时，nova-scheduler显示没有host可供使用。是因为nova在get/resource\_providers接口进行filter时，返回结果为空，filter逻辑有问题。
	- **解决方案:** 修改文件/usr/lib/python2.7/dist-packages/nova/scheduler/client/report.py
	
	```python
    332 # Modify by damon-Damon
    333 #resp = self.get("/resource_providers?%s" % parse.urlencode(filters),
    334 #                version='1.7')
    335 resp = self.get("/resource_providers",
    336                 version='1.7')
	```
	
	- **解决方案解释:** 这种修改方案是不影响后续操作的。从修改代码可以看出我在进行获取resource\_providers的时候不进行filter。不进行filter获取的结果如下所示，可以看出只有一个resource\_provider，调用nova hypervisor-list显示的结果如下所示。可以看出resource\_provider就是hypervisor，对于vc来说就是compute2的cluster，所以对于单一cluster的VIO，进行fliter和不进行filter得到的结果是一样的。如果因为不进行filter，由于资源不够而最终创建虚机失败，nova这边也会接收到vc的error信息，也会抛出来，不影响后续操作，filter只是一个提前的检查而已。
	
	```python
	不进行filter，直接调用self.get("/resource_providers")得到的结果如下：
	{
	    u'resource_providers': [
	        {
	            u'generation': 158,
	            u'links': [
	                {
	                    u'href': u'/resource_providers/577b8b94-08cb-41e2-8c08-1b0124626a25',
	                    u'rel': u'self'
	                },
	                {
	                    u'href': u'/resource_providers/577b8b94-08cb-41e2-8c08-1b0124626a25/aggregates',
	                    u'rel': u'aggregates'
	                },
	                {
	                    u'href': u'/resource_providers/577b8b94-08cb-41e2-8c08-1b0124626a25/inventories',
	                    u'rel': u'inventories'
	                },
	                {
	                    u'href': u'/resource_providers/577b8b94-08cb-41e2-8c08-1b0124626a25/usages',
	                    u'rel': u'usages'
	                }
	            ],
	            u'uuid': u'577b8b94-08cb-41e2-8c08-1b0124626a25',
	            u'parent_provider_uuid': None,
	            u'name': u'domain-c31.7d9decd6-862d-4ae6-89d8-605d426429e4'
	        }
	    ]
	}
	```
	
	nova hypervisor-list 显示的结果
	
	![](../Image/nova-hypervisor-list.png)

#### **二、中兴**
1. vpn可以访问中兴vm的8080端口，通过移动的跳板机访问不了
	- **问题描述**：中兴在VIO部署的虚机，内部启动服务占用8080端口，为虚机绑定floating ip，在外部网络通过挂在vpn可以访问该虚机8080的应用，通过移动内部jumphost无法访问8080的应用。感觉应该是jumphost的问题，与VIO无关
	- **解决方案**：中兴测试发现，不绑定floating ip，通过将vm挂在到external network上面，手动配置一个外部网络的ip，就可以再移动jumphost上面访问该vm的8080服务，简介绕过去了这个问题

#### **三、VIO额外配置**

1. neutron 关闭spoofguard（**注：关闭spoofguard后，创建虚拟机是不能配置安全组**）
	- **操作步骤**
		1. 在控制节点的/etc/neutron/plugin/vmware/nsxv.ini文件中，添加配置项spoofguard_enabled = false
		2. 重启neutron-server服务
		3. 如果配置之前已经创建了网络和端口，需要通过以下命令关闭port_security
			
			```bash
			neutron net-update <net-id>  --port_security_enabled=False
			neutron port-update <port_id> --port_security_enabled=False
			```
2. VIO无法收集串口日志
	- **解决方案：**
		
		针对vc中的所有ESXi host，分别进行firewall的配置，开启serial port端口。步骤如下：
		1. 依次点击ESXi host->Configure->Security Profile->Edit
		2. enable "VM serial port connected over network"和"VM serial port connected over vSPC"端口。
		3. 点击ok保存
3. 添加新的计算节点

	由于172.30.4.14的host经常down掉，决定将这个节点替换掉，移动提供了新的刀片服务器，ip地址是172.30.4.25。咱们自己部署的ESXi 6.5，用户名/密码信息与之前的节点一致。现已添加至vc。后续会将14替换掉。
	
#### **四、Glance 常用指令**

1. 基于vmdk file创建镜像

	```bash
	glance image-create --disk-format vmdk --container-format bare --name centos-vmdk --file grub.vmdk --visibility public --progress --property vmware_disktype=streamOptimized
	```

2. 基于非vmdk创建镜像

	```bash
	glance-import import --name {image name} --url {image url} --image-format {qcow2/raw/vdi}
	```

2. 基于ova file创建镜像

	```bash
	openstack image create --container-format ova --public --file ***.ova --disk-format vmdk <image_name>
	```

#### **五、文件备份**

1. OMS 配置文件 [omjs.properties](./backup/omjs.properties)
2. Neutron 配置文件 [neutron.conf](./backup/neutron.conf)
3. loadbalancer01节点history [loadbalancer01-history](./backup/loadbalancer01-history)
4. oms节点history [oms-history](./backup/oms-history)
