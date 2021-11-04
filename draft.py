import sqlite3
from sqlite3 import Error

#https://realpython.com/python-sql-libraries/#sqlite from here
def create_connection(path):
    connection = None
    try:
        connection = sqlite3.connect(path)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")

    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

def create_tables():
    players = """
    CREATE TABLE IF NOT EXISTS Players (
        name TEXT,
        club TEXT,
        year INTEGER,
        price INTEGER,
        team TEXT,
        gk INTEGER NOT NULL,
        PRIMARY KEY(name, club, year)
    )
    """

    results = """
    CREATE TABLE IF NOT EXISTS Results (
        name TEXT,
        club TEXT,
        year INTEGER,
        round INTEGER,
        goals INTEGER,
        twoMins INTEGER,
        win INTEGER NOT NULL,
        points INTEGER,
        PRIMARY KEY(name, club, year, round)
        FOREIGN KEY (name) REFERENCES Players (name),
        FOREIGN KEY (club) REFERENCES Players (club),
        FOREIGN KEY (year) REFERENCES Players (year),
    )
    """
    execute_query(connection, players)
    execute_query(connection, results)



connection = create_connection("fantasyDatabase.sqlite")