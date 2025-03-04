from __future__ import annotations

from .user import User
from ..._compat import cached_property
from ..._resource import SyncAPIResource

__all__ = ["Users"]


class Users(SyncAPIResource):
    @cached_property
    def user(self) -> User:
        return User(self._client)
