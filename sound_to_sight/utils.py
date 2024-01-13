import json


def export_to_json(player_measures_dict, filename):
    section_dict = {}
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

    # Step 1: Create a sorted list of keys
    section_dict = {key: dict(sorted(inner_dict.items())) for key, inner_dict in section_dict.items()}

    with open(filename, 'w') as json_file:
        json.dump(section_dict, json_file, indent=4)
