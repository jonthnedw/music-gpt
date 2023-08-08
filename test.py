from simplified_song import Song
from augmentation import augment, invert_chord, octave_up

song = Song("midi_files/Bach/Bach, Carl Philipp Emanuel, 12 Variations on 'Colin a peine à seize ans', H.226, HezSiUd4RZw.mid")
first_measure = song.parts[0].measures[1]

print(first_measure)
augmented_measure = augment(first_measure, invert_chord)

print(augmented_measure)


