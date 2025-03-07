from pathlib import Path
from subprocess import DEVNULL
from unittest import TestCase
from unittest.mock import patch

from dakara_feeder.subtitle.extraction import (
    FFmpegNotInstalledError,
    FFmpegSubtitleExtractor,
)


class FFmpegSubtitleExtractorTestCase(TestCase):
    """Test the subtitle extractor based on FFmpeg."""

    @patch("dakara_feeder.subtitle.extraction.subprocess.run", autospec=True)
    def test_is_available(self, mocked_run):
        """Test if the FFmpeg subtitle extractor is available."""
        self.assertTrue(FFmpegSubtitleExtractor.is_available())
        mocked_run.assert_called_with(
            ["ffmpeg", "-version"], stdout=DEVNULL, stderr=DEVNULL
        )

    @patch("dakara_feeder.subtitle.extraction.subprocess.run", autospec=True)
    def test_is_available_not_available(self, mocked_run):
        """Test if the FFmpeg subtitle extractor is not available."""
        mocked_run.side_effect = FileNotFoundError()
        self.assertFalse(FFmpegSubtitleExtractor.is_available())

    @patch.object(FFmpegSubtitleExtractor, "is_available", autospec=True)
    def test_extract_not_available(self, mocked_is_available):
        """Test to extract when FFmpeg is not installed."""
        mocked_is_available.return_value = False
        with self.assertRaisesRegex(FFmpegNotInstalledError, "FFmpeg not installed"):
            FFmpegSubtitleExtractor.extract(Path("nowhere"))
