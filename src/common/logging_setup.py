"""Centralised logging configuration for the Skills Mirage project.

Every module should obtain its logger via get_logger(__name__) rather than
calling logging.getLogger directly, so that the project-wide format is applied
consistently.
"""
from __future__ import annotations

import logging

_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"
_configured = False


def get_logger(name: str) -> logging.Logger:
    """Return a logger with the standard project format.

    Args:
        name: typically __name__ of the calling module.

    Returns:
        A configured Logger instance.
    """
    global _configured
    if not _configured:
        logging.basicConfig(level=logging.INFO, format=_FORMAT)
        _configured = True
    return logging.getLogger(name)
