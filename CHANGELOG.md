# Changelog

All notable changes to this project will be documented in this file.

The format is based on *Keep a Changelog*, and this project aims to follow semantic versioning once releases start.

## Unreleased

### Added
- `docs/TODO.md` backlog for robustness/scalability work.

### Changed
- systemd timer-triggered services now run as `Type=oneshot` and no longer restart in a loop.
- Auth responses now use proper exception raising and consistent success payloads.

### Fixed
- Recent-activity cleanup jq filter (7-day retention).
- Recent-activity monitor now initializes a valid JSON array log and handles paths with spaces.
- Admin user is no longer created with a plaintext password.
- Guard against accidental deletion of the storage root via the delete API.
- Avoid import-time crashes when `STORAGE_DIR` can't be resolved, and fail fast on startup with a clear error.
- Hardened storage path validation to prevent traversal and symlink-based escapes.
- Fixed `/search` `limit` typing and clamped results to protect the Pi/SQLite.
- Folder compression now handles empty folders without errors.
- CORS is no longer configured as wildcard-origins with credentials; it now uses a safe default allowlist and is env-configurable.
- Deleting a directory via the API now removes descendant DB entries (prevents stale search results).

### Security
- Protected `/api/v1/files/*`, `/api/v1/uploads/*`, and `/api/v1/auth/` user listing with JWT verification.
- `GET /api/v1/auth/` now requires an admin role.
