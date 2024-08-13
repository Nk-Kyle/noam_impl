# Generate the data
from faker import Faker
from datetime import timedelta
import random

fake = Faker()

from sqlalchemy import insert

from test.generator.const import (
    MEMBER_COUNT,
    AUTHOR_COUNT,
    BOOK_COUNT,
    BOOK_AUTHOR_AVG_COUNT,
    BOOK_CATEGORY_AVG_COUNT,
    BOOK_LOAN_AVG_COUNT,
    STUDENT_PERCENTAGE,
    FACULTY_NAME_ID,
    PUBLISHER_COUNT,
    CATEGORIES,
)
from test.generator.id import get_next_student_id

from test.generator.models import (
    engine,
    member_table,
    book_table,
    book_author_table,
    book_category_table,
    publisher_table,
    author_table,
    category_table,
    loan_table,
    return_table,
)


def run():
    with engine.connect() as connection:

        # Generate Members
        for _ in range(MEMBER_COUNT):
            faculty_info = random.choice(list(FACULTY_NAME_ID.items()))
            is_student = random.random() < STUDENT_PERCENTAGE
            year = random.randint(2001, 2020) if is_student else None
            stmt = insert(member_table).values(
                name=fake.name(),
                studentId=(
                    get_next_student_id(faculty_info[0], year) if is_student else None
                ),
                year=year,
                faculty_id=faculty_info[1],
                faculty_name=faculty_info[0],
                address_city=fake.city(),
                address_address=fake.address(),
                address_postal=fake.postcode(),
                employeeId=fake.ssn() if not is_student else None,
            )
            connection.execute(stmt)

            if _ % 10_000 == 0:
                connection.commit()
        connection.commit()

        # Generate Publishers
        for _ in range(PUBLISHER_COUNT):
            stmt = insert(publisher_table).values(
                name=fake.company(),
                contact=fake.phone_number(),
            )
            connection.execute(stmt)

            if _ % 10_000 == 0:
                connection.commit()
        connection.commit()

        # Generate Authors
        for _ in range(AUTHOR_COUNT):
            stmt = insert(author_table).values(
                name=fake.name(),
            )
            connection.execute(stmt)

            if _ % 10_000 == 0:
                connection.commit()
        connection.commit()

        # Generate Categories
        for category, subcategories in CATEGORIES.items():
            for subcategory in subcategories:
                stmt = insert(category_table).values(
                    name=category,
                    subcategory=subcategory,
                )
                connection.execute(stmt)
        connection.commit()

        # Generate Books
        for _ in range(BOOK_COUNT):
            stmt = insert(book_table).values(
                name=fake.catch_phrase(),
                description=fake.text(),
                language=fake.language_code(),
                keywords=str(fake.words(nb=5, unique=True)),
                publisher_id=random.randint(1, PUBLISHER_COUNT),
            )
            connection.execute(stmt)

            if _ % 10_000 == 0:
                connection.commit()
        connection.commit()

        # Generate Author-Book relationships
        for book_id in range(1, BOOK_COUNT + 1):
            author_count = random.randint(
                BOOK_AUTHOR_AVG_COUNT - 1, BOOK_AUTHOR_AVG_COUNT + 1
            )
            for _ in range(author_count):
                stmt = insert(book_author_table).values(
                    book_id=book_id,
                    author_id=random.randint(1, AUTHOR_COUNT),
                )
                connection.execute(stmt)

            if book_id % 10_000 == 0:
                connection.commit()
        connection.commit()

        # Generate Category-Book relationships
        for book_id in range(1, BOOK_COUNT + 1):
            category_count = random.randint(
                BOOK_CATEGORY_AVG_COUNT - 1, BOOK_CATEGORY_AVG_COUNT + 1
            )
            for _ in range(category_count):
                stmt = insert(book_category_table).values(
                    book_id=book_id,
                    category_id=random.randint(1, len(CATEGORIES)),
                )
                connection.execute(stmt)
            if book_id % 10_000 == 0:
                connection.commit()
        connection.commit()

        # Generate Book Loans
        loan_cnt = 1
        for book_id in range(1, BOOK_COUNT + 1):
            loan_count = random.randint(0, BOOK_LOAN_AVG_COUNT * 2)
            loan_date_time = fake.date_time_between(start_date="-10y", end_date="now")
            loan_days = random.randint(1, 30)
            return_date_time = loan_date_time + timedelta(
                days=loan_days,
                hours=random.randint(0, 23),
            )
            penalty = 0
            if loan_days > 7:
                penalty = (loan_days - 7) * 1000

            for _ in range(loan_count):
                stmt = insert(loan_table).values(
                    member_id=random.randint(1, MEMBER_COUNT),
                    book_id=book_id,
                    loanedAt=loan_date_time,
                )
                connection.execute(stmt)

                # Generate Return
                stmt = insert(return_table).values(
                    loan_id=loan_cnt,
                    returnedAt=return_date_time,
                    penalty=penalty,
                )
                connection.execute(stmt)
                loan_cnt += 1

            if book_id % 5_000 == 0:
                connection.commit()
        connection.commit()

    # Query the data
    from sqlalchemy import select, text

    with engine.connect() as connection:
        # Query a member
        result = connection.execute(select(member_table).limit(1))
        for row in result:
            print(row)
