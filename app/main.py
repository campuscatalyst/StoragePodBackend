from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import files, auth, system, media, tus_server
from contextlib import asynccontextmanager
from app.db.main import init_db
from app.core.auth import Auth
from starlette.middleware.trustedhost import TrustedHostMiddleware
from app.logger import logger
from app.utils import is_first_boot, scan_and_insert, mark_first_boot_done, create_tmp_uploads_folder
from app.config import STORAGE_DIR

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up: initializing database...")
    logger.info("Starting up the SQL DB")
    
    init_db()
    success = Auth.create_initial_user()

    if not success:
        raise RuntimeError("Failed to create initial user. Aborting startup.")
    
    if is_first_boot():
        create_tmp_uploads_folder()
        scan_and_insert(root_path=STORAGE_DIR)
        mark_first_boot_done()
    
    yield

    print("Shutting down: closing database engine...")  # SQLite doesn’t need manual close

# Create the FastAPI app
app = FastAPI(title="Files Explorer API", lifespan=lifespan)

# if the requested isn't from this then it will return error - 400
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*.campuscatalyst.info", "*.local", "localhost", "127.0.0.1"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=[
        "Location",
        "Tus-Resumable",
        "Tus-Version",
        "Tus-Extension",
        "Tus-Max-Size",
        "Upload-Offset",
        "Upload-Length",
        "Upload-Expires",
    ],
)

app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(tus_server.router, tags=["tus"])
app.include_router(system.router, prefix="/api/v1/system", tags=["system"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(media.router, prefix="/api/v1/media", tags=["media"])

@app.get("/api/v1/server-status")
def server_status():
    return {"status": "online"}
