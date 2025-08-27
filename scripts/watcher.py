from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta, timezone
import time
import json
import os

LOG_FILE = "/var/log/storagepod/storagepod_recent_activity.json"

class ChangeLogger(FileSystemEventHandler):
    def on_any_event(self, event):
        if event.is_directory:
            return
        
        event_type = event.event_type  # created, modified, deleted, moved

        if event_type not in {"created", "modified"}:
            return

        file_path = event.src_path
        timestamp = datetime.now(timezone.utc).isoformat()

        log_entry = {
            "path": file_path,
            "event": event_type,
            "timestamp": timestamp
        }

        print(log_entry)

        # Append to file
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    data = json.load(f)
            else:
                data = []

            data.append(log_entry)    

            data = [
                entry for entry in data if datetime.fromisoformat(entry["timestamp"]) >= datetime.now(timezone.utc) - timedelta(days=7)
            ]

            with open(LOG_FILE, "w") as f:
                json.dump(data, f, indent=2)
            
        except Exception as e:
            print("Log write error:", e)

def getDestinationFolder(base_path="/srv"):
    try:
        for entry in os.listdir(base_path):
            full_path = os.path.join(base_path, entry)
            if os.path.isdir(full_path) and entry.startswith("dev-disk-"):
                return f"{full_path}/Folder1"
        return None
    
    except FileNotFoundError:
        return None

if __name__ == "__main__":
    path = getDestinationFolder()

    if path is None:
        print("Base folder to monitor not found")
        exit(-1)
        
    event_handler = ChangeLogger()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print("Watching for changes...")

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

