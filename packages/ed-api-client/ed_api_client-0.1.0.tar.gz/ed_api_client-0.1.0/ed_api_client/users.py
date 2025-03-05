from dataclasses import dataclass
from typing import List


@dataclass
class User:
    """
    An Ed user account

    ...

    Attributes
    ----------
    id : int
        Unique id for each user. This is unique to Ed and has no overlap with student ids from Canvas or CIS.
    name : str
        The full name of the user
    email : str
        The email address of the user
    role : str
        One of student, staff or admin
    """

    id: int
    name: str
    email: str
    role: str

    def from_json(j: dict):
        return User(j["id"], j["name"], j["email"], j["role"])


class Users:
    def __init__(self):
        self.users = []
        self._usersById = {}
        self._usersByEmail = {}

    def add(self, user: User):
        self.users.append(user)
        self._usersById[user.id] = user
        self._usersByEmail[user.email] = user

    def getById(self, id: int):
        return self._usersById.get(id)

    def getByEmail(self, email: str):
        return self._usersByEmail.get(email)

    def getAllByEmail(self, emails: List[str]):
        users = []
        for email in emails:
            if email in self._usersByEmail:
                users.append(self.getByEmail(email))

        return users
