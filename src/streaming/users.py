from datetime import date

class User:
    def __init__(self, user_id: str, name: str, age: int):
        self.user_id = user_id
        self.name = name
        self.age = age
        self.sessions = []

    def add_session(self, session) -> None:
        self.sessions.append(session)

    def total_listening_seconds(self) -> int:
        return sum(s.duration_listened_seconds for s in self.sessions)

    def total_listening_minutes(self) -> float:
        return self.total_listening_seconds() / 60.0

    def unique_tracks_listened(self) -> set:
        return {s.track.track_id for s in self.sessions}

class FreeUser(User):
    pass

class PremiumUser(User):
    def __init__(self, user_id: str, name: str, age: int, subscription_start: date = None):
        super().__init__(user_id, name, age)
        self.subscription_start = subscription_start

class FamilyAccountUser(PremiumUser):
    def __init__(self, user_id: str, name: str, age: int, subscription_start: date = None):
        super().__init__(user_id, name, age, subscription_start)
        self.sub_users = []

    def add_sub_user(self, member) -> None:
        self.sub_users.append(member)

    def all_members(self) -> list:
        return [self] + self.sub_users

class FamilyMember(User):
    def __init__(self, user_id: str, name: str, age: int, parent: FamilyAccountUser):
        super().__init__(user_id, name, age)
        self.parent = parent
