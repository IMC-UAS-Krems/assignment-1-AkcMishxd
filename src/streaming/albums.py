class Album:
    """
    Represents a music album containing a collection of tracks.
    """
    def __init__(self, album_id: str, title: str, artist, release_year: int):
        """Initializes a new Album."""
        self.album_id = album_id
        self.title = title
        self.artist = artist
        self.release_year = release_year
        self.tracks = []  # List to store AlbumTrack objects in this album

    def add_track(self, track) -> None:
        """
        Adds a track to the album and maintains track numbers in ascending order.
        """
        track.album = self  # Set back-reference from track to this album
        self.tracks.append(track)
        # Sort tracks by track number to keep the correct album sequence
        self.tracks.sort(key=lambda t: t.track_number)

    def track_ids(self) -> set:
        """Returns a set of all unique track Ids in this album."""
        return {t.track_id for t in self.tracks}

    def duration_seconds(self) -> int:
        """Calculates the total duration of the entire album in seconds."""
        # Sum the duration of all consecutive tracks
        return sum(t.duration_seconds for t in self.tracks)
