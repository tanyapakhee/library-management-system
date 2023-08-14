import sqlite3 as sql
DATABASE = 'library.db'

#connect to SQLite
con = sql.connect(DATABASE)

#Create a Connection
cur = con.cursor()

#Drop users table if already exsist.
cur.execute("DROP TABLE IF EXISTS books")
cur.execute("DROP TABLE IF EXISTS members")
cur.execute("DROP TABLE IF EXISTS transactions")
#Create books table  in db_web database
books ='''
CREATE TABLE "books" (
    "bookID" INTEGER PRIMARY KEY AUTOINCREMENT,
    "title" TEXT,
    "authors" TEXT,
    "average_rating" REAL,
    "isbn" TEXT,
    "isbn13" TEXT,
    "language_code" TEXT,
    "num_pages" INTEGER,
    "ratings_count" INTEGER,
    "text_reviews_count" INTEGER,
    "publication_date" TEXT,
    "publisher" TEXT,
    "quantity" INTEGER DEFAULT 1
);
'''
cur.execute(books)
insert_queries = '''
INSERT INTO "books" (
    "title", "authors", "average_rating", "isbn", "isbn13",
    "language_code", "num_pages", "ratings_count", "text_reviews_count",
    "publication_date", "publisher"
) VALUES (
    'Example Book 1',
    'Author A/Author B', 4.5, '1234567890', '9781234567890', 'eng',
    300, 500, 50, '1/1/2023', 'Example Publisher'
);

INSERT INTO "books" (
    "title", "authors", "average_rating", "isbn", "isbn13",
    "language_code", "num_pages", "ratings_count", "text_reviews_count",
    "publication_date", "publisher"
) VALUES (
    'Another Example', 'Author C', 3.2, '9876543210', '9789876543210', 'eng',
    250, 200, 25, '2/15/2022', 'Different Publisher'
);

INSERT INTO "books" (
    "title", "authors", "average_rating", "isbn", "isbn13",
    "language_code", "num_pages", "ratings_count", "text_reviews_count",
    "publication_date", "publisher"
) VALUES (
    'Fiction Adventure', 'Author D/Author E', 4.0, '5678901234', '9785678901234', 'eng',
    400, 800, 75, '5/10/2021', 'Adventure Books'
);
'''

cur.executescript(insert_queries)

members = '''
    CREATE TABLE "members" (
        "memberID" INTEGER PRIMARY KEY AUTOINCREMENT,
        "name" TEXT,
        "contact" TEXT,
        "debt" INTEGER DEFAULT 0
    );
'''
cur.execute(members)

sample_members = '''
INSERT INTO "members" ("name", "contact") VALUES ('Alice Johnson', 'alice@example.com');
INSERT INTO "members" ("name", "contact") VALUES ('Bob Smith', 'bob@example.com');
INSERT INTO "members" ("name", "contact") VALUES ('Carol Davis', 'carol@example.com');
'''
cur.executescript(sample_members)

#commit changes
con.commit()

transactions = '''
CREATE TABLE "transactions" (
    "transactionID" INTEGER PRIMARY KEY AUTOINCREMENT,
    "bookID" INTEGER,
    "memberID" INTEGER,
    "issue_date" TEXT,
    "return_date" TEXT,
    FOREIGN KEY ("bookID") REFERENCES "books" ("bookID"),
    FOREIGN KEY ("memberID") REFERENCES "members" ("memberID")
);'''

cur.execute(transactions)
con.commit()
#close the connection
con.close()