import numpy as np
import cv2
import os
import threading
from pathlib import Path


DETECTOR_BACKENDS = {
    "opencv_dnn": "OpenCV DNN",
    "yolo": "YOLO (Ultralytics)",
}


class Detector:
    def __init__(self, backend="opencv_dnn"):
        self._backend = backend
        self._enabled = False
        self._model = None
        self._classes = []
        self._conf_threshold = 0.5
        self._nms_threshold = 0.4
        self._input_size = (416, 416)
        self._lock = threading.Lock()
        self._detections = []
        self._model_loaded = False
        self._model_path = self._get_model_path()

    def _get_model_path(self):
        return Path.home() / ".rifatcam" / "models"

    @property
    def enabled(self):
        return self._enabled

    @property
    def detections(self):
        with self._lock:
            return list(self._detections)

    def set_backend(self, backend):
        if backend in DETECTOR_BACKENDS:
            self._backend = backend

    def enable(self):
        self._enabled = True
        if not self._model_loaded:
            self._load_model()

    def disable(self):
        self._enabled = False

    def _load_model(self):
        model_dir = self._model_path
        model_dir.mkdir(parents=True, exist_ok=True)

        cfg_path = model_dir / "yolov3.cfg"
        weights_path = model_dir / "yolov3.weights"
        names_path = model_dir / "coco.names"

        if cfg_path.exists() and weights_path.exists():
            try:
                self._model = cv2.dnn.readNet(str(cfg_path), str(weights_path))
                if names_path.exists():
                    self._classes = names_path.read_text().strip().splitlines()
                else:
                    self._classes = [
                        "person",
                        "bicycle",
                        "car",
                        "motorcycle",
                        "airplane",
                        "bus",
                        "train",
                        "truck",
                        "boat",
                        "traffic light",
                        "fire hydrant",
                        "stop sign",
                        "parking meter",
                        "bench",
                        "bird",
                        "cat",
                        "dog",
                        "horse",
                        "sheep",
                        "cow",
                        "elephant",
                        "bear",
                        "zebra",
                        "giraffe",
                        "backpack",
                        "umbrella",
                        "handbag",
                        "tie",
                        "suitcase",
                        "frisbee",
                        "skis",
                        "snowboard",
                        "sports ball",
                        "kite",
                        "baseball bat",
                        "baseball glove",
                        "skateboard",
                        "surfboard",
                        "tennis racket",
                        "bottle",
                        "wine glass",
                        "cup",
                        "fork",
                        "knife",
                        "spoon",
                        "bowl",
                        "banana",
                        "apple",
                        "sandwich",
                        "orange",
                        "broccoli",
                        "carrot",
                        "hot dog",
                        "pizza",
                        "donut",
                        "cake",
                        "chair",
                        "couch",
                        "potted plant",
                        "bed",
                        "dining table",
                        "toilet",
                        "tv",
                        "laptop",
                        "mouse",
                        "remote",
                        "keyboard",
                        "cell phone",
                        "microwave",
                        "oven",
                        "toaster",
                        "sink",
                        "refrigerator",
                        "book",
                        "clock",
                        "vase",
                        "scissors",
                        "teddy bear",
                        "hair drier",
                        "toothbrush",
                    ]
                self._model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
                self._model.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
                self._model_loaded = True
                print("[Detector] YOLOv3 model loaded successfully")
                return
            except Exception as e:
                print(f"[Detector] Failed to load YOLO model: {e}")

        print("[Detector] YOLO model files not found. Using Haar Cascade fallback.")
        try:
            face_cascade = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            if os.path.exists(face_cascade):
                self._model = cv2.CascadeClassifier(face_cascade)
                self._classes = ["face"]
                self._model_loaded = True
                print("[Detector] Haar Cascade loaded for face detection")
        except Exception as e:
            print(f"[Detector] Haar Cascade load failed: {e}")

    def detect(self, frame):
        if frame is None or not self._enabled or not self._model_loaded:
            return []

        if self._backend == "opencv_dnn" and isinstance(self._model, cv2.dnn_Net):
            return self._detect_yolo(frame)
        elif isinstance(self._model, cv2.CascadeClassifier):
            return self._detect_haar(frame)
        return []

    def _detect_yolo(self, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            frame, 1 / 255.0, self._input_size, swapRB=True, crop=False
        )
        self._model.setInput(blob)
        output_layers = self._model.getUnconnectedOutLayersNames()
        layer_outputs = self._model.forward(output_layers)

        boxes, confidences, class_ids = [], [], []
        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self._conf_threshold:
                    center_x = int(detection[0] * w)
                    center_y = int(detection[1] * h)
                    bw = int(detection[2] * w)
                    bh = int(detection[3] * h)
                    x = int(center_x - bw / 2)
                    y = int(center_y - bh / 2)
                    boxes.append([x, y, bw, bh])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(
            boxes, confidences, self._conf_threshold, self._nms_threshold
        )
        results = []
        if len(indices) > 0:
            for i in indices.flatten():
                x, y, bw, bh = boxes[i]
                label = (
                    self._classes[class_ids[i]]
                    if class_ids[i] < len(self._classes)
                    else f"class_{class_ids[i]}"
                )
                results.append(
                    {
                        "bbox": (x, y, bw, bh),
                        "confidence": confidences[i],
                        "label": label,
                        "class_id": class_ids[i],
                    }
                )

        with self._lock:
            self._detections = results
        return results

    def _detect_haar(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self._model.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        results = []
        for x, y, w, h in faces:
            results.append(
                {
                    "bbox": (x, y, w, h),
                    "confidence": 0.9,
                    "label": "face",
                    "class_id": 0,
                }
            )
        with self._lock:
            self._detections = results
        return results

    def draw_detections(self, frame):
        if not self._detections:
            return frame
        result = frame.copy()
        for det in self._detections:
            x, y, w, h = det["bbox"]
            label = f"{det['label']} {det['confidence']:.2f}"
            cv2.rectangle(result, (x, y), (x + w, y + h), (0, 212, 255), 2)
            cv2.rectangle(result, (x, y - 25), (x + w, y), (0, 212, 255), -1)
            cv2.putText(
                result,
                label,
                (x + 5, y - 7),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (10, 14, 23),
                1,
            )
        return result
