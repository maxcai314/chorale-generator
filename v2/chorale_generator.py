"""
The algorithm for choosing candidate voicings for a chorale puzzle,
making sure to obey the rules of voice leading while also
generating musically pleasing results.
"""

from typing import List, Optional, Tuple
from random import Random
from .pitch import Pitch
from .tonality import *
from .chorale import Chorale, VerticalHarmonization, ChordInversion, RealizedHarmony, RealizedChorale


def is_valid_voice_leading(preprevious: Optional[Tuple[VerticalHarmonization, RealizedHarmony]], previous: Optional[Tuple[VerticalHarmonization, RealizedHarmony]], current: Tuple[VerticalHarmonization, RealizedHarmony]) -> bool:
    """Checks whether the voice leading from previous to current is valid."""
    # No voice overlap: alto may not cross previous soprano, etc.
    if current[1].has_voice_crossing():
        return False
    if previous is not None:
        if previous[1].has_voice_crossing():
            return False
        if current[1].alto.semitones >= previous[1].soprano.semitones:
            return False
        if current[1].tenor.semitones >= previous[1].alto.semitones:
            return False
        if current[1].bass.semitones >= previous[1].tenor.semitones:
            return False
    
    # Check for parallel fifths and octaves
    if previous is not None:
        voice_pairs = [
            (previous[1].soprano, previous[1].alto, current[1].soprano, current[1].alto),
            (previous[1].soprano, previous[1].tenor, current[1].soprano, current[1].tenor),
            (previous[1].soprano, previous[1].bass, current[1].soprano, current[1].bass),
            (previous[1].alto, previous[1].tenor, current[1].alto, current[1].tenor),
            (previous[1].alto, previous[1].bass, current[1].alto, current[1].bass),
            (previous[1].tenor, previous[1].bass, current[1].tenor, current[1].bass),
        ]
        
        for v1_prev, v2_prev, v1_curr, v2_curr in voice_pairs:
            interval_prev = v2_prev.interval_to(v1_prev)
            interval_curr = v2_curr.interval_to(v1_curr)
            perfect_fifth = TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.PERFECT)
            octave = TonalInterval.from_size_and_quality(IntervalSize.OCTAVE, IntervalQuality.PERFECT)
            if v1_prev.interval_to(v1_curr).semitones == 0:
                continue  # static motion, skip
            if interval_prev.truncated() == perfect_fifth and interval_curr.truncated() == perfect_fifth:
                return False  # parallel fifths
            if interval_prev.truncated() == octave and interval_curr.truncated() == octave:
                return False  # parallel octaves
    
    # Check for direct fifths and octaves
    # Where the soprano and bass moves in similar motion, where soprano leaps into a perfect fifth or octave with bass
    if previous is not None:
        soprano_motion = current[1].soprano.minus(previous[1].soprano)
        bass_motion = current[1].bass.minus(previous[1].bass)
        if soprano_motion.semitones * bass_motion.semitones > 0:  # similar motion
            if abs(soprano_motion.scale_steps) > IntervalSize.SECOND:  # soprano leapt
                interval_curr = current[1].bass.interval_to(current[1].soprano)
                perfect_fifth = TonalInterval.from_size_and_quality(IntervalSize.FIFTH, IntervalQuality.PERFECT)
                octave = TonalInterval.from_size_and_quality(IntervalSize.OCTAVE, IntervalQuality.PERFECT)
                if interval_curr.truncated() == perfect_fifth or interval_curr.truncated() == octave:
                    return False  # direct fifths/octaves
    
    # Check for resolution of previous tendency tones in soprano
    # Leading tone scale degree 7 should resolve up to tonic (scale degree 1)
    # Dominant chord's scale degree 4 should resolve down to scale degree 3
    if previous is not None:
        prev_harmonization, prev_voicing = previous
        curr_harmonization, curr_voicing = current
        soprano_prev = prev_voicing.soprano
        soprano_curr = curr_voicing.soprano
        
        # Check leading tone resolution
        if soprano_prev.normalized() == LEADING_TONE:
            if soprano_curr.normalized() != TONIC:
                return False  # leading tone did not resolve to tonic
        
        # Check dominant chord 4th resolution
        prev_chord_root = prev_harmonization.chord.root
        if prev_chord_root.normalized() in (DOMINANT, LEADING_TONE):  # V or vii chord
            if soprano_prev.normalized() == SUBDOMINANT:
                if not soprano_curr.normalized() in (MAJOR_MEDIANT, MINOR_MEDIANT):
                    return False  # dominant chord 4th did not resolve to mediant
    
    # The leading tone of scale degree 7 and the scale degree 4 when in dominant chords may not be doubled
    curr_harmonization, curr_voicing = current
    if LEADING_TONE in curr_voicing.get_doubled_tones():
        return False  # leading tone doubled
    if curr_harmonization.chord.root.normalized() in (DOMINANT, LEADING_TONE):  # V or vii chord
        if SUBDOMINANT in curr_voicing.get_doubled_tones():
            return False  # dominant chord 4th doubled
    
    # In second inversion chords, the bass must be doubled; no other tone may be doubled
    is_seventh_chord = curr_harmonization.chord.quality in {
        ChordQuality.MAJOR_SEVENTH, ChordQuality.MINOR_SEVENTH, ChordQuality.DOMINANT_SEVENTH,
        ChordQuality.HALF_DIMINISHED_SEVENTH, ChordQuality.FULLY_DIMINISHED_SEVENTH
    }
    if curr_harmonization.get_inversion() == ChordInversion.SECOND and not is_seventh_chord:
        doubled_tones = curr_voicing.get_doubled_tones()
        if len(doubled_tones) != 1 or doubled_tones[0] != curr_harmonization.bass_note.normalized():
            return False  # invalid doubling in second inversion chord
    
    # Soprano may not make augmented/diminished melodic intervals
    # Soprano may not leap more than a fifth
    if previous is not None:
        prev_harmonization, prev_voicing = previous
        curr_harmonization, curr_voicing = current
        soprano_prev = prev_voicing.soprano
        soprano_curr = curr_voicing.soprano
        melodic_interval = soprano_curr.minus(soprano_prev)
        if melodic_interval.normalized().quality in (IntervalQuality.AUGMENTED, IntervalQuality.DIMINISHED):
            return False  # invalid melodic interval in soprano
        if abs(melodic_interval.scale_steps) > IntervalSize.FIFTH:
            return False  # soprano leap too large
    
    # Cross relations (chromatic alterations in different voices) are not allowed
    if previous is not None:
        prev_harmonization, prev_voicing = previous
        curr_harmonization, curr_voicing = current
        voices_prev = [prev_voicing.soprano, prev_voicing.alto, prev_voicing.tenor, prev_voicing.bass]
        voices_curr = [curr_voicing.soprano, curr_voicing.alto, curr_voicing.tenor, curr_voicing.bass]
        for i in range(4):
            for j in range(4):
                if i != j:
                    # make sure there is no chromatic alteration between voices i and j
                    # where both play the same scale degree but different pitches (due to chromatic alterations)
                    note_prev = voices_prev[i].normalized()
                    note_curr = voices_curr[j].normalized()
                    if note_prev.scale_steps == note_curr.scale_steps:
                        if note_prev.semitones != note_curr.semitones:
                            return False  # cross relation detected
    
    # Check for correct approach/exit of leaps in soprano
    if previous is not None and preprevious is not None:
        _, preprev_voicing = preprevious
        _, prev_voicing = previous
        _, curr_voicing = current
        soprano_preprev = preprev_voicing.soprano
        soprano_prev = prev_voicing.soprano
        soprano_curr = curr_voicing.soprano
        
        # if lept between preprev and prev, now we must make a stepwise motion in opposite direction
        leap_interval = soprano_prev.minus(soprano_preprev)
        if abs(leap_interval.scale_steps) > IntervalSize.THIRD:
            # There was a leap into soprano_prev; check approach to and exit from this note
            leap_interval = soprano_prev.minus(soprano_preprev)
            exit_interval = soprano_curr.minus(soprano_prev)
            if (leap_interval.semitones * exit_interval.semitones) >= 0:
                return False  # didn't step away from leap in opposite direction (should be negative)
            if abs(exit_interval.scale_steps) > IntervalSize.SECOND:
                return False  # did not step away from leap in conjunct motion
        
        # if leapt between prev and curr, must have approached prev in stepwise motion from opposite direction
        leap_interval = soprano_curr.minus(soprano_prev)
        if abs(leap_interval.scale_steps) > IntervalSize.THIRD:
            # There is a leap into soprano_curr; check approach to soprano_prev
            approach_interval = soprano_prev.minus(soprano_preprev)
            leap_interval = soprano_curr.minus(soprano_prev)
            if (approach_interval.semitones * leap_interval.semitones) >= 0:
                return False  # didn't step into leap in opposite direction (should be negative)
            if abs(approach_interval.scale_steps) > IntervalSize.SECOND:
                return False  # did not step into leap in conjunct motion

    return True  # all checks passed


MINOR_PENALTY = 1
MEDIUM_PENALTY = 3
MAJOR_PENALTY = 5

def calculate_voicing_cost(previous: Optional[Tuple[VerticalHarmonization, RealizedHarmony]], current: Tuple[VerticalHarmonization, RealizedHarmony]) -> int:
    """Calculates a cost for the given voicing choice. Lower is better."""
    cost = 0
    curr_harmonization, curr_voicing = current
    
    # Smooth voice leading
    if previous is not None:
        prev_harmonization, prev_voicing = previous
        # Prefer stepwise motion and conjunct motion in inner voices
        for voice_prev, voice_curr in [(prev_voicing.alto, curr_voicing.alto), (prev_voicing.tenor, curr_voicing.tenor)]:
            melodic_interval = voice_prev.interval_to(voice_curr)
            interval_size = abs(melodic_interval.scale_steps)
            if interval_size != 0:
                cost += MEDIUM_PENALTY  # medium penalty for not choosing common tone
            if interval_size > IntervalSize.THIRD:
                cost += interval_size * MINOR_PENALTY  # additional penalty for even larger motions
        # prefer stepwise in soprano (or conjunct)
        soprano_melodic_interval = prev_voicing.soprano.interval_to(curr_voicing.soprano)
        soprano_interval_size = abs(soprano_melodic_interval.scale_steps)
        if soprano_interval_size == 0:
            # cost += MINOR_PENALTY  # minor penalty for static (boring) motion
            if prev_voicing.bass == curr_voicing.bass:
                cost += MEDIUM_PENALTY  # extra penalty for both soprano and bass static, super boring
        elif soprano_interval_size == IntervalSize.SECOND:
            cost += 0  # no penalty for stepwise motion
        elif soprano_interval_size == IntervalSize.THIRD:
            # cost += MINOR_PENALTY  # minor penalty for third
            cost += 0  # no penalty for third, since sometimes it's nice to have a little bit of motion in the soprano
        elif soprano_interval_size == IntervalSize.FOURTH or soprano_interval_size == IntervalSize.FIFTH:
            # cost += MINOR_PENALTY * 2  # double penalty for fourth or fifth
            cost += MEDIUM_PENALTY  # medium penalty for fourth or fifth, since we generally want to avoid large leaps in the soprano
    
    # Prefer contrary motion between soprano and bass
    if previous is not None:
        prev_harmonization, prev_voicing = previous
        soprano_motion = curr_voicing.soprano.minus(prev_voicing.soprano)
        bass_motion = curr_voicing.bass.minus(prev_voicing.bass)
        motion_product = soprano_motion.semitones * bass_motion.semitones
        if motion_product < 0:
            cost += 0  # reward for contrary motion
        elif motion_product == 0 and soprano_motion.semitones != 0:
            cost += 0  # reward for oblique motion
        else:
            cost += MINOR_PENALTY  # penalty for similar motion
    
    # Strongly prefer to double the root or fifth of chord
    doubled_tones = curr_voicing.get_doubled_tones()
    root = curr_harmonization.chord.get_scale_tones()[0].normalized()
    fifth = curr_harmonization.chord.get_scale_tones()[2].normalized()
    for tone in doubled_tones:
        if tone == root or tone == fifth:
            cost += 0  # no penalty for doubling root or fifth
        else:
            cost += MAJOR_PENALTY  # major penalty for doubling other tones
    
    # Strongly prefer to resolve tendency tones in inner voices too
    if previous is not None:
        prev_harmonization, prev_voicing = previous
        curr_harmonization, curr_voicing = current
        alto_prev = prev_voicing.alto
        alto_curr = curr_voicing.alto
        tenor_prev = prev_voicing.tenor
        tenor_curr = curr_voicing.tenor

        for voice_prev, voice_curr in [(alto_prev, alto_curr), (tenor_prev, tenor_curr)]:
            # Check leading tone resolution
            if voice_prev.normalized() == LEADING_TONE:
                if voice_curr.normalized() != TONIC:
                    cost += MAJOR_PENALTY  # leading tone did not resolve to tonic
            
            # Check dominant chord 4th resolution
            prev_chord_root = prev_harmonization.chord.root
            if prev_chord_root.normalized() in (DOMINANT, LEADING_TONE):  # V or vii chord
                if voice_prev.normalized() == SUBDOMINANT:
                    if not voice_curr.normalized() in (MAJOR_MEDIANT, MINOR_MEDIANT):
                        cost += MAJOR_PENALTY  # dominant chord 4th did not resolve to mediant
    
    # Prefer representing the fifth in dominant seventh chords, even though it can be omitted
    if curr_harmonization.chord.quality == ChordQuality.DOMINANT_SEVENTH:
        fifth_tone = curr_harmonization.chord.get_scale_tones()[2]
        if not curr_voicing.contains_tone(fifth_tone):
            cost += MEDIUM_PENALTY  # penalty for omitting the fifth in dominant seventh chord
    
    # if all voicings are exactly the same, major penalty (extremely boring)
    if previous is not None:
        prev_harmonization, prev_voicing = previous
        if prev_voicing == curr_voicing:
            cost += MAJOR_PENALTY * 2  # big penalty for no change at all
    
    return cost * 1000


class ChoraleGenerator:
    def __init__(self, chorale: Chorale, random_seed: int=42, temperature: float=0.0):
        self.realized_chorale = RealizedChorale(chorale)
        self.random = Random(random_seed)
        self.temperature = temperature
    
    def _try_choose_voicing_for_index(self, index: int) -> bool:
        """
        Uses a depth-first recursive backtracking approach to choose a realization for the chorale.
        If successful, a valid realization will be set up in self.realized_chorale, and returns True.
        If unsuccessful, returns False and leaves the chorale unchanged.
        """
        chorale = self.realized_chorale.chorale
        previous_voicing = self.realized_chorale.realized_voicings[index - 1] if index > 0 else None
        preprevious_voicing = self.realized_chorale.realized_voicings[index - 2] if index > 1 else None
        choices = list(chorale.candidates[index])
        self.random.shuffle(choices)

        # first, filter out illegal voice leading
        choices = [choice for choice in choices if is_valid_voice_leading(
            (chorale.harmonizations[index - 2], preprevious_voicing) if preprevious_voicing is not None else None,
            (chorale.harmonizations[index - 1], previous_voicing) if previous_voicing is not None else None,
            (chorale.harmonizations[index], choice)
        )]

        # next, label each choice with its cost, which includes a random component based on temperature
        choice_costs = []
        for choice in choices:
            base_cost = calculate_voicing_cost(
                (chorale.harmonizations[index - 1], previous_voicing) if previous_voicing is not None else None,
                (chorale.harmonizations[index], choice)
            )
            random_component = self.random.uniform(-self.temperature, self.temperature)
            total_cost = base_cost + random_component
            choice_costs.append((choice, total_cost))
        
        # sort choices by cost
        choice_costs.sort(key=lambda x: x[1])
        sorted_choices = [x[0] for x in choice_costs]

        # in our order of preference, try choices until we succeed
        for choice in sorted_choices:
            self.realized_chorale.realized_voicings[index] = choice
            if index == chorale.num_harmonizations() - 1:
                if self.realized_chorale.is_done():
                    return True
                else:
                    raise ValueError("Chorale should be done here; this should not happen")
            else:
                # recurse to next index
                if self._try_choose_voicing_for_index(index + 1):
                    return True # success
        else:
            # no choice worked; backtrack
            self.realized_chorale.realized_voicings[index] = None
            return False
    
    def generate(self) -> bool:
        """Generates a realized chorale."""
        return self._try_choose_voicing_for_index(0)
    
    def get_output_chorale(self) -> RealizedChorale:
        """Returns the generated realized chorale."""
        return self.realized_chorale


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
        VerticalHarmonization(
            bass_note=c_major_key.encode_octave(TONIC, 2),  # C2
            chord=TonalChord(root=TONIC, quality=ChordQuality.MAJOR),  # I chord
        ),
        VerticalHarmonization(
            bass_note=c_major_key.encode_octave(TONIC, 2),  # C2
            chord=TonalChord(root=TONIC, quality=ChordQuality.MAJOR),  # I chord
        ),
        VerticalHarmonization(
            bass_note=c_major_key.encode_octave(DOMINANT, 2),  # G2
            chord=TonalChord(root=TONIC, quality=ChordQuality.MAJOR),  # I chord
        ),
        VerticalHarmonization(
            bass_note=c_major_key.encode_octave(DOMINANT, 2),  # G2
            chord=TonalChord(root=DOMINANT, quality=ChordQuality.MAJOR),  # V chord
        ),
        VerticalHarmonization(
            bass_note=c_major_key.encode_octave(TONIC, 2),  # C2
            chord=TonalChord(root=TONIC, quality=ChordQuality.MAJOR),  # I chord
        ),
    ]

    chorale = Chorale(c_major_key, harmonizations)
    print(chorale)
    generator = ChoraleGenerator(chorale, random_seed=42, temperature=0.0)
    print(f"Generating chorale with temperature {generator.temperature}...")
    success = generator.generate()
    if success:
        realized_chorale = generator.get_output_chorale()
        print("Successfully generated chorale voicings.")
        print("Generated Chorale with Voicings:\n")
        print(realized_chorale)
    else:
        print("Failed to generate chorale voicings.")    
