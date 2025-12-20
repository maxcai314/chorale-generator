from pitch import Pitch
from tonality import ScaleDegree, TonalChord, KeySignature, ChordQuality, scale_degree_to_interval
from bassline import HarmonizedBassline
from chorale import Chorale
from chorale_generator import ChoraleGenerator
from audio_output import chorale_to_midi_file, convert_midi_to_wav

if __name__ == "__main__":
    c_major_key = KeySignature(Pitch.from_note_name("Bb"), is_major=True)
    bass_harmonizations = [  # I V6 I I6 ii V I
        (Pitch.from_note_name("Bb", 2), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("A", 2), TonalChord(ScaleDegree.DOMINANT, ChordQuality.MAJOR)),
        (Pitch.from_note_name("Bb", 2), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("D", 3), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
        (Pitch.from_note_name("Eb", 3), TonalChord(ScaleDegree.SUPERTONIC, ChordQuality.MINOR)),
        (Pitch.from_note_name("F", 3), TonalChord(ScaleDegree.DOMINANT, ChordQuality.MAJOR)),
        (Pitch.from_note_name("Bb", 2), TonalChord(ScaleDegree.TONIC, ChordQuality.MAJOR)),
    ]
    bassline = HarmonizedBassline(c_major_key, bass_harmonizations)
    chorale = Chorale(bassline)
    chorale.set_soprano_note(0, Pitch.from_note_name("Bb", 4)) # starting pitch

    print("Generating Chorale...")
    generator = ChoraleGenerator(chorale, random_seed=42)
    success = generator.generate_soprano()
    if success:
        print("Generated Chorale with Soprano:")
        print(generator.chorale)
    else:
        print("Failed to generate a valid soprano line.")
        exit(1)

    midi_filename = "out/test_chorale_output.mid"
    audio_filename = "out/test_chorale_output.wav"

    chorale_to_midi_file(generator.chorale, midi_filename)
    convert_midi_to_wav(midi_filename, audio_filename)
    print("Done.")