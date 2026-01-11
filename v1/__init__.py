"""Chorale Generator v1 - Original implementation"""

from .pitch import Pitch
from .tonality import ScaleDegree, TonalChord, KeySignature, ChordQuality, scale_degree_to_interval
from .bassline import HarmonizedBassline
from .chorale import Chorale
from .chorale_generator import ChoraleGenerator
from .audio_output import chorale_to_midi_file, chorales_to_midi_file, convert_midi_to_file

__all__ = [
    'Pitch',
    'ScaleDegree',
    'TonalChord',
    'KeySignature',
    'ChordQuality',
    'scale_degree_to_interval',
    'HarmonizedBassline',
    'Chorale',
    'ChoraleGenerator',
    'chorale_to_midi_file',
    'chorales_to_midi_file',
    'convert_midi_to_file',
]
