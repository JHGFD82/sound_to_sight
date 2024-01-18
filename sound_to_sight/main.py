import os
import argparse
from csv_reader import MidiCsvParser
from utils import (export_timeline, export_player_definitions, export_pattern_definitions, export_project_details,
                   calculate_fps, music_to_video_length)

MIN_FPS = 24
MAX_FPS = 60


def main(file_list, fps, video_resolution, sections=None):
    # FILE IMPORT
    for file in file_list:
        if not os.path.isfile(file):
            raise FileNotFoundError(
                f'Failed to open file "{file}". Please ensure that the file exists and that you have entered the '
                f'correct file name.')

    # ADD SECTIONS
    if sections is None:
        print("No sections provided via command-line arguments.")
        sections = (input("If the music has sections you want to designate, enter their bar numbers here separated by "
                          "spaces, or simply hit enter to continue: ").split())

    music = []

    for file in file_list:
        midi_parser = MidiCsvParser(file, fps, sections)
        music_instance, bpm, notes_per_bar, division, total_length = midi_parser.parse()
        pattern_fps = calculate_fps(bpm, notes_per_bar, MIN_FPS, MAX_FPS)
        project_length = music_to_video_length(total_length, bpm, fps)
        music.append(music_instance)

    print('done!')

    export_timeline(music[0], 'timeline.json')
    export_pattern_definitions(music[0], 'patterns.json')
    export_player_definitions(music[0], 'players.json')


# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description="Process some files.")
#     parser.add_argument("-i", "--input_files", nargs="+", help="List of files to process.")
#     parser.add_argument("-s", "--sections", nargs="+", default=None, help="List of sections (if any).")
#     parser.add_argument("-a", "--action_safe", action="store_true",
#                         help="Boolean to accommodate action safe zones in video pixel resolution")
#     parser.add_argument('-b', '--bpm', type=float, required=True, help='Beats per minute of the song')
#     parser.add_argument('-f', '--fps', type=float, required=True, help='Frames per second of the video')
#     args = parser.parse_args()
#
#     main(args.input_files, args.bpm, args.fps, args.sections, args.action_safe)


main(['../../Six Marimbas/Music/Six.csv'], 60, [3840, 2160], sections=[329, 676])
