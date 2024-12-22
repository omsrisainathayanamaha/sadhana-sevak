import re

def process_document(input_file, output_file):
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    processed_lines = []
    stanza_number = None
    commentary = ""

    for line in lines:
        # Remove page numbers and book name mentions
        line = re.sub(r'\bHoly Geeta by Swami Chinmayananda\b', '', line)
        line = re.sub(r'^\s*\d+\s*$', '', line)  # Removes standalone numbers (page numbers)

        # Check for stanza numbers (e.g., "39.", "40.")
        stanza_match = re.match(r'^\s*(\d+)\.\s', line)
        if stanza_match:
            # If a new stanza is detected, save the previous stanza commentary
            if stanza_number is not None:
                processed_lines.append(f"{stanza_number}. {commentary.strip()}\n")
            # Start a new stanza
            stanza_number = stanza_match.group(1)
            commentary = line.strip()
        else:
            # Continue building commentary for the current stanza
            commentary += " " + line.strip()

    # Add the last stanza commentary if any
    if stanza_number is not None:
        processed_lines.append(f"{stanza_number}. {commentary.strip()}\n")

    # Write processed lines to the output file
    with open(output_file, 'w') as f:
        f.writelines(processed_lines)
