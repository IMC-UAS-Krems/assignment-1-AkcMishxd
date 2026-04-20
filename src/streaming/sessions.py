from datetime import datetime

class ListeningSession:
    """
    Records a user's isolated session listening to a specific audio track
    """
    def __init__(self, session_id: str, user, track, timestamp: datetime, duration_listened_seconds: int):
        """Initializes a listening session log entry."""
        self.session_id = session_id
        self.user = user
        self.track = track
        self.timestamp = timestamp
        self.duration_listened_seconds = duration_listened_seconds

    def duration_listened_minutes(self) -> float:
        """Converts the duration of the listening session from seconds to minutes."""
        # Provide float precision of the listened duration
        return self.duration_listened_seconds / 60.0
