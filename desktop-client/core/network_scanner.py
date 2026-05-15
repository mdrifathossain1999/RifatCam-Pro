import socket
import threading
import time
import json
import struct
import subprocess
import re
from utils.helpers import DISCOVERY_PORT, DEFAULT_PORT


DISCOVERY_MAGIC = b"RIFATCAM_DISCOVER"
DISCOVERY_RESPONSE = b"RIFATCAM_HERE"
BROADCAST_ADDR = "255.255.255.255"


class NetworkScanner:
    def __init__(self):
        self._devices = []
        self._lock = threading.Lock()
        self._running = False
        self._scan_thread = None
        self._on_device_found = None
        self._broadcast_socket = None
        self._listen_socket = None

    @property
    def devices(self):
        with self._lock:
            return list(self._devices)

    def set_on_device_found(self, callback):
        self._on_device_found = callback

    def start_discovery(self):
        if self._running:
            return
        self._running = True
        self._scan_thread = threading.Thread(target=self._discovery_worker, daemon=True)
        self._scan_thread.start()

    def stop_discovery(self):
        self._running = False
        if self._broadcast_socket:
            try:
                self._broadcast_socket.close()
            except:
                pass
        if self._listen_socket:
            try:
                self._listen_socket.close()
            except:
                pass

    def _discovery_worker(self):
        try:
            self._listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._listen_socket.settimeout(1.0)
            self._listen_socket.bind(("0.0.0.0", DISCOVERY_PORT))
        except Exception as e:
            print(f"[Discovery] Listen socket error: {e}")
            return

        self._broadcast()
        last_broadcast = time.time()

        while self._running:
            try:
                data, addr = self._listen_socket.recvfrom(1024)
                if data.startswith(DISCOVERY_RESPONSE):
                    try:
                        info = json.loads(
                            data[len(DISCOVERY_RESPONSE) :].decode("utf-8")
                        )
                        device_info = {
                            "ip": addr[0],
                            "port": info.get("port", DEFAULT_PORT),
                            "name": info.get("name", "RifatCam Phone"),
                            "device_id": info.get("device_id", ""),
                            "protocol": info.get("protocol", "mjpeg"),
                            "last_seen": time.time(),
                        }
                        self._add_device(device_info)
                    except (json.JSONDecodeError, UnicodeDecodeError):
                        device_info = {
                            "ip": addr[0],
                            "port": DEFAULT_PORT,
                            "name": "RifatCam Phone",
                            "device_id": "",
                            "protocol": "mjpeg",
                            "last_seen": time.time(),
                        }
                        self._add_device(device_info)
            except socket.timeout:
                pass
            except OSError:
                break

            if time.time() - last_broadcast > 5.0:
                self._broadcast()
                last_broadcast = time.time()

        try:
            self._listen_socket.close()
        except:
            pass

    def _broadcast(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(0.5)
            sock.sendto(DISCOVERY_MAGIC, (BROADCAST_ADDR, DISCOVERY_PORT))
            sock.close()
        except Exception as e:
            pass

    def _add_device(self, device):
        with self._lock:
            for i, d in enumerate(self._devices):
                if d["ip"] == device["ip"]:
                    self._devices[i] = device
                    return
            self._devices.append(device)
        if self._on_device_found:
            self._on_device_found(device)

    def scan_subnet(self, subnet=None):
        if not subnet:
            subnet = self._get_subnet()
        if not subnet:
            return []
        found = []
        threads = []

        def check_ip(ip):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, DEFAULT_PORT))
            if result == 0:
                try:
                    sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock2.settimeout(1)
                    sock2.connect((ip, DEFAULT_PORT))
                    sock2.send(b"GET /info HTTP/1.0\r\nHost: localhost\r\n\r\n")
                    response = sock2.recv(4096)
                    sock2.close()
                    device_info = {
                        "ip": ip,
                        "port": DEFAULT_PORT,
                        "name": f"RifatCam ({ip})",
                        "device_id": "",
                        "protocol": "mjpeg",
                        "last_seen": time.time(),
                    }
                    with self._lock:
                        self._devices.append(device_info)
                    found.append(device_info)
                    if self._on_device_found:
                        self._on_device_found(device_info)
                except:
                    pass
            sock.close()

        base = ".".join(subnet.split(".")[:3])
        for i in range(1, 255):
            ip = f"{base}.{i}"
            t = threading.Thread(target=check_ip, args=(ip,), daemon=True)
            threads.append(t)
            t.start()
            if len(threads) >= 50:
                for t in threads:
                    t.join(timeout=2)
                threads = []

        for t in threads:
            t.join(timeout=2)

        return found

    def _get_subnet(self):
        try:
            result = subprocess.run(
                ["ipconfig"], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.splitlines():
                ip_match = re.search(r"IPv4[^:]*:\s*(\d+\.\d+\.\d+\.\d+)", line)
                if ip_match:
                    ip = ip_match.group(1)
                    return ip
        except:
            pass
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return None

    def check_device(self, ip, port=DEFAULT_PORT, timeout=2):
        url = f"http://{ip}:{port}/video"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            sock.send(f"GET / HTTP/1.0\r\nHost: {ip}\r\n\r\n".encode())
            response = sock.recv(256)
            sock.close()
            if response:
                return True, url
        except:
            pass
        return False, None
