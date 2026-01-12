"""Chorale Generator v2 - Simplified implementation

This version provides a streamlined approach to chorale generation.
"""

from .pitch import Pitch
from .tonality import (
    KeySignature,
    ChordQuality,
    IntervalSize,
    TonalInterval,
    TonalChord,
)

__all__ = [
    'Pitch',
    'ScaleDegree',
    'TonalChord',
    'KeySignature',
    'ChordQuality',
    'scale_degree_to_interval',
]
