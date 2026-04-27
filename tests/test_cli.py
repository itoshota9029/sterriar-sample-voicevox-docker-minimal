"""Tests for CLI module."""

from unittest.mock import Mock, patch

from src.cli import main
from src.voicevox_client import VoiceVoxError


def test_cli_success(tmp_path):
    """Test successful CLI execution."""
    output_file = tmp_path / "test.wav"
    mock_audio_data = b"FAKE_WAV_DATA"

    test_args = [
        "cli.py",
        "Hello",
        "-s",
        "3",
        "-o",
        str(output_file),
        "--url",
        "http://test:50021",
    ]

    with patch("sys.argv", test_args):
        with patch("src.cli.VoiceVoxClient") as mock_client_cls:
            mock_client = Mock()
            mock_client.synthesize.return_value = mock_audio_data
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=None)
            mock_client_cls.return_value = mock_client

            exit_code = main()

            assert exit_code == 0
            mock_client_cls.assert_called_once_with(base_url="http://test:50021")
            mock_client.synthesize.assert_called_once_with(text="Hello", speaker_id=3)
            assert output_file.read_bytes() == mock_audio_data


def test_cli_default_arguments(tmp_path):
    """Test CLI with default arguments."""
    output_file = tmp_path / "output.wav"
    mock_audio_data = b"AUDIO"

    test_args = ["cli.py", "Test text", "-o", str(output_file)]

    with patch("sys.argv", test_args):
        with patch("src.cli.VoiceVoxClient") as mock_client_cls:
            mock_client = Mock()
            mock_client.synthesize.return_value = mock_audio_data
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=None)
            mock_client_cls.return_value = mock_client

            exit_code = main()

            assert exit_code == 0
            mock_client_cls.assert_called_once_with(base_url="http://localhost:50021")
            mock_client.synthesize.assert_called_once_with(text="Test text", speaker_id=1)


def test_cli_voicevox_error(tmp_path, capsys):
    """Test CLI with VoiceVox error."""
    output_file = tmp_path / "error.wav"
    test_args = ["cli.py", "Error test", "-o", str(output_file)]

    with patch("sys.argv", test_args):
        with patch("src.cli.VoiceVoxClient") as mock_client_cls:
            mock_client = Mock()
            mock_client.synthesize.side_effect = VoiceVoxError("Connection refused")
            mock_client.__enter__ = Mock(return_value=mock_client)
            mock_client.__exit__ = Mock(return_value=None)
            mock_client_cls.return_value = mock_client

            exit_code = main()

            assert exit_code == 1
            captured = capsys.readouterr()
            assert "Error: Connection refused" in captured.err
            assert not output_file.exists()
