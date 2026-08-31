import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def build_static_camera_clip(path, seconds: int = 60, fps: int = 10,
                             open_windows=((12.0, 20.0), (38.0, 44.0)),
                             door=(430, 90, 120, 240), size=(640, 480)):
    """A fixed camera watching a door that opens at known times.

    Footage that needs no faces and no people, so the tests about places -
    zones and counting lines - can run anywhere ffmpeg is installed.
    """
    import subprocess

    import cv2
    import numpy as np

    width, height = size
    rng = np.random.default_rng(3)
    back = rng.integers(60, 90, size=(height, width, 3), dtype=np.uint8)
    back = cv2.GaussianBlur(back, (21, 21), 0)
    cv2.rectangle(back, (40, 300), (600, 470), (70, 70, 78), -1)          # floor
    x, y, w, h = door
    cv2.rectangle(back, (x, y), (x + w, y + h), (150, 148, 140), -1)      # shut
    cv2.rectangle(back, (x, y), (x + w, y + h), (40, 40, 45), 2)

    raw = Path(path).with_suffix(".raw")
    with open(raw, "wb") as fh:
        for n in range(seconds * fps):
            t = n / fps
            frame = cv2.add(back, rng.integers(0, 8, back.shape, dtype=np.uint8))
            if any(a <= t <= b for a, b in open_windows):
                cv2.rectangle(frame, (x, y), (x + w, y + h), (18, 18, 22), -1)
            fh.write(frame.tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo",
                    "-pix_fmt", "bgr24", "-s", f"{width}x{height}", "-r", str(fps),
                    "-i", str(raw), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    str(path)], check=True)
    raw.unlink()
    return open_windows
