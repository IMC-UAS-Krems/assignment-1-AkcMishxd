from datetime import datetime, timedelta
from collections import defaultdict
from typing import List, Tuple, Dict, Optional

from streaming.users import User, FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.tracks import Track, Song, Podcast, AudiobookTrack
from streaming.artists import Artist
from streaming.albums import Album
from streaming.playlists import Playlist, CollaborativePlaylist
from streaming.sessions import ListeningSession


class StreamingPlatform:
    def __init__(self, name: str = "MyPlatform"):
        self.name = name
        self.tracks: Dict[str, Track] = {}
        self.users: Dict[str, User] = {}
        self.artists: Dict[str, Artist] = {}
        self.albums: Dict[str, Album] = {}
        self.playlists: Dict[str, Playlist] = {}
        self.sessions: List[ListeningSession] = []

    def add_track(self, track: Track) -> None:
        self.tracks[track.track_id] = track

    def get_track(self, track_id: str) -> Optional[Track]:
        return self.tracks.get(track_id)

    def all_tracks(self) -> List[Track]:
        return list(self.tracks.values())

    def add_user(self, user: User) -> None:
        self.users[user.user_id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def all_users(self) -> List[User]:
        return list(self.users.values())

    def add_artist(self, artist: Artist) -> None:
        self.artists[artist.artist_id] = artist

    def get_artist(self, artist_id: str) -> Optional[Artist]:
        return self.artists.get(artist_id)

    def add_album(self, album: Album) -> None:
        self.albums[album.album_id] = album

    def get_album(self, album_id: str) -> Optional[Album]:
        return self.albums.get(album_id)

    def add_playlist(self, playlist: Playlist) -> None:
        self.playlists[playlist.playlist_id] = playlist

    def record_session(self, session: ListeningSession) -> None:
        self.sessions.append(session)
        if session not in session.user.sessions:
            session.user.add_session(session)

    # ---------------- 10 Query Methods ------------------

    def total_listening_time_minutes(self, start: datetime, end: datetime) -> float:
        total_seconds = 0
        for s in self.sessions:
            if start <= s.timestamp <= end:
                total_seconds += s.duration_listened_seconds
        return total_seconds / 60.0

    def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
        premium_users = [u for u in self.all_users() if type(u) is PremiumUser]
        if not premium_users:
            return 0.0

        if not self.sessions:
            return 0.0

        max_ts = max(s.timestamp for s in self.sessions)
        cutoff = max_ts - timedelta(days=days)

        total_unique = 0
        for u in premium_users:
            unique_tracks = set()
            for s in self.sessions:
                if s.user.user_id == u.user_id and s.timestamp >= cutoff:
                    unique_tracks.add(s.track.track_id)
            total_unique += len(unique_tracks)

        return float(total_unique) / len(premium_users)

    
