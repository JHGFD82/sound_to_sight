import pandas as pd
from typing import List, Optional


def compute_sections_time(bar_division: int, notes_per_bar: int, section_bar_positions: Optional[List[int]]) -> List:
    """
    Compute the time positions that underline sections start.
    Args:
        bar_division (int): The number of divisions in a bar.
        notes_per_bar (int): The number of notes in a bar.
        section_bar_positions (Optional[List[int]]): A list of section bar positions.
    Returns:
        list: sections time positions.
    """
    if section_bar_positions:
        sections_time = [((section - 1) * bar_division * notes_per_bar) for section in
                         ([1] + section_bar_positions if section_bar_positions[0] != 1 else section_bar_positions)]
    else:
        sections_time = [1]
    return sections_time


def apply_section(dataframe: pd.DataFrame, sections_time: List) -> pd.Series:
    """
    Transforms a music position series into a series of corresponding sections.
    Args:
        dataframe (pd.DataFrame): The dataframe from which the 'time' column is extracted.
        sections_time (list): The list of sections beginning time positions.
    Returns:
        pd.Series: A Series with each music position changed into its corresponding section.
    """

    def determine_section(music_time_position):
        section = 1
        for index, start_time in enumerate(sections_time):
            if index + 1 < len(sections_time) and music_time_position < sections_time[index + 1]:
                return section
            section += 1
        return section if music_time_position < sections_time[-1] else section - 1

    music_positions = dataframe['time']
    return music_positions.apply(determine_section).astype('Int32')


def add_sections(dataframe: pd.DataFrame, bar_division: int, notes_per_bar: int,
                 section_bar_positions: Optional[List[int]] = None) -> pd.DataFrame:
    """
    Adds a 'section' column to the given dataframe based on the provided section bar positions, 
    bar division, and notes per bar. If 'section_bar_positions' is not provided,
    a single default section is applied to all the dataframe.

    Args:
        dataframe (pd.DataFrame): The dataframe to which the 'section' column is added.
        bar_division (int): The number of divisions in a bar.
        notes_per_bar (int): The number of notes in a bar.
        section_bar_positions (Optional[List[int]]): A list of section bar positions.

    Returns:
        pd.DataFrame: The dataframe with the 'section' column added.
    """
    sections_time = compute_sections_time(bar_division, notes_per_bar, section_bar_positions)
    dataframe['section'] = apply_section(dataframe, sections_time)

    return dataframe
