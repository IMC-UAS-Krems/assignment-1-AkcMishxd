from typing import List

class Artist:
    def __init__(self, artist_id: str, name: str, genre: str):
        self.artist_id = artist_id
        self.name = name
        self.genre = genre
        self.tracks = []

    def track_count(self) -> int:
        return len(self.tracks)

    def add_track(self, track) -> None:
        self.tracks.append(track)
