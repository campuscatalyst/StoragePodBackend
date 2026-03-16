# StoragePodBackend — TODO

This is a working backlog focused on making the backend robust on Raspberry Pi (resource constrained) and safe as a NAS controller.

Legend: `[P0]` urgent (data loss / security / runaway load), `[P1]` important, `[P2]` nice-to-have.

## [P0] Safety / correctness
- [x] Fix systemd services that are run-by-timer to be `Type=oneshot` and remove `Restart=always` (prevents restart loops).
  - `scripts/system_info/system_info.service:7`
  - `scripts/media_metrics_scanner/media_metrics_scanner.service:7`
- [x] Fix recent-activity cleanup jq filter (uses `env.now` but sets `--arg now`).
  - `scripts/recent_files_monitor/storagepod_cleanup.sh:8`
- [x] Make recent-activity monitor create a valid JSON array file on first run; handle empty/corrupt file gracefully.
  - `scripts/recent_files_monitor/storagepod_monitor.sh:15`
- [x] Make inotify parsing resilient to spaces/newlines in paths (avoid `read event fullpath` splitting).
  - `scripts/recent_files_monitor/storagepod_monitor.sh:20`
- [x] Enforce auth on all file-mutating routes (delete/move/copy/rename/compress) and uploads.
  - `app/api/routes/files.py:7` (auth dependency currently commented)
- [x] Fix FastAPI error handling: don’t `return HTTPException(...)`; `raise` for errors and return normal success responses.
  - `app/core/auth.py:118`, `app/core/auth.py:175`
  - `app/api/routes/tus_server.py:40`
- [x] Fix initial admin credential handling (don’t store plaintext `"admin"`; align “first login via serial” flow with actual behavior).
  - `app/core/auth.py:39`, `app/core/auth.py:130`
- [x] Prevent destructive delete of storage root (`path=""` or `"/"` should be rejected explicitly).
  - `app/core/file_manager.py:300`
- [x] Hard-fail early if `STORAGE_DIR` can’t be resolved (avoid import-time crash on `TEMP_UPLOADS_DIR` join).
  - `app/config.py:18`

## [P0] Security hardening
- [ ] Replace `allow_origins=["*"]` + `allow_credentials=True` with a safe, explicit CORS policy.
  - `app/main.py:38`
- [ ] Add authorization checks for TUS upload creation/completion (otherwise anyone can upload into the storage volume).
  - `app/api/routes/tus_server.py:42`
- [ ] Remove or lock down “get all users” endpoint (or require admin token).
  - `app/api/routes/auth.py:6`
- [x] Harden path validation to prevent traversal and symlink escapes.
  - `app/core/file_manager.py:45`

## [P1] Data integrity (DB ↔ filesystem consistency)
- [ ] Decide the “source of truth” for file metadata:
  - Option A: filesystem is source of truth (DB is cache) → add periodic reconciliation + orphan cleanup.
  - Option B: DB is source of truth → make all operations go through DB transactionally.
- [ ] Update SQLite entries on rename/move/copy/delete (directory deletes should cascade/remove children).
  - `app/core/file_manager.py` (rename/move/copy/delete paths)
- [ ] Handle deletions in the DB when files are removed outside the API (stale search results today).
  - `app/utils.py:31` (scan inserts/merges but never deletes)
- [ ] Move `first_boot.lock` into a persistent location (e.g. inside the DB volume) or store it in SQLite.
  - `app/utils.py:22`

## [P1] Reliability / performance on Raspberry Pi
- [ ] Offload heavy blocking IO (zip, large directory stats, shutil operations) to background worker/threadpool; avoid blocking the event loop.
  - `app/core/file_manager.py` (list/zip/compress/move/copy)
- [ ] Make zip progress robust for empty folders (avoid divide-by-zero).
  - `app/core/file_manager.py` (zip logic)
- [ ] Add timeouts/limits: max results in search, max directory listing size/page, max zip size, max concurrent compress jobs.
- [ ] Add request/response models for consistent API shape and smaller responses (especially for large listings).

## [P2] Observability / operations
- [ ] Align logging paths: app logger defaults to `/var/log/app` but JSON metrics are in `/var/log/storagepod`.
  - `app/logger.py:5`, `app/config.py:21`
- [ ] Add a proper `/healthz` + `/readyz` (DB reachable, storage path resolvable, metrics readable).
- [ ] Pin docker images and Python deps (avoid surprise breakage on Pi).
  - `docker-compose.yaml` (`nginx:latest`)
  - `requirements.txt` (un-pinned versions)

## [P2] Product enhancements (NAS UX)
- [ ] Add folder download (server-side zip stream) or batch download.
  - `app/api/routes/files.py:61`
- [ ] Add pagination/sorting for directory listings.
- [ ] Add filesystem “events” endpoint that exposes recent changes (and optionally a websocket/SSE stream).
