# Bass and harmony. This information should be derivable from figured bass notation.
# Chorales will be generated from this bassline and tonal harmony.

from pitch import Pitch
from tonality import ScaleDegree, TonalChord, KeySignature, ChordQuality
from typing import List, Tuple

# Represents a bassline with chordal harmony associated with each note.
class HarmonizedBassline:
    def __init__(self, key_signature: KeySignature, bass_harmonizations: List[Tuple[Pitch, TonalChord]]=[]):
        self.key_signature = key_signature
        self.bass_harmonizations = list(bass_harmonizations)  # List of dicts mapping bass Pitch to TonalChord
    
    def add_harmonization(self, bass_pitch: Pitch, chord: TonalChord):
        """Adds a bass pitch and its associated chord to the harmonization list."""
        self.bass_harmonizations.append((bass_pitch, chord))
    
    def num_harmonizations(self) -> int:
        """Returns the number of harmonizations in the bassline."""
        return len(self.bass_harmonizations)
    
    def get_bass_pitch(self, index: int) -> Pitch:
        """Returns the bass pitch at the given index."""
        harmonization = self.bass_harmonizations[index]
        return harmonization[0]
    
    def get_chord(self, index: int) -> TonalChord:
        """Returns the chord at the given index."""
        harmonization = self.bass_harmonizations[index]
        return harmonization[1]
    
    def get_harmonization(self, index: int) -> Tuple[Pitch, TonalChord]:
        """Returns the (bass pitch, chord) tuple at the given index."""
        harmonization = self.bass_harmonizations[index]
        return (harmonization[0], harmonization[1])
    
    def bass_is_chord_tone(self, index: int) -> bool:
        """Returns whether the bass note at the given index is a chord tone."""
        bass, chord = self.bass_harmonizations[index]
        chord_notes = chord.get_chord_tones(self.key_signature)
        return any(bass.note_name_equals(note) for note in chord_notes)
    
    def get_inversion_number(self, index: int) -> int:
        """Returns the inversion number (0 for root) of the chord at the given index, or -1 if the bass note is not a chord tone."""
        bass, chord = self.bass_harmonizations[index]
        chord_notes = chord.get_chord_tones(self.key_signature)
        for i, note in enumerate(chord_notes):
            if bass.note_name_equals(note):
                return i  # Inversion number is the index of the bass note in the chord tones
        return -1  # Bass note is not a chord tone

    def __str__(self):
        result = f"HarmonizedBassline in {self.key_signature}\n"
        # format into evenly spaced columns
        result += f"{'Index':<6}{'Bass Pitch':<12}{'Chord':<12}{'Inversion':<6}\n"
        for i, harmonization in enumerate(self.bass_harmonizations):
            bass, chord = harmonization
            chord_label = chord.text_label
            inversion = self.get_inversion_number(i)
            if inversion == -1:
                inversion_text = "NC"
            elif inversion == 0:
                inversion_text = "Root"
            elif inversion == 1:
                inversion_text = "1st"
            elif inversion == 2:
                inversion_text = "2nd"
            elif inversion == 3:
                inversion_text = "3rd"
            else:
                inversion_text = f"{inversion}th"
            result += f"{i:<6}{str(bass):<12}{chord_label:<12}{inversion_text:<6}\n"
        return result

if __name__ == "__main__":
    # Example usage: Create a harmonized bassline in C major
    c_major_key = KeySignature(Pitch.from_note_name("C"), is_major=True)
    bassline = HarmonizedBassline(c_major_key)

    bassline.add_harmonization(Pitch.from_name("C3"), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR))  # I
    bassline.add_harmonization(Pitch.from_name("G3"), TonalChord(ScaleDegree.DOMINANT, ChordQuality.DOMINANT_SEVENTH)) # V7
    bassline.add_harmonization(Pitch.from_name("C3"), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR))  # I
    bassline.add_harmonization(Pitch.from_name("A3"), TonalChord(ScaleDegree.SUBMEDIANT, ChordQuality.MINOR))  # vi
    bassline.add_harmonization(Pitch.from_name("G3"), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR))  # I (2nd inversion)
    bassline.add_harmonization(Pitch.from_name("G3"), TonalChord(ScaleDegree.DOMINANT, ChordQuality.MAJOR))  # V
    bassline.add_harmonization(Pitch.from_name("C3"), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR))  # I

    print(bassline)