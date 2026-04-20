class Track:
    """
    Base class for any playable continuous audio content.
    """
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str):
        """Initializes base track properties."""
        self.track_id = track_id
        self.title = title
        self.duration_seconds = duration_seconds
        self.genre = genre

    def duration_minutes(self) -> float:
        """Returns the duration of the track in minutes"""
        return self.duration_seconds / 60.0

    def __eq__(self, other) -> bool:
        """Tracks are considered identical if they share the same track_id"""
        if not isinstance(other, Track):
            return False
        return self.track_id == other.track_id


class Song(Track):
    """
    A music track, inherently linked to a specific artist.
    """
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, artist):
        """Initializes a song."""
        super().__init__(track_id, title, duration_seconds, genre)
        self.artist = artist


class SingleRelease(Song):
    """
    A song released as a standalone single.
    """
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, artist, release_date):
        """Initializes a single release with a specific release date."""
        super().__init__(track_id, title, duration_seconds, genre, artist)
        self.release_date = release_date


class AlbumTrack(Song):
    """
    A song that is part of a larger album.
    """
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, artist, track_number: int):
        """Initializes an album track with its specific ordering index."""
        super().__init__(track_id, title, duration_seconds, genre, artist)
        self.track_number = track_number
        self.album = None  # The album this track belongs to


class Podcast(Track):
    """
    An episodic podcast track
    """
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, host: str, description: str = ""):
        """Initializes a podcast episode"""
        super().__init__(track_id, title, duration_seconds, genre)
        self.host = host
        self.description = description


class InterviewEpisode(Podcast):
    """
    A podcast episode featuring a guest interview.
    """
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, host: str, guest: str, description: str = ""):
        """Initializes an interview episode."""
        super().__init__(track_id, title, duration_seconds, genre, host, description)
        self.guest = guest


class NarrativeEpisode(Podcast):
    """
    A narrative or serialized podcast episode identifying season and episode numbers.
    """
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, host: str, season: int, episode_number: int, description: str = ""):
        """Initializes a narrative episode."""
        super().__init__(track_id, title, duration_seconds, genre, host, description)
        self.season = season
        self.episode_number = episode_number


class AudiobookTrack(Track):
    """
    A track representing a chapter or section of an audiobook.
    """
    def __init__(self, track_id: str, title: str, duration_seconds: int, genre: str, author: str, narrator: str):
        """Initializes an audiobook track."""
        super().__init__(track_id, title, duration_seconds, genre)
        self.author = author
        self.narrator = narrator
