# create_keyboard


def create_keyboard(df, fake_notes):
	# Create a combined DataFrame of real and fake notes, sorted and cleaned
	note_min, note_max = df['note'].min(), df['note'].max()
	keyb_values = range(note_min, note_max + 1)
	keyboard = pd.DataFrame({'key': list(keyb_values) + fake_notes})

	# Sort, remove fake notes, reset index to align with the marimba's keyboard
	keyboard_dict = (
		keyboard.sort_values('key').reset_index(drop=True)
		.query('key % 1 == 0').reset_index().set_index('key')['index'].astype('Int32')
		.to_dict()
	)

	# Convert keys back to integers
	keyboard_dict = {int(key): val for key, val in keyboard_dict.items()}
	return keyboard_dict