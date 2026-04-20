from datetime import date

class User:
    """
    Base class representing a user of the streaming platform.
    """
    def __init__(self, user_id: str, name: str, age: int):
        """Initializes a standard user profile."""
        self.user_id = user_id
        self.name = name
        self.age = age
        self.sessions = []  # History of the user's listening sessions

    def add_session(self, session) -> None:
        """Records a listening session for this user"""
        self.sessions.append(session)

    def total_listening_seconds(self) -> int:
        """Calculates the user's total listening time in seconds"""
        return sum(s.duration_listened_seconds for s in self.sessions)

    def total_listening_minutes(self) -> float:
        """Calculates the user's total listening time in minutes"""
        return self.total_listening_seconds() / 60.0

    def unique_tracks_listened(self) -> set:
        """Returns a set of unique track IDs the user has listened to."""
        # Extract track IDs from all recorded sessions
        return {s.track.track_id for s in self.sessions}

class FreeUser(User):
    """
    A user on the free tier with limited features.
    """
    pass

class PremiumUser(User):
    """
    A user on the paid premium tier.
    """
    def __init__(self, user_id: str, name: str, age: int, subscription_start: date = None):
        """Initializes a premium user profile."""
        super().__init__(user_id, name, age)
        self.subscription_start = subscription_start

class FamilyAccountUser(PremiumUser):
    """
    A premium user who manages a family subscription and can have dependent sub-users.
    """
    def __init__(self, user_id: str, name: str, age: int, subscription_start: date = None):
        """Initializes a family account manager profile."""
        super().__init__(user_id, name, age, subscription_start)
        self.sub_users = []  # List of dependent FamilyMember users

    def add_sub_user(self, member) -> None:
        """Adds a child/sub-user to the family account."""
        self.sub_users.append(member)

    def all_members(self) -> list:
        """Returns a list of all users in the family plan (including the primary user)."""
        return [self] + self.sub_users

class FamilyMember(User):
    """
    A dependent user profile within a Family Account.
    """
    def __init__(self, user_id: str, name: str, age: int, parent: FamilyAccountUser):
        """Initializes a family member profile."""
        super().__init__(user_id, name, age)
        self.parent = parent  # Reference back to the primary account holder
