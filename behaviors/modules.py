"""
Reusable behavior modules for Mesa agents.

Each class is a self-contained, plug-and-play behavior unit.
Attach any combination to an agent via agent.add_behavior(...).
"""

import random
from .base import BehaviorModule


class RandomMovementBehavior(BehaviorModule):
    """Move the agent to a random neighboring cell each step."""

    name = "random_movement"

    def execute(self, agent) -> None:
        neighbors = agent.model.grid.get_neighborhood(
            agent.pos, moore=True, include_center=False
        )
        if neighbors:
            new_pos = random.choice(neighbors)
            agent.model.grid.move_agent(agent, new_pos)


class EnergyDepletionBehavior(BehaviorModule):
    """
    Reduce agent energy each step.
    The agent must have an `energy` attribute.
    """

    name = "energy_depletion"

    def __init__(self, rate: float = 1.0):
        self.rate = rate

    def execute(self, agent) -> None:
        agent.energy = max(0, agent.energy - self.rate)


class ForageBehavior(BehaviorModule):
    """
    Collect a resource from the current cell.
    Expects the grid to store resource values as cell properties,
    or the model to have a `resources` dict keyed by position.
    """

    name = "forage"

    def __init__(self, gain: float = 10.0):
        self.gain = gain

    def execute(self, agent) -> None:
        resources = getattr(agent.model, "resources", {})
        if agent.pos in resources and resources[agent.pos] > 0:
            collected = min(self.gain, resources[agent.pos])
            resources[agent.pos] -= collected
            agent.energy = min(100, agent.energy + collected)


class RestBehavior(BehaviorModule):
    """
    Recover energy when the agent is resting.
    The agent must have an `energy` attribute.
    """

    name = "rest"

    def __init__(self, recovery_rate: float = 5.0):
        self.recovery_rate = recovery_rate

    def execute(self, agent) -> None:
        agent.energy = min(100, agent.energy + self.recovery_rate)


class LogBehavior(BehaviorModule):
    """
    Debug behavior — print agent state each step.
    Useful during development; remove for production models.
    """

    name = "log"

    def execute(self, agent) -> None:
        state = getattr(agent, "fsm", None)
        state_str = f" | state={state.state}" if state else ""
        energy = getattr(agent, "energy", "n/a")
        print(f"[Step {agent.model.steps}] Agent {agent.unique_id}"
              f" @ {agent.pos} | energy={energy}{state_str}")
