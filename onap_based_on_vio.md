## 基于VIO部署ONAP的技巧

### 针对VIO环境中Neutron与NSX通信不稳定，造成FloatingIp创建失败

**解决办法**：先删除创建失败的FloatingIp，然后在onap_vio.yaml文件中将用新的FloatingIp替换原来的FloatingIp，并update ONAP。

参考指令如下：

```shell
# 查看FloatingIp对应的id
$ neutron floatingip-list
# 找到要删除的floatingip的id，然后删除
$ neutron floatingip-delete <floatingip_id>

# 替换onap_vio.yaml文件中替换floatingip
$ openstack stack update -t onap_vio.yaml -e onap_vio.env <stack_name>
```

### sdc_vm在stack update过程中，由于使用了volume造成在重启失败

失败原因：sdc_vm在启动时需要确认volume的state为available，而在之前的启动过程中已经使用了volume，使之state变为in-use，造成的重启失败。

**解决办法**：在后台将volume的state置为available.

参考指令如下：

```shell
# 由于openstackclient权限问题，需要进入loadbalancer01进行操作
# 找到sdc使用的volume，并获取其volume_id
$ openstack volume list
# 将该volume的state置为available
$ openstack volume set --state available <volume_id>
```
