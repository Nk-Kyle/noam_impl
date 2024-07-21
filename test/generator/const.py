MEMBER_COUNT = 10_000

BOOK_COUNT = 10 * MEMBER_COUNT
STUDENT_PERCENTAGE = 0.99

BOOK_AUTHOR_AVG_COUNT = 2
BOOK_CATEGORY_AVG_COUNT = 2

BOOK_LOAN_AVG_COUNT = 20

# A publisher averages 100 books
PUBLISHER_COUNT = BOOK_COUNT // 100

# An Author averages 5 books
AUTHOR_COUNT = BOOK_COUNT // 5

# Categories
CATEGORIES = {
    "Fiction": [
        "Fantasy",
        "Science Fiction",
        "Mystery",
        "Romance",
        "Historical Fiction",
    ],
    "Non-Fiction": ["Biography", "Self-Help", "Travel", "True Crime", "History"],
    "Children's Books": [
        "Picture Books",
        "Early Readers",
        "Chapter Books",
        "Young Adult",
        "Fairy Tales",
    ],
    "Science": ["Physics", "Biology", "Chemistry", "Astronomy", "Earth Sciences"],
    "Technology": [
        "Programming",
        "Artificial Intelligence",
        "Cybersecurity",
        "Data Science",
        "Networking",
    ],
    "Health & Wellness": [
        "Nutrition",
        "Fitness",
        "Mental Health",
        "Yoga",
        "Alternative Medicine",
    ],
    "Arts & Photography": [
        "Painting",
        "Photography",
        "Sculpture",
        "Graphic Design",
        "Performing Arts",
    ],
    "Business & Economics": [
        "Finance",
        "Marketing",
        "Entrepreneurship",
        "Leadership",
        "Economics",
    ],
    "Cooking & Food": [
        "Baking",
        "Vegan",
        "International Cuisine",
        "Quick & Easy",
        "Desserts",
    ],
    "Travel & Adventure": [
        "Travel Guides",
        "Adventure Travel",
        "Cultural Exploration",
        "Road Trips",
        "Hiking & Camping",
    ],
}


FACULTY_NAME_ID = {
    "Engineering": 1,
    "Science": 2,
    "Business": 3,
    "Arts": 4,
    "Medicine": 5,
}

FACULTY_NAME_CODE = {
    "Engineering": "ENG",
    "Science": "SCI",
    "Business": "BUS",
    "Arts": "ART",
    "Medicine": "MED",
}
