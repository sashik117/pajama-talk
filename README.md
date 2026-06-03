# PajamaTalk

PajamaTalk is a cozy, mobile-first language learning app scaffolded with:

- `frontend/` - Kotlin Compose Multiplatform UI, Voyager tabs, Android-ready structure, and a desktop preview app.
- `web/` - responsive Vite/React preview for fast browser testing on `localhost:3175`.
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

### Backend With PostgreSQL

```powershell
docker compose up --build
```

This starts:

- PostgreSQL on `localhost:5432`
- FastAPI on `localhost:8000`

The API container uses `PAJAMA_DATABASE_URL=postgresql+psycopg://pajama:pajama@postgres:5432/pajamatalk`. Plain local development can still use SQLite through `backend/.env`.

### Frontend Desktop Preview

```powershell
cd frontend
$env:GRADLE_USER_HOME=(Resolve-Path ..).Path + "\.gradle-home"
.\gradlew.bat :desktopApp:run
```

The desktop target exists so the shared Compose UI can be checked on this Windows machine even before Android SDK setup.

### Web Preview

```powershell
cd web
npm install
npm run dev
```

Then open http://127.0.0.1:3175. The web preview talks to FastAPI on `http://127.0.0.1:8000` by default and mirrors the MVP flows: auth/demo login, Aura, Context Buddy, Speaking Rooms, SRS review, word storage, and Vibe settings.

Useful checks:

```powershell
npm run build
npm test
npm run test:e2e
```

`npm run test:e2e` expects FastAPI and the Vite dev server to already be running on `127.0.0.1:8001` and `127.0.0.1:3175`.

### Safe Workspace Cleanup

Generated files can be removed without touching source code:

```powershell
.\scripts\clean-workspace.ps1
```

For a larger cleanup that also removes dependency folders and Gradle caches, use:

```powershell
.\scripts\clean-workspace.ps1 -Deep
```

Deep cleanup saves much more disk space, but the next backend/web/KMP run will need to reinstall or redownload dependencies.

### Frontend Android

Install Android Studio + Android SDK, or use the Android command-line tools. On this Windows workspace the local SDK is installed at `D:/Apps/AndroidSdk`; create `frontend/local.properties` if needed:

```properties
sdk.dir=C\:\\Users\\<you>\\AppData\\Local\\Android\\Sdk
```

Then:

```powershell
cd frontend
.\gradlew.bat :androidApp:assembleDebug -PincludeAndroid=true
```

Fast compile check:

```powershell
cd frontend
$env:ANDROID_SDK_ROOT="D:\Apps\AndroidSdk"
$env:ANDROID_HOME="D:\Apps\AndroidSdk"
.\gradlew.bat :androidApp:compileDebugKotlin -PincludeAndroid=true
```

## Environment

Copy `backend/.env.example` to `backend/.env`. Real AI providers are optional for now; without keys the backend returns deterministic cozy mock responses so the app can be developed offline.

Useful provider settings:

- `PAJAMA_GEMINI_API_KEY` enables Gemini enrichment, context analysis, hints, and speaking replies.
- `PAJAMA_OPENAI_API_KEY` enables the optional OpenAI audio adapters for speech-to-text and text-to-speech.
- `PAJAMA_OPENAI_STT_MODEL`, `PAJAMA_OPENAI_TTS_MODEL`, `PAJAMA_OPENAI_TTS_VOICE`, and `PAJAMA_OPENAI_TTS_FORMAT` tune the voice provider layer.
- `PAJAMA_VOICE_PROVIDER_TIMEOUT_SECONDS` controls the backend timeout for external voice calls.

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
  web/
    src/
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

## Speaking WebSocket

The Speaking Rooms UI now sends practice lines through `WS /speaking/ws`. FastAPI streams assistant tokens back in real time and persists both sides of the room chat in `chat_history`.

Realtime hardening currently includes:

- `GET /speaking/history` for restoring persisted room messages from the backend.
- Typed frontend WebSocket client events.
- Backend `ping` -> `pong` handling for text and voice sockets.
- Frontend heartbeat pings while a turn is open.
- Client-side turn timeouts so stuck WebSocket calls fail clearly.
- A local durable retry queue for failed text and audio turns, so interrupted turns can be retried instead of disappearing.
- Backend stream finalization persists partial assistant replies if a WebSocket disconnects mid-answer.
- Unit tests for reducer snapshots and realtime client behavior.
- Playwright smoke tests for desktop and mobile web flows.

## Voice Mode Architecture

The voice socket now has a real domain/service layer:

- `VoiceRealtimeService` keeps per-call audio buffer state.
- `audio_chunk` events report accepted chunk count, byte count, and provider metadata.
- `end_audio` / `commit_audio` turns transcript hints into a normal speaking turn.
- `tts` events include provider, format, speed, and optional base64 audio payload metadata.
- The backend can use OpenAI transcription and speech generation when `PAJAMA_OPENAI_API_KEY` is configured, then falls back to browser/client speech behavior if the provider fails or no key is present.
- Web call mode records real microphone audio with `MediaRecorder`, sends base64 chunks with MIME metadata through `WS /speaking/voice-ws`, and uses browser speech recognition as a transcript hint when available.
- Web call mode can play provider audio payloads directly and falls back to `speechSynthesis` when only text is available.
- Web speaking turns retry once after a failed socket turn so short local disconnects do not feel like a dead button.
- Web call mode has a compact text fallback that still goes through `WS /speaking/voice-ws`.
- Kotlin Compose has the matching voice text fallback client path, a shared audio-chunk WebSocket client contract, backend room-history restore support, and an Android `MediaRecorder` implementation in `androidMain` for native audio capture.
- Web speaking room, mood, and chat history are stored locally and hydrated from backend history so a browser refresh restores the current practice session instead of dropping the conversation.

## Micro-Grammar Drops

`GET /grammar/drops` returns a soft grammar nudge based on recent chat mistake tags. The Aura screen renders the active drop with a tiny explanation and tap-to-complete quests.

## SRS Review Queue

`GET /words/review-due` returns only words that are due for the active language. The review screen now consumes that due queue instead of showing the first dictionary item.

## Multi-Language Core

PajamaTalk is not English-only. Words are stored with `language_code`, and the frontend can switch between:

`English`, `Ukrainian`, `Russian`, `Slovak`, `Polish`, `Czech`, `French`, `Spanish`, `Italian`, `German`, `Portuguese`, `Korean`, `Japanese`, `Chinese`, and `Turkish`.

The Vibe Check tab also lets the user choose the explanation/native language, including Ukrainian and Russian, so AI enrichment and hints can target the learner's real comfort language.

## Pronunciation And Real Practice Loop

The web preview now treats every visible learning unit as something the learner can hear:

- Daily focus phrases, learning-path examples, Context Buddy phrases, suggested words, dictionary terms, examples, SRS cards, grammar examples, speaking bubbles, hints, and call-summary phrases expose compact listen buttons.
- The learning path includes a listen-and-repeat shadow trainer.
- SRS review includes a small listening check: hear the word, type what you heard, then mark remember/forgot.
- Browser speech uses language-aware `speechSynthesis` locales for all supported learning languages.
- Backend fallback enrichment now generates practical "how to say" pronunciation hints instead of placeholder `/word/` strings, and existing stale placeholder transcriptions are corrected in API responses.

The Compose shared app has matching pronunciation infrastructure:

- Common `PlatformSpeechPlayer` contract.
- Android `TextToSpeech` actual with language locale mapping.
- Desktop no-op actual for safe preview builds.
- Storage and SRS cards expose compact listen actions for terms and examples.

## Still Not Done

- Native production voice capture: Android now has a compiled `MediaRecorder` path in shared KMP; iOS still needs a platform recorder actual on a macOS-capable build environment.
- Full UI decomposition: the React preview now has domain/state/controllers and dedicated speaking/voice/history hooks, but large screen components still need another extraction pass.
- Frontend E2E coverage depth: the suite now covers speaking, call fallback, context, storage, profile, and grammar smoke flows, but not every edge case.
- KMP parity pass: Compose has voice fallback sync, but the full mobile UX still needs another visual polish pass after web stabilizes.
