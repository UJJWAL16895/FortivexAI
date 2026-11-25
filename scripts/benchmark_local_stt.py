"""Measure warm CPU faster-whisper on the two PCM WAV files from benchmark_speech."""

import argparse
import json
import wave
from pathlib import Path
from time import perf_counter

import numpy as np
from faster_whisper import WhisperModel


def main(folder: Path) -> None:
    for name in ("base", "small"):
        started = perf_counter()
        model = WhisperModel(name, device="cpu", compute_type="int8", cpu_threads=4)
        print(name, "load_ms", round((perf_counter() - started) * 1000), flush=True)
        for language in ("en", "hi"):
            with wave.open(str(folder / f"{language}-input.wav")) as clip:
                pcm = np.frombuffer(clip.readframes(clip.getnframes()), dtype="<i2")
            started = perf_counter()
            segments, _ = model.transcribe(
                pcm.astype(np.float32) / 32768, beam_size=1, language=language
            )
            text = " ".join(segment.text.strip() for segment in segments)
            print(
                name,
                language,
                round((perf_counter() - started) * 1000),
                json.dumps(text),
                flush=True,
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    main(parser.parse_args().folder)
