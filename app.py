from flask import Flask, flash, render_template, request, redirect, url_for, g
import sqlite3
from datetime import datetime
import requests

app = Flask(__name__)
app.secret_key = 'my_secret_key_1'

DATABASE = 'library.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_books', methods=['GET'])
def get_books():
    conn = get_db()
    cur = conn.cursor()

    search_query = request.args.get('search_query')  # Get the search query from the URL

    if search_query:
        # If a search query is provided, filter books by name or author
        cur.execute('SELECT bookID, title, authors, ratings_count, quantity FROM books WHERE title LIKE ? OR authors LIKE ?',
                    ('%' + search_query + '%', '%' + search_query + '%'))
    else:
        # If no search query, fetch all books
        cur.execute('SELECT bookID, title, authors, ratings_count, quantity FROM books')

    books = cur.fetchall()

    conn.close()

    return render_template('getbooks.html', books=books)


@app.route('/edit_book/<int:bookID>', methods=['GET', 'POST'])
def edit_book(bookID):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        title = request.form['title']
        authors = request.form['authors']
        average_rating = request.form['average_rating']
        isbn = request.form['isbn']
        isbn13 = request.form['isbn13']
        language_code = request.form['language_code']
        num_pages = request.form['num_pages']
        ratings_count = request.form['ratings_count']
        text_reviews_count = request.form['text_reviews_count']
        publication_date = request.form['publication_date']
        publisher = request.form['publisher']
        quantity = request.form['quantity']

        cur.execute('UPDATE books SET title=?, authors=?, average_rating=?, isbn=?, isbn13=?, language_code=?, '
                    'num_pages=?, ratings_count=?, text_reviews_count=?, publication_date=?, publisher=?, quantity=? '
                    'WHERE bookID=?',
                    (title, authors, average_rating, isbn, isbn13, language_code, num_pages,
                     ratings_count, text_reviews_count, publication_date, publisher,quantity, bookID))
        conn.commit()

        conn.close()

        return redirect(url_for('get_books'))

    # Fetch book details for editing
    cur.execute('SELECT * FROM books WHERE bookID = ?', (bookID,))
    book = cur.fetchone()

    conn.close()

    return render_template('editbook.html', book=book)

@app.route('/delete_book/<int:bookID>', methods=['GET'])
def delete_book(bookID):
    conn = get_db()
    cur = conn.cursor()

    # Delete the book from the database based on the bookID
    cur.execute('DELETE FROM books WHERE bookID = ?', (bookID,))
    conn.commit()

    conn.close()

    return redirect(url_for('get_books'))

@app.route('/get_members', methods=['GET'])
def get_members():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM members')
    members = cur.fetchall()

    return render_template('members.html', members=members)

@app.route('/add_member', methods=['GET', 'POST'])
def add_member():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']

        conn = get_db()
        cur = conn.cursor()

        # Insert a new member into the "members" table
        cur.execute('INSERT INTO members (name, contact) VALUES (?, ?)', (name, contact))
        conn.commit()

        return redirect(url_for('get_members'))  # Redirect to the members list page after adding

    return render_template('addmember.html')

@app.route('/edit_member/<int:memberID>', methods=['GET', 'POST'])
def edit_member(memberID):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        debt = request.form['debt']

        cur.execute('UPDATE members SET name=?, contact=?, debt=? WHERE memberID=?',
                    (name, contact, debt, memberID))
        conn.commit()

        conn.close()

        return redirect(url_for('get_members'))

    # Fetch member details for editing
    cur.execute('SELECT * FROM members WHERE memberID = ?', (memberID,))
    member = cur.fetchone()

    conn.close()

    return render_template('editmember.html', member=member)


@app.route('/delete_member/<int:memberID>', methods=['GET'])
def delete_member(memberID):
    conn = get_db()
    cur = conn.cursor()

    # Delete the member from the database based on the memberID
    cur.execute('DELETE FROM members WHERE memberID = ?', (memberID,))
    conn.commit()

    conn.close()

    return redirect(url_for('get_members'))

@app.route('/view_transactions', methods=['GET'])
def view_transactions():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Fetch all transactions with book and member details
    cur.execute('''SELECT transactions.transactionID, 
                          transactions.issue_date, 
                          transactions.return_date,
                          books.title AS book_title,
                          members.name AS member_name
                   FROM transactions
                   INNER JOIN books ON transactions.bookID = books.bookID
                   INNER JOIN members ON transactions.memberID = members.memberID
                   ORDER BY transactions.transactionID DESC''')
    
    transactions = cur.fetchall()
    print(transactions)
    conn.close()

    return render_template('transactions.html', transactions=transactions)


@app.route('/issue_book', methods=['GET', 'POST'])
def issue_book():
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        search_query = request.form['search_query']

        cur.execute('SELECT * FROM books WHERE title LIKE ? OR authors LIKE ?',
                    ('%' + search_query + '%', '%' + search_query + '%'))
        books = cur.fetchall()

        conn.close()

        return render_template('issuebook.html', books=books)

    conn.close()

    return render_template('issuebook.html')

@app.route('/issue_book_form/<int:bookID>', methods=['GET', 'POST'])
def issue_book_form(bookID):
    conn = get_db()
    cur = conn.cursor()

    # Fetch book details
    cur.execute('SELECT * FROM books WHERE bookID = ?', (bookID,))
    book = cur.fetchone()


    if request.method == 'POST':
        member_id = request.form['member_id']
        
        # Execute confirm_issue logic here
        cur.execute('SELECT debt FROM members WHERE memberID = ?', (member_id,))
        member_debt = cur.fetchone()

        if book and member_debt and book['quantity'] > 0 and member_debt['debt'] < 500:
            # Update book quantity and issue the book
            cur.execute('UPDATE books SET quantity = quantity - 1 WHERE bookID = ?', (bookID,))
            # Record the transaction in the 'transactions' table
            cur.execute('INSERT INTO transactions (bookID, memberID, issue_date) VALUES (?, ?, ?)',
                    (bookID, member_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        
            conn.commit()

            flash('Book issued successfully!')
        else:
            if not book:
                flash('Book not found!')
            elif book['quantity'] <= 0:
                flash('Book is out of stock!')
            elif member_debt['debt'] >= 500:
                flash('Member has too much debt to issue a book!')
    conn.close()

    return render_template('issueform.html', book=book)

@app.route('/return_book/<int:transactionID>', methods=['POST'])
def return_book(transactionID):
    conn = get_db()
    cur = conn.cursor()

    # Update transaction with return date
    cur.execute('UPDATE transactions SET return_date = ? WHERE transactionID = ?',
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), transactionID))

    # Increment book quantity
    cur.execute('SELECT bookID FROM transactions WHERE transactionID = ?', (transactionID,))
    bookID = cur.fetchone()['bookID']
    cur.execute('UPDATE books SET quantity = quantity + 1 WHERE bookID = ?', (bookID,))

    # Increase member's debt
    cur.execute('SELECT memberID FROM transactions WHERE transactionID = ?', (transactionID,))
    memberID = cur.fetchone()['memberID']
    cur.execute('UPDATE members SET debt = debt + 100 WHERE memberID = ?', (memberID,))

    conn.commit()
    conn.close()

    flash('Book returned successfully!')

    return redirect(url_for('return_books'))

@app.route('/add_external_books', methods=['GET', 'POST'])
def add_external_books():
    if request.method == 'POST':
        title = request.form.get('title')
        authors = request.form.get('authors')
        isbn = request.form.get('isbn')
        publisher = request.form.get('publisher')
        n = int(request.form.get('n', 10))  # Default to 10 books if n is not provided
        
        # Initialize variables for pagination
        page = 1
        books_to_fetch = n
        total_books_fetched = 0
        all_books = []
        
        while books_to_fetch > 0:
            api_url = f"https://frappe.io/api/method/frappe-library?page={page}&title={title}&authors={authors}&isbn={isbn}&publisher={publisher}"
            response = requests.get(api_url)
            data = response.json()
            books = data.get('message', [])
            
            if not books:
                break
            
            total_books_fetched += len(books)
            all_books.extend(books)
            
            # If fetched more books than needed, trim the list
            if total_books_fetched > n:
                all_books = all_books[:n]
                break
            
            page += 1
            books_to_fetch = n - total_books_fetched
        
        # Insert or update the books in the database
        conn = get_db()
        cur = conn.cursor()
        for book in all_books:
            cur.execute('SELECT * FROM books WHERE bookID = ?', (book['bookID'],))
            existing_book = cur.fetchone()
            # print(book)
            if existing_book:
                # Update quantity by 1 for existing book
                cur.execute('UPDATE books SET quantity = quantity + 1 WHERE bookID = ?', (existing_book['bookID'],))
            else:
                # Insert a new book record
                try:
                    print(book.keys())
                    if '  num_pages' in book: # bug in the API
                        book['num_pages']=book['  num_pages']
                    elif ' num_pages' in book: # bug in the API
                        book['num_pages']=book[' num_pages']
                    cur.execute('INSERT INTO books (bookID, title, authors, average_rating, isbn, isbn13, language_code, num_pages, ratings_count, text_reviews_count, publication_date, publisher, quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                        (book['bookID'], book['title'], book['authors'], book['average_rating'], book['isbn'], book['isbn13'], book['language_code'], book['num_pages'], book['ratings_count'], book['text_reviews_count'], book['publication_date'], book['publisher'], 1))
                except Exception as e:
                    print("exception occured",e)
        conn.commit()
        conn.close()
        
        flash(f"Added/Updated {len(all_books)} books from the API.")
        
        return redirect(url_for('add_external_books'))
    
    return render_template('addexternalbooks.html')


@app.route('/contact_library', methods=['GET'])
def contact_library():
    library_info = {
        'address': '123 ABC Street, xyzville',
        'contact_number': '123-456-7890',
        'librarian_name': 'Mr. Librarian'
    }
    return render_template('contact_library.html', library_info=library_info)


@app.route('/add_book', methods=['GET','POST'])
def add_book():
    if request.method == 'GET':
        return render_template('add.html')
    title = request.form['title']
    author = request.form['author']
    isbn = request.form['isbn']
    isbn13 = request.form['isbn13']

    conn = get_db()
    cur = conn.cursor()

    # Check if the book already exists based on title, ISBN, or ISBN13
    cur.execute('SELECT * FROM books WHERE title=? OR isbn=? OR isbn13=?', (title, isbn, isbn13))
    existing_book = cur.fetchone()

    if existing_book:
        # Increase the quantity of the existing book by 1
        cur.execute('UPDATE books SET quantity = quantity + 1 WHERE bookID = ?', (existing_book['bookID'],))
    else:
        # Insert a new entry for the book with all fields
        cur.execute('INSERT INTO books (title, authors, average_rating, isbn, isbn13, language_code, num_pages, '
                    'ratings_count, text_reviews_count, publication_date, publisher, quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)',
                    (title, author, request.form.get('average_rating'), isbn, isbn13, request.form.get('language_code'),
                     request.form.get('num_pages'), request.form.get('ratings_count'),
                     request.form.get('text_reviews_count'), request.form.get('publication_date'),
                     request.form.get('publisher')))

    conn.commit()

    return redirect(url_for('index'))
@app.route('/return_books', methods=['GET', 'POST'])
def return_books():
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    member = None
    lent_books = []

    if request.method == 'POST':
        search_query = request.form['search_query']

        # Search for member by name or ID
        cur.execute('SELECT * FROM members WHERE name LIKE ? OR memberID = ?', ('%' + search_query + '%', search_query))

        member = cur.fetchone()

        if member:
            # Fetch books lent to the member
            cur.execute('''SELECT transactions.transactionID,
                                  transactions.issue_date,
                                  books.title AS book_title
                           FROM transactions
                           INNER JOIN books ON transactions.bookID = books.bookID
                           WHERE transactions.memberID = ? AND transactions.return_date IS NULL''', (member['memberID'],))
            lent_books = cur.fetchall()

    conn.close()

    return render_template('returnbook.html', member=member, lent_books=lent_books)

if __name__ == '__main__':
    app.run(debug=True)
