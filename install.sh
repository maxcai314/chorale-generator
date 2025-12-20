echo "Installing sound fonts:"

# let's store this sound font as default
mkdir -p ~/.fluidsynth
wget "https://ftp.osuosl.org/pub/musescore/soundfont/MuseScore_General/MuseScore_General.sf2" -O ~/.fluidsynth/default_sound_font.sf2

echo "Installed sound fonts:"
ls -lh ~/.fluidsynth/