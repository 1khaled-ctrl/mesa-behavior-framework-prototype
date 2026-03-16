"""
Run the predator-prey simulation and print a summary.

This demonstrates BEHAVIOR REUSE — both wolves and sheep share
the same EnergyDepletionBehavior and RandomMovementBehavior modules.

Usage:
    python run_predator_prey.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.predator_prey import PredatorPreyModel


def run(steps: int = 60, n_sheep: int = 20, n_wolves: int = 5):
    print("=" * 60)
    print("  Mesa Behavioral Framework — Predator-Prey Simulation")
    print("  Demonstrating: behavior reuse across agent types")
    print("=" * 60)
    print(f"  Sheep: {n_sheep}   Wolves: {n_wolves}   Steps: {steps}")
    print("-" * 60)

    model = PredatorPreyModel(
        n_sheep=n_sheep, n_wolves=n_wolves,
        width=25, height=25, seed=42
    )

    for step in range(steps):
        model.step()

        if step % 10 == 0 or step == steps - 1:
            d = model.datacollector.model_vars
            sheep   = d["sheep"][-1]
            wolves  = d["wolves"][-1]
            grazing = d["sheep_grazing"][-1]
            fleeing = d["sheep_fleeing"][-1]
            roaming = d["wolves_roaming"][-1]
            hunting = d["wolves_hunting"][-1]
            print(
                f"  Step {step+1:>3} | "
                f"Sheep: {sheep:>3} (grazing {grazing:>2} / fleeing {fleeing:>2}) | "
                f"Wolves: {wolves:>2} (roaming {roaming:>2} / hunting {hunting:>2})"
            )

    print("-" * 60)
    print("\n  Behavior reuse summary:")
    print("  Both agent types used:")
    print("    EnergyDepletionBehavior  ← same class, different rate")
    print("    RandomMovementBehavior   ← identical across both agents")
    print("\n  Simulation complete.")
    print("=" * 60)


if __name__ == "__main__":
    run(steps=60, n_sheep=20, n_wolves=5)
