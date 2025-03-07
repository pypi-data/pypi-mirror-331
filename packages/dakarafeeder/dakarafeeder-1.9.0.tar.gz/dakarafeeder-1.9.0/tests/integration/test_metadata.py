from datetime import timedelta
from importlib.resources import as_file, files
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, skipUnless

from dakara_feeder.metadata import (
    FFProbeMetadataParser,
    MediainfoMetadataParser,
    MediaNotFoundError,
    MediaParseError,
)


@skipUnless(MediainfoMetadataParser.is_available(), "MediaInfo not installed")
class MediainfoMetadataParserIntegrationTestCase(TestCase):
    """Test the Mediainfo metadata parser in an integrated way."""

    def test_parse_not_found_error(self):
        """Test to extract metadata from a file that does not exist."""
        # call the method
        with self.assertRaisesRegex(
            MediaNotFoundError, "Media file 'nowhere' not found"
        ):
            MediainfoMetadataParser.parse(Path("nowhere"))

    def test_get_duration(self):
        """Test to get duration."""
        with as_file(files("tests.resources.media").joinpath("dummy.mkv")) as file:
            parser = MediainfoMetadataParser.parse(file)

        self.assertEqual(
            parser.get_duration(), timedelta(seconds=2, microseconds=23000)
        )

    def test_get_number_audio_tracks(self):
        """Test to get number of audio tracks."""
        with as_file(files("tests.resources.media").joinpath("dummy.mkv")) as file:
            parser = MediainfoMetadataParser.parse(file)

        self.assertEqual(parser.get_audio_tracks_count(), 2)

    def test_get_number_subtitle_tracks(self):
        """Test to get number of subtitle tracks."""
        with as_file(files("tests.resources.media").joinpath("dummy.mkv")) as file:
            parser = MediainfoMetadataParser.parse(file)

        self.assertEqual(parser.get_subtitle_tracks_count(), 1)


@skipUnless(FFProbeMetadataParser.is_available(), "FFProbe not installed")
class FFProbeMetadataParserIntegrationTestCase(TestCase):
    """Test the FFProbe metadata parser in an integrated way."""

    def test_parse_not_found_error(self):
        """Test to extract metadata from a file that does not exist."""
        # call the method
        with self.assertRaisesRegex(
            MediaNotFoundError, "Media file 'nowhere' not found"
        ):
            FFProbeMetadataParser.parse(Path("nowhere"))

    def test_parse_invalid_error(self):
        """Test to extract metadata from a file that cannot be parsed."""
        with TemporaryDirectory() as temp:
            file = Path(temp) / "file"
            file.write_bytes(b"nonsense")

            # call the method
            with self.assertRaisesRegex(
                MediaParseError, "Error when processing media file"
            ):
                FFProbeMetadataParser.parse(file)

    def test_get_duration(self):
        """Test to get duration."""
        with as_file(files("tests.resources.media").joinpath("dummy.mkv")) as file:
            parser = FFProbeMetadataParser.parse(file)

        self.assertEqual(
            parser.get_duration(), timedelta(seconds=2, microseconds=23000)
        )

    def test_get_number_audio_tracks(self):
        """Test to get number of audio tracks."""
        with as_file(files("tests.resources.media").joinpath("dummy.mkv")) as file:
            parser = FFProbeMetadataParser.parse(file)

        self.assertEqual(parser.get_audio_tracks_count(), 2)

    def test_get_number_subtitle_tracks(self):
        """Test to get number of subtitle tracks."""
        with as_file(files("tests.resources.media").joinpath("dummy.mkv")) as file:
            parser = FFProbeMetadataParser.parse(file)

        self.assertEqual(parser.get_subtitle_tracks_count(), 1)
