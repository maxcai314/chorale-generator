# Convert chorales to midi, and midi to audio using FluidSynth.

from mido import MidiFile, MidiTrack, Message, MetaMessage, bpm2tempo
import os
import subprocess
from typing import List

from pitch import Pitch
from tonality import ScaleDegree, TonalChord, KeySignature, ChordQuality, scale_degree_to_interval
from bassline import HarmonizedBassline
from chorale import Chorale

def chorale_to_midi_file(chorale: Chorale, filename: str, bpm: int = 80):
    chorales_to_midi_file([chorale], filename, bpm=bpm)

def chorales_to_midi_file(chorales: List[Chorale], filename: str, bpm: int = 80):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    tpb = mid.ticks_per_beat # Ticks per beat, default is usually 480

    track.append(MetaMessage('set_tempo', tempo=bpm2tempo(bpm), time=0))
    # 0 for Acoustic Grand Piano, 20 for Church Organ, 60 for Muted Trumpet
    # https://midiprog.com/program-numbers/
    track.append(Message('program_change', program=0, time=0))

    attack_velocity = 96
    note_offset = tpb // 256  # slight offset to avoid note-on and note-off at same tick

    for chorale in chorales:
        # Play the soprano and bass notes together for each chord
        # Last chord is for double the duration
        for i in range(chorale.num_chords()):
            bass_note = chorale.get_bass_note(i)
            soprano_note = chorale.get_soprano_note(i)

            # Sustain pedal on
            track.append(Message('control_change', control=64, value=127, time=0))

            if bass_note is not None:
                track.append(Message('note_on', note=bass_note.midi_index, velocity=attack_velocity, time=0))
            if soprano_note is not None:
                track.append(Message('note_on', note=soprano_note.midi_index, velocity=attack_velocity, time=0))

            # Hold notes for a half note (2 beats)
            duration_ticks = tpb * 2
            if i == chorale.num_chords() - 1:
                duration_ticks = tpb * 4  # last chord held for whole note

            if bass_note is not None:
                track.append(Message('note_off', note=bass_note.midi_index, velocity=attack_velocity, time=0))
            if soprano_note is not None:
                track.append(Message('note_off', note=soprano_note.midi_index, velocity=attack_velocity, time=0))
            
            # wait for duration
            track.append(Message('note_on', note=0, velocity=0, time=duration_ticks - note_offset))
            
            # Sustain pedal off
            track.append(Message('control_change', control=64, value=0, time=0))

            # wait for offset
            track.append(Message('note_on', note=0, velocity=0, time=note_offset))

    mid.save(filename)
    print(f"Created MIDI file: {filename}")


def convert_midi_to_wav(midi_file: str, audio_file: str, soundfont="~/.fluidsynth/default_sound_font.sf2"):
    soundfont = os.path.expanduser(soundfont)
    # fluidsynth -F "${WAVFILE}" $SOUNDFONT "${filename}"
    command = ["fluidsynth", "-F", audio_file, soundfont, midi_file]
    subprocess.run(command, check=True)

    print(f"Converted MIDI to audio file: {audio_file}")

def convert_midi_to_mp3(midi_file: str, mp3_file: str, soundfont="~/.fluidsynth/default_sound_font.sf2", temp_wav_file="out/temp_output.wav"):
    convert_midi_to_wav(midi_file, temp_wav_file, soundfont=soundfont)
    # Use lame to convert wav to mp3
    command = ["lame", temp_wav_file, mp3_file]
    subprocess.run(command, check=True)
    os.remove(temp_wav_file)
    print(f"Converted MIDI to MP3 file: {mp3_file}")

def convert_midi_to_file(midi_file: str, output_file: str, soundfont="~/.fluidsynth/default_sound_font.sf2"):
    _, ext = os.path.splitext(output_file)
    ext = ext.lower()
    if ext == ".wav":
        convert_midi_to_wav(midi_file, output_file, soundfont=soundfont)
    elif ext == ".mp3":
        convert_midi_to_mp3(midi_file, output_file, soundfont=soundfont)
    else:
        raise ValueError(f"Unsupported output file format: {ext}")

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

    chorale.set_soprano_note(0, Pitch.from_note_name("E", 5))
    chorale.set_soprano_note(1, Pitch.from_note_name("F", 5))
    chorale.set_soprano_note(2, Pitch.from_note_name("F", 5))
    chorale.set_soprano_note(3, Pitch.from_note_name("E", 5))

    print("Chorale:")
    print(chorale)

    midi_filename = "out/chorale_output.mid"
    audio_filename = "out/chorale_output.wav"

    chorale_to_midi_file(chorale, midi_filename)
    convert_midi_to_wav(midi_filename, audio_filename)
    print("Done.")
