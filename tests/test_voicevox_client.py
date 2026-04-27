"""Tests for VoiceVox client."""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from src.voicevox_client import VoiceVoxClient, VoiceVoxError


def test_get_speakers_success():
    """Test successful speaker retrieval."""
    client = VoiceVoxClient(base_url="http://localhost:50021")
    mock_response = Mock()
    mock_response.json.return_value = [
        {"name": "Speaker1", "styles": [{"id": 1, "name": "Normal"}]},
        {"name": "Speaker2", "styles": [{"id": 2, "name": "Happy"}]},
    ]
    mock_response.raise_for_status = Mock()

    with patch.object(client.session, "get", return_value=mock_response) as mock_get:
        speakers = client.get_speakers()

        assert len(speakers) == 2
        assert speakers[0]["name"] == "Speaker1"
        mock_get.assert_called_once_with("http://localhost:50021/speakers", timeout=10)


def test_get_speakers_network_error():
    """Test speaker retrieval with network error."""
    client = VoiceVoxClient()

    with patch.object(
        client.session, "get", side_effect=requests.ConnectionError("Connection failed")
    ):
        with pytest.raises(VoiceVoxError, match="Failed to get speakers"):
            client.get_speakers()


def test_create_audio_query_success():
    """Test successful audio query creation."""
    client = VoiceVoxClient()
    mock_response = Mock()
    mock_response.json.return_value = {
        "accent_phrases": [{"moras": [], "accent": 1}],
        "speedScale": 1.0,
        "pitchScale": 0.0,
    }
    mock_response.raise_for_status = Mock()

    with patch.object(client.session, "post", return_value=mock_response) as mock_post:
        query = client.create_audio_query(text="こんにちは", speaker_id=1)

        assert "accent_phrases" in query
        assert query["speedScale"] == 1.0
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args.kwargs["params"] == {"text": "こんにちは", "speaker": 1}


def test_create_audio_query_http_error():
    """Test audio query creation with HTTP error."""
    client = VoiceVoxClient()
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = requests.HTTPError("400 Bad Request")

    with patch.object(client.session, "post", return_value=mock_response):
        with pytest.raises(VoiceVoxError, match="Failed to create audio query"):
            client.create_audio_query(text="", speaker_id=999)


def test_synthesize_from_query_success():
    """Test successful audio synthesis from query."""
    client = VoiceVoxClient()
    audio_query = {"accent_phrases": [], "speedScale": 1.0}
    mock_response = Mock()
    mock_response.content = b"RIFF....WAV"
    mock_response.raise_for_status = Mock()

    with patch.object(client.session, "post", return_value=mock_response) as mock_post:
        audio_data = client.synthesize_from_query(audio_query, speaker_id=1)

        assert audio_data == b"RIFF....WAV"
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args.kwargs["params"] == {"speaker": 1}
        assert call_args.kwargs["data"] == json.dumps(audio_query)


def test_synthesize_from_query_timeout():
    """Test audio synthesis with timeout error."""
    client = VoiceVoxClient()
    audio_query = {"accent_phrases": []}

    with patch.object(client.session, "post", side_effect=requests.Timeout("Timeout")):
        with pytest.raises(VoiceVoxError, match="Failed to synthesize audio"):
            client.synthesize_from_query(audio_query, speaker_id=1)


def test_synthesize_high_level_success():
    """Test high-level synthesize method."""
    client = VoiceVoxClient()
    mock_query = {"accent_phrases": [], "speedScale": 1.0}
    mock_audio = b"WAV_DATA"

    with patch.object(client, "create_audio_query", return_value=mock_query) as mock_create:
        with patch.object(client, "synthesize_from_query", return_value=mock_audio) as mock_synth:
            audio_data = client.synthesize(text="テスト", speaker_id=2)

            assert audio_data == b"WAV_DATA"
            mock_create.assert_called_once_with("テスト", 2)
            mock_synth.assert_called_once_with(mock_query, 2)


def test_context_manager():
    """Test client as context manager."""
    with patch("src.voicevox_client.requests.Session") as mock_session_cls:
        mock_session = MagicMock()
        mock_session_cls.return_value = mock_session

        with VoiceVoxClient() as client:
            assert client is not None

        mock_session.close.assert_called_once()


def test_base_url_normalization():
    """Test base URL trailing slash removal."""
    client1 = VoiceVoxClient(base_url="http://localhost:50021/")
    client2 = VoiceVoxClient(base_url="http://localhost:50021")

    assert client1.base_url == "http://localhost:50021"
    assert client2.base_url == "http://localhost:50021"
