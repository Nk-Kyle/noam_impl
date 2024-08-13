# Migrate the tables from the test database to ETF Model

from test.generator.models import engine
from sqlalchemy import text
from test.mongodb.db import client as mongo_client


def run():
    mongo_db = mongo_client["etf"]

    with engine.connect() as conn:
        # =========== Book Collection =================
        book_collection = mongo_db["book"]

        # Inserting data into book collection
        book_collection.drop()
        query = text(
            "SELECT book.id, book.name, book.language, book.description,\
            book.keywords, publisher.id as Publisher_id FROM book JOIN\
            publisher ON book.publisher_id = publisher.id"
        )

        for row in conn.execute(query):
            book_collection.insert_one(
                {
                    "_id": row.id,
                    "name": row.name,
                    "language": row.language,
                    "description": row.description,
                    # Convert keywords to list of keywords and remove [], '', and spaces
                    "keywords": row.keywords.strip("[] ").replace("'", "").split(", "),
                    "Publisher_id": row.Publisher_id,
                }
            )

        # Add Loan Data for each book as a list of subdocuments
        query = text(
            "SELECT loan.id, loan.member_id, loan.book_id, loan.loanedAt,\
            member.year, member.employeeId, member.name, member.studentId, \
            return.id as return_id, return.returnedAt, return.penalty\
            FROM loan JOIN member ON loan.member_id = member.id \
            LEFT JOIN return ON loan.id = return.loan_id \
            "
        )

        for row in conn.execute(query):
            # Add loan data to book collection
            book_collection.update_one(
                {"_id": row.book_id},
                {
                    "$push": {
                        "Loan": {
                            "id": row.id,
                            "loanedAt": row.loanedAt,
                            "Member_id": row.member_id,
                            "Member_year": row.year,
                            "Member_employeeId": row.employeeId,
                            "Member_name": row.name,
                            "Member_type": "Student" if row.studentId else "Teacher",
                            "Member_studentId": row.studentId,
                            "Return_returnedAt": row.returnedAt,
                            "Return_id": row.return_id,
                            "Return_penalty": row.penalty,
                        }
                    }
                },
            )

        # Add Author Data for each book as a list of subdocuments
        query = text(
            "SELECT book_author.book_id, author.id, author.name FROM book_author \
            JOIN author ON book_author.author_id = author.id"
        )

        for row in conn.execute(query):
            # Add author data to book collection
            book_collection.update_one(
                {"_id": row.book_id},
                {
                    "$push": {
                        "Author": {
                            "id": row.id,
                            "name": row.name,
                        }
                    }
                },
            )

        # Add Category Data for each book as a list of subdocuments
        query = text(
            "SELECT book_category.book_id, category.id, category.name, category.subcategory FROM book_category \
            JOIN category ON book_category.category_id = category.id"
        )

        for row in conn.execute(query):
            # Add category data to book collection
            book_collection.update_one(
                {"_id": row.book_id},
                {
                    "$push": {
                        "Category": {
                            "id": row.id,
                            "name": row.name,
                            "subcategory": row.subcategory,
                        }
                    }
                },
            )

        # =========== Member Collection =================
        member_collection = mongo_db["member"]
        member_collection.drop()

        # Inserting data into member collection
        query = text("SELECT * from member")

        for row in conn.execute(query):
            member_collection.insert_one(
                {
                    "_id": row.id,
                    "name": row.name,
                    "type": "Student" if row.studentId else "Teacher",
                    "studentId": row.studentId,
                    "year": row.year,
                    "employeeId": row.employeeId,
                    "Faculty_id": row.faculty_id,
                    "Faculty_name": row.faculty_name,
                    "Address_city": row.address_city,
                    "Address_address": row.address_address,
                    "Address_postal": row.address_postal,
                }
            )

        # Add Loan Data for each member as a list of subdocuments
        query = text(
            "SELECT loan.id, loan.book_id, loan.loanedAt, loan.member_id, book.name,\
            book.description, return.id as return_id, return.returnedAt, \
            return.penalty FROM loan \
            JOIN book ON loan.book_id = book.id \
            JOIN return ON loan.id = return.loan_id"
        )

        for row in conn.execute(query):
            # Add loan data to member collection
            member_collection.update_one(
                {"_id": row.member_id},
                {
                    "$push": {
                        "Loan": {
                            "id": row.id,
                            "loanedAt": row.loanedAt,
                            "Book_id": row.book_id,
                            "Book_name": row.name,
                            "Book_description": row.description,
                            "Return_returnedAt": row.returnedAt,
                            "Return_id": row.return_id,
                            "Return_penalty": row.penalty,
                        }
                    }
                },
            )

        # =========== Publisher Collection =================
        publisher_collection = mongo_db["publisher"]
        publisher_collection.drop()

        # Inserting data into publisher collection
        query = text("SELECT * from publisher")

        for row in conn.execute(query):
            publisher_collection.insert_one(
                {
                    "_id": row.id,
                    "name": row.name,
                    "contact": row.contact,
                }
            )

        # =========== Author Collection =================
        author_collection = mongo_db["author"]
        author_collection.drop()

        # Inserting data into author collection
        query = text("SELECT * from author")

        for row in conn.execute(query):
            author_collection.insert_one(
                {
                    "_id": row.id,
                    "name": row.name,
                }
            )

        # Add Book Data for each author as a list of subdocuments
        query = text(
            "SELECT book_author.author_id, book_author.book_id FROM book_author"
        )

        for row in conn.execute(query):
            # Add book data to author collection
            author_collection.update_one(
                {"_id": row.author_id},
                {
                    "$push": {
                        "Book_id": row.book_id,
                    }
                },
            )
