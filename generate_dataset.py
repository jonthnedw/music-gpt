from io import TextIOWrapper
from augmentation import augment, jitter, octave_down, octave_up, invert_chord
from simplified_song import Song, Measure
from typing import List
from glob import glob
from random import shuffle, randint, choice

MAX_SEQ = 256
MAX_N_ROWS = 25000

MIDI_FILES_PATH = "./midi_files"
OUTPUT_FILE_PATH = f"dataset_{MAX_SEQ}.txt"

augmentation_list = [jitter, octave_down, octave_up, invert_chord]


def write_row(
    measures: List[Measure], ptr: int, file: TextIOWrapper, seq_len=MAX_SEQ
) -> int:
    seq = measures[ptr].as_string(tokenize=True)
    n_notes = measures[ptr].num_notes

    ptr += 1
    next_seq = None

    while ptr < len(measures):
        next_seq = measures[ptr].as_string(tokenize=True)

        if len(seq) + len(next_seq) < seq_len:
            seq += next_seq
            n_notes += measures[ptr].num_notes

        ptr += 1

    file.write(" ".join(seq) + "\n")
    return n_notes


def write_part(
    measures: List[Measure], file: TextIOWrapper, step=2, seq_len=MAX_SEQ
) -> int:
    n_notes = 0
    n_rows = 0
    for i in range(0, len(measures), step):
        n_notes += write_row(measures, i, file, seq_len)
        n_rows += 1

    print(f"Wrote part with {n_notes} notes to {n_rows} rows")
    return n_notes, n_rows


def main():
    bach = list(glob(MIDI_FILES_PATH + "/Bach/*.mid", recursive=True))
    bach = [f for f in bach if "Bach, Johann Sebastian" in f]
    ghibli = list(glob(MIDI_FILES_PATH + "/ghibli_dataset/*.mid", recursive=True))

    file_names = ghibli + bach

    n_notes = 0
    n_rows = 0
    with open(OUTPUT_FILE_PATH, "w") as f_ptr:
        for i, name in enumerate(file_names):
            song = Song(path=name)

            if song.parsed:
                print(f"Song {i+1}/{len(file_names)}.")
                for part in song.parts:
                    notes, rows = write_part(part.measures, f_ptr)
                    n_notes += notes
                    n_rows += rows

                    augmented = [
                        augment(m, choice(augmentation_list)) for m in part.measures
                    ]
                    notes, rows = write_part(augmented, f_ptr, step=4)
                    n_notes += notes
                    n_rows += rows
            if n_rows > MAX_N_ROWS:
                break
    print(f"Dataset generation complete. Total number {n_notes}, Total rows {n_rows}")
    # with open(OUTPUT_FILE_PATH, "w") as dataset_file:
    #     for name in file_names:
    #         s = Song(path=name)
    #         if s.parsed:
    #             for part in s.parts:
    #                 row = []
    #                 measures = []
    #                 for measure in part.measures:
    #                     tokens = measure.as_string(tokenize=True)
    #                     if len(row) + len(tokens) < MAX_SEQ:
    #                         row += tokens
    #                         measures.append(measure)
    #                     else:
    #                         num_rows += 1
    #                         print(
    #                             f"Writing row, row number: {num_rows}, len: {len(row)}"
    #                         )
    #                         dataset_file.write(" ".join(row) + "\n")

    #                         # Augment measure
    #                         augment_choice = choice(augmentation_list)
    #                         aug_seq = " ".join(
    #                             [str(augment(m, augment_choice)) for m in measures]
    #                         )
    #                         num_rows += 1
    #                         print(
    #                             f"Writing augmented row, row number: {num_rows}, len: {len(row)}"
    #                         )
    #                         dataset_file.write(aug_seq + "\n")

    #                         row = tokens
    #                         measures = [measure]

    #                 # Add last measure
    #                 num_rows += 2
    #                 dataset_file.write(" ".join(row) + "\n")
    #                 augment_choice = choice(augmentation_list)
    #                 aug_seq = " ".join(
    #                     [str(augment(m, augment_choice)) for m in measures]
    #                 )
    #                 dataset_file.write(aug_seq + "\n")


if __name__ == "__main__":
    main()
