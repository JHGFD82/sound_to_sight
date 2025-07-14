import json
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from BPMtoFPS import ticks_to_seconds, beats_to_seconds  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from .models import PlayerMeasure


def export_project_details(pattern_fps: int, project_length: float, sections: List[Any], 
                          pattern_length: int, fps: int, video_resolution: Tuple[int, int], 
                          filename: str) -> None:
    project_details: Dict[str, Any] = {'pattern_fps': pattern_fps,
                       'project_length': project_length,
                       'sections': sections,
                       'pattern_length': pattern_length,
                       'fps': fps,
                       'video_resolution': video_resolution}

    with open(filename, 'w') as json_file:
        json.dump(project_details, json_file, indent=4)


def export_timeline(player_measures_dict: Dict[int, List["PlayerMeasure"]], filename: str) -> None:
    section_dict: Dict[int, Dict[int, Dict[int, Dict[Optional[int], int]]]] = {}
    for player in player_measures_dict.values():
        for player_measure in player:
            sec = player_measure.section_number
            meas = player_measure.measure_number
            player_num = player_measure.player_number
            pattern_hash = player_measure.pattern.hash
            play_count = player_measure.play_count

            sec_dict = section_dict.setdefault(sec, {})
            meas_dict = sec_dict.setdefault(meas, {})
            meas_dict[player_num] = {pattern_hash: play_count}

    section_dict = {key: dict(sorted(inner_dict.items())) for key, inner_dict in section_dict.items()}

    with open(filename, 'w') as json_file:
        json.dump(section_dict, json_file, indent=4)


def export_player_definitions(player_measures_dict: Dict[int, List["PlayerMeasure"]], filename: str) -> None:
    player_definitions: Dict[int, Dict[str, str]] = {}
    for player in player_measures_dict.values():
        player_number = player[0].player_number
        instrument = player[0].instrument
        footage = player[0].footage
        layout = player[0].pattern.notes[0].layout

        player_definitions[player_number] = {'instrument': instrument, 'layout': layout, 'footage': footage}

    with open(filename, 'w') as json_file:
        json.dump(player_definitions, json_file, indent=4)


def export_pattern_definitions(player_measures_dict: Dict[int, List["PlayerMeasure"]], filename: str) -> None:
    pattern_definitions: Dict[str, Dict[Optional[int], List[List[Any]]]] = {}
    processed_hashes: set[Optional[int]] = set()  # Set to keep track of processed pattern hashes

    for player in player_measures_dict.values():
        for player_measure in player:
            pattern_hash = player_measure.pattern.hash

            # Skip this pattern if it's already been processed
            if pattern_hash in processed_hashes:
                continue

            # Add the hash to the set of processed hashes
            processed_hashes.add(pattern_hash)

            for note in player_measure.pattern.notes:
                layout = note.layout
                frame_start = note.frame_start
                note_value = note.note_value
                velocity = note.velocity
                frame_duration = note.frame_duration
                x = note.x
                y = note.y

                layout_dict = pattern_definitions.setdefault(layout, {})
                hash_dict = layout_dict.setdefault(pattern_hash, [])
                hash_dict.append([frame_start, note_value, velocity, frame_duration, [x, y]])

    # Sort the pattern definitions
    pattern_definitions = {key: dict(sorted(inner_dict.items())) for key, inner_dict in pattern_definitions.items()}

    with open(filename, 'w') as json_file:
        json.dump(pattern_definitions, json_file)


def calculate_fps(bpm: float, beats_per_measure: int, fps_min: int = 24, fps_max: int = 60) -> Optional[int]:
    # Calculate the duration of one measure in seconds
    duration_of_one_measure = (60 * beats_per_measure) / bpm

    # Iterate through the FPS range to find integer values
    for fps in range(fps_max, fps_min - 1, -1):
        frames_per_measure = fps * duration_of_one_measure

        # Check if the frames per measure is an integer
        if frames_per_measure.is_integer():
            print(f"Adjusting frame rate of patterns to {fps} frames per second.")
            return fps

    return None


def music_to_video_length(length: int, bpm: float, division: int) -> float:
    return ticks_to_seconds(length, int(bpm), division)


def sections_to_video_time(section: int, bpm: float) -> float:
    return beats_to_seconds(section, int(bpm))
