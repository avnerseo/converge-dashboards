"""Optional local object detection with YOLOX-S (80 COCO classes).

Faces answer "who"; objects answer "was anyone there at all", "did a car pull
up", "was someone carrying a bag" - useful when the person never faces the
camera. Decoding follows the OpenCV Zoo reference implementation (Apache-2.0).
"""
from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from . import modelzoo

COCO_CLASSES = (
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush",
)


@dataclass
class ObjectDet:
    label: str
    score: float
    box: tuple[float, float, float, float]      # x, y, w, h in frame pixels


class ObjectEngine:
    INPUT = 640

    def __init__(self, conf_threshold: float = 0.35, nms_threshold: float = 0.5,
                 labels: tuple[str, ...] | None = None, allow_download: bool = True):
        path = modelzoo.get_model("objects", allow_download)
        self.net = cv2.dnn.readNet(str(path))
        self.conf = conf_threshold
        self.nms = nms_threshold
        self.keep = set(labels) if labels else None
        self.strides = (8, 16, 32)
        self._grids, self._strides_col = self._anchors()

    def _anchors(self) -> tuple[np.ndarray, np.ndarray]:
        grids, expanded = [], []
        for stride in self.strides:
            size = self.INPUT // stride
            xv, yv = np.meshgrid(np.arange(size), np.arange(size))
            grid = np.stack((xv, yv), 2).reshape(1, -1, 2)
            grids.append(grid)
            expanded.append(np.full((1, grid.shape[1], 1), stride))
        return (np.concatenate(grids, 1).astype(np.float32),
                np.concatenate(expanded, 1).astype(np.float32))

    def _letterbox(self, bgr: np.ndarray) -> tuple[np.ndarray, float]:
        h, w = bgr.shape[:2]
        ratio = min(self.INPUT / h, self.INPUT / w)
        nh, nw = int(round(h * ratio)), int(round(w * ratio))
        canvas = np.full((self.INPUT, self.INPUT, 3), 114.0, dtype=np.float32)
        resized = cv2.resize(bgr, (nw, nh), interpolation=cv2.INTER_LINEAR)
        canvas[:nh, :nw] = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB).astype(np.float32)
        return canvas, ratio

    def detect(self, frame: np.ndarray) -> list[ObjectDet]:
        padded, ratio = self._letterbox(np.ascontiguousarray(frame))
        blob = np.transpose(padded, (2, 0, 1))[np.newaxis, ...]
        self.net.setInput(blob)
        outs = self.net.forward(self.net.getUnconnectedOutLayersNames())
        preds = np.array(outs[0][0], dtype=np.float32)          # (8400, 85)

        preds[:, :2] = (preds[:, :2] + self._grids[0]) * self._strides_col[0]
        preds[:, 2:4] = np.exp(preds[:, 2:4]) * self._strides_col[0]

        boxes = np.empty_like(preds[:, :4])
        boxes[:, 0] = preds[:, 0] - preds[:, 2] / 2.0
        boxes[:, 1] = preds[:, 1] - preds[:, 3] / 2.0
        boxes[:, 2:4] = preds[:, 2:4]

        scores = preds[:, 4:5] * preds[:, 5:]
        best = np.argmax(scores, axis=1)
        conf = scores[np.arange(scores.shape[0]), best]

        mask = conf >= self.conf
        if not mask.any():
            return []
        boxes, conf, best = boxes[mask], conf[mask], best[mask]

        keep = cv2.dnn.NMSBoxesBatched(boxes.tolist(), conf.tolist(), best.tolist(),
                                       self.conf, self.nms)
        out: list[ObjectDet] = []
        for i in np.array(keep).ravel().astype(int):
            label = COCO_CLASSES[int(best[i])]
            if self.keep and label not in self.keep:
                continue
            x, y, w, h = (float(v) / ratio for v in boxes[i])
            out.append(ObjectDet(label, float(conf[i]), (x, y, w, h)))
        return out
