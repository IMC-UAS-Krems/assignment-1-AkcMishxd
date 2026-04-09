from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional

from streaming.users import User, PremiumUser, FamilyAccountUser
from streaming.tracks import Track, Song
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

    def track_with_most_distinct_listeners(self) -> Optional[Track]:
        if not self.sessions:
            return None

        track_listeners = defaultdict(set)
        for s in self.sessions:
            track_listeners[s.track].add(s.user.user_id)

        if not track_listeners:
            return None

        best_track = max(track_listeners.keys(), key=lambda t: len(track_listeners[t]))
        return best_track

    def avg_session_duration_by_user_type(self) -> List[Tuple[str, float]]:
        type_durations = defaultdict(list)
        for s in self.sessions:
            type_name = type(s.user).__name__
            type_durations[type_name].append(s.duration_listened_seconds)

        result = []
        for type_name, durations in type_durations.items():
            avg = sum(durations) / len(durations)
            result.append((type_name, avg))

        result.sort(key=lambda x: x[1], reverse=True)
        return result

    def total_listening_time_underage_sub_users_minutes(self, age_threshold: int = 18) -> float:
        total_seconds = 0
        for s in self.sessions:
            if isinstance(s.user, FamilyMember) and s.user.age < age_threshold:
                total_seconds += s.duration_listened_seconds
        return total_seconds / 60.0

    def top_artists_by_listening_time(self, n: int = 5) -> List[Tuple[Artist, float]]:
        artist_seconds = defaultdict(int)
        for s in self.sessions:
            if isinstance(s.track, Song):
                artist_seconds[s.track.artist] += s.duration_listened_seconds

        result = [(artist, seconds / 60.0) for artist, seconds in artist_seconds.items()]
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:n]

    def user_top_genre(self, user_id: str) -> Optional[Tuple[str, float]]:
        user = self.get_user(user_id)
        if not user:
            return None

        genre_seconds = defaultdict(int)
        total_seconds = 0
        for s in self.sessions:
            if s.user.user_id == user_id:
                genre_seconds[s.track.genre] += s.duration_listened_seconds
                total_seconds += s.duration_listened_seconds

        if total_seconds == 0:
            return None

        best_genre = max(genre_seconds.keys(), key=lambda g: genre_seconds[g])
        percentage = (genre_seconds[best_genre] / total_seconds) * 100.0
        return (best_genre, percentage)

    def collaborative_playlists_with_many_artists(self, threshold: int = 3) -> List[CollaborativePlaylist]:
        result = []
        for p in self.playlists.values():
            if isinstance(p, CollaborativePlaylist):
                artists = set()
                for track in p.tracks:
                    if isinstance(track, Song):
                        artists.add(track.artist.artist_id)
                if len(artists) > threshold:
                    result.append(p)
        return result

    def avg_tracks_per_playlist_type(self) -> Dict[str, float]:
        stats = {
            "Playlist": {"count": 0, "tracks": 0},
            "CollaborativePlaylist": {"count": 0, "tracks": 0}
        }

        for p in self.playlists.values():
            if type(p) is Playlist:
                stats["Playlist"]["count"] += 1
                stats["Playlist"]["tracks"] += len(p.tracks)
            elif type(p) is CollaborativePlaylist:
                stats["CollaborativePlaylist"]["count"] += 1
                stats["CollaborativePlaylist"]["tracks"] += len(p.tracks)

        result = {"Playlist": 0.0, "CollaborativePlaylist": 0.0}
        if stats["Playlist"]["count"] > 0:
            result["Playlist"] = stats["Playlist"]["tracks"] / stats["Playlist"]["count"]
        if stats["CollaborativePlaylist"]["count"] > 0:
            result["CollaborativePlaylist"] = stats["CollaborativePlaylist"]["tracks"] / stats["CollaborativePlaylist"]["count"]

        return result

    def users_who_completed_albums(self) -> List[Tuple[User, List[str]]]:
        user_history = defaultdict(set)
        for s in self.sessions:
            user_history[s.user.user_id].add(s.track.track_id)

        valid_albums = [a for a in self.albums.values() if a.tracks]
        
        final_result = []
        for user in self.all_users():
            completed_titles = []
            for a in valid_albums:
                album_track_ids = set(a.track_ids())
                if album_track_ids.issubset(user_history[user.user_id]):
                    completed_titles.append(a.title)
                    
            if completed_titles:
                final_result.append((user, completed_titles))

        return final_result
