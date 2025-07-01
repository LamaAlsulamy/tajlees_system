import sqlite3
import csv

# Connect to SQLite database (creates the file if it doesn't exist)
conn = sqlite3.connect('seating_system.db')
cursor = conn.cursor()

# Optional: Enable foreign key support
cursor.execute('PRAGMA foreign_keys = ON;')

# --- Create the Rooms table ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_name TEXT NOT NULL,
        seat_count INTEGER NOT NULL,
        row_count INTEGER NOT NULL
    );
''')

# --- Create the Rankings table ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Rankings (
        id INTEGER PRIMARY KEY,
        category_name TEXT NOT NULL
    );
''')

# --- Create the Attendees table ---
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Attendees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        rank INTEGER NOT NULL,
        selection_order INTEGER
    );
''')

# --- Import Rooms Data from CSV ---
with open('القاعات والكراسي التحديث الاخير.csv', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cursor.execute('''
            INSERT INTO Rooms (room_name, seat_count, row_count)
            VALUES (?, ?, ?)
        ''', (row['اسم القاعة'], int(row['عدد الكراسي']), int(row['عدد الصفوف'])))
    print("Rooms data imported.")

# --- Insert Rankings Data (from your defined hierarchy) ---
ranking_data = [
    (1, 'الملك'),
    (2, 'ولي العهد'),
    (3, 'اصحاب السمو'),
    (4, 'اصحاب المعالي'),
    (5, 'اصحاب الفضيلة'),
    (6, 'اصحاب السعادة'),
    (7, 'شيوخ القبائل')
]

cursor.executemany('''
    INSERT OR IGNORE INTO Rankings (id, category_name)
    VALUES (?, ?)
''', ranking_data)
print("Rankings data imported.")

# --- Import Attendees Data from CSV ---
with open('Sheet 2-جدول الأسماء.csv', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    order = 1  # This represents the selection order.
    for row in reader:
        rank = int(row['رقم الفئة'].strip())
        name = row['الاسم'].strip()
        cursor.execute('''
            INSERT INTO Attendees (name, rank, selection_order)
            VALUES (?, ?, ?)
        ''', (name, rank, order))
        order += 1
    print("Attendees data imported.")

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database setup complete. 'seating_system.db' is ready.")
