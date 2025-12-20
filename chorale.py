# Soprano-Bass first-species counterpoint chorale structure.
# There is no formal rhythm; each chord aligns with one note in the soprano and one note in the bass.

from typing import List, Optional, Tuple
from pitch import Pitch
from tonality import ScaleDegree, TonalChord, KeySignature, ChordQuality, scale_degree_to_interval
from bassline import HarmonizedBassline

# only the soprano line is modifiable in this chorale structure
class Chorale:
    def __init__(self, bassline: HarmonizedBassline, soprano_line: Optional[List[Optional[Pitch]]]=None, soprano_candidates: Optional[List[List[Pitch]]]=None):
        self.bassline = bassline.copy()
        self.soprano_line = list(soprano_line) if soprano_line is not None else [None for _ in range(self.bassline.num_harmonizations())]
        if soprano_candidates is not None:  # only used for optimisations; please don't set this manually
            if len(soprano_candidates) != self.bassline.num_harmonizations():
                raise ValueError("Length of soprano_candidates must match number of chords in bassline")
            self.soprano_candidates = soprano_candidates
        else:
            # calculate candidates for soprano line
            self.soprano_candidates = [[] for _ in range(self.bassline.num_harmonizations())]
            for i in range(self.bassline.num_harmonizations()):
                chord_tones = self.bassline.get_chord_tones(i)
                for note in chord_tones:
                    self.soprano_candidates[i].extend(all_soprano_voicings(note))
    
    @property
    def key_signature(self) -> KeySignature:
        """Returns the key signature of the chorale, which is the key signature of the bassline."""
        return self.bassline.key_signature
    
    def num_chords(self) -> int:
        """Returns the number of chords in the chorale, which is the length of the soprano line and bassline."""
        return len(self.soprano_line)
    
    def get_soprano_note(self, index: int) -> Optional[Pitch]:
        """Returns the soprano note at the given index, or None if it has not been set."""
        return self.soprano_line[index]
    
    def set_soprano_note(self, index: int, pitch: Optional[Pitch]):
        """Sets the soprano note at the given index to the specified pitch, or None."""
        self.soprano_line[index] = pitch
    
    def get_soprano_candidates(self, index: int) -> List[Pitch]:
        """Returns the list of possible soprano candidates at the given index."""
        return self.soprano_candidates[index]
    
    def get_bass_note(self, index: int) -> Pitch:
        """Returns the bass note at the given index."""
        return self.bassline.get_bass_pitch(index)
    
    def get_chord(self, index: int) -> TonalChord:
        """Returns the chord at the given index."""
        return self.bassline.get_chord(index)
    
    def get_bass_harmonization(self, index: int) -> Tuple[Pitch, TonalChord]:
        """Returns the (bass pitch, chord) tuple at the given index."""
        return self.bassline.get_harmonization(index)
    
    def soprano_done(self) -> bool:
        """Returns whether the soprano line has been set for all indices."""
        return all(note is not None for note in self.soprano_line)
    
    def soprano_valid_at(self, index: int) -> bool:
        """
        Returns whether the soprano note at the given index is valid
        within the context of the notes before it.
        This checks against the criteria for proper voice leading:
        - The soprano note must be within the soprano range (G4 to C6).
        - The soprano must play a chord tone of the underlying chord.
        - If there is a previous soprano note, the interval between them must not exceed a perfect fifth.
        - If the soprano made a leap (larger than a third), it must be approached and left with a step in the opposite direction.
        - Sopranos may not step with augmented or diminished melodic intervals.
        - Parallel fifths and octaves between two voices are not allowed.
        - Direct (hidden) fifths and octaves are not allowed, meaning that:
        - Similar motion between the soprano and bass, where the soprano makes a disjunct motion into a fifth or octave are not allowed.
        - Tendency tones (scale degree 7, as well as the 4th scale degree in V7 and vii chords) must either be held statically or be resolved, and may not be doubled.
        - Notes may not be doubled in a seventh chord.
        """
        soprano_note = self.get_soprano_note(index)
        if soprano_note is None:
            return True
                
        # These checks should be redundant if the soprano candidates were generated correctly
        if not is_in_soprano_range(soprano_note):
            return False
        if not soprano_note in self.get_soprano_candidates(index):
            return False
        
        # Check melodic intervals and resolutions
        prev_soprano_note = self.get_soprano_note(index - 1) if index > 0 else None
        prev_prev_soprano_note = self.get_soprano_note(index - 2) if index > 1 else None

        if prev_soprano_note is not None and prev_prev_soprano_note is not None:
            # check if prev two notes made a leap, for which we need to step in opposite direction
            melodic_interval = prev_prev_soprano_note.distance_to(prev_soprano_note)
            if is_leap_interval(melodic_interval):
                step_interval = prev_soprano_note.distance_to(soprano_note)
                if not is_stepwise_interval(step_interval) or (melodic_interval * step_interval > 0):
                    return False  # did not finish a leap correctly
            
            # check if current notes made a leap, for which we need to check if prevprev approached correctly
            melodic_interval = prev_soprano_note.distance_to(soprano_note)
            if is_leap_interval(melodic_interval):
                step_interval = prev_prev_soprano_note.distance_to(prev_soprano_note)
                if not is_stepwise_interval(step_interval) or (melodic_interval * step_interval > 0):
                    return False  # did not approach leap correctly
        
        # Check melodic interval size
        if prev_soprano_note is not None:
            melodic_interval = prev_soprano_note.distance_to(soprano_note)
            if abs(melodic_interval) > 7:  # perfect fifth
                return False
            if abs(melodic_interval) == 6:  # tritone leap
                return False
        
        # Check for parallel and direct fifths and octaves with bass
        bass_note = self.get_bass_note(index)
        prev_bass_note = self.get_bass_note(index - 1) if index > 0 else None
        if prev_soprano_note is not None and prev_bass_note is not None:
            interval_prev = prev_bass_note.distance_to(prev_soprano_note) % 12
            interval_curr = bass_note.distance_to(soprano_note) % 12
            if interval_prev == interval_curr and (interval_curr == 0 or interval_curr == 7):
                return False  # parallel fifth or octave
            
            # Check for direct fifths and octaves
            if (interval_curr == 0 or interval_curr == 7):
                melodic_interval_soprano = prev_soprano_note.distance_to(soprano_note)
                melodic_interval_bass = prev_bass_note.distance_to(bass_note)
                if is_disjunct_interval(melodic_interval_bass):
                    if (melodic_interval_soprano * melodic_interval_bass > 0):
                        return False  # direct fifth or octave
        
        # Check tendency tones resolution and doubling
        chord = self.get_chord(index)
        key_signature = self.bassline.key_signature
        tendency_tones = [ScaleDegree.LEADING_TONE]  # leading tone is always a tendency tone
        if chord.scale_degree == ScaleDegree.DOMINANT and chord.quality == ChordQuality.DOMINANT_SEVENTH:
            tendency_tones.append(ScaleDegree.SUBDOMINANT)  # V7 chord has 4th scale degree as tendency tone
        if chord.scale_degree == ScaleDegree.LEADING_TONE:
            tendency_tones.append(ScaleDegree.SUBDOMINANT)  # vii chord also has 4th scale degree as tendency tone
        
        for scale_degree in tendency_tones:
            scale_degree_pitch = key_signature.tonic.plus_interval(scale_degree_to_interval(scale_degree, key_signature))
            if prev_soprano_note is not None:
                # check for resolution
                if prev_soprano_note.note_name_equals(scale_degree_pitch):
                    if not soprano_note.note_name_equals(prev_soprano_note):
                        # wasn't static, need to check resolution
                        if scale_degree == ScaleDegree.LEADING_TONE:
                            expected_resolution = prev_bass_note.plus_interval(1)  # resolves up to tonic
                        elif scale_degree == ScaleDegree.SUBDOMINANT:
                            expected_resolution = prev_bass_note.plus_interval(-1)  # resolves down to mediant
                        else:
                            raise ValueError("Unexpected scale degree")  # should not happen
                        if soprano_note != expected_resolution:
                            return False  # tendency tone did not resolve correctly
            # check for doubling
            if soprano_note.note_name_equals(scale_degree_pitch) and bass_note.note_name_equals(scale_degree_pitch):
                return False  # tendency tone is doubled
        
        # Finally, valid
        return True

    def soprano_valid(self) -> bool:
        """Returns whether the entire soprano line is valid. This may still be incomplete, even if no violations are found."""
        for i in range(self.num_chords()):
            if not self.soprano_valid_at(i):
                return False
        return True
    
    def copy(self) -> 'Chorale':
        """Returns a copy of the Chorale."""
        return Chorale(self.bassline, self.soprano_line, self.soprano_candidates)
    
    def __str__(self):
        result = f"Chorale in {self.key_signature}\n"
        result += f"{'Index':<6}{'Soprano':<12}{'Bass':<12}{'Chord':<12}{'Inversion':<6}\n"
        for i in range(self.num_chords()):
            soprano_note = self.get_soprano_note(i)
            soprano_note_str = str(soprano_note) if soprano_note is not None else "-"
            bass_pitch, chord = self.get_bass_harmonization(i)
            chord_label = chord.text_label
            inversion = self.bassline.get_inversion_number(i)
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
            result += f"{i:<6}{soprano_note_str:<12}{str(bass_pitch):<12}{chord_label:<12}{inversion_text:<6}\n"
        result += f"Soprano done: {self.soprano_done()}, valid: {self.soprano_valid()}\n"
        return result

def is_stepwise_interval(semitones: int) -> bool:
    """Returns whether the given interval in semitones is a stepwise interval (major or minor second)."""
    return semitones == 1 or semitones == 2 or semitones == -1 or semitones == -2

def is_disjunct_interval(semitones: int) -> bool:
    """Returns whether the given interval in semitones is a disjunct interval (larger than a major second)."""
    return abs(semitones) > 2

def is_leap_interval(semitones: int) -> bool:
    """Returns whether the given interval in semitones is a leap interval (larger than a major third)."""
    return abs(semitones) > 4

def is_in_bass_range(pitch: Pitch) -> bool:
    """Returns whether the given pitch is within the bass range (G2 to C4)."""
    return Pitch.from_note_name('G', 2).midi_index <= pitch.midi_index <= Pitch.from_note_name('C', 4).midi_index

def is_in_soprano_range(pitch: Pitch) -> bool:
    """Returns whether the given pitch is within the soprano range (C4 to G5)."""
    return Pitch.from_note_name('C', 4).midi_index <= pitch.midi_index <= Pitch.from_note_name('G', 5).midi_index

def all_soprano_voicings(pitch: Pitch) -> List[Pitch]:
    """Returns all possible soprano voicings of the given note (shifted by octaves) within the soprano range."""
    voicings = []
    base_note_name = pitch.note_name
    for octave in range(4, 7):  # Soprano range is G4 to C6
        candidate_pitch = Pitch.from_note_name(base_note_name, octave=octave)
        if is_in_soprano_range(candidate_pitch):
            voicings.append(candidate_pitch)
    return voicings


if __name__ == "__main__":
    # Example usage: Create a simple chorale with a bassline and soprano line
    c_major_key = KeySignature(Pitch.from_note_name("C"), is_major=True)
    bass_harmonizations = [
        (Pitch.from_note_name("C", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("D", 3), TonalChord(ScaleDegree.SUPERTONIC, ChordQuality.MINOR)),
        (Pitch.from_note_name("G", 2), TonalChord(ScaleDegree.DOMINANT, ChordQuality.DOMINANT_SEVENTH)),
        (Pitch.from_note_name("C", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
    ]
    bassline = HarmonizedBassline(c_major_key, bass_harmonizations)
    chorale = Chorale(bassline)
    print("Initial Chorale:")
    print(chorale)

    # try an illegal implementation
    bad_chorale = chorale.copy()
    bad_chorale.set_soprano_note(0, Pitch.from_note_name("C", 5))
    bad_chorale.set_soprano_note(1, Pitch.from_note_name("F", 5))  # leap
    bad_chorale.set_soprano_note(2, Pitch.from_note_name("F", 5))
    bad_chorale.set_soprano_note(3, Pitch.from_note_name("E", 5))
    print("Bad Chorale:")
    print(bad_chorale)

    bad_chorale.set_soprano_note(1, Pitch.from_note_name("D", 5))  # but now, parallel octaves!!
    print("Still bad Chorale:")
    print(bad_chorale)

    bad_chorale.set_soprano_note(0, Pitch.from_note_name("E", 5))  # now fixed
    bad_chorale.set_soprano_note(1, Pitch.from_note_name("F", 5))
    print("Fixed Chorale:")
    print(bad_chorale)
