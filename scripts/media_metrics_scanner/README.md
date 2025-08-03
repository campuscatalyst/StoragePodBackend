# Media Metrics Scanner

This script is to collect the number of images, audio, videos, docs in the Folder1. 

NOTE - It will run every 2 hours. 


Steps:
---
    - After cloning copy the scripts to /usr/local/bin
      cd media_metrics_scanner/ && cp media_metrics_scanner.sh /usr/local/bin/

    - Copy service & timer file to - /etc/systemd/system/
      cp media_metrics_scanner.service /etc/systemd/system/
      cp media_metrics_scanner.timer /etc/systemd/system/

    - Give executable permissions - 
      chmod +x /usr/local/bin/media_metrics_scanner.sh

    - Start and enable the timer - 
      sudo systemctl start media_metrics_scanner.timer
      sudo systemctl enable media_metrics_scanner.timer

    - Verify the Timer - 
      systemctl list-timers --all | grep media_metrics_scanner

    - To check the logs - 
      sudo journalctl -u media_metrics_scanner.service -n 20 --no-pager
      systemctl list-timers --all | grep media_metrics_scanner
    
    - To restart the service - 
      sudo systemctl daemon-reload
      sudo systemctl restart media_metrics_scanner.service
    
    - To restart the timer - 
      sudo systemctl daemon-reload
      sudo systemctl restart media_metrics_scanner.timer
