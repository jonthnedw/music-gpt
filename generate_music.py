from augmentation import jitter, octave_down, octave_up, invert_chord
from sys import argv
from transformers import pipeline
from random import choice, randint
from simplified_song import Instrument, Song, Note

DEFAULT_MODEL_PATH = "music-gpt2-2.3"

NOTES = ["A", "B", "C", "D", "E", "F", "G"]
ACCIDENTAL = ["#", "-", ""]
OCTAVE = ["2", "3", "4"]

TIME_SIGNATURE_TOP = ["3", "4"]
TIME_SIGNATURE_BOTTOM = ["4"]

ITERATIONS = 10


def main():
    print(f"Loading model at path {DEFAULT_MODEL_PATH}")
    generator = pipeline("text-generation", model=DEFAULT_MODEL_PATH)

    in_seq = choice(TIME_SIGNATURE_TOP) + "/" + choice(TIME_SIGNATURE_BOTTOM)
    in_seq += f" {choice(NOTES) + choice(ACCIDENTAL) + choice(OCTAVE)}"
    print(f"Generating sequence with initial input: {in_seq}")

    song_seq = []

    for _ in range(ITERATIONS):
        output = generator(in_seq, max_length=256)[0]

        output = output["generated_text"]
        output, last_note = Instrument.sanitize(output)

        song_seq += output

        augmentation = jitter

        seq = output[last_note:-1] if "/" in output[-1] else output[last_note:]

        n = Note(string_list=seq)
        augmentation(n)
        in_seq = str(n)

        print(f"Next in seq {in_seq}")

    s = Song(string_list=song_seq)

    s.to_midi("test.mid")


if __name__ == "__main__":
    main()
