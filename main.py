"""Library Management System - command line app (Python + MySQL)."""
from datetime import date, timedelta

import mysql.connector

from db import get_connection

LOAN_DAYS = 14        # how long a book can be kept
FINE_PER_DAY = 2      # fine in rupees per late day


# ---------- helpers ----------
def run_query(sql, params=(), fetch=True):
    """Run one query and return rows (for SELECT) or the new row id."""
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        if fetch:
            return cur.fetchall()
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def print_table(rows, headers):
    if not rows:
        print("  (no records found)")
        return
    widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    line = " | ".join(str(h).ljust(widths[i]) for i, h in enumerate(headers))
    print("  " + line)
    print("  " + "-" * len(line))
    for r in rows:
        print("  " + " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(r)))


def ask_int(prompt):
    while True:
        value = input(prompt).strip()
        if value.isdigit():
            return int(value)
        print("  Please enter a valid number.")


# ---------- features ----------
def add_book():
    title = input("Title: ").strip()
    author = input("Author: ").strip()
    isbn = input("ISBN (optional): ").strip() or None
    copies = ask_int("Number of copies: ")
    if not title or not author or copies < 1:
        print("  Title, author and at least 1 copy are required.")
        return
    try:
        book_id = run_query(
            "INSERT INTO books (title, author, isbn, total_copies, available_copies) "
            "VALUES (%s, %s, %s, %s, %s)",
            (title, author, isbn, copies, copies), fetch=False)
        print(f"  Book added with ID {book_id}.")
    except mysql.connector.IntegrityError:
        print("  A book with this ISBN already exists.")


def add_member():
    name = input("Name: ").strip()
    email = input("Email: ").strip()
    phone = input("Phone (optional): ").strip() or None
    if not name or not email:
        print("  Name and email are required.")
        return
    try:
        member_id = run_query(
            "INSERT INTO members (name, email, phone, joined_on) VALUES (%s, %s, %s, CURDATE())",
            (name, email, phone), fetch=False)
        print(f"  Member added with ID {member_id}.")
    except mysql.connector.IntegrityError:
        print("  A member with this email already exists.")


def view_books():
    rows = run_query("SELECT book_id, title, author, available_copies, total_copies "
                     "FROM books ORDER BY title")
    print_table(rows, ["ID", "Title", "Author", "Available", "Total"])


def search_books():
    term = input("Search by title or author: ").strip()
    like = f"%{term}%"
    rows = run_query("SELECT book_id, title, author, available_copies FROM books "
                     "WHERE title LIKE %s OR author LIKE %s ORDER BY title", (like, like))
    print_table(rows, ["ID", "Title", "Author", "Available"])


def issue_book():
    book_id = ask_int("Book ID: ")
    member_id = ask_int("Member ID: ")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT title, available_copies FROM books WHERE book_id = %s FOR UPDATE", (book_id,))
        book = cur.fetchone()
        cur.execute("SELECT name FROM members WHERE member_id = %s", (member_id,))
        member = cur.fetchone()
        if not book or not member:
            print("  Invalid book ID or member ID.")
            return
        if book[1] < 1:
            print("  Sorry, no copies of this book are available right now.")
            return
        today = date.today()
        due = today + timedelta(days=LOAN_DAYS)
        cur.execute("INSERT INTO issues (book_id, member_id, issue_date, due_date) VALUES (%s, %s, %s, %s)",
                    (book_id, member_id, today, due))
        cur.execute("UPDATE books SET available_copies = available_copies - 1 WHERE book_id = %s", (book_id,))
        conn.commit()          # both changes are saved together or not at all
        print(f"  '{book[0]}' issued to {member[0]}. Due date: {due}.")
    except mysql.connector.Error as err:
        conn.rollback()
        print("  Database error:", err)
    finally:
        conn.close()


def return_book():
    issue_id = ask_int("Issue ID: ")
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT book_id, due_date, return_date FROM issues WHERE issue_id = %s FOR UPDATE",
                    (issue_id,))
        row = cur.fetchone()
        if not row:
            print("  Invalid issue ID.")
            return
        book_id, due, returned = row
        if returned is not None:
            print("  This book has already been returned.")
            return
        today = date.today()
        late_days = max((today - due).days, 0)
        fine = late_days * FINE_PER_DAY
        cur.execute("UPDATE issues SET return_date = %s, fine = %s WHERE issue_id = %s",
                    (today, fine, issue_id))
        cur.execute("UPDATE books SET available_copies = available_copies + 1 WHERE book_id = %s", (book_id,))
        conn.commit()
        print(f"  Book returned. Late days: {late_days}. Fine: Rs. {fine}.")
    except mysql.connector.Error as err:
        conn.rollback()
        print("  Database error:", err)
    finally:
        conn.close()


def view_issued_books():
    rows = run_query(
        "SELECT i.issue_id, b.title, m.name, i.issue_date, i.due_date "
        "FROM issues i JOIN books b ON i.book_id = b.book_id "
        "JOIN members m ON i.member_id = m.member_id "
        "WHERE i.return_date IS NULL ORDER BY i.due_date")
    print_table(rows, ["Issue ID", "Book", "Member", "Issued", "Due"])


def overdue_books():
    rows = run_query(
        "SELECT i.issue_id, b.title, m.name, i.due_date, DATEDIFF(CURDATE(), i.due_date) AS days_late "
        "FROM issues i JOIN books b ON i.book_id = b.book_id "
        "JOIN members m ON i.member_id = m.member_id "
        "WHERE i.return_date IS NULL AND i.due_date < CURDATE() ORDER BY days_late DESC")
    print_table(rows, ["Issue ID", "Book", "Member", "Due", "Days late"])


def member_history():
    member_id = ask_int("Member ID: ")
    rows = run_query(
        "SELECT b.title, i.issue_date, i.return_date, i.fine "
        "FROM issues i JOIN books b ON i.book_id = b.book_id "
        "WHERE i.member_id = %s ORDER BY i.issue_date DESC", (member_id,))
    print_table(rows, ["Book", "Issued", "Returned", "Fine"])


MENU = [
    ("Add book", add_book),
    ("Add member", add_member),
    ("View all books", view_books),
    ("Search books", search_books),
    ("Issue book", issue_book),
    ("Return book", return_book),
    ("View currently issued books", view_issued_books),
    ("View overdue books", overdue_books),
    ("Member borrowing history", member_history),
]


def main():
    try:
        get_connection().close()
    except mysql.connector.Error as err:
        print("Could not connect to MySQL:", err)
        print("Check DB_HOST, DB_USER, DB_PASSWORD, DB_NAME and that schema.sql has been run.")
        return
    while True:
        print("\n=== Library Management System ===")
        for i, (label, _) in enumerate(MENU, start=1):
            print(f"{i}. {label}")
        print("0. Exit")
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        if choice.isdigit() and 1 <= int(choice) <= len(MENU):
            print()
            MENU[int(choice) - 1][1]()
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()
