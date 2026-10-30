# NeonSAN CI 框架导航


以下路径相对于 ci/ 仓库根目录，仅用于搜索定位；符号、签名及行为均需实读复核。

| 能力 | 待定位符号 | 文件导航 |
| --- | --- | --- |
| 卷管理 | create_volume / list_volume / delete_volume | test_case/services/neonsan_api/api/client/center.py |
| 快照管理 | create_snapshot / delete_snapshot / list_snapshot | test_case/services/neonsan_api/api/client/center.py |
| 克隆管理 | clone_volume / detach_clone_relationship | test_case/services/neonsan_api/api/client/center.py |
| 池管理 | create_pool / list_pool | test_case/services/neonsan_api/api/client/center.py |
| 对象大小 | get_volume_objsize | test_case/services/neonsan_api/api/client/center.py |
| 数据校验 | write_files_to_block / read_file_from_block_device / check_file_md5_block | test_case/services/data_verification/data_set_manage.py |
| 块设备 | QBDDevice.map / unmap / mkfs / mount / umount / remap | test_case/services/qbd/qbd_device.py |
| 故障注入 | FaultStore 相关方法 | test_case/services/fault_injection/fault_injection.py |
| 远程执行 | SSHExecutor.connect / execute | test_case/services/excutor/executor.py |
| CLI | NeonSANCLI.neonsan_cli | test_case/tools/neonsan_cli.py |
| fio | NEONFIO.neonfio | test_case/tools/neonfio.py |
| 协议常量 | QBD_PROTOCOL_TYPE_TCP / QBD_PROTOCOL_TYPE_RDMA | test_case/services/neonsan_api/const/qbd.py |

