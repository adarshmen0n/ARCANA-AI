"""Base classes and shared utilities for ARCANA generation engines."""

import logging
from typing import Optional
from providers.router import ProviderRouter

logger = logging.getLogger("arcana.generation")


class BaseGenerator:
    """Base class for all domain-specific educational generators."""

    def __init__(self, provider_router: ProviderRouter):
        self.router = provider_router
