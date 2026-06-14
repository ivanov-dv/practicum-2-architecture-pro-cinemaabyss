import logging
import random

import config

logger = logging.getLogger(__name__)


def _choose_movies_upstream() -> str:
    if config.GRADUAL_MIGRATION and random.randint(1, 100) <= config.MOVIES_MIGRATION_PERCENT:
        return config.MOVIES_SERVICE_URL
    return config.MONOLITH_URL


def resolve_upstream(path: str) -> str:
    if path.startswith('/api/movies'):
        base = _choose_movies_upstream()
        logger.info('route %s -> %s (percent=%s)', path, base, config.MOVIES_MIGRATION_PERCENT)
        return base
    if path.startswith('/api/events'):
        return config.EVENTS_SERVICE_URL
    return config.MONOLITH_URL
