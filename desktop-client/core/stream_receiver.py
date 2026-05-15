import io
import time
import queue
import threading
import requests
import numpy as np
import cv2
from urllib.parse import urlparse


MJPEG_HEADER = b"--boundary"
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 3
RECONNECT_DELAY = 2.0


class StreamReceiver:
    def __init__(self, url=None):
        self._url = url
        self._running = False
        self._thread = None
        self._frame_queue = queue.Queue(maxsize=4)
        self._fps = 0
        self._frame_count = 0
        self._fps_time = time.time()
        self._connected = False
        self._resolution = (0, 0)
        self._lock = threading.Lock()
        self._on_frame = None
        self._on_disconnect = None

    @property
    def connected(self):
        return self._connected

    @property
    def fps(self):
        return self._fps

    @property
    def resolution(self):
        return self._resolution

    def set_url(self, url):
        self._url = url

    def set_on_frame(self, callback):
        self._on_frame = callback

    def set_on_disconnect(self, callback):
        self._on_disconnect = callback

    def start(self, url=None):
        if url:
            self._url = url
        if not self._url:
            return False
        if self._running:
            return True
        self._running = True
        self._thread = threading.Thread(target=self._stream_worker, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)
        with self._lock:
            self._connected = False

    def get_frame(self, timeout=0.1):
        try:
            return self._frame_queue.get_nowait()
        except queue.Empty:
            return None

    def _update_fps(self):
        self._frame_count += 1
        elapsed = time.time() - self._fps_time
        if elapsed >= 1.0:
            with self._lock:
                self._fps = int(self._frame_count / elapsed)
            self._frame_count = 0
            self._fps_time = time.time()

    def _stream_worker(self):
        while self._running:
            try:
                self._read_mjpeg_stream()
            except Exception as e:
                print(f"[Stream] Error: {e}")
                with self._lock:
                    was_connected = self._connected
                    self._connected = False
                if was_connected and self._on_disconnect:
                    self._on_disconnect()
                if not self._running:
                    break
                time.sleep(RECONNECT_DELAY)

    def _read_mjpeg_stream(self):
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "RifatCam-Pro/1.0",
                "Accept": "*/*",
            }
        )
        resp = None
        try:
            resp = session.get(
                self._url, stream=True, timeout=(CONNECT_TIMEOUT, READ_TIMEOUT)
            )
            resp.raise_for_status()

            with self._lock:
                self._connected = True

            self._mjpeg_read_loop(resp)
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Failed to connect: {e}")
        except Exception as e:
            print(f"[Stream] Read error: {e}")
        finally:
            if resp:
                resp.close()
            session.close()
            with self._lock:
                self._connected = False

    def _mjpeg_read_loop(self, resp):
        boundary = b"--boundary"
        buffer = b""
        frame_start = False
        content_length = 0
        reading_headers = False

        for chunk in resp.iter_content(chunk_size=4096):
            if not self._running:
                break
            if not chunk:
                continue

            buffer += chunk

            while True:
                if not frame_start:
                    idx = buffer.find(boundary)
                    if idx == -1:
                        break
                    buffer = buffer[idx + len(boundary) :]
                    frame_start = True
                    reading_headers = True
                    content_length = 0
                    continue

                if reading_headers:
                    idx = buffer.find(b"\r\n\r\n")
                    if idx == -1:
                        break
                    header_section = buffer[:idx].decode("utf-8", errors="replace")
                    buffer = buffer[idx + 4 :]
                    reading_headers = False
                    for line in header_section.split("\r\n"):
                        if line.lower().startswith("content-length:"):
                            try:
                                content_length = int(line.split(":")[1].strip())
                            except (ValueError, IndexError):
                                content_length = 0
                    if content_length <= 0:
                        frame_start = False
                        continue
                    continue

                if content_length > 0:
                    if len(buffer) >= content_length:
                        frame_data = buffer[:content_length]
                        buffer = buffer[content_length:]
                        self._process_frame(frame_data)
                        frame_start = False
                        reading_headers = False
                        content_length = 0
                    else:
                        break

    def _process_frame(self, jpeg_data):
        try:
            arr = np.frombuffer(jpeg_data, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is not None:
                h, w = frame.shape[:2]
                with self._lock:
                    self._resolution = (w, h)
                if self._frame_queue.full():
                    try:
                        self._frame_queue.get_nowait()
                    except queue.Empty:
                        pass
                self._frame_queue.put(frame)
                self._update_fps()
                if self._on_frame:
                    self._on_frame(frame)
        except Exception as e:
            print(f"[Stream] Frame decode error: {e}")

    def get_info(self):
        if not self._url:
            return {}
        info_url = self._url.replace("/video", "/info")
        try:
            resp = requests.get(info_url, timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass
        return {}


class MJPEGServer:
    def __init__(self, host="0.0.0.0", port=8080):
        self.host = host
        self.port = port
        self._running = False
        self._server = None
        self._frame = None
        self._lock = threading.Lock()
        self._clients = 0

    def update_frame(self, frame):
        with self._lock:
            self._frame = frame

    def start(self):
        from http.server import HTTPServer, BaseHTTPRequestHandler

        class MJPEGHandler(BaseHTTPRequestHandler):
            server_ref = self

            def do_GET(self):
                if self.path == "/video":
                    self.server_ref._clients += 1
                    self.send_response(200)
                    self.send_header(
                        "Content-Type", "multipart/x-mixed-replace; boundary=--boundary"
                    )
                    self.send_header(
                        "Cache-Control", "no-cache, no-store, must-revalidate"
                    )
                    self.send_header("Pragma", "no-cache")
                    self.send_header("Expires", "0")
                    self.send_header("Connection", "close")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    try:
                        while self.server_ref._running:
                            with self.server_ref._lock:
                                frame = self.server_ref._frame
                            if frame is not None:
                                ret, jpeg = cv2.imencode(
                                    ".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85]
                                )
                                if ret:
                                    jpeg_bytes = jpeg.tobytes()
                                    self.wfile.write(b"--boundary\r\n")
                                    self.wfile.write(
                                        f"Content-Type: image/jpeg\r\n".encode()
                                    )
                                    self.wfile.write(
                                        f"Content-Length: {len(jpeg_bytes)}\r\n\r\n".encode()
                                    )
                                    self.wfile.write(jpeg_bytes)
                                    self.wfile.write(b"\r\n")
                            time.sleep(0.03)
                    except (
                        BrokenPipeError,
                        ConnectionResetError,
                        ConnectionAbortedError,
                    ):
                        pass
                    finally:
                        self.server_ref._clients -= 1
                elif self.path == "/info":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    info = '{"status":"active","name":"RifatCam Desktop","version":"1.0.0"}'
                    self.wfile.write(info.encode())
                else:
                    self.send_response(404)
                    self.end_headers()

            def log_message(self, format, *args):
                pass

        self._server = HTTPServer((self.host, self.port), MJPEGHandler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self._running = False
        if self._server:
            self._server.shutdown()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        url = sys.argv[1]
        receiver = StreamReceiver(url)
        receiver.start()
        try:
            while True:
                frame = receiver.get_frame()
                if frame is not None:
                    cv2.imshow("RifatCam Stream Test", frame)
                    print(f"FPS: {receiver.fps}, Res: {receiver.resolution}", end="\r")
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break
        except KeyboardInterrupt:
            pass
        finally:
            receiver.stop()
            cv2.destroyAllWindows()
    else:
        print("Usage: python stream_receiver.py <mjpeg_url>")
