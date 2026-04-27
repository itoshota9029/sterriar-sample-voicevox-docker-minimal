"""Command-line interface for VoiceVox synthesis."""

import argparse
import sys
from pathlib import Path

from src.voicevox_client import VoiceVoxClient, VoiceVoxError


def main() -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(description="Synthesize speech using VoiceVox ENGINE")
    parser.add_argument("text", help="Text to synthesize")
    parser.add_argument("-s", "--speaker", type=int, default=1, help="Speaker ID (default: 1)")
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("output.wav"), help="Output file path"
    )
    parser.add_argument("--url", default="http://localhost:50021", help="VoiceVox ENGINE base URL")

    args = parser.parse_args()

    try:
        with VoiceVoxClient(base_url=args.url) as client:
            print(f"Synthesizing: {args.text}")
            audio_data = client.synthesize(text=args.text, speaker_id=args.speaker)

            args.output.write_bytes(audio_data)
            print(f"Saved to: {args.output}")

        return 0
    except VoiceVoxError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
