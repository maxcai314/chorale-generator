"""Chorale Generator - Multi-version project for generating Bach-style chorales.

This project is organized with version-specific subpackages to support
experimentation and development of different approaches.
"""

from v1 import (
    Pitch,
    ScaleDegree,
    TonalChord,
    KeySignature,
    ChordQuality,
    scale_degree_to_interval,
    HarmonizedBassline,
    Chorale,
    ChoraleGenerator,
    chorale_to_midi_file,
    chorales_to_midi_file,
    convert_midi_to_file,
)

__version__ = "1.0"
__all__ = [
    "Pitch",
    "ScaleDegree",
    "TonalChord",
    "KeySignature",
    "ChordQuality",
    "scale_degree_to_interval",
    "HarmonizedBassline",
    "Chorale",
    "ChoraleGenerator",
    "chorale_to_midi_file",
    "chorales_to_midi_file",
    "convert_midi_to_file",
]
