import asyncio, os
from streaming_form_data.targets import FileTarget
from app.core.utils.upload_tasks import update_progress
from streaming_form_data import StreamingFormDataParser
from app.db.main import get_session
import re
from fastapi import Request
from starlette.requests import ClientDisconnect

class TrackingFileTarget(FileTarget):
    """File target that tracks upload progress for large files"""

    def __init__(self, file_path: str, task_id: str, filename: str):
        """
            file_path - the abs path of the file
            task_id - the task id of the upload
            filename - the file name. 
        """
        super().__init__(filename=file_path)
        self.task_id = task_id
        self.bytes_written = 0 # bytes written to the dest filepath
        self.last_progress_update = 0
        self.progress_threshold = 1024 * 1024 * 16  # Update every 16MB to avoid too frequent updates

    async def update_progress_wrapper(self, written, total):
        with get_session() as session:
            await update_progress(session, self.task_id, written, total)
    
    def on_start(self):
        """Called when file upload starts"""
        super().on_start()
        asyncio.create_task(self.update_progress_wrapper(0, 0))
    
    def on_data_received(self, chunk: bytes):
        """Called for each chunk - optimized for large files"""
        super().on_data_received(chunk)
        self.bytes_written += len(chunk)

        # Only update progress every 16MB to avoid performance overhead
        if self.bytes_written - self.last_progress_update >= self.progress_threshold:
            self.last_progress_update = self.bytes_written
            asyncio.create_task(self.update_progress_wrapper(self.bytes_written, self.bytes_written))
    
    def on_finish(self):
        super().on_finish()
        asyncio.create_task(self.update_progress_wrapper(self.bytes_written, self.bytes_written))

class SingleFileStreamingParser:
    """Custom parser to handle multiple large files in streaming fashion"""

    def __init__(self, request_headers: dict, dest_dir: str, task_id: str, filename: str):
        self.headers = request_headers
        self.dest_dir = dest_dir
        self.task_id = task_id
        self.filename = filename
        self.parser = StreamingFormDataParser(headers=request_headers)

    def _sanitize_filename(self, filename: str):
        """Sanitize filename to prevent directory traversal and ensure uniqueness"""
        filename = os.path.basename(filename)

        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

        # Ensure we have a filename
        if not filename or filename.startswith('.'):
            raise ValueError("Invalid Filename")
         
        return filename
    
    def _create_file_target(self, filename: str):
        """Create a file target for the given filename"""

        safe_filename = self._sanitize_filename(filename=filename)
        file_path = os.path.join(self.dest_dir, safe_filename)

        target = TrackingFileTarget(file_path=file_path, task_id=self.task_id, filename=safe_filename)
        self.saved_filename = safe_filename

        return target
    
    async def parse_and_save_files(self, request: Request):
        """Parse multipart stream and save files, returning list of saved filenames"""
        print("HEADERS:", dict(request.headers))

        self.parser.register('file', self._create_file_target(filename=self.filename))

        try:
            async for chunk in request.stream():
                self.parser.data_received(chunk)
                
        except ClientDisconnect:
            raise
        except Exception as e:
            raise Exception(f"Upload parsing failed: {str(e)}")
        
        return self.filename


