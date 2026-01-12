"""
The layout for a chorale puzzle, defining the bass line and harmonizations,
as well as optional hints for other voices.
"""

from typing import List, Optional, Tuple
from enum import Enum
from .pitch import Pitch
from .tonality import *


SOPRANO_MIN_PITCH = Pitch.from_name("C4")
SOPRANO_MAX_PITCH = Pitch.from_name("G5")
ALTO_MIN_PITCH = Pitch.from_name("G3")
ALTO_MAX_PITCH = Pitch.from_name("C5")
TENOR_MIN_PITCH = Pitch.from_name("C3")
TENOR_MAX_PITCH = Pitch.from_name("G4")
BASS_MIN_PITCH = Pitch.from_name("G2")
BASS_MAX_PITCH = Pitch.from_name("C4")


class ChordInversion(Enum):
    ROOT = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3  # for seventh chords


class VerticalHarmonization:
    """Represents the vertical harmonization at a single point in the chorale."""

    def __init__(
        self,
        bass_note: TonalInterval,
        chord: TonalChord,
        soprano_hint: Optional[TonalInterval] = None,
        alto_hint: Optional[TonalInterval] = None,
        tenor_hint: Optional[TonalInterval] = None,
    ):
        self.bass_note = bass_note
        self.chord = chord
        self.soprano_hint = soprano_hint
        self.alto_hint = alto_hint
        self.tenor_hint = tenor_hint
    
    def get_inversion(self) -> ChordInversion:
        """Returns the inversion of the chord based on the bass note."""
        chord_tones = self.chord.get_scale_tones()
        for i, note in enumerate(chord_tones):
            if self.bass_note.normalized() == note.normalized():
                return ChordInversion(i)
        raise ValueError("Bass note is not a chord tone")
    
    def get_voice_candidates(self, lowest_semitones: int, highest_semitones: int) -> List[TonalInterval]:
        """Returns all possible candidate voicings (at all octaves) for this harmonization."""
        chord_tones = self.chord.get_scale_tones()
        candidates = []
        for tone in chord_tones:
            # this code is kinda slop but cope
            octave_shifted = tone
            octave = TonalInterval.from_size_and_quality(IntervalSize.OCTAVE, IntervalQuality.PERFECT)
            while octave_shifted.semitones + octave.semitones <= highest_semitones:
                octave_shifted = octave_shifted.plus(octave)
            while octave_shifted.semitones >= lowest_semitones:
                if lowest_semitones <= octave_shifted.semitones <= highest_semitones:
                    candidates.append(octave_shifted)
                octave_shifted = octave_shifted.minus(octave)
        return candidates


class RealizedHarmony:
    """
    Represents the realized harmony at a single point in the chorale.
    Contains the tones played by all four voices.
    """
    
    def __init__(
        self,
        soprano: TonalInterval,
        alto: TonalInterval,
        tenor: TonalInterval,
        bass: TonalInterval,
    ):
        self.soprano = soprano
        self.alto = alto
        self.tenor = tenor
        self.bass = bass
    
    def has_voice_crossing(self) -> bool:
        """Returns whether there is any voice crossing in this harmony."""
        return not (self.bass.semitones <= self.tenor.semitones <= self.alto.semitones <= self.soprano.semitones)
    
    def get_doubled_tones(self) -> List[TonalInterval]:
        """Returns a list of tones that are doubled in this harmony."""
        tone_counts = {}
        for tone in [self.soprano, self.alto, self.tenor, self.bass]:
            tone_counts[tone.truncated()] = tone_counts.get(tone.truncated(), 0) + 1
        return [tone for tone, count in tone_counts.items() if count > 1]
    
    def __str__(self):
        return f"S:{self.soprano} A:{self.alto} T:{self.tenor} B:{self.bass}"


class Chorale:
    """
    Represents a chorale layout with bass line and harmonizations.
    """
    
    def __init__(self, key_signature: KeySignature, harmonizations: Optional[List[VerticalHarmonization]]=None, candidates: Optional[List[RealizedHarmony]]=None):
        self.key_signature = key_signature
        self.harmonizations = list(harmonizations) if harmonizations is not None else []
        self.candidates = list(candidates) if candidates is not None else []

        if not self.candidates:
            self.candidates = self._generate_candidates()
        
        if not len(self.candidates) == len(self.harmonizations):
            raise ValueError("Number of candidates must match number of harmonizations")
    
    def _generate_candidates(self) -> List[RealizedHarmony]:
        """Generates all possible vertical harmonizations for the chorale based on the bass line."""
        candidates = []
        for vh in self.harmonizations:
            candidates.append(self._generate_candidates_for(vh))
        return candidates
    
    def _generate_candidates_for(self, harmonization: VerticalHarmonization) -> List[RealizedHarmony]:
        """Generates all possible vertical harmonizations for a single harmonization."""
        candidates: List[RealizedHarmony] = []
        tonic_index = self.key_signature.tonic.midi_index
        soprano_candidates = harmonization.get_voice_candidates(SOPRANO_MIN_PITCH.midi_index - tonic_index, SOPRANO_MAX_PITCH.midi_index - tonic_index)
        alto_candidates = harmonization.get_voice_candidates(ALTO_MIN_PITCH.midi_index - tonic_index, ALTO_MAX_PITCH.midi_index - tonic_index)
        tenor_candidates = harmonization.get_voice_candidates(TENOR_MIN_PITCH.midi_index - tonic_index, TENOR_MAX_PITCH.midi_index - tonic_index)
        bass_candidate = harmonization.bass_note

        for soprano in soprano_candidates:
            if harmonization.soprano_hint and soprano != harmonization.soprano_hint:
                continue
            for alto in alto_candidates:
                if harmonization.alto_hint and alto != harmonization.alto_hint:
                    continue
                if alto.semitones >= soprano.semitones:
                    continue
                for tenor in tenor_candidates:
                    if harmonization.tenor_hint and tenor != harmonization.tenor_hint:
                        continue
                    if tenor.semitones >= alto.semitones:
                        continue
                    candidate = RealizedHarmony(soprano, alto, tenor, bass_candidate)
                    if not candidate.has_voice_crossing():
                        candidates.append(candidate)
        
        for candidate in candidates:
            if candidate.has_voice_crossing():
                raise ValueError("Generated candidate has voice crossing; this should not happen")

        return candidates
    
    def __str__(self):
        result = f"Chorale in {self.key_signature}\n"
        for i, vh in enumerate(self.harmonizations):
            result += f"Harmonization {i}:\n"
            bass_note = self.harmonizations[i].bass_note
            result += f"{self.harmonizations[i].chord.roman_numeral_symbol()} with bass {self.key_signature.realize_note(bass_note).name}\n"
            result += f"Inversion: {self.harmonizations[i].get_inversion().name}\n"
            hints = [self.harmonizations[i].soprano_hint, self.harmonizations[i].alto_hint, self.harmonizations[i].tenor_hint, bass_note]
            hint_strs = [f"{self.key_signature.realize_note(hint).name if hint else '-':<5}" for hint in hints]
            result += f"Hints    {'  '.join(hint_strs)}\n"
            result += "\n"
        return result


if __name__ == "__main__":
    # Example: simple I-V two-chord chorale
    c_major_key = KeySignature(Pitch.from_note_name("C"), is_major=True)
    harmonizations = [
        VerticalHarmonization(
            bass_note=c_major_key.encode_octave(TONIC, 2),  # C2
            chord=TonalChord(root=TONIC, quality=ChordQuality.MAJOR),  # I chord
            soprano_hint=c_major_key.encode_octave(MAJOR_MEDIANT, 5),  # E5
        ),
        VerticalHarmonization(
            bass_note=c_major_key.encode_octave(DOMINANT, 2),  # G2
            chord=TonalChord(root=DOMINANT, quality=ChordQuality.MAJOR),  # V chord
        ),
    ]

    chorale = Chorale(c_major_key, harmonizations)
    print(chorale)
    print("Generated Candidates:\n")

    for i, candidate_list in enumerate(chorale.candidates):
        print(f"Harmonization {i}:")
        bass_note = chorale.harmonizations[i].bass_note
        print(f"{chorale.harmonizations[i].chord.roman_numeral_symbol()} with bass {chorale.key_signature.realize_note(bass_note).name}")
        print(f"Inversion: {chorale.harmonizations[i].get_inversion().name}")
        hints = [chorale.harmonizations[i].soprano_hint, chorale.harmonizations[i].alto_hint, chorale.harmonizations[i].tenor_hint, bass_note]
        hint_strs = [f"{chorale.key_signature.realize_note(hint).name if hint else '-':<5}" for hint in hints]
        print(f"  {'#':<5}  {'S':<5}  {'A':<5}  {'T':<5}  {'B':<5}")
        print(f"HINTS    {'  '.join(hint_strs)}")
        for idx, candidate in enumerate(candidate_list):
            intervals = [candidate.soprano, candidate.alto, candidate.tenor, candidate.bass]
            pitches = [f"{chorale.key_signature.realize_note(interval).name:<5}" for interval in intervals]
            print(f"  {idx:<5}  {'  '.join(pitches)}")
        print()
    
