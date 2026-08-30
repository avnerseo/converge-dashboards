"""Download + cache the ONNX models the local (offline) detectors need.

Everything here comes from OpenCV Zoo (Apache-2.0). Files are cached under
$VSCAN_MODEL_DIR, or ~/.cache/vscan/models by default, and verified by SHA-256,
so a download only ever happens once per machine.
"""
from __future__ import annotations

import hashlib
import os
import tempfile
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

from .util import LOG, human_size

_ZOO_LFS = "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models"
_ZOO_RAW = "https://raw.githubusercontent.com/opencv/opencv_zoo/main/models"


@dataclass(frozen=True)
class ModelSpec:
    key: str
    filename: str
    subdir: str
    sha256: str
    approx_bytes: int
    note: str = ""
    urls: tuple[str, ...] = field(default=())

    def candidate_urls(self) -> list[str]:
        if self.urls:
            return list(self.urls)
        return [f"{_ZOO_LFS}/{self.subdir}/{self.filename}",
                f"{_ZOO_RAW}/{self.subdir}/{self.filename}"]


MODELS: dict[str, ModelSpec] = {
    "face_detect": ModelSpec(
        key="face_detect",
        filename="face_detection_yunet_2023mar.onnx",
        subdir="face_detection_yunet",
        sha256="8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4",
        approx_bytes=232_589,
        note="YuNet face detector",
    ),
    "face_embed": ModelSpec(
        key="face_embed",
        filename="face_recognition_sface_2021dec.onnx",
        subdir="face_recognition_sface",
        sha256="0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79",
        approx_bytes=38_696_353,
        note="SFace 128-d face embeddings",
    ),
    "appearance": ModelSpec(
        key="appearance",
        filename="person_reid_youtu_2021nov_int8bq.onnx",
        subdir="person_reid_youtureid",
        sha256="2b88597426335e6cd625119bdda090f9d3497bc80ba5b8a8910f65b8ccc09471",
        approx_bytes=29_203_236,
        note="Youtu ReID, 768-d appearance vectors (clothing/body, no face needed)",
    ),
    "objects": ModelSpec(
        key="objects",
        filename="object_detection_yolox_2022nov.onnx",
        subdir="object_detection_yolox",
        sha256="c5c2d13e59ae883e6af3b45daea64af4833a4951c92d116ec270d9ddbe998063",
        approx_bytes=35_858_002,
        note="YOLOX-S, 80 COCO classes (person, car, backpack, ...)",
    ),
}


def model_dir() -> Path:
    d = Path(os.environ.get("VSCAN_MODEL_DIR", Path.home() / ".cache" / "vscan" / "models"))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def get_model(key: str, allow_download: bool = True) -> Path:
    """Return a local path to the model, downloading it on first use."""
    spec = MODELS[key]
    dest = model_dir() / spec.filename
    if dest.exists() and dest.stat().st_size > 1024:
        if _sha256(dest) == spec.sha256:
            return dest
        LOG.warning("checksum mismatch for %s - re-downloading", dest.name)
        dest.unlink()
    if not allow_download:
        raise RuntimeError(
            f"model {spec.filename} is missing from {model_dir()} and downloads are "
            "disabled (--offline). Run 'vscan models fetch' on a networked machine "
            "and copy the directory over."
        )

    last_err: Exception | None = None
    for url in spec.candidate_urls():
        LOG.info("downloading %s (%s) from %s", spec.filename,
                 human_size(spec.approx_bytes), url.split("/")[2])
        try:
            with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as tmp:
                tmp_path = Path(tmp.name)
                with urllib.request.urlopen(url, timeout=120) as resp:
                    while True:
                        chunk = resp.read(1 << 20)
                        if not chunk:
                            break
                        tmp.write(chunk)
            got = _sha256(tmp_path)
            if got != spec.sha256:
                tmp_path.unlink(missing_ok=True)
                last_err = RuntimeError(f"checksum mismatch from {url}: {got}")
                continue
            tmp_path.replace(dest)
            return dest
        except Exception as exc:  # network, HTTP, disk
            last_err = exc
            LOG.debug("download failed: %s", exc)
    raise RuntimeError(f"could not fetch {spec.filename}: {last_err}")


def fetch_all(keys: list[str] | None = None) -> list[Path]:
    return [get_model(k) for k in (keys or list(MODELS))]
