#!/bin/bash
/usr/sbin/omv-rpc -u admin 'FileSystemMgmt' 'enumerateMountedFilesystems' '{"includeroot": true}' > /var/log/storagepod/file_systems_info.json