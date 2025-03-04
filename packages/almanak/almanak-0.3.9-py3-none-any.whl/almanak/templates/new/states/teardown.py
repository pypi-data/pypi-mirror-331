from time import sleep
from typing import TYPE_CHECKING

from almanak.enterprise_library.models.action_bundle import ActionBundle


if TYPE_CHECKING:
    from ..strategy import Strategy


def teardown(strategy: "Strategy") -> ActionBundle:
    """
    Concludes the strategy by closing any active positions and preparing the system for a reset or shutdown.
    Leaves the system in a state where it can be cleanly initialized again.

    Returns:
        ActionBundle | None: An action bundle with the teardown actions.
    """
    print("Teardown the strategy")
    print("Sleeping for 2 seconds\n")
    sleep(2)

    # TODO: Implement the strategy teardown logic