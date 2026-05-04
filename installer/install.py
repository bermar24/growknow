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
import http.cookiejar
import json
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
N8N_USER      = "admin@growknow.local"
N8N_PASSWORD  = "GrowKnowApp2026"
BACKEND_PORT  = 8000
FRONTEND_PORT = 5173
OLLAMA_HOST   = "http://localhost:11434"
OLLAMA_MODELS = ["llama3.2", "nomic-embed-text"]
OS            = platform.system()   # "Linux", "Darwin", "Windows"

_N8N_COOKIE_JAR = http.cookiejar.CookieJar()
_N8N_SESSION_READY = False

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
        kwargs["text"] = True
    result = subprocess.run(cmd, **kwargs)
    if check and result.returncode != 0:
        fail(f"Command failed (exit {result.returncode}): {display}")
    return result

def cmd_exists(name: str) -> bool:
    name = os.fspath(name)
    paths = os.environ.get("PATH", "").split(os.pathsep)
    if OS == "Windows":
        exts = [ext.lower() for ext in os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD").split(os.pathsep) if ext]
        for directory in paths:
            if not directory:
                continue
            base = Path(directory)
            for ext in [""] + exts:
                candidate = base / f"{name}{ext}"
                if candidate.is_file():
                    return True
        return False

    for directory in paths:
        if not directory:
            continue
        candidate = Path(directory) / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return True
    return False

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
        ok(f"Node.js already installed: {r.stdout.strip()}")
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

# ── Phase 1.5: Ollama ───────────────────────────────────────────────────────

def install_ollama():
    step("Checking Ollama...")
    if cmd_exists("ollama"):
        r = run(["ollama", "--version"], capture=True, check=False)
        if r.returncode == 0:
            ok(f"Ollama already installed: {r.stdout.strip()}")
        else:
            ok("Ollama command found.")
    else:
        warn("Ollama not found. Installing from the official installer...")
        if OS in {"Linux", "Darwin"}:
            run("curl -fsSL https://ollama.com/install.sh | sh", shell=True)
            ok("Ollama installed.")
        elif OS == "Windows":
            fail("Ollama not found. Install it from https://ollama.com/download, then re-run the installer.")
        else:
            fail(f"Unsupported operating system for automatic Ollama installation: {OS}")

    _ensure_ollama_running()
    _pull_ollama_models()


def _ollama_http_healthcheck() -> bool:
    try:
        resp = urllib.request.urlopen(f"{OLLAMA_HOST}/api/version", timeout=3)
        return resp.status == 200
    except Exception:
        return False


def _ensure_ollama_running():
    step("Ensuring Ollama is running...")
    if _ollama_http_healthcheck():
        ok("Ollama server is running.")
        return

    if not cmd_exists("ollama"):
        fail("Ollama CLI is not available. Install Ollama and re-run the installer.")

    warn("Ollama server is not responding. Starting `ollama serve` in the background...")
    proc = subprocess.Popen(
        ["ollama", "serve"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    for attempt in range(30):
        if _ollama_http_healthcheck():
            ok("Ollama server is running.")
            return
        if proc.poll() is not None:
            break
        time.sleep(2)

    fail("Ollama did not become ready. Start it manually with `ollama serve` and retry.")


def _pull_ollama_models():
    step("Pulling Ollama models used by the workflow...")
    for model in OLLAMA_MODELS:
        run(["ollama", "pull", model])
        ok(f"Model ready: {model}")

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


def _n8n_opener() -> urllib.request.OpenerDirector:
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_N8N_COOKIE_JAR))


def _n8n_xsrf_token() -> str:
    for cookie in _N8N_COOKIE_JAR:
        name = (cookie.name or "").lower()
        if "xsrf" in name or "csrf" in name:
            return cookie.value or ""
    return ""


def _n8n_login(force: bool = False):
    global _N8N_SESSION_READY
    if _N8N_SESSION_READY and not force:
        return

    step("Logging in to n8n...")
    url = f"{N8N_HOST}/rest/login"
    payload = json.dumps({
        "emailOrLdapLoginId": N8N_USER,
        "password": N8N_PASSWORD,
    }).encode()
    opener = _n8n_opener()
    # Prefetch the root URL to allow the server to set any initial cookies (CSRF token)
    try:
        opener.open(urllib.request.Request(N8N_HOST, method="GET"), timeout=5)
    except Exception:
        # ignore network errors here; the subsequent login will show a clearer error
        pass

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Referer": N8N_HOST,
            "X-Requested-With": "XMLHttpRequest",
        },
        method="POST",
    )
    try:
        resp = opener.open(req, timeout=15)
        body = resp.read().decode(errors="ignore")
        _N8N_SESSION_READY = True
        ok("n8n session established.")
        # show cookies for debugging (names only)
        cookie_names = ", ".join(c.name for c in _N8N_COOKIE_JAR)
        ok(f"n8n cookies set: {cookie_names}")
        if body:
            return json.loads(body)
        return {}
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        fail(f"Could not log in to n8n ({e.code}): {body[:300]}")

def _n8n_container_state() -> str:
    result = run(["docker", "inspect", "newsapp-n8n", "--format", "{{.State.Status}}"], capture=True, check=False)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()

def _n8n_container_health() -> str:
    result = run(["docker", "inspect", "newsapp-n8n", "--format", "{{if .State.Health}}{{.State.Health.Status}}{{end}}"], capture=True, check=False)
    if result.returncode != 0:
        return ""
    return result.stdout.strip()

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
    url = f"{N8N_HOST}/rest{path}"
    data = json.dumps(payload).encode() if payload else None
    _n8n_login()
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Referer": N8N_HOST,
        "X-Requested-With": "XMLHttpRequest",
    }
    xsrf = _n8n_xsrf_token()
    if xsrf and method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
        headers["X-XSRF-TOKEN"] = xsrf
        # Some n8n versions/hosts expect this header name
        headers["X-N8N-XSRF-TOKEN"] = xsrf
    # If n8n provided a JWT cookie (n8n-auth) and it is marked Secure (so the
    # cookie may not be sent over plain HTTP), also add an Authorization header
    # with the token so requests succeed on localhost without HTTPS.
    for cookie in _N8N_COOKIE_JAR:
        if (cookie.name or "").lower() == "n8n-auth" and cookie.value:
            headers.setdefault("Authorization", f"Bearer {cookie.value}")
            break
    # Ensure cookies are sent even if marked Secure (some cookie jars won't send them
    # over plain HTTP). Build a Cookie header from the jar so the server receives the
    # session cookie on localhost requests.
    cookie_header = "; ".join(f"{c.name}={c.value}" for c in _N8N_COOKIE_JAR if c.name and c.value)
    if cookie_header:
        headers.setdefault("Cookie", cookie_header)
    req = urllib.request.Request(url, data=data, method=method,
                                  headers=headers)
    try:
        resp = _n8n_opener().open(req, timeout=15)
        raw = resp.read().decode(errors="ignore")
        return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="ignore")
        if e.code == 401:
            global _N8N_SESSION_READY
            _N8N_SESSION_READY = False
            warn("n8n session expired or was not accepted; retrying once after re-login.")
            _n8n_login(force=True)
            try:
                resp = _n8n_opener().open(req, timeout=15)
                raw = resp.read().decode(errors="ignore")
                return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as retry_error:
                retry_body = retry_error.read().decode(errors="ignore")
                warn(f"n8n API {method} {path} → {retry_error.code}: {retry_body[:300]}")
                return {}
        warn(f"n8n API {method} {path} → {e.code}: {body[:300]}")
        return {}

def import_workflow():
    step("Importing n8n workflow...")
    if not WORKFLOW_FILE.exists():
        warn(f"Workflow file not found at {WORKFLOW_FILE} — skipping import.")
        return

    with open(WORKFLOW_FILE) as f:
        workflow = json.load(f)

    # n8n's /rest/workflows import expects a workflow object that includes a top-level
    # "name" property. The file here may be an exported object without a name, so
    # build a minimal payload containing the required fields.
    payload = workflow.copy() if isinstance(workflow, dict) else {"nodes": [], "connections": {}}
    if not payload.get("name"):
        payload["name"] = "Imported · NewsApp"
    # ensure nodes / connections are present
    payload.setdefault("nodes", workflow.get("nodes", []))
    payload.setdefault("connections", workflow.get("connections", {}))
    payload.setdefault("settings", workflow.get("settings", {}))

    result = _n8n_api("POST", "/workflows", payload)
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
    # Try to trigger the workflow. Some n8n versions expect a payload with
    # startNodes (names of trigger nodes). Build a best-effort payload from
    # the local workflow file and retry if needed.
    payloads = [
        {},
    ]
    # gather trigger node names from the workflow file (if available)
    try:
        with open(WORKFLOW_FILE) as f:
            wf = json.load(f)
            start_nodes = []
            for node in wf.get("nodes", []):
                t = node.get("type", "")
                # common trigger node identifiers include 'scheduleTrigger' and 'webhook'
                if "trigger" in t.lower() or "schedule" in t.lower() or "webhook" in t.lower():
                    if node.get("name"):
                        start_nodes.append(node.get("name"))
            if start_nodes:
                payloads.append({"startNodes": start_nodes})
                payloads.append({"startNodes": start_nodes, "executionMode": "trigger"})
    except Exception:
        start_nodes = []

    success = False
    for p in payloads:
        result = _n8n_api("POST", f"/workflows/{wf_id}/run", p)
        if result:
            ok("First workflow run triggered. News will populate shortly.")
            success = True
            break

    if not success:
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
        python "$ROOT/manage.py" runserver 0.0.0.0:{BACKEND_PORT} &
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
        start "NewsApp Backend" cmd /k "cd /d %ROOT% && .venv\\Scripts\\activate && python manage.py runserver 0.0.0.0:{BACKEND_PORT}"

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
    # Use xdg-open on Linux to suppress KDE framework warnings
    if OS == "Linux" and cmd_exists("xdg-open"):
        subprocess.Popen(
            ["xdg-open", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
    else:
        # Fallback to Python's webbrowser on macOS/Windows or if xdg-open not found
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

    # Phase 1.5 — Ollama
    banner("Phase 1.5 · Ollama (Local AI)")
    install_ollama()

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
