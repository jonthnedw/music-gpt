from fractions import Fraction
from random import randint

from typing import List, Union
from music21.stream import Measure as m21Measure
from music21.note import Note as m21Note
from music21.chord import Chord as m21Chord
from music21.stream import Part as m21Part
from music21.meter import TimeSignature
from music21.converter import parse as m21parse
from music21.stream import Score
from music21.midi.translate import streamToMidiFile


def string_to_time_signature(s: str) -> tuple:
    return tuple(s.split("/"))


def time_signature_to_string(t: tuple) -> str:
    return f"{t[0]}/{t[1]}"


class Note:
    """
    The representation of a note is a sequence of numbers. For the model to
    learn music generation, each note is represented as a sequence of 4 components:
    pitch value, duration, offset in measure, velocity.

    A full note representation:
        G#4 0.5 2.5 130 = G#4 half note that is 2.5 quarter notes in the measure
            with 130 velocity.
    """

    def __init__(
        self,
        m21_note: m21Note = None,
        string: str = None,
        string_list: List[str] = None,
    ) -> None:
        self.name: str = None
        self.duration: float = None
        self.offset: float = None
        self.velocity: int = None

        if m21_note:
            self.name = m21_note.pitch.nameWithOctave
            self.duration = float(round(m21_note.quarterLength, 2))
            self.offset = float(round(m21_note.offset, 2))
            self.velocity = int(m21_note.volume.velocity)

        elif string_list or string:
            if string:
                string_list = string.split(" ")
            if len(string_list) != 4:
                raise Exception(f"Cannot convert string list {string_list} to note.")
            self.name = string_list[0]
            self.duration = float(string_list[1])
            self.offset = float(string_list[2])
            self.velocity = int(string_list[3])
        else:
            raise Exception("Object required for note")

    def music21(self) -> m21Note:
        note = m21Note(self.name)
        note.quarterLength = self.duration
        note.offset = self.offset
        note.volume.velocity = self.velocity
        return note

    def as_string(
        self, duration=True, offset=True, velocity=True, tokenize=False
    ) -> str:
        s = [self.name]
        if duration:
            s.append(str(self.duration))
        if offset:
            s.append(str(self.offset))
        if velocity:
            s.append(str(self.velocity))
        return s if tokenize else " ".join(s)

    def __str__(self) -> str:
        return self.as_string()


class Chord:
    def __init__(
        self,
        m21_chord: m21Chord = None,
        string: str = None,
        string_list: List[str] = None,
    ) -> None:
        self.notes: List[Note] = []

        if m21_chord:
            m21_chord.sortAscending()
            for note in m21_chord:
                note.offset += m21_chord.offset
                self.notes.append(Note(note))

        elif string_list or string:
            if string:
                string_list = string.split(" ")

            if len(string_list) % 4 != 0 or len(string_list) == 0:
                raise Exception("String list for chord should be multiple of 4")

            for i in range(int(len(string_list) / 4)):
                self.notes.append(Note(string_list=string_list[i * 4 : i * 4 + 4]))
        else:
            raise Exception("Object required for chord")

        self.offset = self.notes[0].offset

    def music21(self) -> m21Chord:
        return m21Chord([n.music21() for n in self.notes])

    def as_string(
        self, duration=True, offset=True, velocity=True, tokenize=False
    ) -> str:
        s = []
        for note in self.notes:
            if tokenize:
                s += note.as_string(duration, offset, velocity, tokenize)
            else:
                s.append(note.as_string(duration, offset, velocity, tokenize))
        return s if tokenize else " ".join(s)

    def __str__(self) -> str:
        return self.as_string()


class Measure:
    def __init__(
        self,
        time_signature: tuple,
        offset: Fraction = None,
        measure_data: m21Measure = None,
        string: str = None,
        string_list: List[str] = None,
    ) -> None:
        self.time_signature = time_signature
        self.offset = offset
        self.measure_data: List[Union[Note, Chord]] = []
        self.num_notes = 0

        if measure_data:
            # Flatten data
            measure_data = measure_data.flatten()
            for data in measure_data:
                if isinstance(data, m21Note):
                    self.measure_data.append(Note(data))
                    self.num_notes += 1

                elif isinstance(data, m21Chord):
                    self.measure_data.append(Chord(data))
                    self.num_notes += 1

        elif string_list or string:
            if string:
                string_list = string.split(" ")
            if len(string_list) % 4 != 0 or len(string_list) == 0:
                raise Exception("String list for a measure should be multiple of 4.")

            i = 0
            while i < len(string_list):
                j = i + 4
                while j < len(string_list) and string_list[i + 2] == string_list[j + 2]:
                    j += 4
                seq = string_list[i:j]
                data = Note(string_list=seq) if j - i == 4 else Chord(string_list=seq)
                self.num_notes += (j - i) / 4
                self.measure_data.append(data)
                i = j

    def music21(self) -> m21Measure:
        measure = m21Measure(
            timeSignature=TimeSignature(
                f"{self.time_signature[0]}/{self.time_signature[1]}"
            )
        )
        for note_or_chord in self.measure_data:
            offset = note_or_chord.offset
            measure.insert(offset, note_or_chord.music21())
        return measure

    def as_string(
        self, duration=True, offset=True, velocity=True, tokenize=False
    ) -> str:
        # Start with time signature
        s = [f"{self.time_signature[0]}/{self.time_signature[1]}"]

        for note_or_chord in self.measure_data:
            if tokenize:
                s += note_or_chord.as_string(duration, offset, velocity, tokenize)
            else:
                s.append(note_or_chord.as_string(duration, offset, velocity, tokenize))

        return s if tokenize else " ".join(s)

    def __str__(self) -> str:
        return self.as_string()


# Instrument containing a sequence of notes and chords
class Instrument:
    def __init__(
        self, stream: m21Part = None, string: str = None, string_list: List[str] = None
    ) -> None:
        self.measures: List[Measure] = []
        self.num_notes = None

        if stream:
            if len(stream.flat.notes) == 0:
                raise Exception("Instrument stream is empty.")

            self.num_notes = len(stream.flat.notes)

            base_time_signature = (4, 4)
            for measure in stream.getElementsByClass(m21Measure):
                if measure.timeSignature is not None:
                    base_time_signature = (
                        measure.timeSignature.numerator,
                        measure.timeSignature.denominator,
                    )
                self.measures.append(Measure(base_time_signature, measure_data=measure))

        elif string_list or string:
            if string:
                string_list = string.split(" ")

            measure = []
            time_signature_present = False
            n_notes = 0
            for i in range(len(string_list)):
                if "/" not in string_list[i]:
                    n_notes += 1
                else:
                    if time_signature_present:
                        time_signature = string_to_time_signature(measure[0])
                        self.measures.append(
                            Measure(time_signature, string_list=measure[1:])
                        )
                        measure = []
                    else:
                        time_signature_present = True
                measure.append(string_list[i])
            self.num_notes = n_notes

    def music21(self) -> m21Part:
        part = m21Part(id=str(len(self.measures)))
        part.append([measure.music21() for measure in self.measures])

        return part

    def as_string(
        self, duration=True, offset=True, velocity=True, tokenize=False
    ) -> str:
        s = []
        for measure in self.measures:
            if tokenize:
                s += measure.as_string(duration, offset, velocity)
            else:
                s.append(measure.as_string(duration, offset, velocity))

        return s if tokenize else " ".join(s)

    def __str__(self) -> str:
        return self.as_string()


class Song:
    def __init__(
        self,
        path: str = None,
        string: str = None,
        string_list: List[str] = None,
        transpose: int = None,
    ) -> None:
        self.name: str = None
        self.parts: List[Instrument] = None
        self.time_signature = None
        self.num_notes = 0
        self.parsed = False

        try:
            if path.endswith(".mid"):
                stream = m21parse(path)
                parts = stream.parts.stream()

                if transpose:
                    parts = parts.transpose(transpose)

                self.time_signature = (
                    stream.flat.timeSignature.numerator,
                    stream.flat.timeSignature.denominator,
                )
                self.name = path[(-(path[::-1].find("/"))) : -4]
                self.parts = [Instrument(part, self.time_signature) for part in parts]
                self.parsed = True
                self.num_notes = sum([i.num_notes for i in self.parts])
                print(
                    f"Loaded Song: {self.name} with {len(parts)} parts and {self.num_notes} notes."
                )
            elif path.endswith(".txt"):
                with open(path, "r") as f:
                    lines = f.readlines()
                    self.parts = [Instrument(string=" ".join(lines))]
                    self.num_notes = self.parts[0].num_notes
                    self.name = path[(-(path[::-1].find("/"))) : -4]
                    self.parsed = True
                    print(
                        f"Loaded Song: {self.name} with {len(parts)} parts and {self.num_notes} notes."
                    )
            elif string_list or string:
                if string:
                    string_list = string.split(" ")
                self.parts = [Instrument(string_list=string_list)]
                self.num_notes = self.parts[0].num_notes
                self.name = "song_" + str(randint(1, 9999))
                self.parsed = True

        except Exception as e:
            print(f"Failed to load song with path: {path}, exception: {e}.")

    def to_midi(self, path: str) -> None:
        score = Score()

        for i, part in enumerate(self.parts):
            score.insert(i, part.music21())
        file = streamToMidiFile(score)
        file.open(path, "wb")
        file.write()
        file.close()

    def to_text(self, path: str) -> None:
        with open(path, "w") as f:
            for part in self.parts:
                for measure in part.measures:
                    f.write(str(measure) + "\n")
