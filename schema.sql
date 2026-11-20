-- Library Management System: database schema
-- Run once:  mysql -u root -p < schema.sql

CREATE DATABASE IF NOT EXISTS library_db;
USE library_db;

CREATE TABLE IF NOT EXISTS members (
    member_id   INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(120) NOT NULL UNIQUE,
    phone       VARCHAR(15),
    joined_on   DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS books (
    book_id           INT AUTO_INCREMENT PRIMARY KEY,
    title             VARCHAR(200) NOT NULL,
    author            VARCHAR(120) NOT NULL,
    isbn              VARCHAR(20) UNIQUE,
    total_copies      INT NOT NULL DEFAULT 1,
    available_copies  INT NOT NULL DEFAULT 1,
    CONSTRAINT chk_copies CHECK (available_copies >= 0 AND available_copies <= total_copies)
);

-- One row per issue of a book to a member (many-to-many between books and members)
CREATE TABLE IF NOT EXISTS issues (
    issue_id     INT AUTO_INCREMENT PRIMARY KEY,
    book_id      INT NOT NULL,
    member_id    INT NOT NULL,
    issue_date   DATE NOT NULL,
    due_date     DATE NOT NULL,
    return_date  DATE NULL,
    fine         DECIMAL(8,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (book_id)   REFERENCES books(book_id),
    FOREIGN KEY (member_id) REFERENCES members(member_id)
);

-- Sample data (optional)
INSERT INTO books (title, author, isbn, total_copies, available_copies) VALUES
 ('Introduction to Algorithms', 'Thomas H. Cormen', '9780262046305', 2, 2),
 ('Let Us C', 'Yashavant Kanetkar', '9788183331630', 3, 3),
 ('Database System Concepts', 'Silberschatz, Korth, Sudarshan', '9780078022159', 2, 2);

INSERT INTO members (name, email, phone, joined_on) VALUES
 ('Demo Member', 'demo@example.com', '9999999999', CURDATE());
