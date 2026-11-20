# Library Management System

A command-line Library Management System built with **Python** and **MySQL**. It manages books, members and the issue/return process, including due dates and late fines.

## Features
- Add books and members
- View and search books by title or author
- Issue a book (checks availability, sets a 14-day due date)
- Return a book (calculates fine at Rs. 2 per late day)
- View currently issued and overdue books
- View a member's borrowing history

## Database design
Three tables in `library_db`:

| Table | Purpose |
|-------|---------|
| `members` | Library members (unique email) |
| `books` | Books with total and available copies |
| `issues` | One row per issue; links a book to a member through foreign keys |

SQL concepts used: primary and foreign keys, `UNIQUE` and `CHECK` constraints, `JOIN`s, `LIKE` search, `DATEDIFF`, parameterized queries and transactions (issue/return update two tables together).

## Setup
1. Install Python 3 and MySQL 8.
2. Install the dependency:
   ```
   pip install -r requirements.txt
   ```
3. Create the database and tables:
   ```
   mysql -u root -p < schema.sql
   ```
4. Set your MySQL password (and optionally host/user/db name):
   - Windows (PowerShell): `$env:DB_PASSWORD="your_password"`
   - Mac/Linux: `export DB_PASSWORD="your_password"`
5. Run the app:
   ```
   python main.py
   ```

## Project structure
```
main.py            # menu and all features
db.py              # MySQL connection settings
schema.sql         # tables and sample data
requirements.txt
```

## Possible improvements
- Login for librarian and members
- GUI or web version (Flask)
- Book reservations and email reminders
