from typing import List, Tuple, Dict
from random import Random

from pitch import Pitch
from tonality import ScaleDegree, TonalChord, KeySignature, ChordQuality, scale_degree_to_interval
from bassline import HarmonizedBassline
from chorale import Chorale
from chorale_generator import ChoraleGenerator
from audio_output import chorale_to_midi_file, chorales_to_midi_file, convert_midi_to_file

def test_chorale_generator(key_signature: KeySignature,
                           bass_harmonizations: List[Tuple[Pitch, TonalChord]],
                           soprano_hints: Dict[int, Pitch],
                           random_seed: int = 42,
                           bpm: int = 80,
                           midi_filename: str = "out/test_chorale_output.mid",
                           audio_filename: str = "out/test_chorale_output.mp3") -> Chorale:
    bassline = HarmonizedBassline(key_signature, bass_harmonizations)
    chorale = Chorale(bassline)
    for index, pitch in soprano_hints.items():
        chorale.set_soprano_note(index, pitch)

    print("Generating Chorale...")
    generator = ChoraleGenerator(chorale, random_seed=random_seed)
    success = generator.generate_soprano()
    if success:
        print("Generated Chorale with Soprano:")
        print(generator.chorale)
    else:
        print("Failed to generate a valid soprano line.")
        return None

    chorale_to_midi_file(generator.chorale, midi_filename, bpm=bpm)
    convert_midi_to_file(midi_filename, audio_filename)
    print("Done.")
    return generator.chorale

def test_chorale_generator_multi(key_signature: KeySignature,
                           bass_harmonizations: List[Tuple[Pitch, TonalChord]],
                           soprano_hints: Dict[int, Pitch],
                           seed_seed: int = 67,
                           num_trials: int = 5,
                           bpm: int = 80,
                           midi_filename: str = "out/test_chorale_output.mid",
                           audio_filename: str = "out/test_chorale_output.mp3") -> List[Chorale]:
    """
    Creates multiple chorales using different random seeds, returning a list of successful chorales.
    The generated chorales are saved to a single MIDI and WAV file.
    """
    bassline = HarmonizedBassline(key_signature, bass_harmonizations)
    chorale = Chorale(bassline)
    for index, pitch in soprano_hints.items():
        chorale.set_soprano_note(index, pitch)

    result: List[Chorale] = []

    random_seeder = Random(seed_seed)

    for trial in range(num_trials):
        print(f"Generating Chorale Trial {trial + 1}...")
        generator = ChoraleGenerator(chorale, random_seed=random_seeder.randint(0, 2**32 - 1))
        success = generator.generate_soprano()
        if success:
            print("Generated Chorale with Soprano:")
            print(generator.chorale)
            result.append(generator.chorale)
        else:
            print("Failed to generate a valid soprano line.")
            break  # stop on first failure
    
    print(f"Saving {len(result)} chorales to MIDI and WAV...")

    chorales_to_midi_file(result, midi_filename, bpm=bpm)
    convert_midi_to_file(midi_filename, audio_filename)
    print("Done.")
    return result

if __name__ == "__main__":
    b_flat_major_key = KeySignature(Pitch.from_note_name("Bb"), is_major=True)
    bass_harmonizations = [  # I V6 I I6 ii V I
        (Pitch.from_note_name("Bb", 2), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("A", 2), TonalChord(ScaleDegree.DOMINANT, ChordQuality.MAJOR)),
        (Pitch.from_note_name("Bb", 2), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("D", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("Eb", 3), TonalChord(ScaleDegree.SUPERTONIC, ChordQuality.MINOR)),
        (Pitch.from_note_name("F", 3), TonalChord(ScaleDegree.DOMINANT, ChordQuality.MAJOR)),
        (Pitch.from_note_name("Bb", 2), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
    ]
    soprano_hints = {
        0: Pitch.from_note_name("Bb", 4),  # starting pitch
    }
    soprano_hints = {}  # no hints

    test_chorale_generator_multi(b_flat_major_key, bass_harmonizations, soprano_hints,
                                 seed_seed=12345, num_trials=3,
                                 bpm=120,
                                 midi_filename="out/test_major_chorale_output.mid",
                                 audio_filename="out/test_major_chorale_output.mp3")
    
    g_minor_key = KeySignature(Pitch.from_note_name("G"), is_major=False)
    bass_harmonizations_minor = [  # i V6 i iv i6/4 V I
        (Pitch.from_note_name("G", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MINOR)),
        (Pitch.from_note_name("F#", 3), TonalChord(ScaleDegree.DOMINANT, ChordQuality.MAJOR)),
        (Pitch.from_note_name("G", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MINOR)),
        (Pitch.from_note_name("C", 3), TonalChord(ScaleDegree.SUBDOMINANT, ChordQuality.MAJOR)),
        (Pitch.from_note_name("D", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MINOR)),
        (Pitch.from_note_name("D", 3), TonalChord(ScaleDegree.DOMINANT, ChordQuality.MAJOR)),
        (Pitch.from_note_name("G", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),  # picardy third
    ]
    soprano_hints_minor = {
        0: Pitch.from_note_name("D", 5),  # starting pitch
        -1: Pitch.from_note_name("B", 4),  # picardy third ending
    }
    test_chorale_generator_multi(g_minor_key, bass_harmonizations_minor, soprano_hints_minor,
                                 seed_seed=54321, num_trials=3,
                                 bpm=120,
                                 midi_filename="out/test_minor_chorale_output.mid",
                                 audio_filename="out/test_minor_chorale_output.mp3")

    c_minor_key = KeySignature(Pitch.from_note_name("C"), is_major=False)

    c_minor_bass_harmonizations = [
        (Pitch.from_note_name("C", 3),  TonalChord(ScaleDegree.TONIC,       ChordQuality.MINOR)),       # i
        (Pitch.from_note_name("F", 3),  TonalChord(ScaleDegree.SUBDOMINANT, ChordQuality.MINOR)),       # iv
        (Pitch.from_note_name("G", 3),  TonalChord(ScaleDegree.TONIC,       ChordQuality.MINOR)),       # i6/4 (passing)
        (Pitch.from_note_name("Ab", 3), TonalChord(ScaleDegree.SUBDOMINANT, ChordQuality.MINOR)),       # iv6
        (Pitch.from_note_name("F", 3),  TonalChord(ScaleDegree.SUPERTONIC,  ChordQuality.DIMINISHED)),  # ii°6
        (Pitch.from_note_name("G", 3),  TonalChord(ScaleDegree.TONIC,       ChordQuality.MINOR)),       # i6/4 (cadential)
        (Pitch.from_note_name("G", 3),  TonalChord(ScaleDegree.DOMINANT,    ChordQuality.MAJOR)),       # V (uses B♮ implied)
    ]

    c_minor_soprano_hints = {
        # 0: Pitch.from_note_name("C", 5),   # starting pitch
    }

    test_chorale_generator_multi(c_minor_key, c_minor_bass_harmonizations, c_minor_soprano_hints,
                                seed_seed=12345, num_trials=3, bpm=120,
                                midi_filename="out/c_minor_prog.mid",
                                audio_filename="out/c_minor_prog.mp3")
    
    c_major_key = KeySignature(Pitch.from_note_name("C"), is_major=True)
    one_five_one_five_one_bass_harmonizations = [
        (Pitch.from_note_name("C", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("B", 2), TonalChord(ScaleDegree.DOMINANT, ChordQuality.MAJOR)),
        (Pitch.from_note_name("C", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("F", 3), TonalChord(ScaleDegree.SUBDOMINANT, ChordQuality.MAJOR)),
        (Pitch.from_note_name("G", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("G", 3), TonalChord(ScaleDegree.DOMINANT, ChordQuality.MAJOR)),
        (Pitch.from_note_name("C", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
    ]
    one_five_one_five_one_soprano_hints = { }
    test_chorale_generator_multi(c_major_key, one_five_one_five_one_bass_harmonizations, one_five_one_five_one_soprano_hints,
                                 seed_seed=67890, num_trials=5,
                                 bpm=120,
                                 midi_filename="out/test_one_five_one_five_one_chorale_output.mid",
                                 audio_filename="out/test_one_five_one_five_one_chorale_output.mp3")
    
    arpeggiated_bass_harmonizations = [
        (Pitch.from_note_name("C", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("E", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("G", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("G", 3), TonalChord(ScaleDegree.DOMINANT, ChordQuality.MAJOR)),
        (Pitch.from_note_name("G", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("G", 3), TonalChord(ScaleDegree.DOMINANT, ChordQuality.DOMINANT_SEVENTH)),
        (Pitch.from_note_name("C", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
    ]
    arpeggiated_soprano_hints = {}
    test_chorale_generator_multi(c_major_key, arpeggiated_bass_harmonizations, arpeggiated_soprano_hints,
                                 seed_seed=13579, num_trials=5,
                                 bpm=120,
                                 midi_filename="out/test_arpeggiated_chorale_output.mid",
                                 audio_filename="out/test_arpeggiated_chorale_output.mp3")
    
    c_minor_key = KeySignature(Pitch.from_note_name("C"), is_major=False)
    bass_harmonizations_phrygian_half_cadence = [  # i iv6 iv6 V
        (Pitch.from_note_name("C", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MINOR)),
        (Pitch.from_note_name("Ab", 3), TonalChord(ScaleDegree.SUBDOMINANT, ChordQuality.MINOR)),
        (Pitch.from_note_name("Ab", 3), TonalChord(ScaleDegree.SUBDOMINANT, ChordQuality.MINOR)),
        (Pitch.from_note_name("G", 3), TonalChord(ScaleDegree.DOMINANT, ChordQuality.MAJOR)),
    ]
    soprano_hints_phrygian_half_cadence = { }
    test_chorale_generator_multi(c_minor_key, bass_harmonizations_phrygian_half_cadence, soprano_hints_phrygian_half_cadence,
                                 seed_seed=24680, num_trials=5,
                                 bpm=120,
                                 midi_filename="out/test_phrygian_half_cadence_chorale_output.mid",
                                 audio_filename="out/test_phrygian_half_cadence_chorale_output.mp3")
    


