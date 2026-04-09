import hashlib
import os
from typing import Optional

from domain.user import User
from ports.repositories import UserRepository


class UserService:
    """Lógica de negocio de usuarios.
    Solo conoce el puerto (UserRepository), nunca DynamoDB directamente."""

    def __init__(self, repo: UserRepository):
        self._repo = repo

    def login(self, correo: str, password: str) -> Optional[User]:
        credentials = self._repo.find_credentials_by_email(correo)
        if not credentials:
            return None
        if credentials["Password_hash"] != self._hash(password):
            return None
        user_id = credentials["PK"].replace("USER#", "")
        return self._repo.find_profile(user_id)

    def get_profile(self, user_id: str) -> Optional[User]:
        return self._repo.find_profile(user_id)

    def _hash(self, password: str) -> str:
        pepper = os.getenv("PASSWORD_PEPPER", "")
        return hashlib.sha256((password + pepper).encode()).hexdigest()
