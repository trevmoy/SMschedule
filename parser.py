# File to parse schedule and convert into a json.

import fitz  # PyMuPDF
import re
import json
from collections import defaultdict

# === CONFIG ===
PDF_PATH = "Middle School Schedule 24-25.pdf"
OUTPUT_JSON = "class_schedule.json"

# === TIME BLOCKS ===
time_blocks = [
    "7:50-8:15", "8:15-9:10", "9:10-10:05", "10:05-10:20", "10:20-10:40",
    "10:40-11:35", "11:35-12:25", "12:25-12:40", "12:40-1:00", "1:00-1:55", "1:55-2:50"
]

# === DAYS OF THE WEEK ===
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

# === PATTERN TO MATCH CLASS ENTRIES ===
class_entry_pattern = re.compile(r"(?P<class>\d+[A-Z]) - (?P<subject>[\w &]+) \((?P<teacher>\w+)\)")

# === PARSE PDF ===
def parse_schedule(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    lines = full_text.splitlines()

    # Filter relevant lines
    schedule_lines = [
        line.strip() for line in lines
        if any(day in line for day in days) or class_entry_pattern.search(line)
    ]

    schedule = []
    current_day_index = 0
    current_block_index = 0

    for line in schedule_lines:
        if any(day in line for day in days):
            current_day_index = days.index(next(day for day in days if day in line))
            current_block_index = 0
        elif class_entry_pattern.search(line):
            entries = class_entry_pattern.finditer(line)
            for match in entries:
                class_name = match.group("class")
                schedule.append({
                    "day": days[current_day_index],
                    "time": time_blocks[current_block_index] if current_block_index < len(time_blocks) else "Unknown",
                    "class": class_name,
                    "grade": class_name[0],  # First character is the grade
                    "subject": match.group("subject"),
                    "teacher": match.group("teacher")
                })
            current_block_index += 1

    return schedule

# === GROUP BY CLASS ===
def group_by_class(schedule):
    grouped = defaultdict(list)
    for entry in schedule:
        grouped[entry["class"]].append({
            "day": entry["day"],
            "time": entry["time"],
            "subject": entry["subject"],
            "teacher": entry["teacher"]
        })
    return grouped

# === MAIN ===
if __name__ == "__main__":
    parsed_schedule = parse_schedule(PDF_PATH)
    grouped_schedule = group_by_class(parsed_schedule)

    with open(OUTPUT_JSON, "w") as f:
        json.dump(grouped_schedule, f, indent=2)

    print(f"Schedule saved to: {OUTPUT_JSON}")
