from flask import Flask, render_template, request, redirect, url_for, session, flash
# https://www.geeksforgeeks.org/how-to-add-authentication-to-your-app-with-flask-login/
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from db import get_connection
from datetime import date, timedelta
import secrets

app = Flask(__name__)

app.secret_key = secrets.token_hex(32)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, name, email, is_admin):
        self.id = id
        self.name = name
        self.email = email
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute('SELECT User_ID, User_Name, User_Email, User_IsAdmin FROM "User" WHERE User_ID = %s', (user_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if row:
        return User(row[0], row[1], row[2], row[3]) 
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/books')
def books():
    search_term = request.args.get('q')

    conn = get_connection()
    cur = conn.cursor()

    if search_term:
        cur.execute("SELECT * FROM Book WHERE Title ~* %s", (search_term,))
    else:
        cur.execute("SELECT * FROM Book")

    books = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('books.html', books=books, query=search_term)

@app.route('/books/<int:book_id>')
def book_detail(book_id):
    conn = get_connection()
    
    cur = conn.cursor()

    cur.execute("""
        SELECT b.Book_ID, b.Title, a.Author_name, b.Genre_name, p.Publisher_name,
            b.ISBN, b.Copies_available, b.Price, b.Summary
        FROM Book b
        JOIN Author a ON b.Author_ID = a.Author_ID
        JOIN Publisher p ON b.Publisher_ID = p.Publisher_ID
        WHERE b.Book_ID = %s
    """, (book_id,))
    
    book = cur.fetchone()
    cur.close()
    conn.close()

    if not book:
        return "Book not found", 404

    return render_template("book_detail.html", book=book)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        return "Access denied", 403

    # Connect to the database
    conn = get_connection()

    # create a cursor
    cur = conn.cursor()

    # Select all authors from the table
    cur.execute("SELECT * FROM Book")
    # Fetch the data
    books = cur.fetchall()

    # Select all authors from the table
    cur.execute("SELECT Author_ID, Author_name FROM Author")
    # Fetch the data
    authors = cur.fetchall()

    # Select all genres from the table
    cur.execute("SELECT Genre_name FROM Genre")
    # Fetch the data
    genres = cur.fetchall()

    # Select all Publishers from the table
    cur.execute("SELECT Publisher_ID, Publisher_name FROM Publisher")
    # Fetch the data
    publishers = cur.fetchall()

    # Book Data
    cur.execute("SELECT * FROM Book")
    book_rows = cur.fetchall()
    book_data = {}
    for row in book_rows:
        book_data[row[0]] = {
            "title": row[1],
            "author_id": row[2],
            "genre_name": row[3],
            "publisher_id": row[4],
            "isbn": row[5],
            "copies_available": row[6],
            "price": row[7],
            "summary": row[8],
    }

    cur.execute("""
        SELECT b.Borrow_ID, u.User_Name, u.User_Email, bk.Title, b.Borrow_Date, b.Return_Date, b.is_returned
        FROM Borrow b
        JOIN "User" u ON b.User_ID = u.User_ID
        JOIN Book bk ON b.Book_ID = bk.Book_ID
        ORDER BY b.Borrow_Date DESC
    """)
    loans = cur.fetchall()


    # close the cursor and connection
    cur.close()
    conn.close()

    return render_template('admin.html', authors=authors, genres=genres, publishers=publishers, books=books,  book_data=book_data, loans=loans)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO \"User\" (User_Name, User_Email, User_Password) VALUES (%s, %s, %s)", (name, email, password))
        conn.commit()
        cur.close()
        conn.close()
        return redirect('/login')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password  = request.form['password']

        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT User_ID, User_Name, User_Password, User_IsAdmin FROM \"User\" WHERE User_Email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user[2], password):
            user_obj = User(user[0], user[1], email, user[3])
            login_user(user_obj)
            return redirect('/')
        else:
            return "Invalid credentials", 401

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/my-borrows')
@login_required
def my_borrows():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT b.Title, br.Borrow_Date, br.Return_Date, br.Is_Returned
        FROM Borrow br
        JOIN Book b ON br.Book_ID = b.Book_ID
        WHERE br.User_ID = %s
    """, (current_user.id,))
    borrows = cur.fetchall()

    cur.close()
    conn.close()
    return render_template('my_borrows.html', borrows=borrows)

@app.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    borrow_date = date.today()
    return_date = borrow_date + timedelta(weeks=4)
    
    conn = get_connection()
    cur = conn.cursor()

    # Check available copies
    cur.execute("SELECT Copies_available FROM Book WHERE Book_ID = %s", (book_id,))
    result = cur.fetchone()

    if result and result[0] > 0:
        # Proceed with borrow
        cur.execute("""
            INSERT INTO Borrow (User_ID, Book_ID, Borrow_Date, Return_Date, Is_Returned)
            VALUES (%s, %s, %s, %s, %s)
        """, (current_user.id, book_id, borrow_date, return_date, False))

        cur.execute("""
            UPDATE Book
            SET Copies_available = Copies_available - 1
            WHERE Book_ID = %s
        """, (book_id,))

        conn.commit()
        cur.close()
        conn.close()
        return redirect('/my-borrows')
    else:
        cur.close()
        conn.close()
        return "No copies available", 400

@app.route('/mark-returned', methods=['POST'])
@login_required
def mark_returned():
    if not current_user.is_admin:
        return "Access denied", 403

    borrow_id = request.form.get('borrow_id')

    conn = get_connection()
    cur = conn.cursor()

    # Mark the loan as returned
    cur.execute("UPDATE Borrow SET is_returned = TRUE WHERE Borrow_ID = %s", (borrow_id,))

    # Increment book copies
    cur.execute("""
        UPDATE Book SET Copies_available = Copies_available + 1
        WHERE Book_ID = (
            SELECT Book_ID FROM Borrow WHERE Borrow_ID = %s
        )
    """, (borrow_id,))

    conn.commit()
    cur.close()
    conn.close()
    return redirect('/admin')

@app.route('/create', methods=['POST'])
@login_required
def create_entry():
    entry_type = request.form.get('entry_type')

    conn = get_connection()
    cur = conn.cursor()

    if entry_type == 'book':
        title = request.form['title']
        author_id = request.form['author_id']
        genre_name = request.form['genre_name']
        publisher_id = request.form['publisher_id']
        isbn = request.form.get('isbn')
        copies_available = request.form.get('copies_available', 0)
        price = request.form.get('price')
        summary = request.form.get('description')

        cur.execute("""
            INSERT INTO Book (Title, Author_ID, Genre_name, Publisher_ID, ISBN, Copies_available, Price, Summary)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (title, author_id, genre_name, publisher_id, isbn, copies_available, price, summary))

    elif entry_type == 'author':
        author_name = request.form['author_name']
        cur.execute("INSERT INTO Author (Author_name) VALUES (%s)", (author_name,))

    elif entry_type == 'publisher':
        publisher_name = request.form['publisher_name']
        cur.execute("INSERT INTO Publisher (Publisher_name) VALUES (%s)", (publisher_name,))

    elif entry_type == 'genre':
        genre_name = request.form['genre_name']
        cur.execute("INSERT INTO Genre (Genre_name) VALUES (%s)", (genre_name,))

    else:
        conn.close()
        return "Invalid entry type", 400

    conn.commit()
    cur.close()
    conn.close()

    return redirect('/admin')

@app.route('/manage-entry', methods=['POST'])
@login_required
def manage_entry():
    entry_type = request.form.get('manage_type')
    action_type = request.form.get('action_type')

    conn = get_connection()
    cur = conn.cursor()

    try:
        if entry_type == 'book':
            book_id = request.form['book_id']

            if action_type == 'delete':
                cur.execute("DELETE FROM Book WHERE Book_ID = %s", (book_id,))

            elif action_type == 'update':
                # Optional fields: only update if provided
                fields = []
                values = []

                if request.form['title']:
                    fields.append("Title = %s")
                    values.append(request.form['title'])
                if request.form.get('author_id'):
                    fields.append("Author_ID = %s")
                    values.append(request.form['author_id'])
                if request.form.get('genre_name'):
                    fields.append("Genre_name = %s")
                    values.append(request.form['genre_name'])
                if request.form.get('publisher_id'):
                    fields.append("Publisher_ID = %s")
                    values.append(request.form['publisher_id'])
                if request.form.get('isbn'):
                    fields.append("ISBN = %s")
                    values.append(request.form['isbn'])
                if request.form.get('copies_available'):
                    fields.append("Copies_available = %s")
                    values.append(request.form['copies_available'])
                if request.form.get('price'):
                    fields.append("Price = %s")
                    values.append(request.form['price'])
                if request.form.get('description'):
                    fields.append("Summary = %s")
                    values.append(request.form['description'])

                if fields:
                    sql = f"UPDATE Book SET {', '.join(fields)} WHERE Book_ID = %s"
                    values.append(book_id)
                    cur.execute(sql, tuple(values))

        elif entry_type == 'author':
            author_id = request.form['author_id']

            if action_type == 'delete':
                cur.execute("DELETE FROM Author WHERE Author_ID = %s", (author_id,))
            elif action_type == 'update' and request.form.get('author_name'):
                cur.execute("UPDATE Author SET Author_name = %s WHERE Author_ID = %s",
                            (request.form['author_name'], author_id))

        elif entry_type == 'publisher':
            publisher_id = request.form['publisher_id']

            if action_type == 'delete':
                cur.execute("DELETE FROM Publisher WHERE Publisher_ID = %s", (publisher_id,))
            elif action_type == 'update' and request.form.get('publisher_name'):
                cur.execute("UPDATE Publisher SET Publisher_name = %s WHERE Publisher_ID = %s",
                            (request.form['publisher_name'], publisher_id))

        elif entry_type == 'genre':
            genre_name = request.form['genre_name']

            if action_type == 'delete':
                cur.execute("DELETE FROM Genre WHERE Genre_name = %s", (genre_name,))
            elif action_type == 'update' and request.form.get('new_genre_name'):
                cur.execute("UPDATE Genre SET Genre_name = %s WHERE Genre_name = %s",
                            (request.form['new_genre_name'], genre_name))

        conn.commit()
        cur.close()
        conn.close()
        return redirect('/admin')

    except Exception as e:
        cur.close()
        conn.close()
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)