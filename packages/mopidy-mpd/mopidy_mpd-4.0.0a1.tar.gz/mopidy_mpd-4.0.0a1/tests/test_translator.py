import unittest

from mopidy.models import Album, Artist, Playlist, TlTrack, Track

from mopidy_mpd import translator
from mopidy_mpd.protocol import tagtype_list
from tests import path_utils


class TrackMpdFormatTest(unittest.TestCase):
    track = Track(
        uri="à uri",
        artists=[Artist(name="an artist"), Artist(name="yet another artist")],
        name="a nàme",
        album=Album(
            name="an album",
            num_tracks=13,
            artists=[
                Artist(name="an other artist"),
                Artist(name="still another artist"),
            ],
            uri="urischeme:àlbum:12345",
        ),
        track_no=7,
        composers=[Artist(name="a composer"), Artist(name="another composer")],
        performers=[
            Artist(name="a performer"),
            Artist(name="another performer"),
        ],
        genre="a genre",
        date="1977-01-01",
        disc_no=1,
        comment="a comment",
        length=137000,
    )

    def setUp(self):
        self.media_dir = "/dir/subdir"
        path_utils.mtime.set_fake_time(1234567)

    def tearDown(self):
        path_utils.mtime.undo_fake()

    def test_track_to_mpd_format_for_empty_track(self):
        result = translator.track_to_mpd_format(
            Track(uri="a uri", length=137000), tagtype_list.TAGTYPE_LIST
        )
        assert ("file", "a uri") in result
        assert ("Time", 137) in result
        assert ("Artist", "") not in result
        assert ("Title", "") not in result
        assert ("Album", "") not in result
        assert ("Track", 0) not in result
        assert ("Date", "") not in result
        assert len(result) == 2

    def test_track_to_mpd_format_with_position(self):
        result = translator.track_to_mpd_format(
            Track(), tagtype_list.TAGTYPE_LIST, position=1
        )
        assert ("Pos", 1) not in result

    def test_track_to_mpd_format_with_tlid(self):
        result = translator.track_to_mpd_format(
            TlTrack(1, Track()), tagtype_list.TAGTYPE_LIST
        )
        assert ("Id", 1) not in result

    def test_track_to_mpd_format_with_position_and_tlid(self):
        result = translator.track_to_mpd_format(
            TlTrack(2, Track(uri="a uri")),
            tagtype_list.TAGTYPE_LIST,
            position=1,
        )
        assert ("Pos", 1) in result
        assert ("Id", 2) in result

    def test_track_to_mpd_format_for_nonempty_track(self):
        result = translator.track_to_mpd_format(
            TlTrack(122, self.track), tagtype_list.TAGTYPE_LIST, position=9
        )
        assert ("file", "à uri") in result
        assert ("Time", 137) in result
        assert ("Artist", "an artist") in result
        assert ("Artist", "yet another artist") in result
        assert ("Title", "a nàme") in result
        assert ("Album", "an album") in result
        assert ("AlbumArtist", "an other artist") in result
        assert ("AlbumArtist", "still another artist") in result
        assert ("Composer", "a composer") in result
        assert ("Composer", "another composer") in result
        assert ("Performer", "a performer") in result
        assert ("Performer", "another performer") in result
        assert ("Genre", "a genre") in result
        assert ("Track", "7/13") in result
        assert ("Date", "1977-01-01") in result
        assert ("Disc", 1) in result
        assert ("Pos", 9) in result
        assert ("Id", 122) in result
        assert ("X-AlbumUri", "urischeme:àlbum:12345") in result
        assert ("Comment", "a comment") not in result
        assert len(result) == 19

    def test_track_to_mpd_format_with_last_modified(self):
        track = self.track.replace(last_modified=995303899000)
        result = translator.track_to_mpd_format(track, tagtype_list.TAGTYPE_LIST)
        assert ("Last-Modified", "2001-07-16T17:18:19Z") in result

    def test_track_to_mpd_format_with_last_modified_of_zero(self):
        track = self.track.replace(last_modified=0)
        result = translator.track_to_mpd_format(track, tagtype_list.TAGTYPE_LIST)
        keys = [k for k, v in result]
        assert "Last-Modified" not in keys

    def test_track_to_mpd_format_musicbrainz_trackid(self):
        track = self.track.replace(
            musicbrainz_id="715d581b-ef70-46d5-984b-e2c1d8feb8a0"
        )
        result = translator.track_to_mpd_format(track, tagtype_list.TAGTYPE_LIST)
        assert ("MUSICBRAINZ_TRACKID", "715d581b-ef70-46d5-984b-e2c1d8feb8a0") in result

    def test_track_to_mpd_format_musicbrainz_albumid(self):
        album = self.track.album.replace(
            musicbrainz_id="715d581b-ef70-46d5-984b-e2c1d8feb8a0"
        )
        track = self.track.replace(album=album)
        result = translator.track_to_mpd_format(track, tagtype_list.TAGTYPE_LIST)
        assert ("MUSICBRAINZ_ALBUMID", "715d581b-ef70-46d5-984b-e2c1d8feb8a0") in result

    def test_track_to_mpd_format_musicbrainz_albumartistid(self):
        artist = next(iter(self.track.artists)).replace(
            musicbrainz_id="715d581b-ef70-46d5-984b-e2c1d8feb8a0"
        )
        album = self.track.album.replace(artists=[artist])
        track = self.track.replace(album=album)
        result = translator.track_to_mpd_format(track, tagtype_list.TAGTYPE_LIST)
        assert (
            "MUSICBRAINZ_ALBUMARTISTID",
            "715d581b-ef70-46d5-984b-e2c1d8feb8a0",
        ) in result

    def test_track_to_mpd_format_musicbrainz_artistid(self):
        artist = next(iter(self.track.artists)).replace(
            musicbrainz_id="715d581b-ef70-46d5-984b-e2c1d8feb8a0"
        )
        track = self.track.replace(artists=[artist])
        result = translator.track_to_mpd_format(track, tagtype_list.TAGTYPE_LIST)
        assert (
            "MUSICBRAINZ_ARTISTID",
            "715d581b-ef70-46d5-984b-e2c1d8feb8a0",
        ) in result

    def test_concat_multi_values(self):
        artists = [Artist(name="ABBA"), Artist(name="Beatles")]
        translated = translator.concat_multi_values(artists, "name")
        assert translated == "ABBA;Beatles"

    def test_concat_multi_values_artist_with_no_name(self):
        artists = [Artist(name=None)]
        translated = translator.concat_multi_values(artists, "name")
        assert translated == ""

    def test_concat_multi_values_artist_with_no_musicbrainz_id(self):
        artists = [Artist(name="Jah Wobble")]
        translated = translator.concat_multi_values(artists, "musicbrainz_id")
        assert translated == ""

    def test_track_to_mpd_format_with_stream_title(self):
        result = translator.track_to_mpd_format(
            self.track, tagtype_list.TAGTYPE_LIST, stream_title="foo"
        )
        assert ("Name", "a nàme") in result
        assert ("Title", "foo") in result

    def test_track_to_mpd_format_with_empty_stream_title(self):
        result = translator.track_to_mpd_format(
            self.track, tagtype_list.TAGTYPE_LIST, stream_title=""
        )
        assert ("Name", "a nàme") in result
        assert ("Title", "") not in result

    def test_track_to_mpd_format_with_stream_and_no_track_name(self):
        track = self.track.replace(name=None)
        result = translator.track_to_mpd_format(
            track, tagtype_list.TAGTYPE_LIST, stream_title="foo"
        )
        assert ("Name", "") not in result
        assert ("Title", "foo") in result

    def test_track_to_mpd_client_filtered(self):
        configured_tagtypes = [
            "Artist",
            "Album",
            "Title",
            "Track",
            "Name",
            "Genre",
        ]
        result = translator.track_to_mpd_format(
            TlTrack(122, self.track), configured_tagtypes, position=9
        )
        assert ("file", "à uri") in result
        assert ("Time", 137) in result
        assert ("Artist", "an artist") in result
        assert ("Artist", "yet another artist") in result
        assert ("Title", "a nàme") in result
        assert ("Album", "an album") in result
        assert ("Genre", "a genre") in result
        assert ("Track", "7/13") in result
        assert ("Pos", 9) in result
        assert ("Id", 122) in result
        assert len(result) == 10


class PlaylistMpdFormatTest(unittest.TestCase):
    def test_mpd_format(self):
        playlist = Playlist(
            tracks=[
                Track(uri="foo", track_no=1),
                Track(uri="bàr", track_no=2),
                Track(uri="baz", track_no=3),
            ]
        )

        result = translator.playlist_to_mpd_format(playlist, tagtype_list.TAGTYPE_LIST)

        assert result == [
            ("file", "foo"),
            ("Time", 0),
            ("Track", 1),
            ("file", "bàr"),
            ("Time", 0),
            ("Track", 2),
            ("file", "baz"),
            ("Time", 0),
            ("Track", 3),
        ]

    def test_mpd_format_with_range(self):
        playlist = Playlist(
            tracks=[
                Track(uri="foo", track_no=1),
                Track(uri="bàr", track_no=2),
                Track(uri="baz", track_no=3),
            ]
        )

        result = translator.playlist_to_mpd_format(
            playlist, tagtype_list.TAGTYPE_LIST, start=1, end=2
        )

        assert result == [("file", "bàr"), ("Time", 0), ("Track", 2)]
