# StoragePod File Monitor

This script is to monitor the file system for any changes, such as added, deleted, modified etc. 

Steps:
---
    - After cloning copy the scripts to /usr/local/bin
      cd recent_files_monitor/ && cp storagepod_monitor.sh /usr/local/bin/

    - Copy service & timer file to - /etc/systemd/system/
      cp storagepod_monitor.service /etc/systemd/system/

    - Give executable permissions - 
      chmod +x /usr/local/bin/storagepod_monitor.sh
    
    - Install inotify-tools - which is used for monitoring for the file system for any changes. Event based. 
      sudo apt install inotify-tools

    - Start and enable the timer - 
      sudo systemctl start storagepod_monitor.service
      sudo systemctl enable storagepod_monitor.service

    - To restart the service - 
      sudo systemctl daemon-reload
      sudo systemctl restart storagepod_monitor.service
