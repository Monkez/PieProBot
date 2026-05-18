from __future__ import annotations

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

PID_FILE_NAME = "piepro.pid.json"
DEFAULT_REPOSITORY_URL = "https://github.com/Monkez/PieProBot.git"
DEFAULT_PROJECT_ROOT = Path.home() / ".piepro"
USER_CONFIG_FILE = DEFAULT_PROJECT_ROOT / ".runtime" / "user_config.json"
LEGACY_USER_CONFIG_FILE = DEFAULT_PROJECT_ROOT / "config.json"


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "start":
        return start(args)
    if args.command == "stop":
        return stop(args)
    if args.command == "restart":
        stop(args)
        return start(args)
    if args.command == "status":
        return status(args)
    if args.command == "init":
        return init_project(args)
    if args.command == "use":
        return use_project(args)
    if args.command == "autostart":
        return autostart(args)
    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="piepro", description="Manage the local PiePro runtime.")
    parser.add_argument("--root", default=None, help="Project root. Defaults to PIEPRO_HOME or auto-detected root.")
    sub = parser.add_subparsers(dest="command")

    start_parser = sub.add_parser("start", help="Start backend and frontend locally.")
    start_parser.add_argument("--backend-port", type=int, default=8000)
    start_parser.add_argument("--frontend-port", type=int, default=3000)
    start_parser.add_argument("--host", default="127.0.0.1")
    start_parser.add_argument("--backend-only", action="store_true")
    start_parser.add_argument("--no-frontend", action="store_true")
    start_parser.add_argument("--skip-frontend-install", action="store_true")
    start_parser.add_argument("--no-open", action="store_true", help="Do not open the frontend in the browser.")

    stop_parser = sub.add_parser("stop", help="Stop running PiePro services.")
    stop_parser.add_argument("--force", action="store_true", help="Force process termination.")

    restart_parser = sub.add_parser("restart", help="Restart running PiePro services.")
    restart_parser.add_argument("--backend-port", type=int, default=8000)
    restart_parser.add_argument("--frontend-port", type=int, default=3000)
    restart_parser.add_argument("--host", default="127.0.0.1")
    restart_parser.add_argument("--backend-only", action="store_true")
    restart_parser.add_argument("--no-frontend", action="store_true")
    restart_parser.add_argument("--skip-frontend-install", action="store_true")
    restart_parser.add_argument("--force", action="store_true")
    restart_parser.add_argument("--no-open", action="store_true", help="Do not open the frontend in the browser.")

    sub.add_parser("status", help="Show service PID and health status.")

    init_parser = sub.add_parser("init", help="Clone the PiePro project files for uv tool installs.")
    init_parser.add_argument("path", nargs="?", default=None, help=f"Target directory. Defaults to {DEFAULT_PROJECT_ROOT}.")
    init_parser.add_argument("--repo", default=DEFAULT_REPOSITORY_URL, help="Repository URL to clone.")

    use_parser = sub.add_parser("use", help="Set the default PiePro project root.")
    use_parser.add_argument("path", help="Existing PiePro project directory.")

    autostart_parser = sub.add_parser("autostart", help="Manage Windows startup integration.")
    autostart_sub = autostart_parser.add_subparsers(dest="autostart_command")
    enable_parser = autostart_sub.add_parser("enable", help="Start PiePro automatically when Windows signs in.")
    enable_parser.add_argument("--open", action="store_true", help="Open the frontend browser on Windows sign-in.")
    enable_parser.add_argument("--backend-port", type=int, default=8000)
    enable_parser.add_argument("--frontend-port", type=int, default=3000)
    enable_parser.add_argument("--host", default="127.0.0.1")
    autostart_sub.add_parser("disable", help="Remove PiePro from Windows startup.")
    autostart_sub.add_parser("status", help="Show Windows startup integration status.")
    return parser


def resolve_root(raw_root: str | None = None, *, auto_init: bool = False) -> Path:
    candidates: list[Path] = []
    if raw_root:
        candidates.append(Path(raw_root))
    if os.getenv("PIEPRO_HOME"):
        candidates.append(Path(os.environ["PIEPRO_HOME"]))
    saved_root = read_user_config().get("default_root")
    if saved_root:
        candidates.append(Path(str(saved_root)))
    candidates.append(DEFAULT_PROJECT_ROOT)
    candidates.append(Path.cwd())
    candidates.extend(Path.cwd().parents)
    package_root = Path(__file__).resolve().parents[1]
    candidates.append(package_root)
    candidates.extend(package_root.parents)

    for candidate in candidates:
        resolved = candidate.resolve()
        if is_project_root(resolved):
            return resolved
    if auto_init and not raw_root and not os.getenv("PIEPRO_HOME"):
        init_project(argparse.Namespace(path=None, repo=DEFAULT_REPOSITORY_URL))
        if is_project_root(DEFAULT_PROJECT_ROOT.resolve()):
            return DEFAULT_PROJECT_ROOT.resolve()
    raise SystemExit(f"Could not find PiePro project root. Run `piepro init` to install the source into {DEFAULT_PROJECT_ROOT}.")


def is_project_root(path: Path) -> bool:
    return (path / "backend" / "app" / "main.py").exists() and (path / "config").exists()


def runtime_paths(root: Path) -> tuple[Path, Path, Path]:
    runtime = root / "runtime"
    logs = root / "logs"
    runtime.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    return runtime, logs, runtime / PID_FILE_NAME


def start(args: argparse.Namespace) -> int:
    root = resolve_root(args.root, auto_init=True)
    _, logs, pid_file = runtime_paths(root)
    state = read_state(pid_file)

    services: dict[str, Any] = {}
    backend_url = f"http://{args.host}:{args.backend_port}"
    existing_backend = state.get("services", {}).get("backend", {})
    if existing_backend and is_process_alive(existing_backend.get("pid")):
        services["backend"] = existing_backend
        print(f"backend already running pid={existing_backend.get('pid')} url={existing_backend.get('url')}")
    else:
        backend_log = logs / "backend.cli.log"
        backend = spawn(
            [
                python_command(),
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                args.host,
                "--port",
                str(args.backend_port),
            ],
            cwd=root / "backend",
            env={**os.environ, "TWIN_AGENT_ROOT": str(root)},
            log_path=backend_log,
        )
        services["backend"] = {"pid": backend.pid, "url": backend_url, "log": str(backend_log)}
        print(f"backend started pid={backend.pid} url={backend_url}")

    frontend_url: str | None = None
    if not args.backend_only and not args.no_frontend:
        frontend_dir = root / "frontend"
        if frontend_dir.exists():
            if not args.skip_frontend_install:
                ensure_frontend_dependencies(frontend_dir)
            frontend_url = f"http://{args.host}:{args.frontend_port}/dashboard"
            existing_frontend = state.get("services", {}).get("frontend", {})
            if existing_frontend and is_process_alive(existing_frontend.get("pid")):
                services["frontend"] = existing_frontend
                print(f"frontend already running pid={existing_frontend.get('pid')} url={existing_frontend.get('url')}")
            else:
                if shutil.which("node.exe") or shutil.which("node") or npm_command():
                    frontend_log = logs / "frontend.cli.log"
                    frontend_command = build_frontend_command(frontend_dir, args.frontend_port)
                    frontend = spawn(
                        frontend_command,
                        cwd=frontend_dir,
                        env={**os.environ, "NEXT_PUBLIC_API_BASE": backend_url},
                        log_path=frontend_log,
                    )
                    services["frontend"] = {"pid": frontend.pid, "url": frontend_url, "log": str(frontend_log)}
                    print(f"frontend started pid={frontend.pid} url={frontend_url}")
                else:
                    print("frontend skipped: npm was not found")

    write_state(
        pid_file,
        {
            "root": str(root),
            "started_at": datetime.now(timezone.utc).isoformat(),
            "services": services,
        },
    )
    if frontend_url and not args.no_open:
        if wait_for_http(frontend_url, timeout_seconds=15):
            webbrowser.open(frontend_url)
            print(f"opened frontend: {frontend_url}")
        else:
            print(f"frontend is starting; open manually when ready: {frontend_url}")
    return 0


def init_project(args: argparse.Namespace) -> int:
    target = Path(args.path).expanduser().resolve() if args.path else DEFAULT_PROJECT_ROOT.resolve()
    if is_project_root(target):
        write_user_config({"default_root": str(target)})
        print(f"PiePro project already initialized at {target}")
        print("Default PiePro root saved. You can now run `piepro start` from any directory.")
        return 0
    if not shutil.which("git"):
        raise SystemExit("git is required for piepro init")
    clone_project(args.repo, target)
    write_user_config({"default_root": str(target)})
    print(f"PiePro project initialized at {target}")
    print("Default PiePro root saved. You can now run `piepro start` from any directory.")
    print("Next:")
    print("  piepro start")
    return 0


def clone_project(repo: str, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists() or not any(target.iterdir()):
        subprocess.run(["git", "clone", repo, str(target)], check=True)
        return

    if target != DEFAULT_PROJECT_ROOT.resolve() or not can_overlay_default_root(target):
        raise SystemExit(f"Target directory is not empty: {target}")

    temp_target = target.parent / f"{target.name}.download-{int(time.time())}"
    subprocess.run(["git", "clone", repo, str(temp_target)], check=True)
    try:
        shutil.copytree(temp_target, target, dirs_exist_ok=True)
    finally:
        shutil.rmtree(temp_target, ignore_errors=True)


def can_overlay_default_root(target: Path) -> bool:
    allowed_names = {"config.json", ".runtime"}
    return all(item.name in allowed_names for item in target.iterdir())


def use_project(args: argparse.Namespace) -> int:
    root = resolve_root(args.path)
    write_user_config({"default_root": str(root)})
    print(f"Default PiePro root saved: {root}")
    print("You can now run `piepro start` from any directory.")
    return 0


def autostart(args: argparse.Namespace) -> int:
    command = getattr(args, "autostart_command", None)
    if command == "enable":
        return enable_autostart(args)
    if command == "disable":
        return disable_autostart()
    if command == "status":
        return autostart_status()
    print("Usage: piepro autostart enable|disable|status")
    return 1


def startup_script_path() -> Path:
    if os.name != "nt":
        raise SystemExit("PiePro autostart is currently supported on Windows only.")
    appdata = os.getenv("APPDATA")
    if not appdata:
        raise SystemExit("APPDATA is not set; cannot locate Windows Startup folder.")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup" / "PieProAutostart.vbs"


def enable_autostart(args: argparse.Namespace) -> int:
    root = resolve_root(getattr(args, "root", None), auto_init=True)
    write_user_config({"default_root": str(root)})
    script_path = startup_script_path()
    script_path.parent.mkdir(parents=True, exist_ok=True)
    command = build_autostart_command(root, args)
    script_path.write_text(build_hidden_vbs(command), encoding="utf-8")
    print(f"PiePro autostart enabled: {script_path}")
    print(f"Startup command: {command}")
    return 0


def disable_autostart() -> int:
    script_path = startup_script_path()
    script_path.unlink(missing_ok=True)
    print("PiePro autostart disabled")
    return 0


def autostart_status() -> int:
    script_path = startup_script_path()
    if script_path.exists():
        print(f"PiePro autostart: enabled ({script_path})")
        return 0
    print("PiePro autostart: disabled")
    return 1


def build_autostart_command(root: Path, args: argparse.Namespace) -> str:
    executable = pythonw_command()
    command = [
        executable,
        "-m",
        "piepro.cli",
        "--root",
        str(root),
        "start",
        "--host",
        str(getattr(args, "host", "127.0.0.1")),
        "--backend-port",
        str(getattr(args, "backend_port", 8000)),
        "--frontend-port",
        str(getattr(args, "frontend_port", 3000)),
    ]
    if not getattr(args, "open", False):
        command.append("--no-open")
    return subprocess.list2cmdline(command)


def build_hidden_vbs(command: str) -> str:
    escaped = command.replace('"', '""')
    return "\n".join(
        [
            "Set shell = CreateObject(\"WScript.Shell\")",
            f"shell.Run \"{escaped}\", 0, False",
            "",
        ]
    )


def stop(args: argparse.Namespace) -> int:
    root = resolve_root(getattr(args, "root", None))
    _, _, pid_file = runtime_paths(root)
    state = read_state(pid_file)
    services = state.get("services", {})
    if not services:
        print("piepro is not running")
        return 0

    for name, service in services.items():
        pid = service.get("pid")
        if is_process_alive(pid):
            terminate_process(int(pid), force=getattr(args, "force", False))
            print(f"{name} stopped pid={pid}")
        else:
            print(f"{name} not running pid={pid}")
        port = port_from_url(str(service.get("url", "")))
        if port:
            port_pid = find_pid_by_port(port)
            if port_pid and is_process_alive(port_pid):
                terminate_process(port_pid, force=True)
                print(f"{name} port {port} released pid={port_pid}")
    pid_file.unlink(missing_ok=True)
    return 0


def status(args: argparse.Namespace) -> int:
    root = resolve_root(args.root)
    _, _, pid_file = runtime_paths(root)
    state = read_state(pid_file)
    services = state.get("services", {})
    if not services:
        print("piepro status: stopped")
        return 1

    overall_ok = True
    print(f"piepro root: {root}")
    for name, service in services.items():
        pid = service.get("pid")
        alive = is_process_alive(pid)
        url = service.get("url", "")
        health = "unknown"
        if url:
            health = "healthy" if http_ok(f"{url}/health") else "unhealthy"
            if name == "frontend":
                health = "healthy" if http_ok(str(url), timeout=6.0) else "unhealthy"
        if name == "backend" and url:
            overall_ok = overall_ok and health == "healthy"
        else:
            overall_ok = overall_ok and (alive or health == "healthy") and health in {"unknown", "healthy"}
        print(f"{name}: pid={pid} alive={alive} health={health} url={url}")
    return 0 if overall_ok else 1


def spawn(command: list[str], cwd: Path, env: dict[str, str], log_path: Path) -> subprocess.Popen[Any]:
    log_handle = log_path.open("ab")
    creationflags = 0
    start_new_session = False
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]
    else:
        start_new_session = True
    return subprocess.Popen(
        command,
        cwd=str(cwd),
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        creationflags=creationflags,
        start_new_session=start_new_session,
    )


def ensure_frontend_dependencies(frontend_dir: Path) -> None:
    if (frontend_dir / "node_modules" / ".bin" / "next").exists() or (frontend_dir / "node_modules" / ".bin" / "next.cmd").exists():
        return
    npm = npm_command()
    if not npm:
        print("frontend dependency install skipped: npm was not found")
        return
    print("installing frontend dependencies with npm install...")
    subprocess.run([npm, "install"], cwd=str(frontend_dir), check=True)


def python_command() -> str:
    if os.name == "nt":
        candidate = Path(sys.prefix) / "Scripts" / "python.exe"
    else:
        candidate = Path(sys.prefix) / "bin" / "python"
    if candidate.exists():
        return str(candidate)
    return sys.executable


def pythonw_command() -> str:
    if os.name == "nt":
        candidate = Path(sys.executable).with_name("pythonw.exe")
        if candidate.exists():
            return str(candidate)
    return python_command()


def build_frontend_command(frontend_dir: Path, port: int) -> list[str]:
    node = shutil.which("node.exe") or shutil.which("node")
    if not node:
        npm = npm_command()
        if not npm:
            raise SystemExit("Node.js/npm was not found.")
        return [npm, "run", "dev", "--", "-p", str(port)]
    next_script = frontend_dir / "node_modules" / "next" / "dist" / "bin" / "next"
    if next_script.exists():
        return [node, str(next_script), "dev", "-H", "0.0.0.0", "-p", str(port)]
    npm = npm_command()
    if not npm:
        raise SystemExit("Next.js was not installed and npm was not found.")
    return [npm, "run", "dev", "--", "-p", str(port)]


def npm_command() -> str | None:
    return shutil.which("npm.cmd") or shutil.which("npm")


def read_state(pid_file: Path) -> dict[str, Any]:
    if not pid_file.exists():
        return {}
    try:
        return json.loads(pid_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def write_state(pid_file: Path, state: dict[str, Any]) -> None:
    pid_file.write_text(json.dumps(state, indent=2), encoding="utf-8")


def read_user_config() -> dict[str, Any]:
    for path in (USER_CONFIG_FILE, LEGACY_USER_CONFIG_FILE):
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    return {}


def write_user_config(patch: dict[str, Any]) -> None:
    USER_CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    config = read_user_config()
    config.update(patch)
    USER_CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")


def is_process_alive(pid: Any) -> bool:
    if not pid:
        return False
    pid = int(pid)
    if os.name == "nt":
        result = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"], capture_output=True, text=True, check=False)
        return str(pid) in result.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def terminate_process(pid: int, force: bool = False) -> None:
    if os.name == "nt":
        command = ["taskkill", "/PID", str(pid), "/T"]
        if force:
            command.append("/F")
        subprocess.run(command, check=False, capture_output=True)
        return
    sig = signal.SIGKILL if force else signal.SIGTERM
    try:
        os.kill(pid, sig)
    except OSError:
        pass


def port_from_url(url: str) -> int | None:
    try:
        parsed = urlparse(url)
        return parsed.port
    except ValueError:
        return None


def find_pid_by_port(port: int) -> int | None:
    if os.name == "nt":
        command = [
            "powershell",
            "-NoProfile",
            "-Command",
            f"(Get-NetTCPConnection -LocalPort {port} -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess)",
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        text = result.stdout.strip()
        return int(text) if text.isdigit() else None
    for command in (["lsof", "-ti", f":{port}"], ["fuser", f"{port}/tcp"]):
        executable = shutil.which(command[0])
        if not executable:
            continue
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        text = (result.stdout or result.stderr).strip().split()
        if text and text[0].isdigit():
            return int(text[0])
    return None


def http_ok(url: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return 200 <= response.status < 300
    except (urllib.error.URLError, TimeoutError):
        return False


def wait_for_http(url: str, timeout_seconds: float = 15.0) -> bool:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if http_ok(url, timeout=1.5):
            return True
        time.sleep(0.5)
    return False


if __name__ == "__main__":
    raise SystemExit(main())
