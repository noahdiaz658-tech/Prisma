import sqlite3

connection = sqlite3.connect("../../memory/appMemory.db", timeout=5)
cursor = connection.cursor()

def get_cursor():
    return cursor

def get_connection():
    return connection

