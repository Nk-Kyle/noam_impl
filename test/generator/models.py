import datetime

# Defining the model for the generator
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime

# Create sqlite engine in test/data/library.db
engine = create_engine("sqlite:///test/data/library.sqlite", echo=False)

# Define the table
metadata = MetaData()

member_table = Table(
    "member",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String),
    Column("studentId", String, nullable=True),
    Column("year", Integer, nullable=True),
    Column("employeeId", String, nullable=True),
    Column("faculty_id", Integer),
    Column("faculty_name", String),
    Column("address_city", String),
    Column("address_address", String),
    Column("address_postal", String),
)

loan_table = Table(
    "loan",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("member_id", Integer, ForeignKey("member.id")),
    Column("book_id", Integer, ForeignKey("book.id")),
    Column("loanedAt", DateTime, default=datetime.datetime.now),
)

return_table = Table(
    "return",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("loan_id", Integer, ForeignKey("loan.id")),
    Column("returnedAt", DateTime, default=datetime.datetime.now),
    Column("penalty", Integer, default=0),
)

book_table = Table(
    "book",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("publisher_id", Integer, ForeignKey("publisher.id")),
    Column("name", String),
    Column("description", String),
    Column("language", String),
    Column("keywords", String),
)

author_table = Table(
    "author",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String),
)

book_author_table = Table(
    "book_author",
    metadata,
    Column("book_id", Integer, ForeignKey("book.id")),
    Column("author_id", Integer, ForeignKey("author.id")),
)

category_table = Table(
    "category",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String),
    Column("subcategory", String),
)

book_category_table = Table(
    "book_category",
    metadata,
    Column("book_id", Integer, ForeignKey("book.id")),
    Column("category_id", Integer, ForeignKey("category.id")),
)

publisher_table = Table(
    "publisher",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String),
    Column("contact", String),
)

# Create the tables
metadata.create_all(engine)
