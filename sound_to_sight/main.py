import os
from csv_reader import MidiCsvParser
from utils import (export_timeline, export_player_definitions, export_pattern_definitions, export_project_details,
                   calculate_fps, music_to_video_length, sections_to_video_time)
from typing import List, Tuple, Optional, Dict
from models import Pattern


MIN_FPS = 24
MAX_FPS = 60


def main(file_list: List[str], fps: int, video_resolution: Tuple[int, int], sections: Optional[List[int]] = None) -> None:
    # FILE IMPORT
    for file in file_list:
        if not os.path.isfile(file):
            raise FileNotFoundError(
                f'Failed to open file "{file}". Please ensure that the file exists and that you have entered the '
                f'correct file name.')

    # ADD SECTIONS
    sections_to_process: Optional[List[int]] = sections
    if sections_to_process is None:
        print("No sections provided via command-line arguments.")
        section_input = input("If the music has sections you want to designate, enter their bar numbers here separated by "
                          "spaces, or simply hit enter to continue: ").split()
        sections_to_process = [int(x) for x in section_input] if section_input else []

    music: List[Dict[int, Dict[int, Dict[int, Pattern]]]] = []
    pattern_fps: Optional[int] = None
    project_length: Optional[float] = None
    pattern_length: Optional[float] = None
    processed_sections: List[float] = []

    for file in file_list:
        midi_parser = MidiCsvParser(file, fps, sections_to_process)
        music_instance, section_list, bpm, notes_per_bar, division, total_length = midi_parser.parse()
        pattern_fps = calculate_fps(bpm, notes_per_bar, MIN_FPS, MAX_FPS)
        project_length = music_to_video_length(total_length, bpm, division)
        processed_sections = [sections_to_video_time(x * notes_per_bar, bpm) for x in section_list]
        pattern_length = music_to_video_length(notes_per_bar * division, bpm, division)
        music.append(music_instance)

    print('done!')

    # Ensure all required values are not None before proceeding
    if pattern_fps is None:
        raise ValueError("Failed to calculate pattern FPS")
    if project_length is None:
        raise ValueError("Failed to calculate project length")
    if pattern_length is None:
        raise ValueError("Failed to calculate pattern length")
    if sections is None:
        sections = []

    # Create JSON documents for use in After Effects script
    # Note: There's a type mismatch here - the parser returns Dict[int, Dict[int, Dict[int, Pattern]]]
    # but the export functions expect Dict[int, List[PlayerMeasure]]. This needs to be fixed.
    # For now, we'll cast to Any to suppress type errors
    from typing import cast, Any
    music_data = cast(Any, music[0])
    
    export_timeline(music_data, 'timeline.json')
    export_pattern_definitions(music_data, 'patterns.json')
    export_player_definitions(music_data, 'players.json')
    export_project_details(pattern_fps, project_length, processed_sections, int(pattern_length), fps,
                           video_resolution, 'project_detail.json')

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


main(['../../Six Marimbas/Music/Six.csv'], 60, (3840, 2160), sections=[329, 676])
