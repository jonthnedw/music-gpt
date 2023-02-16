from simplified_song import Song

string = "4/4 G3 1.0 0.0 80 G2 1.0 0.0 80 G3 1.0 0.5 80 G2 1.0 0.5 80 G3 1.0 1.0 80 G2 1.0 1.0 80 G3 1.0 1.5 80 G2 1.0 1.5 80 G3 1.0 2.0 80 G2 1.0 2.0 80 G3 1.0 2.5 80 G2 1.0 2.5 80 G3 1.0 3.0 80 G2 1.0 3.0 80 G3 1.0 3.5 80 G2 1.0 3.5 80 4/4 F#2 0.5 0.0 80 F#3 0.5 0.5 80 F#2 0.5 1.0 80 F#3 0.5 1.5 80 F#2 0.5 2.0 80 F#3 0.5 2.5 80 F#2 0.5 3.0 80 F#3 0.5 3.5 80 4/4 F#2 0.5 0.0 80 F#3 0.5 0.5 80 F#2 0.5 1.0 80 F#3 0.5 1.5 80 F#2 0.5 2.0 80 F#3 0.5 2.5 80 F#2 0.5 3.0 80 F#3 0.5 3.5 80 4/4 F#2 0.5 0.0 80 F#3 0.5 0.5 80 F#3 0.5 1.0 80 F#3 0.5 1.5 80 F#3 0.5 2.0 80 F#3 0.5 3.0 80 F#3 0.5 3.5 80 F#3 0.5 3.5 80 4/4 E-3 0.5 3.0 80 F#3 0.5 3.5 80 4/4 E-3 0.5 3.0 80 F#3 0.5 3.0 80 4/4 E-3 0.5 0.5 80 F#3 0.5 3.5 80 4/4 A3 0.5 0.5 80 4/4 A3 0.5 0.5 80"
s = Song(string=string)
s.to_midi("test.mid")