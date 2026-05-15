import time
import threading
import numpy as np
import cv2


class MotionDetector:
    def __init__(self, sensitivity=0.5, min_area=5000):
        self._sensitivity = sensitivity
        self._min_area = min_area
        self._bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=500, varThreshold=36, detectShadows=False
        )
        self._previous_frame = None
        self._motion_detected = False
        self._motion_count = 0
        self._last_motion_time = 0
        self._cooldown = 1.0
        self._enabled = False
        self._lock = threading.Lock()
        self._on_motion = None
        self._on_motion_end = None
        self._monitor_thread = None
        self._running = False

    @property
    def enabled(self):
        return self._enabled

    @property
    def motion_detected(self):
        return self._motion_detected

    @property
    def motion_count(self):
        return self._motion_count

    def set_sensitivity(self, val):
        self._sensitivity = max(0.1, min(1.0, val))
        threshold = int(100 - (self._sensitivity * 90))
        self._bg_subtractor.setVarThreshold(threshold)

    def set_min_area(self, area):
        self._min_area = area

    def set_on_motion(self, callback):
        self._on_motion = callback

    def set_on_motion_end(self, callback):
        self._on_motion_end = callback

    def enable(self):
        self._enabled = True
        if not self._running:
            self._running = True

    def disable(self):
        self._enabled = False
        self._motion_detected = False

    def detect(self, frame):
        if frame is None or not self._enabled:
            return False

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        fg_mask = self._bg_subtractor.apply(gray)
        thresh = cv2.threshold(fg_mask, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        motion = False
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self._min_area:
                motion = True
                break

        now = time.time()
        with self._lock:
            if (
                motion
                and not self._motion_detected
                and (now - self._last_motion_time) > self._cooldown
            ):
                self._motion_detected = True
                self._motion_count += 1
                self._last_motion_time = now
                if self._on_motion:
                    self._on_motion()
            elif not motion and self._motion_detected:
                self._motion_detected = False
                if self._on_motion_end:
                    self._on_motion_end()

        return self._motion_detected


class MotionAlert:
    def __init__(self):
        self._alerts = []
        self._lock = threading.Lock()

    def add_alert(self, alert_type, message, frame=None):
        with self._lock:
            self._alerts.append(
                {
                    "type": alert_type,
                    "message": message,
                    "timestamp": time.time(),
                    "frame": frame,
                }
            )
            if len(self._alerts) > 100:
                self._alerts.pop(0)

    def get_alerts(self, clear=False):
        with self._lock:
            alerts = list(self._alerts)
            if clear:
                self._alerts.clear()
            return alerts
