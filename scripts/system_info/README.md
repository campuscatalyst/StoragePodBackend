# System Info Service

This script is to collect the system info related data. This will run the following scripts every 5 mins. 

- get_filesystem_info - It will give the info regarding the filesystem.
- get_disks_info - It will give the details about the harddisks present in the storage pod. 
- get_smart_info - This will give SMART info related to the harddisks. 
- get_system_metrics - It will give the Raspberry pi system details, like cpu usage, memory consumption etc. 


Steps:
---
    - After cloning copy the scripts to /usr/local/bin
      cd system_info/ && cp *.sh /usr/local/bin/

    - Copy service & timer file to - /etc/systemd/system/
      cp system_info.service /etc/systemd/system/
      cp system_info.timer /etc/systemd/system/

    - Give executable permissions - 
      chmod +x /usr/local/bin/run_all.sh
      chmod +x /usr/local/bin/get_disks_info.sh
      chmod +x /usr/local/bin/get_filesystem_info.sh
      chmod +x /usr/local/bin/get_smart_info.sh
      chmod +x /usr/local/bin/get_system_metrics.sh

    - Start and enable the timer - 
      sudo systemctl start system_info.timer
      sudo systemctl enable system_info.timer

    - Verify the Timer - 
      systemctl list-timers --all | grep system_info

    - To check the logs - 
      sudo journalctl -u system_info.service -n 20 --no-pager
      systemctl list-timers --all | grep system_info
    
    - To restart the service - 
      sudo systemctl daemon-reload
      sudo systemctl restart system_info.service
    
    - To restart the timer - 
      sudo systemctl daemon-reload
      sudo systemctl restart system_info.timer
