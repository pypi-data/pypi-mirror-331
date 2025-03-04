from __future__ import annotations

from .monte_carlo import MonteCarlo
from ..._compat import cached_property
from ..._resource import SyncAPIResource

__all__ = ["Simulations"]


class Simulations(SyncAPIResource):
    @cached_property
    def monte_carlo(self) -> MonteCarlo:
        return MonteCarlo(self._client)
