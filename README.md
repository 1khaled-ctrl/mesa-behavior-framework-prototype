# Mesa Behavioral Framework — Prototype

A prototype implementation of a modular behavioral framework for [Mesa](https://github.com/projectmesa/mesa), the Python agent-based modeling library.

This project is part of my **Google Summer of Code 2026** proposal:
> *Behavioral Framework for Agent Models in Mesa*

---

## Motivation

In Mesa, agent behavior is typically written directly inside the `step()` method. As simulations grow more complex, this leads to:

- Tightly coupled logic that is hard to maintain
- No standard way to reuse behavior across models
- Difficulty implementing complex decision structures

This prototype explores a design that addresses these limitations through **modular, composable behavior**.

---

## Design Overview

```
Agent
 ├── BehaviorMixin
 │     ├── add_behavior(module)
 │     ├── remove_behavior(name)
 │     └── run_behaviors()
 │
 ├── StateMachine
 │     ├── states: [searching, resting]
 │     ├── add_transition(from, condition, to)
 │     └── step(agent)  ← evaluates conditions, updates state
 │
 └── BehaviorModules           ← plug-and-play, reusable across models
       ├── RandomMovementBehavior
       ├── EnergyDepletionBehavior
       ├── ForageBehavior
       └── RestBehavior
```

### How it works

Each agent tick:
1. `fsm.step(agent)` — evaluates transition conditions, moves to new state if needed
2. `run_behaviors()` — executes all attached modules in order
3. State-specific logic runs based on current FSM state

### Core Components

| Component | Description |
|---|---|
| `BehaviorModule` | Base class for a single reusable behavior unit |
| `StateMachine` | Finite-state controller with conditional transitions |
| `BehaviorMixin` | Mixin that gives any Mesa agent a behavior system |

---

## Example Usage

```python
from behaviors import BehaviorMixin, StateMachine, RandomMovementBehavior, RestBehavior
import mesa

class MyAgent(BehaviorMixin, mesa.Agent):
    def __init__(self, model):
        super().__init__(model)
        self.energy = 100

        # Define behavioral states
        self.fsm = StateMachine(
            states=["searching", "resting"],
            initial="searching"
        )
        self.fsm.add_transition("searching", lambda a: a.energy <= 20, "resting")
        self.fsm.add_transition("resting",   lambda a: a.energy >= 80, "searching")

        # Attach reusable behavior modules
        self.add_behavior(RandomMovementBehavior())
        self.add_behavior(RestBehavior(recovery_rate=5.0))

    def step(self):
        self.fsm.step(self)       # update state
        self.run_behaviors()      # execute attached modules
```

---

## Project Structure

```
mesa-behavior-framework-prototype/
├── behaviors/
│   ├── base.py            # BehaviorModule, StateMachine, BehaviorMixin
│   └── modules.py         # Reusable behavior implementations
├── models/
│   ├── forager.py         # Example 1: foraging simulation
│   └── predator_prey.py   # Example 2: predator-prey (shows behavior reuse)
├── run_simulation.py      # Run forager demo
├── run_predator_prey.py   # Run predator-prey demo
├── requirements.txt
└── README.md
```

---

## Behavior Reuse — Key Idea

The same `BehaviorModule` can be attached to completely different agent types.
In the predator-prey model, both `WolfAgent` and `SheepAgent` share the same modules:

```
SheepAgent                          WolfAgent
 ├── StateMachine                    ├── StateMachine
 │     ├── grazing                   │     ├── roaming
 │     └── fleeing                   │     └── hunting
 │                                   │
 └── BehaviorModules                 └── BehaviorModules
       ├── EnergyDepletionBehavior  ←──── EnergyDepletionBehavior  (reused)
       ├── RandomMovementBehavior   ←──── RandomMovementBehavior   (reused)
       ├── GrazeBehavior                  HuntBehavior
       └── FleeBehavior                   (wolf-specific)
```

Writing a behavior once and reusing it across models is the core goal of this framework.

---

## Running the Demo

```bash
# Install dependencies
pip install -r requirements.txt

# Run the forager simulation
python run_simulation.py
```

### Example Output

```
=======================================================
  Mesa Behavioral Framework — Forager Simulation
=======================================================
  Agents: 10   Steps: 50
-------------------------------------------------------
  Step   1 | Searching:   8 | Resting:   2 | Resources: 1180.0
  Step  11 | Searching:   6 | Resting:   4 | Resources:  940.2
  Step  21 | Searching:   7 | Resting:   3 | Resources:  820.5
  Step  31 | Searching:   8 | Resting:   2 | Resources:  760.1
  Step  41 | Searching:   9 | Resting:   1 | Resources:  710.4
  Step  50 | Searching:   9 | Resting:   1 | Resources:  680.8
-------------------------------------------------------

  Final agent stats (step 50):
  Avg energy : 61.4
  Min energy : 22.0
  Max energy : 98.5

  Final state distribution:
    searching    █████████ (9)
    resting      █ (1)
=======================================================
```

---

## GSoC Proposal Connection

This prototype is a proof-of-concept for the ideas described in my GSoC 2026 proposal. The full project would:

- Integrate the framework directly into the Mesa library
- Support more behavioral patterns (behavior trees, priority queues)
- Include multiple example models
- Add full documentation and tutorials

---

## Requirements

- Python 3.10+
- Mesa 3.x

---

## Author

**Khaled Saber** — Computer Science student, GSoC 2026 applicant
- GitHub: [@1khaled-ctrl](https://github.com/1khaled-ctrl)
