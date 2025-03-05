"""Data loader package for FlashScore data."""

from .base import DataLoader
from .processors import FootballProcessor, HandballProcessor, VolleyballProcessor

__all__ = [
    "DataLoader",
    "HandballProcessor",
    "FootballProcessor",
    "VolleyballProcessor",
]
