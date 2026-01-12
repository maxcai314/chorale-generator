"""Barebones pitch implementation for v2"""

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
LETTER_MAPPINGS = {
    'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11
}


class Pitch:
    """Simplified pitch representation using MIDI index."""
    
    def __init__(self, midi_index: int):
        if not (0 <= midi_index <= 127):
            raise ValueError("MIDI index must be between 0 and 127")
        self.midi_index = midi_index

    @property
    def name(self) -> str:
        """Returns pitch name in scientific notation (e.g., C4, A#3)."""
        octave = (self.midi_index // 12) - 1
        note = NOTE_NAMES[self.midi_index % 12]
        return f"{note}{octave}"
    
    @property
    def note_name(self) -> str:
        """Returns note name without octave (e.g., C, D#)."""
        return NOTE_NAMES[self.midi_index % 12]
    
    @property
    def octave(self) -> int:
        """Returns octave number."""
        return (self.midi_index // 12) - 1
    
    @classmethod
    def from_name(cls, name: str) -> 'Pitch':
        """Create Pitch from name string (e.g., 'C4', 'A#3')."""
        note_part = name[:-1]
        octave_part = int(name[-1])
        letter_name = note_part[0].upper()
        alterations = note_part[1:]
        
        if letter_name not in LETTER_MAPPINGS:
            raise ValueError(f"Invalid letter name: {note_part}")
        
        letter_index = LETTER_MAPPINGS[letter_name]
        alterations_index = 0
        for char in alterations:
            if char == '#':
                alterations_index += 1
            elif char == 'b':
                alterations_index -= 1
        
        midi_index = (octave_part + 1) * 12 + letter_index + alterations_index
        return cls(midi_index)
    
    @classmethod
    def from_note_name(cls, note_name: str, octave: int = 4) -> 'Pitch':
        """Create Pitch from note name and octave."""
        return cls.from_name(f"{note_name}{octave}")

    def plus_interval(self, semitones: int) -> 'Pitch':
        """Return new Pitch transposed by given semitones."""
        return Pitch(self.midi_index + semitones)
    
    def distance_to(self, other: 'Pitch') -> int:
        """Return signed distance in semitones to another pitch."""
        return other.midi_index - self.midi_index
    
    def distance_between(self, other: 'Pitch') -> int:
        """Return absolute distance in semitones to another pitch."""
        return abs(self.distance_to(other))
    
    def note_name_equals(self, other: 'Pitch') -> bool:
        """Check if two pitches have the same note name (ignoring octave)."""
        return (self.midi_index % 12) == (other.midi_index % 12)
    
    def __str__(self) -> str:
        return self.name
    
    def __repr__(self) -> str:
        return f"Pitch({self.name})"
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Pitch):
            return NotImplemented
        return self.midi_index == other.midi_index
    
    def __hash__(self):
        return hash(self.midi_index)
