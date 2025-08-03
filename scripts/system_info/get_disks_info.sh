#!/bin/bash
/usr/sbin/omv-rpc -u admin 'DiskMgmt' 'getList' '{"start": 0, "limit": 50}' > /var/log/storagepod/hard_disks_info.json