# Soprano-Bass first-species counterpoint chorale generator.
# There is no formal rhythm; each chord aligns with one note in the soprano and one note in the bass.

from typing import List, Optional, Tuple
from pitch import Pitch
from tonality import ScaleDegree, TonalChord, KeySignature, ChordQuality, scale_degree_to_interval
from bassline import HarmonizedBassline
from chorale import Chorale
from random import Random

class ChoraleGenerator:
    def __init__(self, chorale: Chorale, random_seed: int=42):
        self.chorale = chorale.copy()
        self.random = Random(random_seed)
    
    def _try_generate_soprano_for_index(self, index: int) -> bool:
        """
        Uses a depth-first recursive backtracking approach to fill in the soprano line.
        If successful, a valid soprano line will be set up in self.chorale, and returns True.
        If unsuccessful, returns False and leaves the soprano line unchanged.
        """
        if self.chorale.get_soprano_note(index) is not None:
            # Soprano note already set, move to next index
            if index == self.chorale.num_chords() - 1:
                return self.chorale.soprano_valid_at(index) and self.chorale.soprano_valid() and self.chorale.soprano_done()
            else:
                return self._try_generate_soprano_for_index(index + 1)

        candidate_notes = list(self.chorale.get_soprano_candidates(index))
        # an algorithm could sort using some heuristic to prioritize conjunct motion here
        self.random.shuffle(candidate_notes)  # Randomize order to get different results on different runs
        for candidate in candidate_notes:
            self.chorale.set_soprano_note(index, candidate)
            if not self.chorale.soprano_valid_at(index):
                continue  # try next candidate
            if index == self.chorale.num_chords() - 1:
                if self.chorale.soprano_valid_at(index) and self.chorale.soprano_valid() and self.chorale.soprano_done():
                    return True  # successfully filled in entire soprano line
            if self._try_generate_soprano_for_index(index + 1):
                return True  # successful in deeper recursion
        else:
            self.chorale.set_soprano_note(index, None)  # backtrack
            return False  # no candidates worked out
    
    def generate_soprano(self) -> bool:
        """Attempts to generate a valid soprano line for the chorale. Returns True if successful, False otherwise."""
        return self._try_generate_soprano_for_index(0)


if __name__ == "__main__":
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

    print("Generating Soprano...")
    generator = ChoraleGenerator(chorale, random_seed=42)
    success = generator.generate_soprano()
    if success:
        print("Generated Chorale with Soprano:")
        print(generator.chorale)
    else:
        print("Failed to generate a valid soprano line.")
