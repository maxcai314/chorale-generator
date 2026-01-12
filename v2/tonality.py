"""
Improved tonality implementation for v2:
Most calculations are done using tonal intervals, which track both semitones and scale steps.
In order to track the function of notes, we use scale steps, and only switch to absolute pitch
at the end when generating the output MIDI.
"""

from enum import Enum, IntEnum
from typing import List, Dict
from .pitch import Pitch


class KeySignature:
    """Represents a major or minor key."""
    
    def __init__(self, tonic: Pitch, is_major: bool = True):
        self.tonic = tonic
        self.is_major = is_major
    
    def encode_octave(self, tone: 'TonalInterval', octave_number: int) -> 'TonalInterval':
        """Encodes the correct desired octave into a TonalInterval for this given key."""
        basic_pitch = Pitch(self.tonic.midi_index + tone.semitones)
        octave_shift = octave_number - basic_pitch.octave
        octave_interval = TonalInterval.from_size_and_quality(IntervalSize.OCTAVE, IntervalQuality.PERFECT)
        return TonalInterval(
            semitones=tone.semitones + octave_shift * octave_interval.semitones,
            scale_steps=tone.scale_steps + octave_shift * octave_interval.scale_steps
        )
    
    def realize_note(self, tone: 'TonalInterval') -> Pitch:
        return self.tonic.plus_interval(tone.semitones)
    
    def __str__(self):
        key_type = "Major" if self.is_major else "Minor"
        return f"{self.tonic.note_name} {key_type}"
    
    def __repr__(self):
        return f"KeySignature({self.tonic.name}, {'major' if self.is_major else 'minor'})"


class IntervalSize(IntEnum):
    """The scale steps of a tonal interval, regardless of quality"""
    UNISON = 0
    SECOND = 1
    THIRD = 2
    FOURTH = 3
    FIFTH = 4
    SIXTH = 5
    SEVENTH = 6
    OCTAVE = 7


class IntervalQuality(Enum):
    """The quality of a tonal interval."""
    PERFECT = "perfect"
    MAJOR = "major"
    MINOR = "minor"
    AUGMENTED = "augmented"
    DIMINISHED = "diminished"    


class TonalInterval:
    """Represents a tonal intervial, measured both by semitones and tonal size (scale steps)."""
    def __init__(self, semitones: int, scale_steps: int):
        self.semitones = semitones
        self.scale_steps = scale_steps
    
    @property
    def num_octaves(self) -> int:
        """Returns the number of complete octaves spanned by this interval."""
        return self.scale_steps // 7
    
    def normalized(self) -> 'TonalInterval':
        """
        Returns the interval normalized by naïvely removing octaves.
        The resultant interval will have scale_steps in [0, 7) (less than an octave).
        """
        removed_octaves = self.num_octaves
        return TonalInterval(
            semitones=self.semitones - removed_octaves * 12,
            scale_steps=self.scale_steps - removed_octaves * 7
        )
    
    def truncated(self) -> 'TonalInterval':
        """
        Returns the interval truncated to within a single octave.
        The resultant interval will have scale_steps in [0, 7] (up to and including an octave).
        If the original interval is two octaves (14 scale steps), for example, it will return a full octave rather than unison.
        A unison interval (0 scale steps) will only be returned if the original interval is also a unison.
        A tenth (9 scale steps) will be truncated to a third (2 scale steps).
        """
        removed_octaves = self.num_octaves
        remaining_steps = self.scale_steps - removed_octaves * 7
        if remaining_steps == 0 and removed_octaves > 0:  # avoid truncating to unison
            remaining_steps += 7
            removed_octaves -= 1
        return TonalInterval(
            semitones=self.semitones - removed_octaves * 12,
            scale_steps=remaining_steps
        )
    
    @property
    def quality(self) -> IntervalQuality:
        """Returns the quality of the interval based on its semitones and scale steps."""
        normalized = self.normalized()
        scale_steps = normalized.scale_steps
        semitones = normalized.semitones

        if scale_steps in (IntervalSize.UNISON, IntervalSize.FOURTH, IntervalSize.FIFTH, IntervalSize.OCTAVE):
            if semitones == {0:0, 3:5, 4:7, 7:12}[scale_steps]:
                return IntervalQuality.PERFECT
            elif semitones == {0:-1, 3:4, 4:6, 7:11}[scale_steps]:
                return IntervalQuality.DIMINISHED
            elif semitones == {0:1, 3:6, 4:8, 7:13}[scale_steps]:
                return IntervalQuality.AUGMENTED
        else:  # major/minor intervals
            if semitones == {1:2, 2:4, 5:9, 6:11}[scale_steps]:
                return IntervalQuality.MAJOR
            elif semitones == {1:1, 2:3, 5:8, 6:10}[scale_steps]:
                return IntervalQuality.MINOR
            elif semitones == {1:0, 2:2, 5:7, 6:9}[scale_steps]:
                return IntervalQuality.DIMINISHED
            elif semitones == {1:3, 2:5, 5:10, 6:12}[scale_steps]:
                return IntervalQuality.AUGMENTED
        
        raise ValueError(f"Cannot determine quality for interval with {semitones} semitones and {scale_steps} scale steps")
    
    @property
    def truncated_size(self) -> IntervalSize:
        """Returns the size of the interval truncated to within a single octave."""
        removed_octaves = self.num_octaves
        remaining_steps = self.scale_steps - removed_octaves * 7
        if remaining_steps == 0 and removed_octaves > 0:  # avoid truncating to unison
            remaining_steps += 7
        return IntervalSize(remaining_steps)
    
    @property
    def normalized_size(self) -> IntervalSize:
        """Returns the size of the interval normalized by removing octaves."""
        removed_octaves = self.num_octaves
        remaining_steps = self.scale_steps - removed_octaves * 7
        return IntervalSize(remaining_steps)
    
    def plus(self, other: 'TonalInterval') -> 'TonalInterval':
        """Returns the sum of this interval and another interval."""
        return TonalInterval(
            semitones=self.semitones + other.semitones,
            scale_steps=self.scale_steps + other.scale_steps
        )
    
    def minus(self, other: 'TonalInterval') -> 'TonalInterval':
        """Returns the difference of this interval and another interval."""
        return TonalInterval(
            semitones=self.semitones - other.semitones,
            scale_steps=self.scale_steps - other.scale_steps
        )
    
    def interval_to(self, other: 'TonalInterval') -> 'TonalInterval':
        """Returns the tonal interval from self upwards to another pitch."""
        result = other.minus(self)
        if result.num_octaves < 0:
            result = result.normalized()
        return result
    
    @classmethod
    def from_size_and_quality(cls, size: IntervalSize, quality: IntervalQuality) -> 'TonalInterval':
        """Constructs a TonalInterval from its size and quality."""
        base_semitones = {
            IntervalSize.UNISON: 0,
            IntervalSize.SECOND: 2,
            IntervalSize.THIRD: 4,
            IntervalSize.FOURTH: 5,
            IntervalSize.FIFTH: 7,
            IntervalSize.SIXTH: 9,
            IntervalSize.SEVENTH: 11,
            IntervalSize.OCTAVE: 12
        }[size]

        quality_adjustment = {
            IntervalQuality.PERFECT: 0,
            IntervalQuality.MAJOR: 0,
            IntervalQuality.MINOR: -1,
            IntervalQuality.AUGMENTED: 1,
            IntervalQuality.DIMINISHED: -1
        }[quality]

        if size in (IntervalSize.UNISON, IntervalSize.FOURTH, IntervalSize.FIFTH, IntervalSize.OCTAVE):
            if quality == IntervalQuality.MAJOR or quality == IntervalQuality.MINOR:
                raise ValueError(f"Invalid quality {quality} for perfect interval size {size}")
        else:
            if quality == IntervalQuality.PERFECT:
                raise ValueError(f"Invalid quality {quality} for major/minor interval size {size}")

        semitones = base_semitones + quality_adjustment
        return cls(semitones=semitones, scale_steps=size)
    
    def __repr__(self):
        return f"Interval(semitones={self.semitones}, scale_steps={self.scale_steps})"
    
    def __str__(self):
        return f"{self.quality.value.capitalize()} {self.truncated_size.name.capitalize()} ({self.semitones} semitones, {self.scale_steps} scale steps)"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TonalInterval):
            return NotImplemented
        return self.semitones == other.semitones and self.scale_steps == other.scale_steps
    
    def __hash__(self):
        return hash((self.semitones, self.scale_steps))

# predefined variables for common tonal intervals
TONIC: TonalInterval = TonalInterval.from_size_and_quality(IntervalSize.UNISON, IntervalQuality.PERFECT)
SUPERTONIC: TonalInterval = TonalInterval.from_size_and_quality(IntervalSize.SECOND, IntervalQuality.MAJOR)
MINOR_MEDIANT: TonalInterval = TonalInterval.from_size_and_quality(IntervalSize.THIRD, IntervalQuality.MINOR)
MAJOR_MEDIANT: TonalInterval = TonalInterval.from_size_and_quality(IntervalSize.THIRD, IntervalQuality.MAJOR)
SUBDOMINANT: TonalInterval = TonalInterval.from_size_and_quality(IntervalSize.FOURTH, IntervalQuality.PERFECT)
DOMINANT: TonalInterval = TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.PERFECT)
MINOR_SUBMEDIANT: TonalInterval = TonalInterval.from_size_and_quality(IntervalSize.SIXTH, IntervalQuality.MINOR)
MAJOR_SUBMEDIANT: TonalInterval = TonalInterval.from_size_and_quality(IntervalSize.SIXTH, IntervalQuality.MAJOR)
SUBTONIC: TonalInterval = TonalInterval.from_size_and_quality(IntervalSize.SEVENTH, IntervalQuality.MINOR)
LEADING_TONE: TonalInterval = TonalInterval.from_size_and_quality(IntervalSize.SEVENTH, IntervalQuality.MAJOR)


class ChordQuality(Enum):
    """Chord quality types."""
    MAJOR = "major"
    MINOR = "minor"
    DIMINISHED = "diminished"
    AUGMENTED = "augmented"
    DOMINANT_SEVENTH = "dominant_seventh"
    MAJOR_SEVENTH = "major_seventh"
    MINOR_SEVENTH = "minor_seventh"
    HALF_DIMINISHED_SEVENTH = "half_diminished_seventh"
    FULLY_DIMINISHED_SEVENTH = "diminished_seventh"


LOWERCASE_CHORD_QUALITIES: List[ChordQuality] = [
    ChordQuality.MINOR,
    ChordQuality.DIMINISHED,
    ChordQuality.MINOR_SEVENTH,
    ChordQuality.HALF_DIMINISHED_SEVENTH,
    ChordQuality.FULLY_DIMINISHED_SEVENTH
]

UPPERCASE_CHORD_QUALITIES: List[ChordQuality] = [
    ChordQuality.MAJOR,
    ChordQuality.AUGMENTED,
    ChordQuality.DOMINANT_SEVENTH,
    ChordQuality.MAJOR_SEVENTH
]

ROMAN_NUMERALS: List[str] = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
ADDITIONAL_CHORD_SYMBOLS: Dict[ChordQuality, str] = {
    ChordQuality.DIMINISHED: "o",
    ChordQuality.AUGMENTED: "+",
    ChordQuality.DOMINANT_SEVENTH: "dom7",
    ChordQuality.MAJOR_SEVENTH: "7",
    ChordQuality.MINOR_SEVENTH: "7",
    ChordQuality.HALF_DIMINISHED_SEVENTH: "ø7",
    ChordQuality.FULLY_DIMINISHED_SEVENTH: "o7"
}

CHORD_NOTES: Dict[ChordQuality, List[TonalInterval]] = {
    ChordQuality.MAJOR: [
        TonalInterval.from_size_and_quality(IntervalSize.UNISON, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.THIRD, IntervalQuality.MAJOR),
        TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.PERFECT)
    ],
    ChordQuality.MINOR: [
        TonalInterval.from_size_and_quality(IntervalSize.UNISON, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.THIRD, IntervalQuality.MINOR),
        TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.PERFECT)
    ],
    ChordQuality.DIMINISHED: [
        TonalInterval.from_size_and_quality(IntervalSize.UNISON, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.THIRD, IntervalQuality.MINOR),
        TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.DIMINISHED)
    ],
    ChordQuality.AUGMENTED: [
        TonalInterval.from_size_and_quality(IntervalSize.UNISON, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.THIRD, IntervalQuality.MAJOR),
        TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.AUGMENTED)
    ],
    ChordQuality.DOMINANT_SEVENTH: [
        TonalInterval.from_size_and_quality(IntervalSize.UNISON, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.THIRD, IntervalQuality.MAJOR),
        TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.SEVENTH, IntervalQuality.MINOR)
    ],
    ChordQuality.MAJOR_SEVENTH: [
        TonalInterval.from_size_and_quality(IntervalSize.UNISON, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.THIRD, IntervalQuality.MAJOR),
        TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.SEVENTH, IntervalQuality.MAJOR)
    ],
    ChordQuality.MINOR_SEVENTH: [
        TonalInterval.from_size_and_quality(IntervalSize.UNISON, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.THIRD, IntervalQuality.MINOR),
        TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.SEVENTH, IntervalQuality.MINOR)
    ],
    ChordQuality.HALF_DIMINISHED_SEVENTH: [
        TonalInterval.from_size_and_quality(IntervalSize.UNISON, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.THIRD, IntervalQuality.MINOR),
        TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.DIMINISHED),
        TonalInterval.from_size_and_quality(IntervalSize.SEVENTH, IntervalQuality.MINOR)
    ],
    ChordQuality.FULLY_DIMINISHED_SEVENTH: [
        TonalInterval.from_size_and_quality(IntervalSize.UNISON, IntervalQuality.PERFECT),
        TonalInterval.from_size_and_quality(IntervalSize.THIRD, IntervalQuality.MINOR),
        TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.DIMINISHED),
        TonalInterval.from_size_and_quality(IntervalSize.SEVENTH, IntervalQuality.DIMINISHED)
    ],
}


class TonalChord:
    """Represent a tonal chord, tracking its function via quality and root relative to the key signature's tonic."""
    def __init__(self, root: TonalInterval, quality: ChordQuality):
        self.root = root  # TonalInterval from key tonic to chord root
        self.quality = quality
    
    def roman_numeral_symbol(self) -> str:
        """Returns the roman numeral analysis symbol for this chord."""
        result = ROMAN_NUMERALS[self.root.truncated_size]
        if self.quality in LOWERCASE_CHORD_QUALITIES:
            result = result.lower()
        result += ADDITIONAL_CHORD_SYMBOLS.get(self.quality, "")
        return result
    
    def __str__(self):
        return f"{self.quality.value} chord on scale {self.root.truncated()}"
    
    def __repr__(self):
        return f"TonalChord(root={self.root}, quality={self.quality})"
    
    def get_scale_tones(self) -> List[TonalInterval]:
        """Get the list of notes spelled out, relative to the key's tonic."""
        return [self.root.plus(interval) for interval in self.get_root_intervals()]
    
    def get_root_intervals(self) -> List[TonalInterval]:
        """Get the list of tonal intervals from the chord root."""
        return CHORD_NOTES[self.quality]
    

if __name__ == "__main__":
    # calculate distance from subdominant (fa) to leading tone (ti) in major key
    scale_fa = TonalInterval.from_size_and_quality(IntervalSize.FOURTH, IntervalQuality.PERFECT)
    scale_ti = TonalInterval.from_size_and_quality(IntervalSize.SEVENTH, IntervalQuality.MAJOR)
    interval_fa_to_ti = scale_fa.interval_to(scale_ti)
    interval_ti_to_fa = scale_ti.interval_to(scale_fa)
    print(f"Interval from fa to ti: {interval_fa_to_ti}")
    print(f"Interval from ti to fa: {interval_ti_to_fa}")
    print(f"Combined interval: {interval_fa_to_ti.plus(interval_ti_to_fa)}")
    print()

    # calculate distance from from submediant (fa) to leading tone (si) in minor key
    scale_fa_minor = TonalInterval.from_size_and_quality(IntervalSize.SIXTH, IntervalQuality.MINOR)
    scale_si_minor = TonalInterval.from_size_and_quality(IntervalSize.SEVENTH, IntervalQuality.MAJOR)
    interval_fa_to_si = scale_fa_minor.interval_to(scale_si_minor)
    interval_si_to_fa = scale_si_minor.interval_to(scale_fa_minor)
    print(f"Interval from fa (minor) to si (minor): {interval_fa_to_si}")
    print(f"Interval from si (minor) to fa (minor): {interval_si_to_fa}")
    print(f"Combined interval: {interval_fa_to_si.plus(interval_si_to_fa)}")
    print() 

    # construct V7 chord
    scale_dominant = TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.PERFECT)
    v7_chord = TonalChord(root=scale_dominant, quality=ChordQuality.DOMINANT_SEVENTH)
    print(f"V7 chord: {v7_chord}")
    print(f"Roman numeral: {v7_chord.roman_numeral_symbol()}")
    print("Chord tones (relative to key tonic):")
    for tone in v7_chord.get_scale_tones():
        print(f" - {tone}")
    print()

    # construct iiø7 chord
    scale_supertonic = TonalInterval.from_size_and_quality(IntervalSize.SECOND, IntervalQuality.MAJOR)
    ii_half_dim7_chord = TonalChord(root=scale_supertonic, quality=ChordQuality.HALF_DIMINISHED_SEVENTH)
    print(f"iiø7 chord: {ii_half_dim7_chord}")
    print(f"Roman numeral: {ii_half_dim7_chord.roman_numeral_symbol()}")
    print("Chord tones (relative to key tonic):")
    for tone in ii_half_dim7_chord.get_scale_tones():
        print(f" - {tone}")
    print()
