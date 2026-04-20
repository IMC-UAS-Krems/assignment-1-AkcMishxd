from typing import List

class Artist:
    """
    Represents an artist on the streaming platform.
    """
    def __init__(self, artist_id: str, name: str, genre: str):
        """Initializes a new Artist."""
        self.artist_id = artist_id
        self.name = name
        self.genre = genre
        self.tracks = []  # List of all tracks created by this artist

    def track_count(self) -> int:
        """Returns the total number of tracks released by this artist."""
        return len(self.tracks)

    def add_track(self, track) -> None:
        """Appends a new track to the artist's discography."""
        self.tracks.append(track)
