# Cherry Production API

A Flask-based backend for a music content service. This repository provides RESTful song, tag, artist, title, and upload APIs plus a simple dashboard for access log analytics.

## Features

- REST API for songs, tags, artists, titles, and types
- Search and filter songs by title, artist, type, and keyword
- Audio, image, and PDF upload endpoints backed by Cloudinary
- Play count / like tracking for songs
- Admin-protected create/update/delete operations
- Dashboard and analytics endpoints for log-based statistics
- Health check and service info endpoints

## Tech Stack

- Python 3
- Flask 3
- Flask-RESTful
- Flask-SQLAlchemy
- Flask-CORS
- Cloudinary uploads
- MySQL / PostgreSQL via SQLAlchemy

## Requirements

- Python 3.11+ (or compatible)
- `pip`
- Local MySQL database for development, or a production `DATABASE_URL`

## Installation

1. Clone the repository

   ```bash
   git clone https://github.com/cherry-lcy/cherryproduction-server.git
   cd my-music-site-server
   ```

2. Create and activate a Python virtual environment

   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1   # PowerShell
   # or
   .\venv\Scripts\activate.bat   # cmd.exe
   ```

3. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The app loads configuration from environment variables and `.env`.

Required environment variables for production:

- `FLASK_ENV` — `production` or `development`
- `DATABASE_URL` — SQLAlchemy database URL for production
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

### Development database fallback

When `FLASK_ENV` is not set to `production`, the app uses the local MySQL URI configured in `config.py`.

## Run Locally

### Using Flask

```powershell
$env:FLASK_APP = 'app'
$env:FLASK_ENV = 'development'
flask run
```

### Using Gunicorn

```powershell
gunicorn app:app
```

## Endpoints

### Health and info

- `GET /`
- `GET /health`
- `GET /info`

### Dashboard

- `GET /dashboard` — dashboard UI
- `GET /dashboard/api/stats` — dashboard analytics JSON

### Songs

- `GET /api/songs` — list all songs
- `POST /api/songs` — create a song (admin only, form-data)
- `DELETE /api/songs` — delete a song by JSON payload (admin only)

- `GET /api/song/<id>` — get a song by ID
- `PUT /api/song/<id>` — update a song by ID (admin only)
- `DELETE /api/song/<id>` — delete a song by ID (admin only)

### Search and play count

- `GET /api/songs/search` — search songs by query params
  - supported params: `title`, `artist`, `type`, `q`, `sort_by`, `order`, `limit`, `page`, `per_page`, `language`
- `GET /api/like/<id>` — read play count for a song
- `POST /api/like/<id>` — increment play count
- `DELETE /api/like/<id>` — decrement play count

### Uploads

- `POST /api/upload-audio` — upload audio file (admin only, multipart form-data)
- `POST /api/upload-image` — upload image file (admin only, multipart form-data)
- `POST /api/upload-pdf` — upload PDF file (admin only, multipart form-data)
- `POST /api/upload-signature` — upload signature payload

### Tags

- `GET /api/tags` — list all tags
- `GET /api/tags/<title>` — list tags for a song title
- `POST /api/tags/<title>` — add a tag to a song (admin only)
- `DELETE /api/tags/<title>` — delete tags for a song title (admin only)
- `GET /api/tag/<id>` — list tags by song ID
- `DELETE /api/tag/<id>` — delete a tag by ID (admin only)

### Metadata

- `GET /api/artists` — list artists
- `GET /api/titles` — list titles
- `GET /api/titles/<artist>` — list titles by artist
- `GET /api/types` — list song types

## Notes

- Database tables are created automatically when the app starts.
- The app initializes CORS, logging, and RESTful routes in `app.py`.
- Uploads rely on Cloudinary credentials to be available in environment variables.

## Deployment

This app is ready for deployment on platforms like Railway or any WSGI-compatible host.

This app is currently deployed on Render.com privately.

- `Procfile` and `railway.toml` are included for deployment setup.
- Use `gunicorn app:app` in production.

### Related Repositories and Sites
Frontend Repository: https://github.com/cherry-lcy/cherryproduction
Live Site: 