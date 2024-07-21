import random
from collections import defaultdict
from .const import FACULTY_NAME_CODE

faculty_year_id = defaultdict(int)


def get_next_student_id(faculty_name: str, year: int) -> int:
    # Each call to this function should return an incrementing integer.
    # Format: {faculty_code}{year[2:]}{id.zfill(5)}
    faculty_year_id[(faculty_name, year)] += 1
    val = faculty_year_id[(faculty_name, year)]

    return f"{FACULTY_NAME_CODE[faculty_name]}{str(year)[2:]}{str(val).zfill(5)}"
