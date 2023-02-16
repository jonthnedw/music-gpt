from simplified_song import Measure, Note, Chord
from copy import deepcopy
from random import randint

JITTER_RANGE = 10


def augment(m: Measure, augmentation) -> Measure:
    n_m: Measure = deepcopy(m)

    for note_or_chord in n_m.measure_data:
        if augmentation == invert_chord:
            if isinstance(note_or_chord, Chord):
                augmentation(note_or_chord)
            continue
        if isinstance(note_or_chord, Chord):
            for note in note_or_chord.notes:
                augmentation(note)
        elif isinstance(note_or_chord, Note):
            augmentation(note_or_chord)
    return n_m


def jitter(note: Note) -> None:
    note.velocity += randint(-JITTER_RANGE, JITTER_RANGE)


def octave_up(note: Note) -> None:
    if int(note.name[-1]) + 1 < 10:
        note.name = note.name[:-1] + str(int(note.name[-1]) + 1)


def octave_down(note: Note) -> None:
    if int(note.name[-1]) - 1 > 0:
        note.name = note.name[:-1] + str(int(note.name[-1]) - 1)


def invert_chord(chord: Chord) -> None:
    octave_down(chord.notes[-1])
