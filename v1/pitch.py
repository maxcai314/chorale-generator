# Handles musical pitch and interval representations.

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
LETTER_MAPPINGS = {
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
    'A': 9,
    'B': 11
}

class Pitch:
    def __init__(self, midi_index: int):
        if not (0 <= midi_index <= 127):
            raise ValueError("MIDI index must be between 0 and 127")
        self.midi_index = midi_index

    @property
    def name(self) -> str:
        """Returns the pitch name in scientific pitch notation (e.g., C4, A#3). Does not adjust to key signature."""
        octave = (self.midi_index // 12) - 1
        note = NOTE_NAMES[self.midi_index % 12]
        return f"{note}{octave}"
    
    @property
    def note_name(self) -> str:
        """Returns the pitch name without the octave number (e.g., C, D#, Eb). Does not adjust to key signature."""
        return NOTE_NAMES[self.midi_index % 12]
    
    @property
    def octave(self) -> int:
        """Returns the octave number of the pitch."""
        return (self.midi_index // 12) - 1
    
    @classmethod
    def from_name(cls, name: str) -> 'Pitch':
        note_part = name[:-1]
        octave_part = int(name[-1])
        # split note part into letter and alterations (e.g., C#, Db, Ebb)
        letter_name = note_part[0].upper()
        alterations = note_part[1:]
        if letter_name not in LETTER_MAPPINGS:
            raise ValueError(f"Invalid letter name name: {note_part}")
        letter_index = LETTER_MAPPINGS[letter_name]
        alterations_index = 0
        for char in alterations:
            if char == '#':
                alterations_index += 1
            elif char == 'b':
                alterations_index -= 1
            else:
                raise ValueError(f"Invalid alteration character: {char}")
        midi_index = (octave_part + 1) * 12 + letter_index + alterations_index
        return cls(midi_index)
    
    @classmethod
    def from_note_name(cls, note_name: str, octave: int=4) -> 'Pitch':
        """Constructs a Pitch from a note name and octave number. By default, octave is 4."""
        if octave < 0 or octave > 9:
            raise ValueError("Octave must be within 0 and 9")
        return cls.from_name(f"{note_name}{octave}")

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Pitch(midi_index={self.midi_index})"

    def plus_interval(self, semitones: int) -> 'Pitch':
        new_index = self.midi_index + semitones
        return Pitch(new_index)
    
    def distance_to(self, other: 'Pitch') -> int:
        """Returns the distance in semitones from self upwards to other. May be negative."""
        return other.midi_index - self.midi_index
    
    def distance_between(self, other: 'Pitch') -> int:
        """Returns the absolute distance in semitones between self and other."""
        return abs(other.midi_index - self.midi_index)
    
    def note_name_equals(self, other: 'Pitch') -> bool:
        """Returns whether two notes are equal in note name, ignoring octave. For example, C4 and C5 are equal."""
        return (self.midi_index % 12) == (other.midi_index % 12)
    
    def __hash__(self):
        return hash(self.midi_index)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pitch):
            return NotImplemented
        return self.midi_index == other.midi_index

_BASE_TONAL_INTERVALS = {
    1: 0,  # Unison
    2: 2,  # Major Second
    3: 4,  # Major Third
    4: 5,  # Perfect Fourth
    5: 7,  # Perfect Fifth
    6: 9,  # Major Sixth
    7: 11, # Major Seventh
    8: 12  # Octave
}

_TONE_QUALITIY_OFFSETS = {
    'P': 0,
    'M': 0,
    'm': -1,
    'A': 1,
    'd': -1
}

def text_to_interval(text: str) -> int:
    """Convert interval text (e.g., 'm3', 'P5', 'A4') to semitone distance."""
    quality = text[0]
    number = int(text[1:])

    if number < 1:
        raise ValueError(f"Interval number must be >= 1, got {number}")

    octaves, tonal_interval_idx = divmod(number - 1, 7)
    tonal_interval = tonal_interval_idx + 1
    
    if tonal_interval not in _BASE_TONAL_INTERVALS:
        raise ValueError(f"Invalid interval number: {number}")
    
    semitones = _BASE_TONAL_INTERVALS[tonal_interval]
    
    if quality in _TONE_QUALITIY_OFFSETS:
        semitones += _TONE_QUALITIY_OFFSETS[quality]
        semitones += octaves * 12
        return semitones
    else:
        raise ValueError(f"Invalid interval quality: {quality}")

def interval_to_text(semitones: int) -> str:
    """Convert semitone distance to interval text (e.g., 'm3', 'P5', 'A4')."""
    if semitones < 0:
        raise ValueError("Semitones must be non-negative")
    octaves, base_interval = divmod(semitones, 12)
    
    # Find the closest base interval in _BASE_TONAL_INTERVALS value set
    # greater than or equal to base_interval
    # i.e. the number 10 would be 1 less than 11 (Major Seventh)
    possible_intervals = sorted(_BASE_TONAL_INTERVALS.items(), key=lambda x: x[1])
    for tonal_interval, base_semitones in possible_intervals:
        if base_semitones >= base_interval:
            semitone_diff = base_interval - base_semitones
            tonal_interval_number = tonal_interval
            break
    else:
        raise ValueError(f"No base interval found for {semitones} semitones")
    # Determine quality based on semitone_diff
    if tonal_interval_number in [1, 4, 5, 8]:  # Perfect intervals
        if semitone_diff == 0:
            quality = 'P'
        elif semitone_diff == 1:
            quality = 'A'
        elif semitone_diff == -1:
            quality = 'd'
        else:
            raise ValueError(f"No valid quality for {semitones} semitones")
    elif tonal_interval_number in [2, 3, 6, 7]:  # Major/Minor intervals
        if semitone_diff == 0:
            quality = 'M'
        elif semitone_diff == -1:
            quality = 'm'
        elif semitone_diff == 1:
            quality = 'A'
        elif semitone_diff == -2:
            quality = 'd'
        else:
            raise ValueError(f"No valid quality for {semitones} semitones")
    else:
        raise ValueError(f"No valid interval number for {semitones} semitones")
    
    interval_number = tonal_interval_number + octaves * 7
    return f"{quality}{interval_number}"
