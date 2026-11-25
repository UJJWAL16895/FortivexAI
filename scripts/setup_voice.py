"""Download the optional faster-whisper models before running live local STT."""

from faster_whisper.utils import download_model


def main() -> None:
    for name in ("base", "small"):
        download_model(name)
        print(f"Whisper {name} weights available.", flush=True)
    print("Set VOICE_STT=local in .env and restart for warm CPU transcription.")


if __name__ == "__main__":
    main()
