from datetime import timedelta
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from dakara_feeder.directory import SongPaths
from dakara_feeder.feeder.songs import KaraFolderNotFound, SongsFeeder
from dakara_feeder.metadata import FFProbeMetadataParser
from dakara_feeder.song import BaseSong
from dakara_feeder.subtitle.parsing import Pysubs2SubtitleParser


@patch("dakara_feeder.feeder.songs.HTTPClientDakara", autospec=True)
class SongsFeederTestCase(TestCase):
    """Test the feeder class."""

    def setUp(self):
        # create base config
        self.config = {"server": {}, "kara_folder": "basepath"}

    @patch.object(SongsFeeder, "check_kara_folder_path", autospec=True)
    @patch("dakara_feeder.feeder.songs.get_custom_song", autospec=True)
    def test_load_no_song_class(
        self,
        mocked_get_custom_song,
        mocked_check_kara_folder_path,
        mocked_http_client_class,
    ):
        """Test to run side-effect tasks."""
        # create the object
        feeder = SongsFeeder(self.config, progress=False)

        # pre assert
        self.assertIs(feeder.song_class, BaseSong)

        # call the method
        feeder.load()

        # post assert
        self.assertIs(feeder.song_class, BaseSong)

        # assert the call
        mocked_get_custom_song.assert_not_called()
        mocked_check_kara_folder_path.assert_called_with(feeder)
        mocked_http_client_class.return_value.authenticate.assert_called_with()

    @patch.object(SongsFeeder, "check_kara_folder_path", autospec=True)
    @patch("dakara_feeder.feeder.songs.get_custom_song", autospec=True)
    def test_load_with_song_class(
        self,
        mocked_get_custom_song,
        mocked_check_kara_folder_path,
        mocked_http_client_class,
    ):
        """Test to run side-effect tasks."""

        class MySong(BaseSong):
            pass

        # prepare mocks
        mocked_get_custom_song.return_value = MySong

        # create the config
        config = {
            "server": {},
            "kara_folder": "basepath",
            "custom_song_class": "module.MySong",
        }

        # create the object
        feeder = SongsFeeder(config, progress=False)

        # pre assert
        self.assertIs(feeder.song_class, BaseSong)

        # call the method
        feeder.load()

        # post assert
        self.assertIs(feeder.song_class, MySong)

        # assert the call
        mocked_get_custom_song.assert_called_with("module.MySong")

    @patch.object(Path, "is_dir", autospec=True)
    def test_check_kara_folder_path_exists(
        self, mocked_is_dir, mocked_http_client_class
    ):
        """Test to check when the kara folder exists."""
        # setup the mock
        mocked_is_dir.return_value = True

        # create the object
        feeder = SongsFeeder(self.config)

        # call the method
        feeder.check_kara_folder_path()

        # assert the call
        mocked_is_dir.assert_called_with(Path("basepath"))

    @patch.object(Path, "is_dir", autospec=True)
    def test_check_kara_folder_path_not_exists(
        self, mocked_is_dir, mocked_http_client_class
    ):
        """Test to check when the kara folder does not exists."""
        # setup the mock
        mocked_is_dir.return_value = False

        # create the object
        feeder = SongsFeeder(self.config)

        # call the method
        with self.assertRaisesRegex(
            KaraFolderNotFound, "Karaoke folder 'basepath' does not exist"
        ):
            feeder.check_kara_folder_path()

    @patch.object(Pysubs2SubtitleParser, "parse", autospec=True)
    @patch.object(FFProbeMetadataParser, "parse", autospec=True)
    @patch("dakara_feeder.feeder.songs.list_directory", autospec=True)
    def test_feed(
        self,
        mocked_list_directory,
        mocked_metadata_parse,
        mocked_subtitle_parse,
        mocked_http_client_class,
    ):
        """Test to feed."""
        # create the mocks
        mocked_http_client_class.return_value.retrieve_songs.return_value = [
            {"id": 0, "path": Path("directory_0/song_0.mp4")},
            {"id": 1, "path": Path("directory_1/music_1.mp4")},
        ]
        mocked_http_client_class.return_value.prune_artists.return_value = 2
        mocked_http_client_class.return_value.prune_works.return_value = 1
        mocked_list_directory.return_value = [
            SongPaths(Path("directory_0/song_0.mp4")),
            SongPaths(
                Path("directory_2/song_2.mp4"),
                subtitle=Path("directory_2/song_2.ass"),
            ),
        ]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )
        mocked_metadata_parse.return_value.get_audio_tracks_count.return_value = 1
        mocked_subtitle_parse.return_value.get_lyrics.return_value = "lyri lyri"

        # create the object
        feeder = SongsFeeder(self.config, progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.feeder.songs", "DEBUG") as logger_feeder:
            with self.assertLogs("dakara_base.progress_bar") as logger_progress:
                feeder.feed()

        # assert the mocked calls
        mocked_http_client_class.return_value.retrieve_songs.assert_called_with()
        mocked_list_directory.assert_called_with(Path("basepath"))
        mocked_http_client_class.return_value.post_song.assert_called_with(
            [
                {
                    "title": "song_2",
                    "filename": "song_2.mp4",
                    "directory": "directory_2",
                    "duration": 1,
                    "has_instrumental": False,
                    "artists": [],
                    "works": [],
                    "tags": [],
                    "version": "",
                    "detail": "",
                    "detail_video": "",
                    "lyrics": "lyri lyri",
                }
            ]
        )
        mocked_http_client_class.return_value.delete_song.assert_called_with(1)
        mocked_http_client_class.return_value.prune_artists.assert_called_with()
        mocked_http_client_class.return_value.prune_works.assert_called_with()
        mocked_subtitle_parse.assert_called_with(
            Path("basepath/directory_2/song_2.ass")
        )
        mocked_subtitle_parse.return_value.get_lyrics.assert_called_with()

        self.assertListEqual(
            logger_feeder.output,
            [
                "INFO:dakara_feeder.feeder.songs:Found 2 songs in server",
                "INFO:dakara_feeder.feeder.songs:Found 2 songs in local directory",
                "INFO:dakara_feeder.feeder.songs:Found 1 songs to add",
                "INFO:dakara_feeder.feeder.songs:Found 1 songs to delete",
                "INFO:dakara_feeder.feeder.songs:Found 0 songs to update",
                "INFO:dakara_feeder.feeder.songs:Deleted 2 artists without songs "
                "on server",
                "INFO:dakara_feeder.feeder.songs:Deleted 1 works without songs "
                "on server",
            ],
        )
        self.assertListEqual(
            logger_progress.output,
            [
                "INFO:dakara_base.progress_bar:Parsing songs to add",
                "INFO:dakara_base.progress_bar:Uploading added songs",
                "INFO:dakara_base.progress_bar:Deleting removed songs",
            ],
        )

    @patch.object(FFProbeMetadataParser, "parse", autospec=True)
    @patch("dakara_feeder.feeder.songs.list_directory", autospec=True)
    def test_renamed_file(
        self, mocked_list_directory, mocked_metadata_parse, mocked_http_client_class
    ):
        """Test feed when a file has been renamed."""
        # mock content of server (old files)
        mocked_http_client_class.return_value.retrieve_songs.return_value = [
            {"id": 0, "path": Path("directory_0/song.mp4")},
            {"id": 1, "path": Path("directory_1/music.mp4")},
        ]
        mocked_http_client_class.return_value.prune_artists.return_value = 0
        mocked_http_client_class.return_value.prune_works.return_value = 0

        # mock content of file system (new files)
        # Simulate file music.mp4 renamed to musics.mp4
        mocked_list_directory.return_value = [
            SongPaths(Path("directory_0/song.mp4")),
            SongPaths(Path("directory_1/musics.mp4")),
        ]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )
        mocked_metadata_parse.return_value.get_audio_tracks_count.return_value = 1

        # create the object
        feeder = SongsFeeder(self.config, progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.feeder.songs", "DEBUG") as logger:
            with self.assertLogs("dakara_base.progress_bar"):
                feeder.feed()

        # assert the mocked calls
        mocked_http_client_class.return_value.retrieve_songs.assert_called_with()
        mocked_list_directory.assert_called_with(Path("basepath"))
        mocked_http_client_class.return_value.put_song.assert_called_with(
            1,
            {
                "title": "musics",
                "filename": "musics.mp4",
                "directory": "directory_1",
                "duration": 1,
                "has_instrumental": False,
                "artists": [],
                "works": [],
                "tags": [],
                "version": "",
                "detail": "",
                "detail_video": "",
                "lyrics": "",
            },
        )
        self.assertListEqual(
            logger.output,
            [
                "INFO:dakara_feeder.feeder.songs:Found 2 songs in server",
                "INFO:dakara_feeder.feeder.songs:Found 2 songs in local directory",
                "INFO:dakara_feeder.feeder.songs:Found 0 songs to add",
                "INFO:dakara_feeder.feeder.songs:Found 0 songs to delete",
                "INFO:dakara_feeder.feeder.songs:Found 1 songs to update",
                "INFO:dakara_feeder.feeder.songs:Deleted 0 artists without songs "
                "on server",
                "INFO:dakara_feeder.feeder.songs:Deleted 0 works without songs "
                "on server",
            ],
        )

    @patch.object(Pysubs2SubtitleParser, "parse", autospec=True)
    @patch.object(FFProbeMetadataParser, "parse", autospec=True)
    @patch("dakara_feeder.feeder.songs.list_directory", autospec=True)
    def test_feed_with_force_update(
        self,
        mocked_list_directory,
        mocked_metadata_parse,
        mocked_subtitle_parse,
        mocked_http_client_class,
    ):
        """Test to feed."""
        # create the mocks
        mocked_http_client_class.return_value.retrieve_songs.return_value = [
            {"id": 1, "path": Path("music_1.mp4")}
        ]
        mocked_http_client_class.return_value.prune_artists.return_value = 0
        mocked_http_client_class.return_value.prune_works.return_value = 0
        mocked_list_directory.return_value = [
            SongPaths(Path("music_1.mp4"), subtitle=Path("music_1.ass"))
        ]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )
        mocked_metadata_parse.return_value.get_audio_tracks_count.return_value = 1
        mocked_subtitle_parse.return_value.get_lyrics.return_value = "lyri lyri"

        # create the object
        feeder = SongsFeeder(self.config, force_update=True, progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.feeder.songs", "DEBUG") as logger:
            with self.assertLogs("dakara_base.progress_bar"):
                feeder.feed()

        # assert the mocked calls
        mocked_http_client_class.return_value.retrieve_songs.assert_called_with()
        mocked_list_directory.assert_called_with(Path("basepath"))
        mocked_http_client_class.return_value.put_song.assert_called_with(
            1,
            {
                "title": "music_1",
                "filename": "music_1.mp4",
                "directory": "",
                "duration": 1,
                "has_instrumental": False,
                "artists": [],
                "works": [],
                "tags": [],
                "version": "",
                "detail": "",
                "detail_video": "",
                "lyrics": "lyri lyri",
            },
        )

        self.assertListEqual(
            logger.output,
            [
                "INFO:dakara_feeder.feeder.songs:Found 1 songs in server",
                "INFO:dakara_feeder.feeder.songs:Found 1 songs in local directory",
                "INFO:dakara_feeder.feeder.songs:Found 0 songs to add",
                "INFO:dakara_feeder.feeder.songs:Found 0 songs to delete",
                "INFO:dakara_feeder.feeder.songs:Found 1 songs to update",
                "INFO:dakara_feeder.feeder.songs:Deleted 0 artists without songs "
                "on server",
                "INFO:dakara_feeder.feeder.songs:Deleted 0 works without songs "
                "on server",
            ],
        )

    @patch.object(Pysubs2SubtitleParser, "parse", autospec=True)
    @patch.object(FFProbeMetadataParser, "parse", autospec=True)
    @patch("dakara_feeder.feeder.songs.list_directory", autospec=True)
    def test_feed_with_no_prune(
        self,
        mocked_list_directory,
        mocked_metadata_parse,
        mocked_subtitle_parse,
        mocked_http_client_class,
    ):
        """Test to feed without prune artists and works without songs."""
        # create the mocks
        mocked_http_client_class.return_value.retrieve_songs.return_value = [
            {"id": 0, "path": Path("directory_0/song_0.mp4")}
        ]
        mocked_list_directory.return_value = [SongPaths(Path("directory_0/song_0.mp4"))]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )
        mocked_subtitle_parse.return_value.get_lyrics.return_value = "lyri lyri"

        # create the object
        feeder = SongsFeeder(self.config, progress=False, prune=False)

        # call the method
        with self.assertLogs("dakara_feeder.feeder.songs", "DEBUG") as logger_feeder:
            feeder.feed()

        # assert the mocked calls
        mocked_http_client_class.return_value.retrieve_songs.assert_called_with()
        mocked_list_directory.assert_called_with(Path("basepath"))
        mocked_http_client_class.return_value.post_song.assert_not_called()
        mocked_http_client_class.return_value.delete_song.assert_not_called()
        mocked_http_client_class.return_value.prune_artists.assert_not_called()
        mocked_http_client_class.return_value.prune_works.assert_not_called()
        mocked_subtitle_parse.assert_not_called()

        self.assertListEqual(
            logger_feeder.output,
            [
                "INFO:dakara_feeder.feeder.songs:Found 1 songs in server",
                "INFO:dakara_feeder.feeder.songs:Found 1 songs in local directory",
                "INFO:dakara_feeder.feeder.songs:Found 0 songs to add",
                "INFO:dakara_feeder.feeder.songs:Found 0 songs to delete",
                "INFO:dakara_feeder.feeder.songs:Found 0 songs to update",
            ],
        )

    @patch.object(Pysubs2SubtitleParser, "parse", autospec=True)
    @patch.object(FFProbeMetadataParser, "parse", autospec=True)
    @patch("dakara_feeder.feeder.songs.list_directory", autospec=True)
    def test_create_two_songs(
        self,
        mocked_list_directory,
        mocked_metadata_parse,
        mocked_subtitle_parse,
        mocked_http_client_class,
    ):
        """Test to create two songs."""
        # create the mocks
        mocked_http_client_class.return_value.retrieve_songs.return_value = []
        mocked_http_client_class.return_value.prune_artists.return_value = 0
        mocked_http_client_class.return_value.prune_works.return_value = 0
        mocked_list_directory.return_value = [
            SongPaths(Path("directory_0/song_0.mp4")),
            SongPaths(Path("directory_1/song_1.mp4")),
        ]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )
        mocked_metadata_parse.return_value.get_audio_tracks_count.return_value = 1

        # create the object
        feeder = SongsFeeder(self.config, progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.feeder.songs", "DEBUG") as logger:
            with self.assertLogs("dakara_base.progress_bar"):
                feeder.feed()

        # assert the mocked calls
        mocked_http_client_class.return_value.retrieve_songs.assert_called_with()
        mocked_list_directory.assert_called_with(Path("basepath"))
        songs = [
            {
                "title": "song_0",
                "filename": "song_0.mp4",
                "directory": "directory_0",
                "duration": 1,
                "has_instrumental": False,
                "artists": [],
                "works": [],
                "tags": [],
                "version": "",
                "detail": "",
                "detail_video": "",
                "lyrics": "",
            },
            {
                "title": "song_1",
                "filename": "song_1.mp4",
                "directory": "directory_1",
                "duration": 1,
                "has_instrumental": False,
                "artists": [],
                "works": [],
                "tags": [],
                "version": "",
                "detail": "",
                "detail_video": "",
                "lyrics": "",
            },
        ]
        post_calls = mocked_http_client_class.return_value.post_song.mock_calls

        # check called once
        self.assertEqual(len(post_calls), 1)

        # check one positional argument
        (
            _,
            args,
            kwargs,
        ) = post_calls[0]
        self.assertEqual(len(args), 1)
        self.assertEqual(len(kwargs), 0)

        # check first arguement is the list of the two expected songs
        self.assertCountEqual(args[0], songs)
        mocked_http_client_class.return_value.delete_song.assert_not_called()

        self.assertListEqual(
            logger.output,
            [
                "INFO:dakara_feeder.feeder.songs:Found 0 songs in server",
                "INFO:dakara_feeder.feeder.songs:Found 2 songs in local directory",
                "INFO:dakara_feeder.feeder.songs:Found 2 songs to add",
                "INFO:dakara_feeder.feeder.songs:Found 0 songs to delete",
                "INFO:dakara_feeder.feeder.songs:Found 0 songs to update",
                "INFO:dakara_feeder.feeder.songs:Deleted 0 artists without songs "
                "on server",
                "INFO:dakara_feeder.feeder.songs:Deleted 0 works without songs "
                "on server",
            ],
        )

    @patch.object(FFProbeMetadataParser, "parse", autospec=True)
    @patch("dakara_feeder.feeder.songs.list_directory", autospec=True)
    def test_feed_custom_song_class(
        self, mocked_list_directory, mocked_metadata_parse, mocked_http_client_class
    ):
        """Test to feed using a custom song class."""
        # create the mocks
        mocked_http_client_class.return_value.retrieve_songs.return_value = []
        mocked_http_client_class.return_value.prune_artists.return_value = 0
        mocked_http_client_class.return_value.prune_works.return_value = 0
        mocked_list_directory.return_value = [SongPaths(Path("directory_0/song_0.mp4"))]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )
        mocked_metadata_parse.return_value.get_audio_tracks_count.return_value = 2

        class Song(BaseSong):
            def get_artists(self):
                return ["artist1", "artist2"]

        # create the config
        config = {
            "server": {},
            "custom_song_class": "custom_song_module",
            "kara_folder": "basepath",
        }

        # create the object
        feeder = SongsFeeder(config, progress=False)
        feeder.song_class = Song

        # call the method
        with self.assertLogs("dakara_feeder.feeder.songs", "DEBUG"):
            with self.assertLogs("dakara_base.progress_bar"):
                feeder.feed()

        # assert the mocked calls
        mocked_http_client_class.return_value.post_song.assert_called_with(
            [
                {
                    "title": "song_0",
                    "filename": "song_0.mp4",
                    "directory": "directory_0",
                    "duration": 1,
                    "has_instrumental": True,
                    "artists": ["artist1", "artist2"],
                    "works": [],
                    "tags": [],
                    "version": "",
                    "detail": "",
                    "detail_video": "",
                    "lyrics": "",
                }
            ]
        )

    @patch.object(Pysubs2SubtitleParser, "parse", autospec=True)
    @patch.object(FFProbeMetadataParser, "parse", autospec=True)
    @patch("dakara_feeder.feeder.songs.list_directory", autospec=True)
    def test_feed_extra_audio_file(
        self,
        mocked_list_directory,
        mocked_metadata_parse,
        mocked_subtitle_parse,
        mocked_http_client_class,
    ):
        """Test to feed a song with an extra audio file."""
        # create the mocks
        mocked_http_client_class.return_value.retrieve_songs.return_value = []
        mocked_list_directory.return_value = [
            SongPaths(
                Path("music_1.mp4"),
                audio=Path("music_1.flac"),
                subtitle=Path("music_1.ass"),
            )
        ]
        mocked_metadata_parse.return_value.get_duration.return_value = timedelta(
            seconds=1
        )
        mocked_metadata_parse.return_value.get_audio_tracks_count.return_value = 1
        mocked_subtitle_parse.return_value.get_lyrics.return_value = "lyri lyri"

        # create the config
        config = {"server": {}, "kara_folder": "basepath"}

        # create the object
        feeder = SongsFeeder(config, progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.feeder.songs", "DEBUG"):
            # with self.assertLogs("dakara_base.progress_bar"):
            feeder.feed()

        # assert the mocked calls
        mocked_http_client_class.return_value.retrieve_songs.assert_called_with()
        mocked_list_directory.assert_called_with(Path("basepath"))
        mocked_http_client_class.return_value.post_song.assert_called_with(
            [
                {
                    "title": "music_1",
                    "filename": "music_1.mp4",
                    "directory": "",
                    "duration": 1,
                    "has_instrumental": True,
                    "artists": [],
                    "works": [],
                    "tags": [],
                    "version": "",
                    "detail": "",
                    "detail_video": "",
                    "lyrics": "lyri lyri",
                }
            ]
        )
