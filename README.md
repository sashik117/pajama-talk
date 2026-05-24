# PajamaTalk

PajamaTalk is a cozy, mobile-first language learning app scaffolded with:

- `frontend/` - Kotlin Compose Multiplatform UI, Voyager tabs, Android-ready structure, and a desktop preview app.
- `backend/` - FastAPI REST API with JWT auth, word storage, AI enrichment stubs, SRS scheduling, context analysis, grammar drops, and a speaking WebSocket.

The app is designed around soft pressure, personal context, and a lofi pastel interface.

## Quick Start

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Then open:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

### Frontend Desktop Preview

```powershell
cd frontend
$env:GRADLE_USER_HOME=(Resolve-Path ..).Path + "\.gradle-home"
.\gradlew.bat :desktopApp:run
```

The desktop target exists so the shared Compose UI can be checked on this Windows machine even before Android SDK setup.

### Frontend Android

Install Android Studio + Android SDK, then create `frontend/local.properties`:

```properties
sdk.dir=C\:\\Users\\<you>\\AppData\\Local\\Android\\Sdk
```

Then:

```powershell
cd frontend
.\gradlew.bat :androidApp:assembleDebug -PincludeAndroid=true
```

## Environment

Copy `backend/.env.example` to `backend/.env`. Real AI providers are optional for now; without keys the backend returns deterministic cozy mock responses so the app can be developed offline.

## Project Shape

```text
PajamaTalk/
  backend/
    app/
      api/
      core/
      db/
      models/
      schemas/
      services/
      main.py
    tests/
  frontend/
    shared/
    androidApp/
    desktopApp/
```

## Sprint 3A Status

The shared Compose app now talks to FastAPI in dev mode:

- Shows a mobile-first auth gate with login, registration, and a one-tap demo profile.
- Loads real words from `GET /words`.
- Adds enriched words through `POST /words/enrich`.
- Reviews cards through `POST /words/{id}/review`.
- Analyzes pasted text through `POST /context/analyze`.
- Loads speaking rooms through `GET /speaking/rooms`.

The frontend tries `http://127.0.0.1:8000` first, then `http://127.0.0.1:8001`.

## Sprint 3B Status

Profile settings are now persisted through `PATCH /auth/me`:

- Active learning language.
- Native language.
- Learning vibe and daily minutes.
- AI tone.

The `Vibe Check` tab now reflects live word counts for the selected language and lets the user update vibe/tone from the UI.

## Sprint 4A Status

The backend now has an AI provider layer:

- Uses Gemini `generateContent` when `PAJAMA_GEMINI_API_KEY` is present.
- Falls back to deterministic mock enrichment when no key is configured.
- Keeps word enrichment and context analysis behind one service API.
- Adds `GET /stats/me` for profile-aware word, review, and vibe stats.

## Speaking Hints

`POST /speaking/hints` returns three short reply options for the current room:

- `simple`
- `conversational`
- `spicy`

The Speaking Rooms UI exposes this through the hints button in the dialog preview.

## SRS Review Queue

`GET /words/review-due` returns only words that are due for the active language. The review screen now consumes that due queue instead of showing the first dictionary item.

## Multi-Language Core

PajamaTalk is not English-only. Words are stored with `language_code`, and the frontend can switch between:

`English`, `Slovak`, `Polish`, `Czech`, `French`, `Spanish`, `Italian`, `Korean`, `Japanese`, `Chinese`, and `Turkish`.
