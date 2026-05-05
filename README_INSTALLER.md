# GrowKnow Installer Guide

This document explains how to install and run GrowKnow on **Linux**. If you are on Windows, use **WSL2** and follow the Linux steps inside the WSL terminal.

## Index

- [Prerequisites](#prerequisites)
- [Quick start](#quick-start)
- [What the installer does](#what-the-installer-does)
- [Service URLs](#service-urls)
- [After installation](#after-installation)
- [Project structure](#project-structure)
- [Manual dependency installation](#manual-dependency-installation)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Install or verify the following before running the installer:

- Python 3.9 or newer
- Node.js and npm
- Docker with Docker Compose support
- Ollama

Recommended setup on Linux:

- Use a recent Ubuntu-based distribution or a compatible system.
- Make sure your user can run Docker without permission errors.
- If you plan to use the browser UI and n8n together, keep ports `5173`, `8000`, `5678`, and `11434` available.

### Windows note

Use **WSL2** with a Linux distribution such as Ubuntu, then run the same Linux commands from inside WSL. This keeps the runtime behavior aligned with the documented installer flow.

## Quick start

From the project root:

```bash
bash install.sh
```

The installer delegates to the Python installer under `installer/install.py`.

## What the installer does

The current installer flow is organized in phases:

### Phase 1: system dependencies

- Checks for Python 3.9+.
- Ensures Python packages needed for virtual environments and pip are available.
- Checks Node.js/npm.
- Checks Docker support for the n8n container.

### Phase 2: Ollama and local models

- Checks whether Ollama is installed.
- Starts the Ollama service if needed.
- Pulls the local models used by the automation workflow.

### Phase 3: n8n automation

- Starts n8n with Docker Compose.
- Waits for n8n to become healthy.
- Imports the workflow stored in `n8n/workflow.json`.
- Triggers the first ingestion run.

### Phase 4: Django backend

- Creates a virtual environment if needed.
- Installs the backend Python dependencies.
- Runs database migrations.

### Phase 5: frontend setup

- Installs the frontend dependencies in `frontend/`.

### Phase 6: launch

- Starts the services needed for local development.
- Opens the application in the browser when supported by the environment.

## Service URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:5173 |
| Backend | http://localhost:8000 |
| n8n | http://localhost:5678 |
| Ollama | http://localhost:11434 |

## After installation

To run the project again after it has been installed:

```bash
bash run.sh
```

If you are using WSL on Windows, run the command inside your WSL terminal.

## Project structure

```text
growknow/
├── install.sh              # Linux entry point for installation
├── run.sh                  # Launcher script used after setup
├── docker-compose.yml      # n8n container definition
├── installer/
│   └── install.py          # Main installer logic
├── n8n/
│   ├── workflow.json       # n8n automation workflow
│   └── data/               # n8n persistent data
├── backend/                # Django project
└── frontend/               # Vite/React app
```

## Manual dependency installation

If automatic setup fails, install these manually and then re-run `bash install.sh`:

| Dependency | Official source |
|---|---|
| Python | https://python.org |
| Node.js | https://nodejs.org |
| Docker | https://www.docker.com/ |
| Ollama | https://ollama.com/download |

You can also verify Ollama manually:

```bash
ollama serve
```

In another terminal:

```bash
ollama run llama3.2
```

Type `/bye` to exit the model session.

## Troubleshooting

### Docker permission denied on Linux

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### n8n does not start

```bash
docker compose logs n8n
```

### n8n cannot reach Ollama or Django

- Make sure `host.docker.internal` resolves from inside the container.
- On Linux, the Compose file should map `host.docker.internal` through the host gateway.
- Confirm Ollama is reachable:

```bash
curl http://localhost:11434/api/version
```

### Ollama model credetial fails
Set the `BaseURL` in your Ollama client configuration to point to the correct address, especially if you are running from WSL or a non-Linux environment:

```bash
BaseURL = http://host.docker.internal:11434
```

### Port already in use

Check whether another process is using ports `5678`, `8000`, or `5173`:

```bash
lsof -i :5678
```

### Reset everything

```bash
docker compose down -v
rm -rf .venv
bash install.sh
```
