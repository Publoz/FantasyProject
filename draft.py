from os import name
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

    tmp_results = """
    CREATE TABLE IF NOT EXISTS TmpResults (
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
    execute_query(connection, players)
    execute_query(connection, results)
    execute_query(connection, tmp_results)
    execute_query(connection, gms)

def update_results():
    query = """
    UPDATE Results
    SET points = goals - (twoMins*2) + (win * 3);
    """
    execute_query(connection, query)

def load_file_results(path):
    file = open(path, "r")
    year = int(file.read(4))
    file.read(1)
    round = int(file.readline().strip('\n'))

    winners = set()
    line = file.readline() # <winners>
    line = file.readline() #first winners
    while(line.strip('\n') != "<\Winners>"):
        winners.add(line.strip('\n'))
        line = file.readline()

    
    while(True):
        club = file.readline().strip('\n')
        team = file.readline().strip('\n')
        win = 0
        if( (club + team) in winners):
            win = 1
        
        line = file.readline()

        #Loop through team
        while(line != team[:1] + '\\' + team[1:]):
            chunks = line.split()
            name = ""
            goals = 0
            two_mins = 0
            for i in range(len(chunks)):
                if(chunks[i].isdigit()):
                    goals = chunks[i]
                    if(i == len(chunks)-1):
                        break
                    else:
                        two_mins = chunks[i+1]
                        break
                else:
                    name += chunks[i]

            query = """
                INSERT INTO TmpResults
                VALUES ({}, {}, {}, {}, {}, {}, {}, NULL)
            """.format(name, club, year, round, goals, two_mins, win)
            line = file.readline()
        #assert file.readline() == 
    

                





    file.close()


#--------------------------------START----------------------------------------------
connection = create_connection("fantasyDatabase.sqlite")
#load_file_results("exFile.txt")
