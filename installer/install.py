#!/usr/bin/env python3
"""
NewsApp Installer — install.py
Cross-platform installer for Linux/macOS/Windows.
Called by install.sh (Linux/macOS) or install.bat (Windows).

Phases:
  1. System dependencies  (Python already running us, so just Node + Docker)
  2. n8n via Docker Compose
  3. Django backend
  4. Vite frontend
  5. Desktop shortcut + launch
"""

import os
import sys
import platform
import subprocess
import time
import urllib.request
import urllib.error
import json
import shutil
import textwrap
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent   # project root (one level up from installer/)
BACKEND_DIR   = ROOT / "backend"
FRONTEND_DIR  = ROOT / "frontend"
N8N_DIR       = ROOT / "n8n"
N8N_DATA_DIR  = N8N_DIR / "data"
WORKFLOW_FILE = N8N_DIR / "workflow.json"
VENV_DIR      = ROOT / ".venv"

# ── Config ───────────────────────────────────────────────────────────────────
N8N_HOST      = "http://localhost:5678"
N8N_USER      = "admin@newsapp.local"
N8N_PASSWORD  = "newsapp2024"
BACKEND_PORT  = 8000
FRONTEND_PORT = 5173
OS            = platform.system()   # "Linux", "Darwin", "Windows"

# ── Helpers ──────────────────────────────────────────────────────────────────

def banner(text: str):
    width = 60
    print("\n" + "═" * width)
    print(f"  {text}")
    print("═" * width)

def step(msg: str):
    print(f"\n▶  {msg}")

def ok(msg: str):
    print(f"   ✔  {msg}")

def warn(msg: str):
    print(f"   ⚠  {msg}")

def fail(msg: str):
    print(f"\n✖  ERROR: {msg}")
    sys.exit(1)

def run(cmd, cwd=None, check=True, shell=False, capture=False):
    """Run a command, printing it first."""
    display = cmd if isinstance(cmd, str) else " ".join(str(c) for c in cmd)
    print(f"   $ {display}")
    kwargs = dict(cwd=cwd, shell=(shell or isinstance(cmd, str)))
    if capture:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
    result = subprocess.run(cmd, **kwargs)
    if check and result.returncode != 0:
        fail(f"Command failed (exit {result.returncode}): {display}")
    return result

def cmd_exists(name: str) -> bool:
    return shutil.which(name) is not None

def python_bin() -> Path:
    """Return path to the venv python executable."""
    if OS == "Windows":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"

def pip_bin() -> Path:
    if OS == "Windows":
        return VENV_DIR / "Scripts" / "pip.exe"
    return VENV_DIR / "bin" / "pip"

def prepare_n8n_data_dir():
    """Ensure the host bind-mount for n8n is writable before starting the container."""
    step("Preparing n8n data directory...")
    N8N_DATA_DIR.mkdir(parents=True, exist_ok=True)

    if OS == "Linux":
        try:
            os.chmod(N8N_DATA_DIR, 0o777)
            for child in N8N_DATA_DIR.rglob("*"):
                try:
                    os.chmod(child, 0o777 if child.is_dir() else 0o666)
                except OSError:
                    pass
            ok(f"n8n data directory is writable: {N8N_DATA_DIR}")
        except OSError as e:
            warn(f"Could not adjust permissions on {N8N_DATA_DIR}: {e}")
    else:
        ok(f"n8n data directory ready: {N8N_DATA_DIR}")

# ── Phase 1: System Dependencies ─────────────────────────────────────────────

def check_python():
    step("Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        fail(f"Python 3.9+ is required. You have {sys.version}. "
             "Download from https://python.org")
    ok(f"Python {version.major}.{version.minor}.{version.micro}")

def install_node():
    step("Checking Node.js and npm...")
    if cmd_exists("node") and cmd_exists("npm"):
        r = run(["node", "--version"], capture=True, check=False)
        ok(f"Node.js already installed: {r.stdout.decode().strip()}")
        return

    warn("Node.js not found. Attempting installation...")
    if OS == "Linux":
        run("curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -", shell=True)
        run("sudo apt-get install -y nodejs", shell=True)
    elif OS == "Darwin":
        if cmd_exists("brew"):
            run(["brew", "install", "node"])
        else:
            fail("Homebrew not found. Please install Node.js manually from https://nodejs.org "
                 "then re-run the installer.")
    elif OS == "Windows":
        fail("Node.js not found. Please install it from https://nodejs.org (LTS version), "
             "then re-run install.bat.")
    ok("Node.js installed.")

def install_docker():
    step("Checking Docker...")
    if cmd_exists("docker"):
        ok("Docker already installed.")
        _ensure_docker_running()
        return

    warn("Docker not found. Attempting installation...")
    if OS == "Linux":
        run("sudo apt-get update", shell=True)
        run("sudo apt-get install -y docker.io docker-compose-plugin", shell=True)
        run("sudo systemctl enable --now docker", shell=True)
        # Add current user to docker group so sudo isn't needed later
        user = os.environ.get("USER", "")
        if user:
            run(f"sudo usermod -aG docker {user}", shell=True, check=False)
        warn("You may need to log out and back in for docker group permissions. "
             "If docker commands fail, run: newgrp docker")
    elif OS == "Darwin":
        fail("Docker not found. Install Docker Desktop from https://docker.com/products/docker-desktop "
             "then re-run the installer.")
    elif OS == "Windows":
        fail("Docker not found. Install Docker Desktop from https://docker.com/products/docker-desktop "
             "then re-run install.bat.")
    ok("Docker installed.")

def _ensure_docker_running():
    step("Ensuring Docker daemon is running...")
    result = run(["docker", "info"], capture=True, check=False)
    if result.returncode == 0:
        ok("Docker daemon is running.")
        return
    if OS == "Linux":
        run("sudo systemctl start docker", shell=True)
        time.sleep(3)
    elif OS == "Darwin":
        run(["open", "-a", "Docker"])
        print("   Waiting for Docker Desktop to start", end="", flush=True)
        for _ in range(30):
            time.sleep(2)
            r = run(["docker", "info"], capture=True, check=False)
            if r.returncode == 0:
                print(" ✔")
                return
            print(".", end="", flush=True)
        fail("Docker did not start in time. Please start Docker Desktop manually and retry.")
    elif OS == "Windows":
        warn("Please make sure Docker Desktop is running, then press Enter to continue.")
        input()

# ── Phase 2: n8n via Docker Compose ──────────────────────────────────────────

def start_n8n():
    step("Starting n8n via Docker Compose...")
    compose_file = ROOT / "docker-compose.yml"
    if not compose_file.exists():
        fail(f"docker-compose.yml not found at {compose_file}")

    prepare_n8n_data_dir()

    # docker compose v2 (plugin) vs v1 (standalone)
    compose_cmd = _docker_compose_cmd()

    run(compose_cmd + ["up", "-d", "--pull", "always"], cwd=ROOT)
    ok("n8n container started.")

def _docker_compose_cmd():
    """Return ['docker', 'compose'] or ['docker-compose'] depending on what's installed."""
    r = run(["docker", "compose", "version"], capture=True, check=False)
    if r.returncode == 0:
        return ["docker", "compose"]
    if cmd_exists("docker-compose"):
        return ["docker-compose"]
    fail("Neither 'docker compose' nor 'docker-compose' found. "
         "Please install Docker Compose: https://docs.docker.com/compose/install/")

def wait_for_n8n():
    step(f"Waiting for n8n to be ready at {N8N_HOST} ...")
    compose_cmd = _docker_compose_cmd()

    for attempt in range(60):
        health = _n8n_container_health()
        state = _n8n_container_state()

        if health == "healthy" and _n8n_http_healthcheck():
            ok("n8n is up!")
            return

        if state in {"exited", "dead"}:
            warn(f"n8n container state is {state}; showing recent logs:")
            run(compose_cmd + ["logs", "--no-color", "--tail=80", "n8n"], cwd=ROOT, check=False)
            fail("n8n container exited before becoming ready. Check the logs above.")

        print(f"   ... attempt {attempt + 1}/60 (container: {state or 'unknown'}, health: {health or 'unknown'})", end="\r")
        time.sleep(3)

    warn("n8n did not become ready in time; showing recent logs:")
    run(compose_cmd + ["logs", "--no-color", "--tail=80", "n8n"], cwd=ROOT, check=False)
    fail("n8n did not become ready in time. Check the logs above.")

def _n8n_http_healthcheck() -> bool:
    try:
        req = urllib.request.urlopen(f"{N8N_HOST}/healthz", timeout=3)
        return req.status == 200
    except Exception:
        return False

def _n8n_container_state() -> str:
    result = run(["docker", "inspect", "newsapp-n8n", "--format", "{{.State.Status}}"], capture=True, check=False)
    if result.returncode != 0:
        return ""
    return result.stdout.decode().strip()

def _n8n_container_health() -> str:
    result = run(["docker", "inspect", "newsapp-n8n", "--format", "{{if .State.Health}}{{.State.Health.Status}}{{end}}"], capture=True, check=False)
    if result.returncode != 0:
        return ""
    return result.stdout.decode().strip()

def setup_n8n_owner():
    """POST to n8n's owner setup endpoint to create the default admin user."""
    step("Creating n8n admin user...")
    url = f"{N8N_HOST}/rest/owner/setup"
    payload = json.dumps({
        "email": N8N_USER,
        "firstName": "News",
        "lastName": "App",
        "password": N8N_PASSWORD,
    }).encode()
    req = urllib.request.Request(url, data=payload,
                                  headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        ok(f"n8n admin user created: {N8N_USER} / {N8N_PASSWORD}")
        return resp
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        if "already" in body.lower() or e.code in (400, 409):
            ok("n8n owner already configured — skipping.")
        else:
            warn(f"n8n owner setup returned {e.code}: {body[:200]}")

def _n8n_api(method: str, path: str, payload=None) -> dict:
    """Make an authenticated request to the n8n REST API."""
    import base64
    creds = base64.b64encode(f"{N8N_USER}:{N8N_PASSWORD}".encode()).decode()
    url = f"{N8N_HOST}/rest{path}"
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, method=method,
                                  headers={
                                      "Content-Type": "application/json",
                                      "Authorization": f"Basic {creds}",
                                  })
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        warn(f"n8n API {method} {path} → {e.code}: {body[:300]}")
        return {}

def import_workflow():
    step("Importing n8n workflow...")
    if not WORKFLOW_FILE.exists():
        warn(f"Workflow file not found at {WORKFLOW_FILE} — skipping import.")
        return

    with open(WORKFLOW_FILE) as f:
        workflow = json.load(f)

    result = _n8n_api("POST", "/workflows", workflow)
    wf_id = result.get("data", {}).get("id") or result.get("id")
    if wf_id:
        ok(f"Workflow imported (id={wf_id}).")
        # Activate it
        _n8n_api("PATCH", f"/workflows/{wf_id}", {"active": True})
        ok("Workflow activated.")
        return wf_id
    else:
        warn("Could not confirm workflow import. Check n8n UI at http://localhost:5678")
        return None

def trigger_first_run(wf_id):
    """Trigger the workflow once so it populates the DB on first install."""
    if not wf_id:
        return
    step("Triggering first workflow run...")
    result = _n8n_api("POST", f"/workflows/{wf_id}/run", {})
    if result:
        ok("First workflow run triggered. News will populate shortly.")
    else:
        warn("Could not trigger first run — you can do it manually in n8n.")

# ── Phase 3: Django Backend ───────────────────────────────────────────────────

def setup_backend():
    step("Creating Python virtual environment...")
    if not VENV_DIR.exists():
        run([sys.executable, "-m", "venv", str(VENV_DIR)])
        ok("Virtual environment created.")
    else:
        ok("Virtual environment already exists.")

    step("Installing backend dependencies...")
    run([str(pip_bin()), "install", "--upgrade", "pip"], check=False)
    run([str(pip_bin()), "install", "-r", str(BACKEND_DIR / "requirements.txt")])
    # Install test deps too
    run([str(pip_bin()), "install", "behave", "behave-django"], check=False)
    ok("Backend dependencies installed.")

    step("Running Django migrations...")
    run([str(python_bin()), "manage.py", "migrate", "--settings=backend.settings"],
        cwd=ROOT)
    ok("Migrations applied.")

# ── Phase 4: Frontend ─────────────────────────────────────────────────────────

def setup_frontend():
    step("Installing frontend dependencies (npm install)...")
    run(["npm", "install"], cwd=FRONTEND_DIR)
    ok("Frontend dependencies installed.")

# ── Phase 5: Desktop Shortcut ─────────────────────────────────────────────────

def create_desktop_shortcut():
    step("Creating desktop shortcut...")
    desktop = Path.home() / "Desktop"
    desktop.mkdir(exist_ok=True)

    if OS == "Linux":
        _create_shortcut_linux(desktop)
    elif OS == "Darwin":
        _create_shortcut_mac(desktop)
    # elif OS == "Windows":
    #     _create_shortcut_windows(desktop)

def _create_shortcut_linux(desktop: Path):
    run_script = ROOT / "run.sh"
    icon = ROOT / "installer" / "icon.png"  # optional
    entry = textwrap.dedent(f"""\
        [Desktop Entry]
        Version=1.0
        Type=Application
        Name=NewsApp
        Comment=Start the NewsApp local server
        Exec=bash -c '{run_script}'
        Icon={icon if icon.exists() else "web-browser"}
        Terminal=true
        Categories=Development;
    """)
    shortcut = desktop / "NewsApp.desktop"
    shortcut.write_text(entry)
    shortcut.chmod(0o755)
    ok(f"Desktop shortcut created: {shortcut}")

def _create_shortcut_mac(desktop: Path):
    run_script = ROOT / "run.sh"
    app_dir = desktop / "NewsApp.app" / "Contents" / "MacOS"
    app_dir.mkdir(parents=True, exist_ok=True)
    launcher = app_dir / "NewsApp"
    launcher.write_text(textwrap.dedent(f"""\
        #!/bin/bash
        bash '{run_script}'
    """))
    launcher.chmod(0o755)
    ok(f"App bundle created: {desktop / 'NewsApp.app'}")
#
# def _create_shortcut_windows(desktop: Path):
#     """Use PowerShell to create a .lnk shortcut."""
#     run_bat = ROOT / "run.bat"
#     ps_script = textwrap.dedent(f"""\
#         $WshShell = New-Object -comObject WScript.Shell
#         $Shortcut = $WshShell.CreateShortcut("{desktop}\\NewsApp.lnk")
#         $Shortcut.TargetPath = "{run_bat}"
#         $Shortcut.WorkingDirectory = "{ROOT}"
#         $Shortcut.Description = "Start NewsApp"
#         $Shortcut.Save()
#     """)
#     tmp = ROOT / "installer" / "_make_shortcut.ps1"
#     tmp.write_text(ps_script)
#     run(["powershell", "-ExecutionPolicy", "Bypass", "-File", str(tmp)])
#     tmp.unlink(missing_ok=True)
#     ok(f"Desktop shortcut created: {desktop / 'NewsApp.lnk'}")

# ── Phase 6: Launch ───────────────────────────────────────────────────────────

def launch_app():
    """Write and launch run.sh / run.bat, then open the browser."""
    step("Launching the application...")
    _write_run_scripts()

    if OS == "Windows":
        run_script = ROOT / "run.bat"
        subprocess.Popen(["cmd", "/c", str(run_script)], cwd=ROOT,
                         creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        run_script = ROOT / "run.sh"
        run_script.chmod(0o755)
        subprocess.Popen(["bash", str(run_script)], cwd=ROOT)

    print("\n   Waiting for servers to start...")
    time.sleep(6)
    _open_browser(f"http://localhost:{FRONTEND_PORT}")
    ok(f"App opened at http://localhost:{FRONTEND_PORT}")

def _write_run_scripts():
    """Generate run.sh and run.bat so the desktop shortcut works standalone."""

    # ── run.sh ────────────────────────────────────────────────────────────────
    run_sh = ROOT / "run.sh"
    run_sh.write_text(textwrap.dedent(f"""\
        #!/usr/bin/env bash
        # NewsApp launcher — generated by installer
        set -e
        ROOT="$(cd "$(dirname "$0")" && pwd)"

        mkdir -p "$ROOT/n8n/data"
        chmod -R a+rwX "$ROOT/n8n/data" 2>/dev/null || true

        echo "▶  Starting n8n..."
        docker compose -f "$ROOT/docker-compose.yml" up -d

        echo "▶  Starting Django backend (port {BACKEND_PORT})..."
        source "$ROOT/.venv/bin/activate"
        python "$ROOT/manage.py" runserver {BACKEND_PORT} &
        BACKEND_PID=$!

        echo "▶  Starting Vite frontend (port {FRONTEND_PORT})..."
        # To serve a production build instead, run: npm run build
        cd "$ROOT/frontend" && npm run dev &
        FRONTEND_PID=$!

        echo ""
        echo "══════════════════════════════════════════"
        echo "  NewsApp running!"
        echo "  Frontend  → http://localhost:{FRONTEND_PORT}"
        echo "  Backend   → http://localhost:{BACKEND_PORT}"
        echo "  n8n       → http://localhost:5678"
        echo "  Press Ctrl+C to stop all services."
        echo "══════════════════════════════════════════"

        trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; docker compose -f \\"$ROOT/docker-compose.yml\\" stop" EXIT
        wait
    """))
    run_sh.chmod(0o755)

    # ── run.bat ───────────────────────────────────────────────────────────────
    run_bat = ROOT / "run.bat"
    run_bat.write_text(textwrap.dedent(f"""\
        @echo off
        REM NewsApp launcher — generated by installer
        SET ROOT=%~dp0

        echo Starting n8n...
        docker compose -f "%ROOT%docker-compose.yml" up -d

        echo Starting Django backend (port {BACKEND_PORT})...
        start "NewsApp Backend" cmd /k "cd /d %ROOT% && .venv\\Scripts\\activate && python manage.py runserver {BACKEND_PORT}"

        echo Starting Vite frontend (port {FRONTEND_PORT})...
        REM To serve a production build instead, run: npm run build
        start "NewsApp Frontend" cmd /k "cd /d %ROOT%frontend && npm run dev"

        echo.
        echo ==========================================
        echo   NewsApp is starting!
        echo   Frontend  ^> http://localhost:{FRONTEND_PORT}
        echo   Backend   ^> http://localhost:{BACKEND_PORT}
        echo   n8n       ^> http://localhost:5678
        echo ==========================================

        timeout /t 5
        start http://localhost:{FRONTEND_PORT}
    """))

def _open_browser(url: str):
    import webbrowser
    webbrowser.open(url)

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    banner("NewsApp Installer")
    print(f"  OS: {OS}  |  Root: {ROOT}")

    # Phase 1 — System deps
    banner("Phase 1 · System Dependencies")
    check_python()
    install_node()
    install_docker()

    # Phase 2 — n8n
    banner("Phase 2 · n8n (Docker)")
    start_n8n()
    wait_for_n8n()
    setup_n8n_owner()
    wf_id = import_workflow()
    trigger_first_run(wf_id)

    # Phase 3 — Backend
    banner("Phase 3 · Django Backend")
    setup_backend()

    # Phase 4 — Frontend
    banner("Phase 4 · Vite Frontend")
    setup_frontend()

    # Phase 5 — Shortcut + Launch
    banner("Phase 5 · Desktop Shortcut & Launch")
    create_desktop_shortcut()
    launch_app()

    banner("✔  Installation complete!")
    print(textwrap.dedent(f"""
      Frontend   → http://localhost:{FRONTEND_PORT}
      Backend    → http://localhost:{BACKEND_PORT}
      n8n        → http://localhost:5678
                   user:     {N8N_USER}
                   password: {N8N_PASSWORD}

      Next time, just double-click the "NewsApp" shortcut on your Desktop.
    """))

if __name__ == "__main__":
    main()
