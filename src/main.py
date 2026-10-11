#!/usr/bin/env python3
"""Main entry point for Qiskit Fall Fest 2026 Track 2 project submission."""

import sys
import os

# Ensure src/ is on sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from quantum_optimizer.cli import main

if __name__ == "__main__":
    sys.exit(main())
