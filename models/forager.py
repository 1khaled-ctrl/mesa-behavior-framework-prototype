"""
Forager simulation — demonstration of the behavioral framework.

Agents have three behavioral states:
  searching  →  forage if resource found  →  resting (low energy)
  resting    →  recover energy            →  searching (energy restored)

Each state activates a different set of behavior modules,
showing how the StateMachine + BehaviorMixin work together.
"""

import mesa
import random
from behaviors import (
    BehaviorMixin,
    StateMachine,
    RandomMovementBehavior,
    EnergyDepletionBehavior,
    ForageBehavior,
    RestBehavior,
)


class ForagerAgent(BehaviorMixin, mesa.Agent):
    """
    An agent that searches for food, collects it, and rests when tired.

    Behavioral states
    -----------------
    searching : moves around and tries to forage
    resting   : stays put and recovers energy
    """

    def __init__(self, model, energy: float = 50.0):
        super().__init__(model)
        self.energy = energy

        # --- State machine ---
        self.fsm = StateMachine(
            states=["searching", "resting"],
            initial="searching",
        )
        self.fsm.add_transition(
            "searching",
            lambda a: a.energy <= 20,
            "resting",
        )
        self.fsm.add_transition(
            "resting",
            lambda a: a.energy >= 80,
            "searching",
        )

        # --- Behavior modules (always active) ---
        self.add_behavior(EnergyDepletionBehavior(rate=2.0))

        # State-specific behaviors are called manually in step()
        self._movement = RandomMovementBehavior()
        self._forage   = ForageBehavior(gain=15.0)
        self._rest     = RestBehavior(recovery_rate=8.0)

    def step(self) -> None:
        # 1. Update FSM state
        self.fsm.step(self)

        # 2. Run always-on behaviors (energy drain)
        self.run_behaviors()

        # 3. Run state-specific behaviors
        if self.fsm.state == "searching":
            self._movement.execute(self)
            self._forage.execute(self)
        elif self.fsm.state == "resting":
            self._rest.execute(self)


class ForagerModel(mesa.Model):
    """
    A simple foraging world.

    Parameters
    ----------
    n_agents : number of forager agents
    width    : grid width
    height   : grid height
    resource_density : fraction of cells that contain resources
    seed     : random seed for reproducibility
    """

    def __init__(
        self,
        n_agents: int = 10,
        width: int = 20,
        height: int = 20,
        resource_density: float = 0.3,
        seed: int = 42,
    ):
        super().__init__(seed=seed)

        self.grid = mesa.space.MultiGrid(width, height, torus=True)
        self.steps = 0

        # Place resources on random cells
        self.resources: dict[tuple, float] = {}
        for x in range(width):
            for y in range(height):
                if self.random.random() < resource_density:
                    self.resources[(x, y)] = 20.0

        # Create and place agents
        for _ in range(n_agents):
            agent = ForagerAgent(self)
            x = self.random.randrange(width)
            y = self.random.randrange(height)
            self.grid.place_agent(agent, (x, y))

        # Data collector
        self.datacollector = mesa.DataCollector(
            agent_reporters={
                "energy": "energy",
                "state":  lambda a: a.fsm.state,
            },
            model_reporters={
                "searching_agents": lambda m: sum(
                    1 for a in m.agents if a.fsm.state == "searching"
                ),
                "resting_agents": lambda m: sum(
                    1 for a in m.agents if a.fsm.state == "resting"
                ),
                "total_resources": lambda m: sum(m.resources.values()),
            },
        )

    def step(self) -> None:
        self.steps += 1
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

        # Slowly regenerate resources
        for pos in self.resources:
            self.resources[pos] = min(20.0, self.resources[pos] + 0.2)
