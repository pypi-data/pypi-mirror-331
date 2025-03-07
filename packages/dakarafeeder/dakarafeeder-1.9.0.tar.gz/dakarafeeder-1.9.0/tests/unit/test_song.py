from datetime import timedelta
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from dakara_feeder.directory import SongPaths
from dakara_feeder.metadata import FFProbeMetadataParser, MediaParseError
from dakara_feeder.song import BaseSong
from dakara_feeder.subtitle.parsing import Pysubs2SubtitleParser, SubtitleParseError


class BaseSongTestCase(TestCase):
    """Test the BaseSong class."""

    @patch.object(Pysubs2SubtitleParser, "parse", autospec=True)
    @patch.object(FFProbeMetadataParser, "parse", autospec=True)
    def test_subtitle_parser_error(self, mocked_metadata_parse, mocked_subtitle_parse):
        """Test an invalid subtitle file raises no exception but logs error."""
        # setup mocks
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )
        mocked_metadata_parse.return_value.get_audio_tracks_count.return_value = 1
        mocked_subtitle_parse.side_effect = SubtitleParseError("invalid")

        # create paths
        paths = SongPaths(Path("file.mp4"), subtitle=Path("file.ass"))

        # create BaseSong instance
        song = BaseSong(Path("/base-dir"), paths)

        # get song representation
        with self.assertLogs("dakara_feeder.song") as logger:
            representation = song.get_representation()

        # check no lyrics has been found
        self.assertEqual(representation["lyrics"], "")

        # assert logs

        self.assertListEqual(
            logger.output, ["ERROR:dakara_feeder.song:Lyrics not parsed: invalid"]
        )

    @patch.object(Pysubs2SubtitleParser, "parse", autospec=True)
    @patch.object(FFProbeMetadataParser, "parse", autospec=True)
    def test_metadata_error(self, mocked_metadata_parse, mocked_subtitle_parse):
        """Test an invalid video file raises no exception but logs error."""
        # setup mocks
        mocked_metadata_parse.side_effect = MediaParseError("invalid")
        mocked_subtitle_parse.return_value.get_lyrics.return_value = ""

        # create paths
        paths = SongPaths(Path("file.mp4"), subtitle=Path("file.ass"))

        # create BaseSong instance
        song = BaseSong(Path("/base-dir"), paths)

        # get song representation
        with self.assertLogs("dakara_feeder.song") as logger:
            representation = song.get_representation()

        # check duration defaults to zero
        self.assertEqual(representation["duration"], 0)

        # assert logs

        self.assertListEqual(
            logger.output, ["ERROR:dakara_feeder.song:Cannot parse metadata: invalid"]
        )
