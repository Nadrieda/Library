-- Case insensitive text extension
CREATE EXTENSION IF NOT EXISTS citext;

-- Drop existing tables
DROP TABLE IF EXISTS "User", Book, Author, Publisher, Genre, Borrow CASCADE;

-- Recreate tables
CREATE TABLE IF NOT EXISTS Author (
    Author_ID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Author_name CITEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Publisher (
    Publisher_ID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Publisher_name CITEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS Genre (
    Genre_name CITEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Book (
    Book_ID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    Title TEXT NOT NULL ,
    Author_ID INT NOT NULL REFERENCES Author(Author_ID),
    Genre_name CITEXT NOT NULL REFERENCES Genre(Genre_name),
    Publisher_ID INT NOT NULL REFERENCES Publisher(Publisher_ID),
    ISBN VARCHAR(20) UNIQUE,
    Copies_available INT DEFAULT 0 CHECK (Copies_available >= 0),
    Price NUMERIC(10, 2),
    Summary TEXT
);

CREATE TABLE IF NOT EXISTS "User" (
    User_ID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    User_Name VARCHAR(100) NOT NULL,
    User_Email CITEXT UNIQUE NOT NULL,
    User_Password TEXT NOT NULL,
    User_IsAdmin BOOLEAN DEFAULT FALSE
);

CREATE TABLE Borrow (
    Borrow_ID INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    User_ID INTEGER REFERENCES "User"(User_ID) ON DELETE CASCADE,
    Book_ID INTEGER REFERENCES Book(Book_ID) ON DELETE CASCADE,
    Borrow_Date DATE DEFAULT CURRENT_DATE,
    Return_Date DATE,
    Is_Returned BOOLEAN DEFAULT FALSE
);

INSERT INTO "User" (User_Name, User_Email, User_Password, User_IsAdmin)
VALUES (
    'Admin',
    'admin@admin.com',
    'scrypt:32768:8:1$Ce2zrYeYhtLCLoRX$922f99b12f3c25109ffc1f85bc7f39c9a2b32f232aec134b4698ffb114005297379d2ad0810e71e7ea2766c2719e1147f9766b30ad937866eada274c8eca1737',
    TRUE
);

INSERT INTO "User" (User_Name, User_Email, User_Password, User_IsAdmin)
VALUES (
    'TestUser',
    'test@test.com',
    'scrypt:32768:8:1$XFKrLTITcaZRvDuK$6dcb13eb8632324817c942ad87102204645bf2f28680ce60cbed9f3141bdd1b697a262db67c0fc2ca5e91aaaa2c2fc3240369748bc31380962799c333a0f2d1d',
    False
);

INSERT INTO Author (Author_name) VALUES ('J. R. R. Tolkien')
ON CONFLICT (Author_name) DO NOTHING;

INSERT INTO Genre (Genre_name) VALUES ('Fantasy')
ON CONFLICT (Genre_name) DO NOTHING;

INSERT INTO Publisher (Publisher_name) VALUES ('Harpercollins')
ON CONFLICT (Publisher_name) DO NOTHING;

INSERT INTO Book (
    Title, Author_ID, Genre_name, Publisher_ID,
    ISBN, Copies_available, Price, Summary
) VALUES (
    'The Fellowship of the Ring',
    (SELECT Author_ID FROM Author WHERE Author_name = 'J. R. R. Tolkien'),
    'Fantasy',
    (SELECT Publisher_ID FROM Publisher WHERE Publisher_name = 'Harpercollins'),
    '9780008567125',
    3,
    189.95,
    'Sauron, the Dark Lord, has gathered to him all the Rings of Power - the means by which he intends to rule Middle-earth. All he lacks in his plans for dominion is the One Ring - the ring that rules them all - which has fallen into the hands of the hobbit, Bilbo Baggins.'
);

INSERT INTO Book (
    Title, Author_ID, Genre_name, Publisher_ID,
    ISBN, Copies_available, Price, Summary
) VALUES (
    'The Return of the King',
    (SELECT Author_ID FROM Author WHERE Author_name = 'J. R. R. Tolkien'),
    'Fantasy',
    (SELECT Publisher_ID FROM Publisher WHERE Publisher_name = 'Harpercollins'),
    '9780008567149',
    5,
    194.95,
    'The Companions of the Ring have become involved in separate adventures as the quest continues. Aragorn, revealed as the hidden heir of the ancient Kings of the West, joined with the Riders of Rohan against the forces of Isengard, and took part in the desperate victory of the Hornburg. Merry and Pippin, captured by orcs, escaped into Fangorn Forest and there encountered the Ents.'
);

INSERT INTO Book (
    Title, Author_ID, Genre_name, Publisher_ID,
    ISBN, Copies_available, Price, Summary
) VALUES (
    'The Two Towers',
    (SELECT Author_ID FROM Author WHERE Author_name = 'J. R. R. Tolkien'),
    'Fantasy',
    (SELECT Publisher_ID FROM Publisher WHERE Publisher_name = 'Harpercollins'),
    '9780008567132',
    6,
    194.95,
    'Frodo and the Companions of the Ring have been beset by danger during their quest to prevent the Ruling Ring from falling into the hands of the Dark Lord by destroying it in the Cracks of Doom. They have lost the wizard, Gandalf, in the battle with an evil spirit in the Mines of Moria; and at the Falls of Rauros, Boromir, seduced by the power of the Ring, tried to seize it by force. While Frodo and Sam made their escape the rest of the company were attacked by Orcs.'
);

INSERT INTO Book (
    Title, Author_ID, Genre_name, Publisher_ID,
    ISBN, Copies_available, Price, Summary
) VALUES (
    'The Hobbit',
    (SELECT Author_ID FROM Author WHERE Author_name = 'J. R. R. Tolkien'),
    'Fantasy',
    (SELECT Publisher_ID FROM Publisher WHERE Publisher_name = 'Harpercollins'),
    '9780007487301',
    2,
    184.95,
    'Bilbo Baggins is a hobbit who enjoys a comfortable, unambitious life, rarely travelling further than the pantry of his hobbit-hole in Bag End.'
);
