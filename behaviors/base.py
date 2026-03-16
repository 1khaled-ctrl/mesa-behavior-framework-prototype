"""
Base classes for the Mesa Behavioral Framework prototype.

This module defines the core abstractions:
  - BehaviorModule  : a reusable, attachable unit of agent logic
  - StateMachine    : finite-state behavior controller
  - BehaviorMixin   : mixin that gives any Mesa Agent a behavior controller
"""


class BehaviorModule:
    """
    A single reusable unit of agent behavior.

    Subclass this and override `execute(agent)` to define what the
    behavior does each step.  Behaviors are meant to be composable —
    an agent can carry several at once.
    """

    name: str = "unnamed_behavior"

    def execute(self, agent) -> None:
        """Run one step of this behavior for the given agent."""
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"<BehaviorModule: {self.name}>"


class StateMachine:
    """
    A simple finite-state machine (FSM) for agent behavior.

    States are plain strings.  Transitions are registered as
    (current_state, condition_fn) → next_state mappings.
    On each step, the FSM evaluates registered transitions in order
    and moves to the first state whose condition returns True.

    Example
    -------
    fsm = StateMachine(states=["idle", "searching", "resting"], initial="idle")
    fsm.add_transition("idle", lambda a: a.energy < 50, "searching")
    fsm.add_transition("searching", lambda a: a.energy <= 0, "resting")
    fsm.add_transition("resting", lambda a: a.energy >= 100, "idle")
    """

    def __init__(self, states: list, initial: str):
        if initial not in states:
            raise ValueError(f"Initial state '{initial}' not in states {states}")
        self.states = states
        self.state = initial
        self._transitions: list[tuple] = []   # (from_state, condition, to_state)

    def add_transition(self, from_state: str, condition, to_state: str) -> None:
        """Register a conditional transition from one state to another."""
        if from_state not in self.states:
            raise ValueError(f"Unknown state: {from_state}")
        if to_state not in self.states:
            raise ValueError(f"Unknown state: {to_state}")
        self._transitions.append((from_state, condition, to_state))

    def step(self, agent) -> None:
        """Evaluate all transitions and update state if a condition is met."""
        for from_state, condition, to_state in self._transitions:
            if self.state == from_state and condition(agent):
                self.state = to_state
                return

    def __repr__(self) -> str:
        return f"<StateMachine state={self.state!r} states={self.states}>"


class BehaviorMixin:
    """
    Mixin for Mesa agents that adds a behavior module list and
    an optional state machine.

    Usage
    -----
    class MyAgent(BehaviorMixin, mesa.Agent):
        def __init__(self, model):
            super().__init__(model)
            self.add_behavior(MovementBehavior())
            self.fsm = StateMachine(["idle", "moving"], initial="idle")

        def step(self):
            if self.fsm:
                self.fsm.step(self)
            self.run_behaviors()
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._behaviors: list[BehaviorModule] = []
        self.fsm: StateMachine | None = None

    def add_behavior(self, behavior: BehaviorModule) -> None:
        """Attach a behavior module to this agent."""
        self._behaviors.append(behavior)

    def remove_behavior(self, name: str) -> None:
        """Detach a behavior module by name."""
        self._behaviors = [b for b in self._behaviors if b.name != name]

    def run_behaviors(self) -> None:
        """Execute all attached behavior modules in order."""
        for behavior in self._behaviors:
            behavior.execute(self)

    @property
    def behavior_names(self) -> list[str]:
        return [b.name for b in self._behaviors]
