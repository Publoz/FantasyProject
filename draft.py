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
        playerName TEXT,
        club TEXT,
        year INTEGER,
		price INTEGER,
		team TEXT,
		gk INTEGER NOT NULL,
		PRIMARY KEY(playerName, club, year)
	);
    """

    results = """
    CREATE TABLE IF NOT EXISTS Results (
        playerName TEXT,
        club TEXT,
        year INTEGER,
		round INTEGER,
		goals INTEGER,
		twoMins INTEGER,
		win INTEGER NOT NULL,
		points INTEGER,
		PRIMARY KEY(playerName, club, year, round),
		FOREIGN KEY(playerName, club, year) REFERENCES Players(playerName, club, year)
	);
    """

    gms = """
    CREATE TABLE IF NOT EXISTS Gms (
        playerName TEXT,
        club TEXT,
        year INTEGER,
        round INTEGER,
        gmName TEXT,
		PRIMARY KEY(playerName, club, year, round, gmName)
		FOREIGN KEY(playerName, club, year) REFERENCES players(playerName, club, year),
		FOREIGN KEY(playerName, club, year, round) REFERENCES results(playerName, club, year, round)
	);
    """

def update_results():
    query = """
    UPDATE Results
    SET points = goals - (twoMins*2) + (win * 3);
    """
    execute_query(connection, query)



    execute_query(connection, players)
    execute_query(connection, results)



connection = create_connection("fantasyDatabase.sqlite")