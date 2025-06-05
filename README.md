### Installing dependencies:
pip install -r requirements.txt

### PostgreSQL setup
This project uses PostgreSQL as the database, which needs to be installed. https://www.postgresql.org/download/<br/>
You will need to create a database and then modify the connection settings in db.py.

### Initialize database:

run 'setup_db.py'

Succesfully running 'setup_db.py' should give you 1 Author, 1 Publisher, 1 Genre, 4 Books and 2 user accounts. A normal user account with email="test@test.com" and password="test". It should also give an admin account with email="admin@admin.com" and password="admin" this account may add, modify and delete database entries. You can also run 'setup_db.py' again to reset the database.

### To start app:

run app.py

Then visit http://localhost:5000