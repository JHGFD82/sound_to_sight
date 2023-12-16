#add_sections.py

def add_sections(df, sections):
    '''



    '''
    # Add the starting position for the first section

    sections = [(x * 8 - 7) for x in ([1] + sections if sections[0] != 1 else sections)]

    # Function to determine the section based on position
    def find_section(position):
        for i, start in enumerate(sections):
            if position < sections[i + 1] if i + 1 < len(sections) else True:
                return i + 1

    # Apply the function to each row in the DataFrame
    df['section'] = df['time'].apply(find_section).astype('Int32')
    return df