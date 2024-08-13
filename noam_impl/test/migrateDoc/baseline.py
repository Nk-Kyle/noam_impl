# Migrate the tables from the test database to ETF Model

from test.generator.models import engine
from sqlalchemy import text
from test.mongodb.db import client as mongo_client


def run():
    mongo_db = mongo_client["baseline"]

    with engine.connect() as conn:
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

        # =========== Book Collection =================
        book_collection = mongo_db["book"]

        # Inserting data into book collection
        book_collection.drop()
        query = text(
            "SELECT book.id, book.name, book.language, book.description,\
            book.keywords, book.publisher_id FROM book"
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
                    "publisherID": row.publisher_id,
                }
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

        # Add Author Id for each book and author as a list of id
        query = text("SELECT * FROM book_author")
        for row in conn.execute(query):
            # Add author data to book collection
            book_collection.update_one(
                {"_id": row.book_id},
                {
                    "$push": {
                        "authorID": row.author_id,
                    }
                },
            )

            author_collection.update_one(
                {"_id": row.author_id},
                {
                    "$push": {
                        "bookID": row.book_id,
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
                    "type": "Student" if row.studentId else "Teacher",
                    "name": row.name,
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

        # =========== Loan Collection =================
        loan_collection = mongo_db["loan"]
        loan_collection.drop()

        # Inserting data into loan collection
        query = text("SELECT * from loan")

        for row in conn.execute(query):
            loan_collection.insert_one(
                {
                    "_id": row.id,
                    "memberID": row.member_id,
                    "bookID": row.book_id,
                    "loanedAt": row.loanedAt,
                }
            )

        # =========== Return Collection =================
        return_collection = mongo_db["return"]
        return_collection.drop()

        # Inserting data into return collection
        query = text("SELECT * from return")

        for row in conn.execute(query):
            return_collection.insert_one(
                {
                    "_id": row.id,
                    "loanID": row.loan_id,
                    "returnedAt": row.returnedAt,
                    "penalty": row.penalty,
                }
            )
