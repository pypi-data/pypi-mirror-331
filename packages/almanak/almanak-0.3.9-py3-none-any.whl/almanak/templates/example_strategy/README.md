# Strategy Example Template

This template provides a starting point for creating a new strategy on the Almanak platform and is meant to help new users get familiar with the framework as well as have suggestions of implementation that any strategy can take benefit of.

It provides a foundational structure that you can modify and extend according to your needs.


> Everything in this template can be deleted or changed **EXCEPT** that there should a `strategy.py` file that with a `Strategy` Class that extends `StrategyUniV3` and its dependencies, e.g. `PersistentStateBase` and `StrategyConfigBase`.

## Limitations

Currently we only support `UniSwap` as a protocol SDK and all token pairs will have to do with `WETH`. This is temporary limitation is being worked on and will soon be removed.

## Setup Guide

Use these commands to setup your development environment on the strategy.

```bash
pip install virtualenv
python -m venv .env
source .env/bin/activate
pip install -r requirements.txt
```

## Run Strategy Locally

Use the following command to test the strategy locally before deploying it.

```bash
python strategy.py
```

## Where to Start?

The example sets up (although doesn't finish) an LP Strategy using Uniswap with token pair of `WETH_WBTC`.

We suggest you look at the code so you can understand how it get an idea on how the code is organized.
Then, if you wish to continue with LP Strategy template, search for the TODO sections with a search for "# TODO:" to find areas that you should review or change.

Otherwise, feel free to delete the `states` folder and start designing your strategy in the `strategy.py`.

These are suggested states and configurations for a strategy, you may modify them as needed.

States:
    
    INITIALIZATION: Set up the strategy's initial state.
    CHECK_FOR_REBALANCE: Determine if rebalancing is needed based on market conditions.
    OPEN_POSITION: Create actions to open a new position.
    CLOSE_POSITION: Close existing positions and collect liquidity.
    COMPLETED: Final state after successful execution.
    TEARDOWN: Clean up resources and terminate the strategy.
    TERMINATED: Strategy has ended and requires manual intervention to restart.

Guidelines recommendations:
- Ensure proper handling of state transitions.
- Avoid hardcoding protocol-specific logic; aim for modularity.
- Implement exception handling and logging where appropriate.