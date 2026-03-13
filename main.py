"""
Autonomous AI Discovery Engine with Multi-Agent Debate Simulation.
(Refactored for Production architecture)
"""

from __future__ import annotations
from agents.supervisor_agent import start_pipeline
from core.pipeline import run_pipeline


def main():
    """Main entrypoint required by user specification."""
    start_pipeline()


if __name__ == "__main__":
    main()
