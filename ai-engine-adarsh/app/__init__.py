"""ARCANA-AI Brain Application Package."""

import os
import sys

# Ensure project root (containing 'shared' package) is discoverable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

__version__ = "0.1.0"
