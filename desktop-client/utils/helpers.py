import os
import json
import datetime
import socket
import uuid
from pathlib import Path


APP_NAME = "RifatCam Pro"
APP_VERSION = "1.0.0"
COMPANY_NAME = "RifatCam"
DEFAULT_PORT = 8080
DISCOVERY_PORT = 5005
BUFFER_SIZE = 65536


def get_app_data_dir():
    path = Path.home() / ".rifatcam"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_screenshots_dir():
    path = get_app_data_dir() / "screenshots"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_recordings_dir():
    path = get_app_data_dir() / "recordings"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_settings_path():
    return get_app_data_dir() / "settings.json"


def get_device_id():
    device_id_path = get_app_data_dir() / "device_id"
    if device_id_path.exists():
        return device_id_path.read_text().strip()
    did = str(uuid.uuid4())[:8]
    device_id_path.write_text(did)
    return did


def load_settings():
    path = get_settings_path()
    defaults = {
        "auto_connect": False,
        "auto_record": False,
        "motion_detection": False,
        "save_screenshots": True,
        "save_recordings": True,
        "preferred_resolution": "720p",
        "fps_limit": 30,
        "theme": "dark",
        "show_fps": True,
        "enable_notifications": True,
        "last_device_ip": "",
        "recording_format": "mp4",
        "motion_sensitivity": 0.5,
        "enable_ai_detection": False,
    }
    if path.exists():
        try:
            saved = json.loads(path.read_text())
            defaults.update(saved)
        except (json.JSONDecodeError, IOError):
            pass
    return defaults


def save_settings(settings):
    path = get_settings_path()
    try:
        path.write_text(json.dumps(settings, indent=2))
        return True
    except IOError:
        return False


def timestamp_str():
    return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")


def format_number(n):
    if n >= 1000000:
        return f"{n / 1000000:.1f}M"
    if n >= 1000:
        return f"{n / 1000:.1f}K"
    return str(n)


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def validate_ip(ip):
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False


def human_readable_size(size_bytes):
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
