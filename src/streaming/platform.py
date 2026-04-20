from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional
from collections import defaultdict

from streaming.users import User, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.tracks import Track, Song
from streaming.artists import Artist
from streaming.albums import Album
from streaming.playlists import Playlist, CollaborativePlaylist
from streaming.sessions import ListeningSession


class StreamingPlatform:
    """
    Central platform class that synchronizes all entities and user behavior tracking
    """
    def __init__(self, name: str = "MyPlatform"):
        """Initializes the streaming platform"""
        self.name = name
        self.tracks: Dict[str, Track] = {}
        self.users: Dict[str, User] = {}
        self.artists: Dict[str, Artist] = {}
        self.albums: Dict[str, Album] = {}
        self.playlists: Dict[str, Playlist] = {}
        self.sessions: List[ListeningSession] = []

    # ---------------- Track ------------------
    def add_track(self, track: Track) -> None:
        """Registers a track with the platform"""
        self.tracks[track.track_id] = track

    def get_track(self, track_id: str) -> Optional[Track]:
        """Retrieves a track by its Id"""
        return self.tracks.get(track_id)

    def all_tracks(self) -> List[Track]:
        """Returns a list of all tracks registered on the platform"""
        return list(self.tracks.values())

    # ---------------- User ------------------
    def add_user(self, user: User) -> None:
        """Registers a user with the platform"""
        self.users[user.user_id] = user

    def get_user(self, user_id: str) -> Optional[User]:
        """Retrieves a user by their Id"""
        return self.users.get(user_id)

    def all_users(self) -> List[User]:
        """Returns a list of all users registered on the platform"""
        return list(self.users.values())

    # ---------------- Artist ------------------
    def add_artist(self, artist: Artist) -> None:
        """Registers an artist with the platform"""
        self.artists[artist.artist_id] = artist

    def get_artist(self, artist_id: str) -> Optional[Artist]:
        """Retrieves an artist by their Id"""
        return self.artists.get(artist_id)

    # ---------------- Album ------------------
    def add_album(self, album: Album) -> None:
        """Registers an album with the platform"""
        self.albums[album.album_id] = album

    def get_album(self, album_id: str) -> Optional[Album]:
        """Retrieves an album by its Id"""
        return self.albums.get(album_id)

    # ---------------- Playlist ------------------
    def add_playlist(self, playlist: Playlist) -> None:
        """Registers a playlist with the platform"""
        self.playlists[playlist.playlist_id] = playlist
    # ---------------- Session ------------------
    def record_session(self, session: ListeningSession) -> None:
        """Records a new listening session, updating the global history and user's history"""
        self.sessions.append(session)
        # Ensure the session is recorded for the individual user as well
        if session not in session.user.sessions:
            session.user.add_session(session)

    # ---------------- 10 Query Methods ------------------

    def total_listening_time_minutes(self, start: datetime, end: datetime) -> float:
        """
        Q1: Total Cumulative Listening Time
        Returns the total listening time across all users within a specified timeframe
        """
        total_seconds = 0
        for s in self.sessions:
            if start <= s.timestamp <= end:
                total_seconds += s.duration_listened_seconds
        return total_seconds / 60.0

    def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
        """
        Q2: Average Unique Tracks per Premium User
        Returns the average number of distinct tracks played per premium user in the last X days
        """
        premium_users = [u for u in self.all_users() if type(u) is PremiumUser]
        if not premium_users:
            return 0.0

        if not self.sessions:
            return 0.0

        # Determine cutoff date dynamically based on the latest recorded session
        max_ts = max(s.timestamp for s in self.sessions)
        cutoff = max_ts - timedelta(days=days)

        total_unique = 0
        for u in premium_users:
            unique_tracks = set()
            for s in self.sessions:
                # Limit tracking only to the recent specified window
                if s.user.user_id == u.user_id and s.timestamp >= cutoff:
                    unique_tracks.add(s.track.track_id)
            total_unique += len(unique_tracks)

        return float(total_unique) / len(premium_users)

    def track_with_most_distinct_listeners(self) -> Optional[Track]:
        """
        Q3: Track with Most Distinct Listeners
        Identifies the track with the highest number of unique users who have listened to it
        """
        if not self.sessions:
            return None

        track_listeners = defaultdict(set)
        track_map = {}
        for s in self.sessions:
            track_listeners[s.track.track_id].add(s.user.user_id)
            track_map[s.track.track_id] = s.track

        if not track_listeners:
            return None

        best_track_id = max(track_listeners.keys(), key=lambda t: len(track_listeners[t]))
        return track_map[best_track_id]

    def avg_session_duration_by_user_type(self) -> List[Tuple[str, float]]:
        """
        Q4: Average Session Duration by User Type
        Computes the average duration of a session for each specific user tier
        """
        type_durations = defaultdict(list)
        for s in self.sessions:
            type_name = type(s.user).__name__
            type_durations[type_name].append(s.duration_listened_seconds)

        result = []
        for type_name, durations in type_durations.items():
            avg = sum(durations) / len(durations)
            result.append((type_name, avg))

        # Expected to be sorted from longest to shortest
        result.sort(key=lambda x: x[1], reverse=True)
        return result

    def total_listening_time_underage_sub_users_minutes(self, age_threshold: int = 18) -> float:
        """
        Q5: Total Listening Time for Underage Sub-Users
        Gathers listening time only for FamilyMember accounts below the given age threshold
        """
        total_seconds = 0
        for s in self.sessions:
            if isinstance(s.user, FamilyMember) and s.user.age < age_threshold:
                total_seconds += s.duration_listened_seconds
        return total_seconds / 60.0

    def top_artists_by_listening_time(self, n: int = 5) -> List[Tuple[Artist, float]]:
        """
        Q6: Top Artists by Listening Time
        Ranks top artists based on consecutive minutes users spent listening to their songs
        """
        artist_seconds = defaultdict(int)
        for s in self.sessions:
            # Only count actual Song items, skip Audiobooks/Podcasts
            if isinstance(s.track, Song):
                artist_seconds[s.track.artist] += s.duration_listened_seconds

        result = [(artist, seconds / 60.0) for artist, seconds in artist_seconds.items()]
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:n]

    def user_top_genre(self, user_id: str) -> Optional[Tuple[str, float]]:
        """
        Q7: Users Top Genre
        Identifies the genre a particular user listens to the most, mapped to percentage of their time
        """
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
        """
        Q8: Collaborative Playlists with Many Artists
        Identifies extensive collaborative playlists hitting a specific diverse artist threshold
        """
        result = []
        for p in self.playlists.values():
            if isinstance(p, CollaborativePlaylist):
                artists = set()
                # Determine how many unique artists span the playlist's tracks
                for track in p.tracks:
                    if isinstance(track, Song):
                        artists.add(track.artist.artist_id)
                if len(artists) > threshold:
                    result.append(p)
        return result

    def avg_tracks_per_playlist_type(self) -> Dict[str, float]:
        """
        Q9: Average Tracks per Playlist Type
        Separates averages for individual/personal playlists vs collaborative
        """
        stats = {
            "Playlist": {"count": 0, "tracks": 0},
            "CollaborativePlaylist": {"count": 0, "tracks": 0}
        }

        for p in self.playlists.values():
            # Check the exact class type
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
        """
        Q10: Users Who Completed Albums
        Returns users mapped with albums they listened to exhaustively.
        """
        user_history = defaultdict(set)
        for s in self.sessions:
            user_history[s.user.user_id].add(s.track.track_id)

        # Optimization: only checking albums that actually have tracks
        valid_albums = [a for a in self.albums.values() if a.tracks]
        
        final_result = []
        for user in self.all_users():
            completed_titles = []
            for a in valid_albums:
                album_track_ids = set(a.track_ids())
                # An album is completed exactly if the user has a listen history superset of the album's track list
                if album_track_ids.issubset(user_history[user.user_id]):
                    completed_titles.append(a.title)
                    
            if completed_titles:
                final_result.append((user, completed_titles))

        return final_result
