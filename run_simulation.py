"""
Run the forager simulation and print a summary.

Usage:
    python run_simulation.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from models.forager import ForagerModel


def run(steps: int = 50, n_agents: int = 10):
    print("=" * 55)
    print("  Mesa Behavioral Framework — Forager Simulation")
    print("=" * 55)
    print(f"  Agents: {n_agents}   Steps: {steps}")
    print("-" * 55)

    model = ForagerModel(n_agents=n_agents, width=20, height=20, seed=42)

    for step in range(steps):
        model.step()

        if step % 10 == 0 or step == steps - 1:
            data = model.datacollector.model_vars
            searching = data["searching_agents"][-1]
            resting   = data["resting_agents"][-1]
            resources = data["total_resources"][-1]
            print(
                f"  Step {step+1:>3} | "
                f"Searching: {searching:>3} | "
                f"Resting: {resting:>3} | "
                f"Resources: {resources:>6.1f}"
            )

    print("-" * 55)

    # Agent-level summary
    agent_data = model.datacollector.get_agent_vars_dataframe()
    final = agent_data.xs(steps, level="Step")
    print(f"\n  Final agent stats (step {steps}):")
    print(f"  Avg energy : {final['energy'].mean():.1f}")
    print(f"  Min energy : {final['energy'].min():.1f}")
    print(f"  Max energy : {final['energy'].max():.1f}")

    state_counts = final["state"].value_counts()
    print(f"\n  Final state distribution:")
    for state, count in state_counts.items():
        bar = "█" * count
        print(f"    {state:<12} {bar} ({count})")

    print("\n  Simulation complete.")
    print("=" * 55)


if __name__ == "__main__":
    run(steps=50, n_agents=10)
