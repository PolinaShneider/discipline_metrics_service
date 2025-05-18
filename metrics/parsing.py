import re

def parse_course_structure(text):
    structure = {}
    current_section = None

    for line in text.strip().split("\n"):
        match_section = re.match(r"^(\d+)\.\s(.+)", line.strip())
        if match_section:
            section_title = match_section.groups()[1].strip()
            current_section = section_title
            structure[current_section] = []
        elif current_section and line.strip().startswith("- "):
            topic = line.strip()[2:].strip()
            structure[current_section].append(topic)

    return structure
