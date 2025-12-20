# Handles key signatures and tonal harmony.

from typing import List, Dict
from enum import Enum, IntEnum
from pitch import Pitch  # Assuming pitch.py is in the same directory

class KeySignature:
    def __init__(self, tonic: Pitch, is_major: bool = True):
        self.tonic = tonic
        self.is_major = is_major
    
    def __str__(self):
        key_type = "Major" if self.is_major else "Minor"
        return f"{self.tonic.note_name} {key_type}"

class ChordQuality(Enum):
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    MAJOR_SEVENTH = "major_seventh"
    MINOR_SEVENTH = "minor_seventh"
    DOMINANT_SEVENTH = "dominant_seventh"
    HALF_DIMINISHED_SEVENTH = "half_diminished_seventh"
    DIMINISHED_SEVENTH = "diminished_seventh"

CHORD_TONE_OFFSETS: Dict[ChordQuality, List[int]] = {
    ChordQuality.MAJOR: [0, 4, 7],
    ChordQuality.MINOR: [0, 3, 7],
    ChordQuality.DIMINISHED: [0, 3, 6],
    ChordQuality.AUGMENTED: [0, 4, 8],
    ChordQuality.MAJOR_SEVENTH: [0, 4, 7, 11],
    ChordQuality.MINOR_SEVENTH: [0, 3, 7, 10],
    ChordQuality.DOMINANT_SEVENTH: [0, 4, 7, 10],
    ChordQuality.HALF_DIMINISHED_SEVENTH: [0, 3, 6, 10],
    ChordQuality.DIMINISHED_SEVENTH: [0, 3, 6, 9],
}

# Only used for chord roots, so scale degrees have same function in both major and minor keys
class ScaleDegree(IntEnum):
    TONIC = 1
    SUPERTONIC = 2
    MEDIANT = 3
    SUBDOMINANT = 4
    DOMINANT = 5
    SUBMEDIANT = 6
    LEADING_TONE = 7

MAJOR_SCALE_INTERVALS: Dict[ScaleDegree, int] = {
    ScaleDegree.TONIC: 0,
    ScaleDegree.SUPERTONIC: 2,
    ScaleDegree.MEDIANT: 4,
    ScaleDegree.SUBDOMINANT: 5,
    ScaleDegree.DOMINANT: 7,
    ScaleDegree.SUBMEDIANT: 9,
    ScaleDegree.LEADING_TONE: 11,
}

MINOR_SCALE_INTERVALS: Dict[ScaleDegree, int] = {
    ScaleDegree.TONIC: 0,
    ScaleDegree.SUPERTONIC: 2,
    ScaleDegree.MEDIANT: 3,
    ScaleDegree.SUBDOMINANT: 5,
    ScaleDegree.DOMINANT: 7,
    ScaleDegree.SUBMEDIANT: 8,
    ScaleDegree.LEADING_TONE: 10,
}

# represent a tonal chord; can be implemented in any key signature
class TonalChord:
    def __init__(self, scale_degree: ScaleDegree, quality: ChordQuality):
        self.scale_degree = scale_degree
        self.quality = quality
    
    def __str__(self):
        return f"{self.quality.value} chord on {self.scale_degree.name.lower()}"
    
    def get_chord_tones(self, key_signature: KeySignature) -> List[Pitch]:
        """Get the pitches of the chord tones based on the key root."""
        scale_intervals = MAJOR_SCALE_INTERVALS if key_signature.is_major else MINOR_SCALE_INTERVALS
        root_interval = scale_intervals[self.scale_degree]
        chord_root = key_signature.tonic.plus_interval(root_interval)
        chord_tones = CHORD_TONE_OFFSETS[self.quality]
        return [chord_root.plus_interval(semitone) for semitone in chord_tones]


if __name__ == "__main__":
    # Example usage: Create a V7 (dominant seventh) chord in C major
    major_key = KeySignature(Pitch.from_note_name("C"), is_major=True)
    V7_chord = TonalChord(ScaleDegree.DOMINANT, ChordQuality.DOMINANT_SEVENTH)
    V7_chord_tones = V7_chord.get_chord_tones(major_key)
    print(f"V7 Chord in {major_key}: {[str(p) for p in V7_chord_tones]}")

    # create ii diminished chord in A minor
    minor_key = KeySignature(Pitch.from_note_name("A"), is_major=False)
    ii_chord = TonalChord(ScaleDegree.SUPERTONIC, ChordQuality.DIMINISHED)
    ii_chord_tones = ii_chord.get_chord_tones(minor_key)
    print(f"ii diminished Chord in {minor_key}: {[str(p) for p in ii_chord_tones]}")