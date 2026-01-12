from typing import List, Tuple, Dict, Optional
from random import Random

from v2.pitch import Pitch
from v2.tonality import *
from v2.chorale import Chorale, VerticalHarmonization, ChordInversion, RealizedHarmony, RealizedChorale
from v2.chorale_generator import ChoraleGenerator
from v2.audio_output import chorale_to_midi_file, chorales_to_midi_file, convert_midi_to_file


def test_chorale_with_temperatures(
    chorale: Chorale,
    temperatures: List[float],
    random_seed: int = 42,
    midi_filename: str = "out/test_chorale_v2_output.mid",
    audio_filename: str = "out/test_chorale_v2_output.mp3"
) -> List[RealizedChorale]:
    """
    Generate and test a chorale with different temperature settings.
    
    Args:
        chorale: The Chorale puzzle to solve
        temperatures: List of temperature values to test (e.g., [0.0, 1.0, 5.0])
        random_seed: Random seed for reproducibility (default 42)
        midi_filename: Output MIDI filename
        audio_filename: Output audio filename
    
    Returns:
        List of generated RealizedChorale objects
    """
    output_chorales = []
    
    for temperature in temperatures:
        generator = ChoraleGenerator(chorale, random_seed=random_seed, temperature=temperature)
        print(f"Generating chorale with temperature {temperature}...")
        success = generator.generate()
        
        if success:
            realized_chorale = generator.get_output_chorale()
            print(f"- Successfully generated chorale at temperature {temperature}")
            print(realized_chorale)
            output_chorales.append(realized_chorale)
        else:
            print(f"- Failed to generate chorale at temperature {temperature}")
    
    # Output all generated chorales to MIDI and audio
    if output_chorales:
        print(f"\nGenerating MIDI and audio output to {midi_filename}...")
        chorales_to_midi_file(output_chorales, midi_filename)
        convert_midi_to_file(midi_filename, audio_filename)
        print(f"Done. Output saved to:\n  - {midi_filename}\n  - {audio_filename}")
    else:
        print("No chorales were successfully generated.")
    
    return output_chorales


if __name__ == "__main__":
    if False: # DISABLED TEMPORARILY
        # Example: simple I-V two-chord chorale
        c_major_key = KeySignature(Pitch.from_note_name("C"), is_major=True)
        harmonizations = [
            VerticalHarmonization(
                bass_note=c_major_key.encode_octave(TONIC, 3),  # C3
                chord=TonalChord(root=TONIC, quality=ChordQuality.MAJOR),  # I chord
                soprano_hint=c_major_key.encode_octave(MAJOR_MEDIANT, 5),  # E5
            ),
            VerticalHarmonization(
                bass_note=c_major_key.encode_octave(DOMINANT, 3),  # G3
                chord=TonalChord(root=DOMINANT, quality=ChordQuality.MAJOR),  # V chord
            ),
            VerticalHarmonization(
                bass_note=c_major_key.encode_octave(TONIC, 3),  # C3
                chord=TonalChord(root=TONIC, quality=ChordQuality.MAJOR),  # I chord
            ),
            VerticalHarmonization(
                bass_note=c_major_key.encode_octave(TONIC, 3),  # C3
                chord=TonalChord(root=TONIC, quality=ChordQuality.MAJOR),  # I chord
            ),
            VerticalHarmonization(
                bass_note=c_major_key.encode_octave(DOMINANT, 3),  # G3
                chord=TonalChord(root=TONIC, quality=ChordQuality.MAJOR),  # I chord
            ),
            VerticalHarmonization(
                bass_note=c_major_key.encode_octave(DOMINANT, 3),  # G3
                chord=TonalChord(root=DOMINANT, quality=ChordQuality.MAJOR),  # V chord
            ),
            VerticalHarmonization(
                bass_note=c_major_key.encode_octave(TONIC, 3),  # C3
                chord=TonalChord(root=TONIC, quality=ChordQuality.MAJOR),  # I chord
            ),
        ]

        # Create the chorale puzzle
        chorale = Chorale(c_major_key, harmonizations)
        print("Initial Chorale Puzzle:")
        print(chorale)
        print("\n" + "="*40 + "\n")
        
        # Test with different temperatures
        temperatures = [0.0, 1.0, 5.0, 100.0]
        output_chorales = test_chorale_with_temperatures(
            chorale,
            temperatures,
            random_seed=42,
            midi_filename="out/chorale_c_major_temperature_output.mid",
            audio_filename="out/chorale_c_major_temperature_output.mp3"
        )

    f_minor_key = KeySignature(Pitch.from_note_name("F"), is_major=False)
    # i i6 V viiº4/3 i6 V7 i
    f_minor_harmonizations = [
        VerticalHarmonization(
            bass_note=f_minor_key.encode_octave(TONIC, 2),  # F2
            chord=TonalChord(root=TONIC, quality=ChordQuality.MINOR),  # i chord
            soprano_hint=f_minor_key.encode_octave(DOMINANT, 5),  # C5
            alto_hint=f_minor_key.encode_octave(MINOR_MEDIANT, 4),  # Ab4
            tenor_hint=f_minor_key.encode_octave(MINOR_MEDIANT, 3),  # Ab3
        ),
        VerticalHarmonization(
            bass_note=f_minor_key.encode_octave(MINOR_MEDIANT, 2),  # Ab3
            chord=TonalChord(root=TONIC, quality=ChordQuality.MINOR),  # i chord
        ),
        VerticalHarmonization(
            bass_note=f_minor_key.encode_octave(DOMINANT, 3),  # C3
            chord=TonalChord(root=DOMINANT, quality=ChordQuality.MAJOR),  # V chord
        ),
        VerticalHarmonization(
            bass_note=f_minor_key.encode_octave(SUBDOMINANT, 2),  # Bb2
            chord=TonalChord(root=LEADING_TONE, quality=ChordQuality.FULLY_DIMINISHED_SEVENTH),  # viiº4/3 chord
        ),
        VerticalHarmonization(
            bass_note=f_minor_key.encode_octave(MINOR_MEDIANT, 2),  # Ab3
            chord=TonalChord(root=TONIC, quality=ChordQuality.MINOR),  # i6 chord
        ),
        VerticalHarmonization(
            bass_note=f_minor_key.encode_octave(DOMINANT, 3),  # C3
            chord=TonalChord(root=DOMINANT, quality=ChordQuality.DOMINANT_SEVENTH),  # V7 chord
        ),
        VerticalHarmonization(
            bass_note=f_minor_key.encode_octave(TONIC, 2),  # F2
            chord=TonalChord(root=TONIC, quality=ChordQuality.MINOR),  # i chord
        ),
    ]
    f_minor_chorale = Chorale(f_minor_key, f_minor_harmonizations)
    print("Initial F Minor Chorale Puzzle:")
    print(f_minor_chorale)
    print("\n" + "="*40 + "\n")
    temperatures = [0.0, 1.0, 5.0, 100.0]
    output_chorales_minor = test_chorale_with_temperatures(
        f_minor_chorale,
        temperatures,
        random_seed=123,
        midi_filename="out/chorale_f_minor_temperature_output.mid",
        audio_filename="out/chorale_f_minor_temperature_output.mp3"
    )
