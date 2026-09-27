"""Pytest test session configuration for ARCANA AI Brain."""

import os
import sys

# Ensure both ai-engine-adarsh and root ARCANA-PROJECT are on sys.path
ENGINE_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(ENGINE_DIR, ".."))

for path in [ENGINE_DIR, PROJECT_ROOT]:
    if path not in sys.path:
        sys.path.insert(0, path)
