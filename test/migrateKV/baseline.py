# Migrate the tables from the test database to ETF Model

from test.generator.models import engine
from sqlalchemy import text
from test.riakdb.db import client as riak_client
from riak import RiakObject


def run():
    riak_db_baseline = riak_client.bucket_type("baseline")

    with engine.connect() as conn:
        # =========== Member Table =================
        member_bucket = riak_db_baseline.bucket("member")

        # Inserting data into member kv
        query = text("SELECT * from member")

        # Get columns from the table
        columns = [column for column in conn.execute(query).keys()]

        # Get all members from the table
        for row in conn.execute(query):
            # Member id
            member_id = row.id

            # Add per column to the member bucket
            for column in columns:
                if column == "id":
                    continue
                obj = RiakObject(riak_client, member_bucket, f"{member_id}_{column}")
                obj.data = getattr(row, column)
                if obj.data is not None:
                    obj.store()

        # =========== Loan Table =================
        loan_bucket = riak_db_baseline.bucket("loan")

        # Inserting data into loan kv
        query = text("SELECT * from loan")

        # Get columns from the table
        columns = [column for column in conn.execute(query).keys()]

        # Get all loans from the table
        for row in conn.execute(query):
            # Loan id
            loan_id = row.id

            # Add per column to the loan bucket
            for column in columns:
                if column == "id":
                    continue
                obj = RiakObject(riak_client, loan_bucket, f"{loan_id}_{column}")
                obj.data = getattr(row, column)
                obj.store()

        # =========== Return Table =================
        return_bucket = riak_db_baseline.bucket("return")

        # Inserting data into return kv
        query = text("SELECT * from return")

        # Get columns from the table
        columns = [column for column in conn.execute(query).keys()]

        # Get all returns from the table
        for row in conn.execute(query):
            # Return id
            return_id = row.id

            # Add per column to the return bucket
            for column in columns:
                if column == "id":
                    continue
                obj = RiakObject(riak_client, return_bucket, f"{return_id}_{column}")
                obj.data = getattr(row, column)
                obj.store()

        # =========== Book Table =================
        book_bucket = riak_db_baseline.bucket("book")

        # Inserting data into book kv
        query = text("SELECT * from book")

        # Get columns from the table
        columns = [column for column in conn.execute(query).keys()]

        # Get all books from the table
        for row in conn.execute(query):
            # Book id
            book_id = row.id

            # Add per column to the book bucket
            for column in columns:
                if column == "id":
                    continue
                obj = RiakObject(riak_client, book_bucket, f"{book_id}_{column}")
                obj.data = getattr(row, column)
                obj.store()

        # =========== Author Table =================
        author_bucket = riak_db_baseline.bucket("author")

        # Inserting data into author kv
        query = text("SELECT * from author")

        # Get columns from the table
        columns = [column for column in conn.execute(query).keys()]

        # Get all authors from the table
        for row in conn.execute(query):
            # Author id
            author_id = row.id

            # Add per column to the author bucket
            for column in columns:
                if column == "id":
                    continue
                obj = RiakObject(riak_client, author_bucket, f"{author_id}_{column}")
                obj.data = getattr(row, column)
                obj.store()

        # =========== Book Author Table =================
        book_author_bucket = riak_db_baseline.bucket("book_author")

        # Inserting data into book_author kv
        query = text("SELECT * from book_author")

        # Get all book authors from the table
        for row in conn.execute(query):

            # Get book_id
            book_author = book_author_bucket.get(f"book_{row.book_id}_author").data

            if book_author is None:
                obj = RiakObject(
                    riak_client, book_author_bucket, f"book_{row.book_id}_author"
                )
                obj.data = [row.author_id]
            else:
                # Append author_id to the existing list and update the object
                book_author.append(row.author_id)
                book_author.store()

            # Get author_id
            author_book = book_author_bucket.get(f"author_{row.author_id}_book").data

            if author_book is None:
                obj = RiakObject(
                    riak_client, book_author_bucket, f"author_{row.author_id}_book"
                )
                obj.data = [row.book_id]
            else:
                # Append book_id to the existing list and update the object
                author_book.append(row.book_id)
                author_book.store()

        # =========== Category Table =================
        category_bucket = riak_db_baseline.bucket("category")

        # Inserting data into category kv
        query = text("SELECT * from category")

        # Get columns from the table
        columns = [column for column in conn.execute(query).keys()]

        # Get all categories from the table
        for row in conn.execute(query):
            # Category id
            category_id = row.id

            # Add per column to the category bucket
            for column in columns:
                if column == "id":
                    continue
                obj = RiakObject(
                    riak_client, category_bucket, f"{category_id}_{column}"
                )
                obj.data = getattr(row, column)
                obj.store()

        # =========== Book Category Table =================
        book_category_bucket = riak_db_baseline.bucket("book_category")

        # Inserting data into book_category kv
        query = text("SELECT * from book_category")

        # Get all book categories from the table
        for row in conn.execute(query):

            # Get book_id
            book_category = book_category_bucket.get(
                f"book_{row.book_id}_category"
            ).data

            if book_category is None:
                obj = RiakObject(
                    riak_client, book_category_bucket, f"book_{row.book_id}_category"
                )
                obj.data = [row.category_id]
            else:
                # Append category_id to the existing list and update the object
                book_category.append(row.category_id)
                book_category.store()

            # Get category_id
            category_book = book_category_bucket.get(
                f"category_{row.category_id}_book"
            ).data

            if category_book is None:
                obj = RiakObject(
                    riak_client,
                    book_category_bucket,
                    f"category_{row.category_id}_book",
                )
                obj.data = [row.book_id]
            else:
                # Append book_id to the existing list and update the object
                category_book.append(row.book_id)
                category_book.store()

        # =========== Publisher Table =================
        publisher_bucket = riak_db_baseline.bucket("publisher")

        # Inserting data into publisher kv
        query = text("SELECT * from publisher")

        # Get columns from the table
        columns = [column for column in conn.execute(query).keys()]

        # Get all publishers from the table
        for row in conn.execute(query):
            # Publisher id
            publisher_id = row.id

            # Add per column to the publisher bucket
            for column in columns:
                if column == "id":
                    continue
                obj = RiakObject(
                    riak_client, publisher_bucket, f"{publisher_id}_{column}"
                )
                obj.data = getattr(row, column)
                obj.store()
