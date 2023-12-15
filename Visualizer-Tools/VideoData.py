def adjust_y_values(df):
		''' Calculate the exact y-axis value that will be used in After Effects. To do this, we need the minimum value
	and maximum value to set a range. Because each section has its own range, we'll do it per section and figure out
	how to transition between them later.'''

	# Set up variables for video size, object size, and limits of note placement based on action-safe zone.
	# After Effects compositions put (0,0) in the top left corner of the frame.
	total_h = 2160 # height of 4k UHD resolution
	as_h = 2160 - 2008 # 2008 is total height of action-safe zone for 4k UHD TVs
	ring_size = 1000 # total size of ring at its largest point
	shape_range = total_h - as_h - ring_size # total amount of room within which rings can be positioned
	shape_edge = total_h - as_h / 2 - ring_size / 2
	# The variable shape_edge is the lowest point to where a note can be placed in a video composition.

	def adjust_section(group):
		s_note_min = group['y'].min() # lowest pitch of section
		s_note_max = group['y'].max() # highest pitch of section
		s_note_range = s_note_max - s_note_min + 1 # total number of pitch values
		dist = shape_range / s_note_range # distance between pitches in video
   		# Set the lowest note to 0 so that the section uses the full available range within the action safe zone,
		# then calculate the new y-axis value: multiply it by distance, and subtract by the shape_edge.
		group['y'] = (shape_edge - (group['y'] - s_note_min) * dist).round(1)
		return group

	return df.groupby('section').apply(adjust_section).reset_index(drop=True) # Apply the function to each section

def timecode_frames(df):
	# For the last column for timecodes, they are generated from the BPMtoFPS script.
	df['timecode'] = BPMtoFPS(df['time'] - 1)

	# After Effects scripting needs time in # of frames, so the following code converts timecode to frames.
	def timecode_to_frames(timecode, frame_rate):
		seconds, frames = map(int, timecode.split(":"))
		total_frames = seconds * frame_rate + frames
		return int(total_frames)

	frame_rate = 30 # frames per second of video project
	df['frames'] = df['timecode'].apply(lambda x: timecode_to_frames(x, frame_rate)) # apply function to each row of dataframe

	# The final step is to export the data to CSV, for use in After Effects.
	df.to_csv('Six Marimbas Data.csv')

	return df