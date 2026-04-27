"""VoiceVox ENGINE REST API client."""

import json
from typing import Any

import requests


class VoiceVoxError(Exception):
    """VoiceVox API error."""


class VoiceVoxClient:
    """Client for VoiceVox ENGINE REST API."""

    def __init__(self, base_url: str = "http://localhost:50021") -> None:
        """Initialize the client.

        Args:
            base_url: Base URL of VoiceVox ENGINE (default: http://localhost:50021)
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()

    def get_speakers(self) -> list[dict[str, Any]]:
        """Get available speakers.

        Returns:
            List of speaker information dictionaries.

        Raises:
            VoiceVoxError: If the API request fails.
        """
        url = f"{self.base_url}/speakers"
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise VoiceVoxError(f"Failed to get speakers: {e}") from e

    def create_audio_query(self, text: str, speaker_id: int) -> dict[str, Any]:
        """Create audio query from text.

        Args:
            text: Text to synthesize.
            speaker_id: Speaker ID.

        Returns:
            Audio query dictionary.

        Raises:
            VoiceVoxError: If the API request fails.
        """
        url = f"{self.base_url}/audio_query"
        params = {"text": text, "speaker": speaker_id}
        try:
            response = self.session.post(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise VoiceVoxError(f"Failed to create audio query: {e}") from e

    def synthesize_from_query(self, audio_query: dict[str, Any], speaker_id: int) -> bytes:
        """Synthesize audio from audio query.

        Args:
            audio_query: Audio query dictionary.
            speaker_id: Speaker ID.

        Returns:
            Audio data in WAV format.

        Raises:
            VoiceVoxError: If the API request fails.
        """
        url = f"{self.base_url}/synthesis"
        params = {"speaker": speaker_id}
        headers = {"Content-Type": "application/json"}
        try:
            response = self.session.post(
                url, params=params, data=json.dumps(audio_query), headers=headers, timeout=30
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise VoiceVoxError(f"Failed to synthesize audio: {e}") from e

    def synthesize(self, text: str, speaker_id: int = 1) -> bytes:
        """Synthesize audio from text (high-level method).

        Args:
            text: Text to synthesize.
            speaker_id: Speaker ID (default: 1).

        Returns:
            Audio data in WAV format.

        Raises:
            VoiceVoxError: If the synthesis fails.
        """
        audio_query = self.create_audio_query(text, speaker_id)
        return self.synthesize_from_query(audio_query, speaker_id)

    def close(self) -> None:
        """Close the session."""
        self.session.close()

    def __enter__(self) -> "VoiceVoxClient":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()
