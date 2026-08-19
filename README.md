# fearcond

# VRET PhD Project Kamilla Bergsnev — Unity Experiments (Grand Canyon & Finnmark)

Overview
--------
This repository contains the Unity experiments and supporting code for:
- Main PhD experiment: Grand Canyon AI‑augmented VRET (inhibitory‑learning / expectancy‑violation focus).
- Secondary project (with Ana Luisa Sanchez Laws): Finnmark Crisis Preparedness V‑CBAT (core educational demo + research subsample with randomized assets).

This README gives the developer quickstart, run/build instructions, event logging conventions, and how Unity integrates with the local AI agent and clinician dashboard.

Contacts
--------
- PhD lead: Kamilla Bergsnev, kamilla.bergsnev@gmail.com
- Developer: Ana Luisa Sanchez Laws, ana.l.laws@uit.no

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
- Unity LTS: 2021.3.x or 2022.3.x
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
- Tagging: use semantic tags for release builds, e.g., `v0.1
