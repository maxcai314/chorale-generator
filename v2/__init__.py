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
    TONIC, SUPERTONIC, MINOR_MEDIANT, MAJOR_MEDIANT,
    SUBDOMINANT, DOMINANT, MINOR_SUBMEDIANT, MAJOR_SUBMEDIANT,
    SUBTONIC, LEADING_TONE
)

from .chorale import (
    ChordInversion,
    VerticalHarmonization,
    RealizedHarmony,
    Chorale,
    RealizedChorale
)

from .chorale_generator import ChoraleGenerator

from .audio_output import chorale_to_midi_file, chorales_to_midi_file, convert_midi_to_file

__all__ = [
    'Pitch',
    'ScaleDegree',
    'TonalChord',
    'KeySignature',
    'ChordQuality',
    'scale_degree_to_interval',
    'ChordInversion',
    'VerticalHarmonization',
    'RealizedHarmony',
    'Chorale',
    'RealizedChorale',
    'ChoraleGenerator',
    'chorale_to_midi_file',
    'chorales_to_midi_file',
    'convert_midi_to_file'
]