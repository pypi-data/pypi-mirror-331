from __future__ import annotations

from .jobs.jobs import Jobs
from ..._compat import cached_property
from ..._resource import SyncAPIResource

__all__ = ["Training"]


class Training(SyncAPIResource):
    @cached_property
    def jobs(self) -> Jobs:
        return Jobs(self._client)
