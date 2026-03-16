"""
Predator-Prey simulation — second demonstration of the behavioral framework.

This model shows BEHAVIOR REUSE across different agent types.
Both Wolf and Sheep agents share the same behavior modules
(RandomMovementBehavior, EnergyDepletionBehavior) but use
different StateMachine states and additional specialized behaviors.

Agent behavioral states
-----------------------
Sheep : grazing  →  fleeing (wolf nearby)  →  grazing
Wolf  : roaming  →  hunting (sheep nearby) →  roaming

This shows how the same BehaviorModule can be attached to completely
different agents with different logic — the core idea of the framework.
"""

import mesa
from behaviors import (
    BehaviorMixin,
    StateMachine,
    BehaviorModule,
    RandomMovementBehavior,
    EnergyDepletionBehavior,
)


# ── Custom behavior modules for this model ────────────────────────────────────

class GrazeBehavior(BehaviorModule):
    """Sheep recovers energy by grazing on grass."""

    name = "graze"

    def __init__(self, gain: float = 5.0):
        self.gain = gain

    def execute(self, agent) -> None:
        agent.energy = min(100, agent.energy + self.gain)


class FleeBehavior(BehaviorModule):
    """Sheep moves away from the nearest wolf."""

    name = "flee"

    def execute(self, agent) -> None:
        neighbors = agent.model.grid.get_neighborhood(
            agent.pos, moore=True, include_center=False, radius=2
        )
        # Move to the cell that maximizes distance from nearest wolf
        wolves = [
            a for a in agent.model.agents
            if isinstance(a, WolfAgent)
        ]
        if not wolves or not neighbors:
            return

        nearest_wolf = min(wolves, key=lambda w: _dist(agent.pos, w.pos))
        best = max(neighbors, key=lambda p: _dist(p, nearest_wolf.pos))
        agent.model.grid.move_agent(agent, best)


class HuntBehavior(BehaviorModule):
    """Wolf chases and eats sheep on the same cell."""

    name = "hunt"

    def __init__(self, kill_gain: float = 30.0):
        self.kill_gain = kill_gain

    def execute(self, agent) -> None:
        # Move toward the nearest sheep
        sheep_list = [
            a for a in agent.model.agents
            if isinstance(a, SheepAgent)
        ]
        if not sheep_list:
            return

        neighbors = agent.model.grid.get_neighborhood(
            agent.pos, moore=True, include_center=False
        )
        nearest = min(sheep_list, key=lambda s: _dist(agent.pos, s.pos))

        # Step toward it
        if neighbors:
            best = min(neighbors, key=lambda p: _dist(p, nearest.pos))
            agent.model.grid.move_agent(agent, best)

        # Eat any sheep on the same cell
        cell_mates = agent.model.grid.get_cell_list_contents([agent.pos])
        for other in cell_mates:
            if isinstance(other, SheepAgent):
                agent.energy = min(100, agent.energy + self.kill_gain)
                other.remove()
                break


def _dist(a, b) -> float:
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


# ── Agents ────────────────────────────────────────────────────────────────────

class SheepAgent(BehaviorMixin, mesa.Agent):
    """
    Sheep grazes peacefully but flees when a wolf is nearby.

    States: grazing → fleeing → grazing
    Reused behaviors: RandomMovementBehavior, EnergyDepletionBehavior
    New behaviors:    GrazeBehavior, FleeBehavior
    """

    def __init__(self, model, energy: float = 50.0):
        super().__init__(model)
        self.energy = energy

        self.fsm = StateMachine(
            states=["grazing", "fleeing"],
            initial="grazing",
        )
        self.fsm.add_transition(
            "grazing",
            lambda a: self._wolf_nearby(radius=3),
            "fleeing",
        )
        self.fsm.add_transition(
            "fleeing",
            lambda a: not self._wolf_nearby(radius=4),
            "grazing",
        )

        # Shared reusable modules
        self.add_behavior(EnergyDepletionBehavior(rate=1.5))

        # State-specific (called manually)
        self._move  = RandomMovementBehavior()
        self._graze = GrazeBehavior(gain=4.0)
        self._flee  = FleeBehavior()

    def _wolf_nearby(self, radius: int) -> bool:
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius=radius
        )
        return any(isinstance(n, WolfAgent) for n in neighbors)

    def step(self) -> None:
        self.fsm.step(self)
        self.run_behaviors()

        if self.fsm.state == "grazing":
            self._move.execute(self)
            self._graze.execute(self)
        elif self.fsm.state == "fleeing":
            self._flee.execute(self)

        if self.energy <= 0:
            self.remove()


class WolfAgent(BehaviorMixin, mesa.Agent):
    """
    Wolf roams the grid but switches to active hunting when sheep are nearby.

    States: roaming → hunting → roaming
    Reused behaviors: RandomMovementBehavior, EnergyDepletionBehavior
    New behaviors:    HuntBehavior
    """

    def __init__(self, model, energy: float = 50.0):
        super().__init__(model)
        self.energy = energy

        self.fsm = StateMachine(
            states=["roaming", "hunting"],
            initial="roaming",
        )
        self.fsm.add_transition(
            "roaming",
            lambda a: self._sheep_nearby(radius=4),
            "hunting",
        )
        self.fsm.add_transition(
            "hunting",
            lambda a: not self._sheep_nearby(radius=6),
            "roaming",
        )

        # Shared reusable module — same class as Sheep, different rate
        self.add_behavior(EnergyDepletionBehavior(rate=2.5))

        self._move  = RandomMovementBehavior()
        self._hunt  = HuntBehavior(kill_gain=35.0)

    def _sheep_nearby(self, radius: int) -> bool:
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=False, radius=radius
        )
        return any(isinstance(n, SheepAgent) for n in neighbors)

    def step(self) -> None:
        self.fsm.step(self)
        self.run_behaviors()

        if self.fsm.state == "roaming":
            self._move.execute(self)
        elif self.fsm.state == "hunting":
            self._hunt.execute(self)

        if self.energy <= 0:
            self.remove()


# ── Model ─────────────────────────────────────────────────────────────────────

class PredatorPreyModel(mesa.Model):
    """
    A predator-prey ecosystem demonstrating behavior reuse.

    Both Wolves and Sheep share EnergyDepletionBehavior and
    RandomMovementBehavior — showing how the same modules work
    across completely different agent types.

    Parameters
    ----------
    n_sheep  : initial number of sheep
    n_wolves : initial number of wolves
    width    : grid width
    height   : grid height
    seed     : random seed
    """

    def __init__(
        self,
        n_sheep: int = 20,
        n_wolves: int = 5,
        width: int = 25,
        height: int = 25,
        seed: int = 42,
    ):
        super().__init__(seed=seed)
        self.grid = mesa.space.MultiGrid(width, height, torus=True)
        self.steps = 0

        for _ in range(n_sheep):
            agent = SheepAgent(self, energy=self.random.randint(30, 80))
            self.grid.place_agent(agent, (
                self.random.randrange(width),
                self.random.randrange(height),
            ))

        for _ in range(n_wolves):
            agent = WolfAgent(self, energy=self.random.randint(30, 70))
            self.grid.place_agent(agent, (
                self.random.randrange(width),
                self.random.randrange(height),
            ))

        self.datacollector = mesa.DataCollector(
            model_reporters={
                "sheep":  lambda m: sum(1 for a in m.agents if isinstance(a, SheepAgent)),
                "wolves": lambda m: sum(1 for a in m.agents if isinstance(a, WolfAgent)),
                "sheep_grazing": lambda m: sum(
                    1 for a in m.agents
                    if isinstance(a, SheepAgent) and a.fsm.state == "grazing"
                ),
                "sheep_fleeing": lambda m: sum(
                    1 for a in m.agents
                    if isinstance(a, SheepAgent) and a.fsm.state == "fleeing"
                ),
                "wolves_roaming": lambda m: sum(
                    1 for a in m.agents
                    if isinstance(a, WolfAgent) and a.fsm.state == "roaming"
                ),
                "wolves_hunting": lambda m: sum(
                    1 for a in m.agents
                    if isinstance(a, WolfAgent) and a.fsm.state == "hunting"
                ),
            }
        )

    def step(self) -> None:
        self.steps += 1
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")
