from importlib.resources import as_file, files
from pathlib import Path
from shutil import copy
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from dakara_feeder.directory import (
    SongPaths,
    get_main_type,
    group_by_type,
    list_directory,
)


class ListDirectoryTestCase(TestCase):
    """Test the directory lister."""

    @patch("dakara_feeder.directory.get_main_type", autospec=True)
    @patch.object(Path, "is_file", autospec=True)
    @patch.object(Path, "rglob", autospec=True)
    def test_list_directory(self, mocked_rglob, mocked_is_file, mocked_get_main_type):
        """Test to list a directory."""
        # mock directory structure
        mocked_is_file.return_value = True
        mocked_rglob.return_value = (
            item
            for item in [
                Path("directory/file0.mkv"),
                Path("directory/file1.mkv"),
                Path("directory/file1.ass"),
                Path("directory/file1.ogg"),
                Path("directory/subdirectory/file2.mkv"),
                Path("directory/subdirectory/file3.mkv"),
                Path("directory/subdirectory/file3.ass"),
                Path("directory/subdirectory/empty"),
                Path("directory/file0.ass"),
            ]
        )
        mocked_get_main_type.side_effect = get_main_type_mock
        # call the function
        with self.assertLogs("dakara_feeder.directory", "DEBUG") as logger:
            listing = list_directory(Path("directory"))

        # check the structure
        self.assertEqual(len(listing), 4)
        self.assertCountEqual(
            [
                SongPaths(Path("file0.mkv"), subtitle=Path("file0.ass")),
                SongPaths(
                    Path("file1.mkv"),
                    audio=Path("file1.ogg"),
                    subtitle=Path("file1.ass"),
                ),
                SongPaths(Path("subdirectory/file2.mkv")),
                SongPaths(
                    Path("subdirectory/file3.mkv"),
                    subtitle=Path("subdirectory/file3.ass"),
                ),
            ],
            listing,
        )

        # check the logger was called
        self.assertListEqual(
            logger.output,
            [
                "DEBUG:dakara_feeder.directory:Listing 'directory'",
                "DEBUG:dakara_feeder.directory:Listed 9 files",
                "DEBUG:dakara_feeder.directory:Found 4 different videos",
            ],
        )

    @patch("dakara_feeder.directory.get_main_type", autospec=True)
    @patch.object(Path, "is_file", autospec=True)
    @patch.object(Path, "rglob", autospec=True)
    def test_list_directory_same_stem(
        self, mocked_rglob, mocked_is_file, mocked_get_main_type
    ):
        """Test case when files with the same name exists in different directories."""
        # mock directory structure
        mocked_is_file.return_value = True
        mocked_rglob.return_value = (
            item
            for item in [
                Path("directory/file0.mkv"),
                Path("directory/file0.ass"),
                Path("directory/subdirectory/file0.mkv"),
                Path("directory/subdirectory/file0.ass"),
            ]
        )
        mocked_get_main_type.side_effect = get_main_type_mock

        # call the function
        with self.assertLogs("dakara_feeder.directory", "DEBUG") as logger:
            listing = list_directory(Path("directory"))

        # check the structure
        self.assertEqual(len(listing), 2)
        self.assertCountEqual(
            [
                SongPaths(Path("file0.mkv"), subtitle=Path("file0.ass")),
                SongPaths(
                    Path("subdirectory/file0.mkv"),
                    subtitle=Path("subdirectory/file0.ass"),
                ),
            ],
            listing,
        )

        # check the logger was called
        self.assertListEqual(
            logger.output,
            [
                "DEBUG:dakara_feeder.directory:Listing 'directory'",
                "DEBUG:dakara_feeder.directory:Listed 4 files",
                "DEBUG:dakara_feeder.directory:Found 2 different videos",
            ],
        )

    @patch("dakara_feeder.directory.get_main_type", autospec=True)
    @patch.object(Path, "is_file", autospec=True)
    @patch.object(Path, "rglob", autospec=True)
    def test_list_dot_in_filename(
        self, mocked_rglob, mocked_is_file, mocked_get_main_type
    ):
        """Test case with a dot in filename."""
        # mock directory structure
        mocked_is_file.return_value = True
        mocked_rglob.return_value = (
            item
            for item in [
                Path("directory/file0.ass"),
                Path("directory/file0.extra.ass"),
                Path("directory/file0.mkv"),
            ]
        )
        mocked_get_main_type.side_effect = get_main_type_mock

        # call the function
        with self.assertLogs("dakara_feeder.directory", "DEBUG") as logger:
            listing = list_directory(Path("directory"))

        # check the structure
        self.assertEqual(len(listing), 1)
        self.assertCountEqual(
            [SongPaths(Path("file0.mkv"), subtitle=Path("file0.ass"))],
            listing,
        )

        # check the logger was called
        self.assertListEqual(
            logger.output,
            [
                "DEBUG:dakara_feeder.directory:Listing 'directory'",
                "DEBUG:dakara_feeder.directory:Listed 3 files",
                "DEBUG:dakara_feeder.directory:Found 1 different videos",
            ],
        )


class ListDirectoryIntegrationTestCase(TestCase):
    """Integration test for the directory lister."""

    def test_list_directory(self):
        """Test to list a directory using test ressource dummy files."""
        # call the function
        with TemporaryDirectory() as temp:
            # copy required files
            with as_file(files("tests.resources.media").joinpath("dummy.ass")) as file:
                copy(file, temp)

            with as_file(files("tests.resources.media").joinpath("dummy.mkv")) as file:
                copy(file, temp)

            with self.assertLogs("dakara_feeder.directory", "DEBUG"):
                listing = list_directory(Path(temp))

        # check the structure
        self.assertEqual(len(listing), 1)
        self.assertEqual(
            SongPaths(Path("dummy.mkv"), subtitle=Path("dummy.ass")), listing[0]
        )


class GetMainTypeTestCase(TestCase):
    """Test MIME can be guessed successfully."""

    def test_video(self):
        """Test the common video files."""
        with as_file(files("tests.resources.filetype").joinpath("file.avi")) as file:
            self.assertEqual(get_main_type(file), "video")

        with as_file(files("tests.resources.filetype").joinpath("file.mkv")) as file:
            self.assertEqual(get_main_type(file), "video")

        with as_file(
            files("tests.resources.filetype").joinpath("file_upper.MKV")
        ) as file:
            self.assertEqual(get_main_type(file), "video")

        with as_file(files("tests.resources.filetype").joinpath("file.mp4")) as file:
            self.assertEqual(get_main_type(file), "video")

    def test_audio(self):
        """Test the common audio files."""
        with as_file(files("tests.resources.filetype").joinpath("file.flac")) as file:
            self.assertEqual(get_main_type(file), "audio")

        with as_file(files("tests.resources.filetype").joinpath("file.mp3")) as file:
            self.assertEqual(get_main_type(file), "audio")

        with as_file(files("tests.resources.filetype").joinpath("file.ogg")) as file:
            self.assertEqual(get_main_type(file), "audio")

    def test_subtitle(self):
        """Test the common subtitles files."""
        with as_file(files("tests.resources.filetype").joinpath("file.ass")) as file:
            self.assertIsNone(get_main_type(file))

        with as_file(files("tests.resources.filetype").joinpath("file.ssa")) as file:
            self.assertIsNone(get_main_type(file))

        with as_file(files("tests.resources.filetype").joinpath("file.srt")) as file:
            self.assertIsNone(get_main_type(file))


@patch("dakara_feeder.directory.get_main_type", autospec=True)
class GroupByTypeTestCase(TestCase):
    """Test the group_by_type function."""

    def test_one_video_one_audio_one_subtitle(self, mocked_get_main_type):
        """Test to group one video, one audio and one subtitle."""
        mocked_get_main_type.side_effect = get_main_type_mock
        results = group_by_type(
            [Path("video.mp4"), Path("subtitle.ass"), Path("audio.ogg")],
            Path("directory"),
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0],
            SongPaths(
                Path("video.mp4"),
                audio=Path("audio.ogg"),
                subtitle=Path("subtitle.ass"),
            ),
        )

    def test_one_video_no_subtitle(self, mocked_get_main_type):
        """Test to group one video and no subtitle."""
        mocked_get_main_type.side_effect = get_main_type_mock
        results = group_by_type([Path("video.mp4")], Path("directory"))

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], SongPaths(Path("video.mp4")))

    def test_one_video_one_subtitle_plus_others(self, mocked_get_main_type):
        """Test to group one video, one subtitle and other files."""
        mocked_get_main_type.side_effect = get_main_type_mock
        results = group_by_type(
            [
                Path("video.mp4"),
                Path("subtitle.ass"),
                Path("other.other"),
                Path("other.kara"),
            ],
            Path("directory"),
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0],
            SongPaths(
                Path("video.mp4"),
                subtitle=Path("subtitle.ass"),
                others=[Path("other.other"), Path("other.kara")],
            ),
        )

    def test_one_video_two_subtitles(self, mocked_get_main_type):
        """Test to group one video and two subtitles."""
        mocked_get_main_type.side_effect = get_main_type_mock
        with self.assertLogs("dakara_feeder.directory") as logger:
            results = group_by_type(
                [Path("video.mp4"), Path("subtitles.ass"), Path("subtitles.ssa")],
                Path("directory"),
            )

        self.assertEqual(len(results), 0)

        self.assertListEqual(
            logger.output,
            [
                "WARNING:dakara_feeder.directory:"
                "More than one subtitle for video 'video.mp4'"
            ],
        )

    def test_one_video_two_audios(self, mocked_get_main_type):
        """Test to group one video and two audio files."""
        mocked_get_main_type.side_effect = get_main_type_mock
        with self.assertLogs("dakara_feeder.directory") as logger:
            results = group_by_type(
                [Path("video.mp4"), Path("audio.ogg"), Path("audio.flac")],
                Path("directory"),
            )

        self.assertEqual(len(results), 0)

        self.assertListEqual(
            logger.output,
            [
                "WARNING:dakara_feeder.directory:"
                "More than one audio file for video 'video.mp4'"
            ],
        )

    def test_no_video_no_subtitle_other(self, mocked_get_main_type):
        """Test to group no video, no subtitle and one other file."""
        mocked_get_main_type.side_effect = get_main_type_mock
        results = group_by_type([Path("other.kara")], Path("directory"))

        self.assertEqual(len(results), 0)

    def test_two_videos_one_subtitle(self, mocked_get_main_type):
        """Test to group two videos and one subtitle."""
        mocked_get_main_type.side_effect = get_main_type_mock
        results = group_by_type(
            [Path("video.mp4"), Path("video.mkv"), Path("subtitle.ass")],
            Path("directory"),
        )

        self.assertEqual(len(results), 2)
        self.assertCountEqual(
            results,
            [
                SongPaths(Path("video.mp4"), subtitle=Path("subtitle.ass")),
                SongPaths(Path("video.mkv"), subtitle=Path("subtitle.ass")),
            ],
        )


def get_main_type_mock(path):
    """Detect audio or video type from file extension.

    Used to mock real method which needs actual files to be present.

    Args:
        path (path.Path): Path to a file.

    Returns:
        str: "video" if file extension is "mp4" or "mkv",
        "audio" if file extension is "ogg" or "flac",
        None otherwise.
    """
    ext = path.suffix

    if ext in [".mp4", ".mkv"]:
        return "video"
    if ext in [".ogg", ".flac"]:
        return "audio"

    return None
