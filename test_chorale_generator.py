from pitch import Pitch
from tonality import ScaleDegree, TonalChord, KeySignature, ChordQuality, scale_degree_to_interval
from bassline import HarmonizedBassline
from chorale import Chorale
from chorale_generator import ChoraleGenerator

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
