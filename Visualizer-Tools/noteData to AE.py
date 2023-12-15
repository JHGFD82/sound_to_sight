import csv
import json

def parse_csv(file_path):
	"""
	Parse the CSV file and return the data as a list of dictionaries.

	Each dictionary represents a row in the CSV, with keys corresponding to the column headers.
	"""
	data = []
	with open(file_path, newline='') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			# Convert certain fields to their appropriate data types
			row['time'] = int(row['time'])
			row['note'] = int(row['note'])
			row['velocity'] = int(row['velocity'])
			row['player'] = int(row['player'])
			row['section'] = int(row['section'])
			row['y'] = float(row['y'])
			row['side'] = row['side'] == 'True'
			row['frames'] = int(row['frames'])
			data.append(row)
	return data


def find_repeating_groups(data):
    groups = []
    group_counts = {}
    current_group = []
    current_group_num = 0
    current_time_frame = 1

    for row in data:
        # Check if the row's time is within the current time frame
        if current_time_frame <= row['time'] < current_time_frame + 8:
            current_group.append(row)
            # Special case for player 6
            if row['player'] == 6 and len(current_group) == 8:
                # Your criteria for the first 8 notes of player 6 go here
                pass
        elif row['player'] == 6 and current_time_frame <= row['time'] < current_time_frame + 16:
            pass
        else:
            if current_group:
                current_group_num += 1
                section_number = current_group[0]['section']
                player_number = current_group[0]['player']
                group_name = f"{section_number}-{player_number}-{current_group_num}"

                # Count the group occurrence
                if group_name not in groups[-1]['name']:
                    groups.append({'name': group_name, 'group': current_group, 'count': 1})
                else:
                    groups[-1]['count'] += 1

            # Start a new group
            current_group = [row]
            current_time_frame = row['time'] - (row['time'] % 8) + 1

        # Special handling for the last group
        if row is data[-1] and current_group:
            group_id = ''.join([f"{r['note']}-{r['velocity']}" for r in current_group])
            section_number = current_group[0]['section']
            player_number = current_group[0]['player']
            group_name = f"{section_number}-{player_number}-{group_id}"
            if group_name not in group_counts:
                group_counts[group_name] = 1
                groups.append({'name': group_name, 'group': current_group, 'count': group_counts[group_name]})
            else:
                group_counts[group_name] += 1

    # Update the counts in the final list of groups
    for group in groups:
        group['count'] = group_counts[group['name']]

    return groups






# def create_structured_document(groups):
	# Create a structured document from the groups
	# ...

# Read and process the CSV file
note_data = parse_csv("Six Marimbas Data.csv")
print(note_data)
repeating_groups = find_repeating_groups(note_data)
# print(repeating_groups)
# structured_doc = create_structured_document(repeating_groups)

# Export to JSON
# with open("output.json", "w") as json_file:
# 	json.dump(structured_doc, json_file)