# StoragePod Recent Files Monitor

This script is to monitor the file system for any changes, such as added, deleted, modified etc. 

Steps for enabling StoragePod Monitor:
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

Steps for enabling StoragePod Recent files Cleanup:
---
    - After cloning copy the scripts to /usr/local/bin
      cd recent_files_monitor/ && cp storagepod_cleanup.sh /usr/local/bin/

    - Copy service & timer file to - /etc/systemd/system/
      cp cleanup_recent_activity.service /etc/systemd/system/
      cp cleanup_recent_activity.timer /etc/systemd/system/

    - Give executable permissions - 
      chmod +x /usr/local/bin/storagepod_cleanup.sh

    - Verify the Timer - 
      systemctl list-timers --all | grep cleanup_recent_activity

    - To check the logs - 
      sudo journalctl -u cleanup_recent_activity.service -n 20 --no-pager
      systemctl list-timers --all | grep cleanup_recent_activity
    
    - To restart the service - 
      sudo systemctl daemon-reload
      sudo systemctl restart cleanup_recent_activity.service
    
    - To restart the timer - 
      sudo systemctl daemon-reload
      sudo systemctl restart cleanup_recent_activity.timer