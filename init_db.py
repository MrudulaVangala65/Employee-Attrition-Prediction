import sqlite3

# Connect to the database
conn = sqlite3.connect('user.db')
c = conn.cursor()

# Create the User table
c.execute('''CREATE TABLE IF NOT EXISTS User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)''')

# Insert the default admin user
c.execute("INSERT OR IGNORE INTO User (username, password) VALUES (?, ?)", ("admin", "admin"))
c.execute("INSERT OR IGNORE INTO User (username, password) VALUES (?, ?)", ("Admin", "Admin"))
# Commit changes and close connection
conn.commit()
conn.close()
