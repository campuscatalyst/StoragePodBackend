import os
import logging
from logging.handlers import TimedRotatingFileHandler

class AppLogger:
    def __init__(self, log_dir: str | None = None, log_file: str = "app.log"):
        preferred_dir = log_dir or os.environ.get("LOG_DIR") or "/var/log/storagepod"
        self.log_path = self._resolve_log_path(preferred_dir, log_file)
        self._setup_logger()

    def _resolve_log_path(self, preferred_dir: str, log_file: str) -> str:
        candidates = [
            preferred_dir,
            "/var/log/app",
            "/tmp/storagepod_logs",
        ]

        last_error: Exception | None = None
        for candidate in candidates:
            try:
                os.makedirs(candidate, exist_ok=True)
                return os.path.join(candidate, log_file)
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"Unable to create any log directory: {last_error}")

    def _setup_logger(self):
        self.logger = logging.getLogger("app_logger")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False  # Avoid duplicate logs

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"
        )

        # File Handler with daily rotation
        file_handler = TimedRotatingFileHandler(
            filename=self.log_path,
            when="midnight",
            backupCount=7,
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)

        # Add handlers only if not already added
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


# Export default logger instance
logger = AppLogger().get_logger()
