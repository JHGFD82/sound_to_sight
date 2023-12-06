# Six Marimbas Visualizer
Documentation of progress with building a music visualizer for the Steve Reich composition "Six Marimbas" (1986)

"Six Marimbas" by Steve Reich is hopefully the start of a visualization project that I plan to adapt to visualize the composer's more complicated works, in an attempt to translate the tonality of the works into combinations of colors, shapes, and animations. This first composition is ideal as a starting point for a data- and script-driven project due to a few convenient factors:

1. The only instrument in the piece is marimba. This means that if one were to translate an instrument into a shape, then only one shape is needed.
2. All notes played in the composition are eighth notes. The lack of diversity in note length may translate to more consistent animations.
3. While the piece is played at a fast tempo of 192 BPM, there is no variations in speed or note placement anywhere throughout its duration. This is typical of Reich's work which primarily focuses on music as a gradual process over a consistent pulse. Animating the piece is therefore easier than pieces that include ramps in speed due to note assignments coming down to mathematical precision, versus placing animations based on an artist's interpretation of the change in speed.

# Developing the Data

There are numerous recordings of "Six Marimbas" that can be used as the basis for the visualizer. However, the lack of a conductor or metronome and the direction given by Reich for the player to control the flow of the piece makes them inadequate for a video project where rigid timing is mandatory. This, of course, goes against Reich's own wishes for how the piece should be performed. Indeed, analyzing the original score published by Boosey & Hawkes results in every measure of the piece being notated with a suggested repetition count (e.g., "8x-12x", "2x-3x"), and entire sections where one marimba player is directed to advance to the next measure only when another player performing the same musical phrase advances to the next measure first. Despite this, visualizing the music at a rigid tempo may still provide insight into the visual translation of harmony inherent in the work. With a structure in place to optimize the placement of colors, shapes, and animations, further adjustments to adapt to actual recordings would become a practical exercise and could also produce interesting results in video form. The "data" of this project, therefore, is the music itself, interpreted in rigid structural form, in digital format.

## The Score

The score for "Six Marimbas" is written in the D-flat major scale, which consists of D-flat, E-flat, F, G-flat, A-flat, B-flat, and C notes, and is written in the 4/4 time signature. Players are given a suggested number of repeats for each measure, for a total of 163 measures. The tempo is marked as 192 BPM with no ramps contained to modify the play speed internally. Players are, however, given relative directions for the strength of their playing, with the highest direction given near the end ("ff", fortissimo, marimba 6, bar 153), and various moments of players being instructed to ramp down their playing volune to silence.

To translate the piece into data, Logic Pro was used to transcribe the written score into MIDI format (resulting audio files not included in this repository). Three versions of the composition were produced in the software:

1. Base - The initial reconstruction of the composition. Features digital audio workspace productivity enhancements such as loops, automation, and panning to aid the process of transcription. Adjustments to the transcription were made here first and then adjusted into the versions explained below.
2. Midi - The composition at its most basic form, panning is removed, automation on note velocity converted to flat integers, and loops rendered as solid regions, resulting in one audio block per instrument, which is then exported into separate MIDI files ("Six Marimbas Track 1", "Six Marimbas Track 2", etc.).
3. Audio - For use in the video, this version includes additional enhancements such as quantization randomization, variable note lengths and velocities, and mastering to mimic a realistic sound environment, which still maintaining a consistent structure. The resulting mix was then exported to lossless AIFF format ("Six Marimbas audio.aiff"), not included in this repository.

## The conversion

The first part of translating MIDI files into usable data involved converting them into CSV format using [MIDICSV](https://www.fourmilab.ch/webtools/midicsv/). A Python script ("MusicData.py") was then constructed to transform the CSV output into a Pandas DataFrame, including timings, pitch placement, velocities, and player.

## The Video

The final construction of the visualizer should take place in Blender, however initial experiments are being conducted in Adobe After Effects. Project files and exports are not included in this repository.