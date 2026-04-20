class Playlist:
    """
    A personal playlist created by a user, containing an ordered collection of tracks
    """
    def __init__(self, playlist_id: str, name: str, owner):
        """Initializes a new Playlist."""
        self.playlist_id = playlist_id
        self.name = name
        self.owner = owner
        self.tracks = []  # Tracks in the playlist

    def add_track(self, track) -> None:
        """Adds a track to the playlist if it is not already present."""
        if track not in self.tracks:
            self.tracks.append(track)

    def remove_track(self, track_id: str) -> None:
        """Removes a track from the playlist by its ID."""
        # Filter out the track with the given track Id
        self.tracks = [t for t in self.tracks if t.track_id != track_id]

    def total_duration_seconds(self) -> int:
        """Calculates the total duration of all tracks in the playlist"""
        return sum(t.duration_seconds for t in self.tracks)


class CollaborativePlaylist(Playlist):
    """
    A playlist that allows multiple users to contribute tracks.
    """
    def __init__(self, playlist_id: str, name: str, owner):
        """Initializes a new CollaborativePlaylist, setting the owner as the first contributor."""
        super().__init__(playlist_id, name, owner)
        self.contributors = [owner]  # The owner is inherently a contributor

    def add_contributor(self, user) -> None:
        """Adds a new user to the list of contributors if not already present."""
        if user not in self.contributors:
            self.contributors.append(user)

    def remove_contributor(self, user) -> None:
        """Removes a contributor from the playlist. The owner cannot be removed."""
        # Prevent removing the original owner
        if user != self.owner and user in self.contributors:
            self.contributors.remove(user)
