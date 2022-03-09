import sqlite3

connection = sqlite3.connect('database.db')

# Initiate database from file schema.sql
with open('schema.sql') as f:
    connection.executescript(f.read())


connection.commit()
connection.close()