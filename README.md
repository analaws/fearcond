# fearcond

# VRET PhD Project — Unity Experiments (Grand Canyon & Finnmark)

Overview
--------
This repository contains the Unity experiments and supporting code for:
- Main PhD experiment: Grand Canyon AI‑augmented VRET (inhibitory‑learning / expectancy‑violation focus).
- Secondary project: Finnmark Crisis Preparedness V‑CBAT (core educational demo + research subsample with randomized assets).

This README gives the developer quickstart, run/build instructions, event logging conventions, and how Unity integrates with the local AI agent and clinician dashboard.

Contacts
--------
- PhD lead: Kamilla Bergsnev — kamilla.bergsnev@gmail.com
- Developer: Ana Luisa Sanchez Laws
- Master students (operators): [Names]

Repo layout
----------
- /unity/                — Unity project(s); main scenes and scripts.
- /dashboard/            — Clinician dashboard source (Node/React or simple server).
- /agent/                — Local agent client / integration stubs (if used).
- /data_schema/          — JSON schema files and example JSONL events.
- /scripts/              — Helper scripts (time sync, validate logs, upload).
- /docs/                 — Protocols, SOPs, consent templates, pilot plan.
- /ops/                  — Operator quick guides, emergency SOP, competency checklist.
- /deploy/               — Build instructions, packaging notes.
- /logs/                 — Example logs (gitignored in real runs).

Core decisions (immutable for data integrity)
--------------------------------------------
- Event logging uses JSONL (one JSON object per line) with ISO 8601 UTC timestamps.
- Each event is atomic and persisted to local storage immediately; session bundles are uploaded to secure storage after session.
- Agent integration is local: your own agent runs on a local port and Unity communicates via WebSocket (recommended) or local REST calls. A stub agent is provided in /agent for development.

Prerequisites (developer)
-------------------------
- Unity LTS: 6.5 
- XR plugin: OpenXR (or Oculus integration if targeting Quest). Install XR Interaction Toolkit.
- Node.js (LTS) and npm — for dashboard dev (if using web dashboard)
- Git, git-lfs (if large assets)
- Polar SDK or BLE lib (if using PPG devices)
- Optional: Python 3 for small validation scripts

Branching & workflow
--------------------
- `main` — protected; stable release builds only.
- `dev` — active development branch.
- Feature branches: `feature/<short-name>`, PRs to `dev`.
- Tagging: use semantic tags for release builds, e.g., `v0.1.0-pilot`.

Quickstart — clone & open
-------------------------
1. Clone: git clone cd

2. Open Unity Hub and add the project `unity/` using the chosen Unity LTS version.
3. Install required Unity packages: XR Interaction Toolkit, Input System (if needed), Addressables (optional).

Run a local development build (Unity)
------------------------------------
1. Open the Unity project, switch platform to the target HMD (Android/Quest or PCVR).
2. In `Build Settings`, add the scenes:
- `Scenes/Calibration.unity`
- `Scenes/GrandCanyon.unity`
- `Scenes/Finnmark.unity`
- `Scenes/Neutral.unity`
3. Ensure `Player Settings` has the correct company name, bundle id, and WebSocket permission if using Quest.
4. Press Play for editor testing. Note: in-editor PPG integration may be stubbed or use microphone/keyboard test inputs.

Local agent integration (your agent, run locally)
-------------------------------------------------
We assume you run your own agent locally (no external GuestXR kiln). The Unity client connects to your agent via WebSocket. Default endpoints (configurable in `Assets/Config/connection.json`):

- Agent WebSocket (suggestion feed):
- `ws://localhost:9001/agent`   — Unity -> Agent: send `{ "type":"sensor_update", "session_id": "...", "hr": 86.4, "nlp_markers": {...} }`
- Agent -> Unity: `{ "type":"suggestion", "action":"increase", "target_level":3, "message":"Maintain level 3 for 60s", "confidence":0.82 }`

- Dashboard WebSocket:
- `ws://localhost:9002/dashboard` — Unity publishes telemetry; dashboard posts operator actions.

Message examples
- Unity sends sensor update:
`json
{
 "type": "sensor_update",
 "session_id": "GXR2026_0001",
 "timestamp_utc": "2026-09-21T10:13:44Z",
 "hr_bpm": 86.4,
 "nlp": {
   "speech_latency_ms": 400,
   "keyword_hits": ["fall", "freeze"],
   "valence_score": -0.78
 },
 "trial_number": 2
}

Agent suggestion (agent -> unity):
{
  "type": "suggestion",
  "session_id": "GXR2026_0001",
  "timestamp_utc": "2026-09-21T10:13:45Z",
  "action": "maintain",
  "target_level": 3,
  "message": "Maintain level 3 for 60s to test expectancy mismatch.",
  "suggestion_id": "sug_0001",
  "confidence": 0.89
}
Operator action (dashboard -> unity -> logged event):
{
  "type": "operator_action",
  "session_id": "GXR2026_0001",
  "timestamp_utc": "2026-09-21T10:13:46Z",
  "operator_id": "OP_JK",
  "action": "accept",
  "suggestion_id": "sug_0001",
  "override_reason_code": null
}`

**Logging & file locations**

Local log directory on operator PC (configurable): ./logs/sessions/. Each session is a folder session_<session_id>/ containing:
events.jsonl — atomic events in chronological order
physio.csv — raw physiological export (if device provides)
audio/ — short audio clips (de-identified filenames)
screenshot/ — optional scene capture at peak event
metadata.json — session metadata (session_id, participant_id, condition, environment_id, asset_pair)
After session end, a script scripts/upload_session.sh session_<id> bundles and uploads to secure server (SFTP) and writes checksum.

**Event schema**

See /data_schema/event_schema.json (contains the full JSON Schema). Use a simple validator during dev:

python3 -m pip install jsonschema
python3 scripts/validate_event.py events.jsonl data_schema/event_schema.json

**Development notes & priorities**

Implement event logger and JSONL writes first (critical).
Implement PPG integration and basic smoothing/peak detection.
Implement agent WebSocket stub and suggestion handling.
Implement clinician dashboard simple UI (Accept/Override) and operator logging.
Implement Grand Canyon scene flow and objective V-BAT metrics.
Implement Finnmark scene skeleton, asset pool, and randomization engine.
Pilot & iterate.

**Pilot checklist (minimum)**

Event logging verified for 10 consecutive sessions; timestamps sync within 200 ms.
HR stream present and peaks visible for expected trials.
Operator can accept/override agent suggestions; events recorded.
No crash for the full pilot session sequence.
Data uploaded to secure server and validated against schema.

**
Operator quick guide (one-liner)**

Turn on devices and check connections.
Start dashboard server: cd dashboard && npm start.
Start Unity operator build and connect to dashboard.
Start sensors, press baseline, confirm HR visible.
Start session, follow on-screen prompts; use stop button if required.
After session run scripts/upload_session.sh <session_id>.

**Support & escalation**

Developer issues: open GitHub issue with [dev] tag.
Data / ethics incidents: notify PhD lead immediately; log incident to /ops/incidents.log.

**License & attribution**

BSD-3 Clause. 
Third‑party assets and license constraints (Unity Asset Store packs, audio, etc.):

**Acknowledgements**

This project builds on the GuestXR architecture developed together with Bernhard Spanlang (Kiin / VirtualBodyworks) conceptually; the local agent implementation is custom code owned by the research team.
