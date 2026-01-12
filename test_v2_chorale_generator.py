from typing import List, Tuple, Dict
from random import Random

from v2.pitch import Pitch
from v2.tonality import *
from v2.chorale import Chorale, VerticalHarmonization, ChordInversion, RealizedHarmony, RealizedChorale
from v2.chorale_generator import ChoraleGenerator
from v2.audio_output import chorale_to_midi_file, chorales_to_midi_file, convert_midi_to_file

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

    output_chorales_c_major = []

    chorale = Chorale(c_major_key, harmonizations)
    print(chorale)

    for temperature in [0.0, 1.0, 5.0, 100.0]:
        generator = ChoraleGenerator(chorale, random_seed=42, temperature=temperature)
        print(f"Generating chorale with temperature {generator.temperature}...")
        success = generator.generate()
        if success:
            realized_chorale = generator.get_output_chorale()
            print("Successfully generated chorale voicings.")
            print("Generated Chorale with Voicings:\n")
            print(realized_chorale)
            output_chorales_c_major.append(realized_chorale)
        else:
            print("Failed to generate chorale voicings.")    
    
    # Output to MIDI files
    midi_filename = "out/chorale_c_major_temperature_output.mid"
    audio_filename = "out/chorale_c_major_temperature_output.mp3"

    chorales_to_midi_file(output_chorales_c_major, midi_filename)
    convert_midi_to_file(midi_filename, audio_filename)
    print("Done.")
