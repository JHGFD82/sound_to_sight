# generate_fake_notes


def generate_fake_notes(start=4.5, pattern=[7, 5], upper_bound=128):
    current_value = start
    i = 0
    while current_value <= upper_bound:
        yield current_value
        current_value += pattern[i % len(pattern)]
        i += 1
