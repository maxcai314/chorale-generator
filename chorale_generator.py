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

        # Prioritize static/stepwise motion and de-prioritize leaps, with random tie-breaks to keep variety.
        def motion_key(note: Pitch):
            prev = self.chorale.get_soprano_note(index - 1) if index > 0 else None
            if prev is None:
                return (0, self.random.random())  # no context, keep it mostly random
            interval = abs(prev.distance_to(note))
            if interval == 0:
                category = 12  # repeated note
            elif interval <= 2:
                category = 10  # stepwise (m2/M2)
            elif interval <= 4:
                category = 15  # small leap (m3/M3)
            else:
                category = 30  # larger leap
            # if contrary motion with bass, prioritize more
            bass_note = self.chorale.get_bass_note(index)
            prev_bass = self.chorale.get_bass_note(index - 1) if index > 0 else None
            if prev_bass is not None and bass_note is not None:
                bass_motion = bass_note.distance_to(prev_bass)
                soprano_motion = note.distance_to(prev) if prev is not None else 0
                motion_product = bass_motion * soprano_motion
                if motion_product < 0:
                    category -= 3  # strongly favor contrary motion
                elif motion_product == 0:
                    category -= 1  # favor oblique motion
                else:
                    category += 3  # disfavor similar motion
            return (self.random.randint(0, category), self.random.random())
        
        candidate_notes = list((i, motion_key(i)) for i in self.chorale.get_soprano_candidates(index))
        candidate_notes.sort(key=lambda x: x[1])  # sort by motion preference
        candidate_notes = [i[0] for i in candidate_notes]  # extract sorted notes

        # candidate_notes = list(self.chorale.get_soprano_candidates(index))
        # self.random.shuffle(candidate_notes)  # randomize order to avoid deterministic patterns
        
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
