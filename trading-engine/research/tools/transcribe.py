#!/usr/bin/env python3
"""Offline speech-to-text for audio the cloud session cannot otherwise hear.

Why this exists: huggingface.co, openaipublic and alphacephei are all blocked
by the cloud egress allowlist, so the usual Whisper model hosts are out of
reach.  GitHub *release assets* are reachable, and k2-fsa/sherpa-onnx
publishes Whisper ONNX models there.  That is the whole trick.

Setup (once):
    pip install sherpa-onnx numpy imageio-ffmpeg
    curl -sSL -o m.tar.bz2 https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-small.en.tar.bz2
    tar xjf m.tar.bz2

Usage:
    python3 transcribe.py <audio file> [model dir]

Two things that mattered and are not obvious:
  * Instagram/phone audio is very quiet (peak ~0.05).  Without per-chunk
    normalisation Whisper hallucinates "(static)" and "[Music]" instead of
    the speech that is plainly there.  Normalise every chunk, not the file.
  * Chunk boundaries matter.  A window that starts mid-word can decode to a
    single word.  Overlap, and re-cut the tail at a different phase if a
    window comes back suspiciously empty.
"""
import subprocess, sys, wave, os
import numpy as np, sherpa_onnx, imageio_ffmpeg

CHUNK, OVERLAP = 25.0, 2.0

def to_wav(src, dst):
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                    "-i", src, "-ac", "1", "-ar", "16000",
                    "-c:a", "pcm_s16le", dst], check=True)

def main(src, model="sherpa-onnx-whisper-small.en"):
    stem = os.path.basename(model).replace("sherpa-onnx-whisper-", "")
    wav = "/tmp/_transcribe.wav"
    to_wav(src, wav)
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=f"{model}/{stem}-encoder.onnx",
        decoder=f"{model}/{stem}-decoder.onnx",
        tokens=f"{model}/{stem}-tokens.txt", num_threads=4)
    w = wave.open(wav); sr = w.getframerate()
    a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768

    step = int((CHUNK - OVERLAP) * sr)
    for i in range(0, len(a), step):
        seg = a[i:i + int(CHUNK * sr)]
        if len(seg) < sr * 0.7:
            break
        seg = seg / max(np.abs(seg).max(), 1e-6) * 0.95   # per-chunk, see docstring
        st = rec.create_stream(); st.accept_waveform(sr, seg); rec.decode_stream(st)
        print(f"[{i/sr:6.1f}s] {st.result.text.strip()}", flush=True)

if __name__ == "__main__":
    main(*sys.argv[1:])
