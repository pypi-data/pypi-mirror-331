from importlib.resources import as_file, files
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from dakara_feeder.subtitle.parsing import (
    Pysubs2SubtitleParser,
    SubtitleNotFoundError,
    SubtitleParseError,
    TXTSubtitleParser,
)


class TXTSubtitleParserTestCase(TestCase):
    """Test the subtitle parser based on plain txt files."""

    def test_parse(self):
        """Parse text file."""
        with as_file(files("tests.resources.subtitles").joinpath("plain.txt")) as file:
            parser = TXTSubtitleParser.parse(file)
            self.assertEqual(parser.get_lyrics(), file.read_text())

    def test_parse_string(self):
        """Parse text."""
        parser = TXTSubtitleParser.parse_string("Piyo!")
        self.assertEqual(parser.get_lyrics(), "Piyo!")


class Pysubs2SubtitleParserTestCase(TestCase):
    """Test the subtitle parser based on pysubs2."""

    def generic_test_subtitle(self, file_name):
        """Run lyrics extraction test on specified file.

        Open and extract lyrics from the file, and test that the result is the
        same as the corresponding file with "_expected" prefix.

        This method is called from other tests methods.
        """
        # open and parse given file
        with as_file(files("tests.resources.subtitles").joinpath(file_name)) as file:
            parser = Pysubs2SubtitleParser.parse(file)
            lyrics = parser.get_lyrics()
            lines = lyrics.splitlines()

        # open expected result
        with as_file(
            files("tests.resources.subtitles").joinpath(file_name + "_expected")
        ) as file:
            expected_lines = file.read_text().splitlines()

        # check against expected file
        self.assertListEqual(lines, expected_lines)

    def test_simple(self):
        """Test simple ass."""
        self.generic_test_subtitle("simple.ass")

    def test_simple_string(self):
        """Test simple ass file from string."""
        # open and parse given file
        with as_file(files("tests.resources.subtitles").joinpath("simple.ass")) as file:
            content = file.read_text()
            parser = Pysubs2SubtitleParser.parse_string(content)
            lyrics = parser.get_lyrics()
            lines = lyrics.splitlines()

        # open expected result
        with as_file(
            files("tests.resources.subtitles").joinpath("simple.ass_expected")
        ) as file:
            expected_lines = file.read_text().splitlines()

        # check against expected file
        self.assertListEqual(lines, expected_lines)

    def test_duplicate_lines(self):
        """Test ass with duplicate lines."""
        self.generic_test_subtitle("duplicate_lines.ass")

    def test_drawing_commands(self):
        """Test ass containing drawing commands."""
        self.generic_test_subtitle("drawing_commands.ass")

    def test_comment_and_whitespace(self):
        """Test ass containing comment and whitespace."""
        self.generic_test_subtitle("comment_and_whitespace.ass")

    def test_not_found_error(self):
        """Test when the ass file to parse does not exist."""
        # call the method
        with self.assertRaisesRegex(
            SubtitleNotFoundError, "Subtitle file 'nowhere' not found"
        ):
            Pysubs2SubtitleParser.parse(Path("nowhere"))

    @patch("dakara_feeder.subtitle.parsing.pysubs2.load", autospec=True)
    def test_parse_error(self, mocked_load):
        """Test when the ass file to parse is invalid."""
        # prepare the mock
        mocked_load.side_effect = Exception("invalid")

        # call the method
        with self.assertRaisesRegex(
            SubtitleParseError, "Error when parsing subtitle file 'nowhere': invalid"
        ):
            Pysubs2SubtitleParser.parse(Path("nowhere"))

    @patch("dakara_feeder.subtitle.parsing.pysubs2.SSAFile.from_string", autospec=True)
    def test_parse_string_error(self, mocked_from_string):
        """Test when the ass stream to parse is invalid."""
        # prepare the mock
        mocked_from_string.side_effect = Exception("invalid")

        # call the method
        with self.assertRaisesRegex(
            SubtitleParseError, "Error when parsing subtitle content: invalid"
        ):
            Pysubs2SubtitleParser.parse_string("data")
