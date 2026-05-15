import os
import time
import threading
import cv2
from datetime import datetime
from pathlib import Path


class Recorder:
    def __init__(self, output_dir=None):
        self._output_dir = (
            Path(output_dir) if output_dir else Path.home() / ".rifatcam" / "recordings"
        )
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._recording = False
        self._writer = None
        self._lock = threading.Lock()
        self._frame_queue = []
        self._thread = None
        self._fps = 20.0
        self._codec = "avc1"
        self._output_path = None
        self._start_time = None

    @property
    def is_recording(self):
        return self._recording

    @property
    def recording_time(self):
        if self._start_time and self._recording:
            return time.time() - self._start_time
        return 0

    @property
    def output_path(self):
        return self._output_path

    def set_fps(self, fps):
        self._fps = max(1, min(fps, 60))

    def start_recording(self, width, height, fps=None):
        if self._recording:
            return False
        if fps:
            self._fps = fps
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rifatcam_recording_{timestamp}.mp4"
        self._output_path = str(self._output_dir / filename)

        fourcc_map = {
            "avc1": cv2.VideoWriter_fourcc(*"avc1"),
            "mp4v": cv2.VideoWriter_fourcc(*"mp4v"),
            "x264": cv2.VideoWriter_fourcc(*"x264"),
            "mjpg": cv2.VideoWriter_fourcc(*"MJPG"),
        }
        fourcc = fourcc_map.get(self._codec, cv2.VideoWriter_fourcc(*"avc1"))

        self._writer = cv2.VideoWriter(
            self._output_path, fourcc, self._fps, (width, height)
        )
        if not self._writer.isOpened():
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self._writer = cv2.VideoWriter(
                self._output_path, fourcc, self._fps, (width, height)
            )

        if not self._writer.isOpened():
            return False

        self._recording = True
        self._start_time = time.time()
        self._thread = threading.Thread(target=self._write_worker, daemon=True)
        self._thread.start()
        return True

    def write_frame(self, frame):
        if not self._recording or self._writer is None:
            return
        with self._lock:
            self._frame_queue.append(frame.copy())

    def stop_recording(self):
        if not self._recording:
            return None
        self._recording = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)
        with self._lock:
            if self._writer:
                self._writer.release()
                self._writer = None
            self._frame_queue.clear()
        duration = time.time() - self._start_time if self._start_time else 0
        self._start_time = None
        return {"path": self._output_path, "duration": duration, "fps": self._fps}

    def _write_worker(self):
        while self._recording or self._frame_queue:
            frame = None
            with self._lock:
                if self._frame_queue:
                    frame = self._frame_queue.pop(0)
            if frame is not None:
                try:
                    self._writer.write(frame)
                except Exception:
                    pass
            else:
                time.sleep(0.01)


class ScreenshotCapture:
    def __init__(self, output_dir=None):
        self._output_dir = (
            Path(output_dir)
            if output_dir
            else Path.home() / ".rifatcam" / "screenshots"
        )
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def capture(self, frame):
        if frame is None:
            return None
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rifatcam_screenshot_{timestamp}.png"
        output_path = str(self._output_dir / filename)
        cv2.imwrite(output_path, frame)
        return output_path
