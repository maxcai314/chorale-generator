# Handles key signatures and tonal harmony.

from typing import List, Dict
from enum import Enum, IntEnum

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

if __name__ == "__main__":
    from pitch import Pitch  # Assuming pitch.py is in the same directory

    # Example usage: Create a V7 (dominant seventh) chord in C major
    key_root = Pitch.from_note_name("C", 4)
    dominant_root = key_root.plus_interval(MAJOR_SCALE_INTERVALS[ScaleDegree.DOMINANT])
    chord_tones = CHORD_TONE_OFFSETS[ChordQuality.DOMINANT_SEVENTH]
    chord_pitches = [dominant_root.plus_interval(semitone) for semitone in chord_tones]
    print("Dominant Seventh Chord in C Major:", [str(p) for p in chord_pitches])

    # create ii diminished chord in A minor
    key_root_minor = Pitch.from_note_name("A", 4)
    supertonic_root = key_root_minor.plus_interval(MINOR_SCALE_INTERVALS[ScaleDegree.SUPERTONIC])
    diminished_chord_tones = CHORD_TONE_OFFSETS[ChordQuality.DIMINISHED]
    diminished_chord_pitches = [supertonic_root.plus_interval(semitone) for semitone in diminished_chord_tones]
    print("ii diminished Chord in A Minor:", [str(p) for p in diminished_chord_pitches])
