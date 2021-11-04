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

def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        print("Read successful")
        return result
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

def rem(value):
    value = str(value)
    return value.strip('\n').strip(',')

def load_file_results(path):
    file = open(path, "r")
    line = file.readline().split(',')
    year = line[0]
    pos = year.find('2') #get rid of random values at start
    year = year[pos:]
    year = int(year)
    round = int(line[1])
    
    winners = set()
    

    assert file.readline().strip('\n').strip(',') == "<winners>", "Not winners second line"
    line = rem(file.readline())
    while(rem(line) != "<\winners>"):
        winners.add(line)
        line = rem(file.readline())
           
    club = rem(file.readline())
    
    # while(line != team[:1] + '\\' + team[1:]):

    for x in file:

        name = ""
        goals = 0
        two_mins = 0
        win = 0
        if(club == ""):
            club = rem(x)
            continue

        elif(rem(x) == club[:0] + '\\' + club[0:]):
            club = ""
            continue

        else:
            data = rem(x).split(',')
            name = data[0]
            goals = data[1]
            if(len(data) == 3):
                two_mins = data[2]
            if(club in winners):
                win = 1


        query = """
                INSERT INTO TmpResults
                VALUES ('{}', '{}', {}, {}, {}, {}, {}, NULL)
            """.format(name, club, year, round, goals, two_mins, win)

        execute_query(connection, query)        
        




    file.close()


#--------------------------------START----------------------------------------------
connection = create_connection("fantasyDatabase.sqlite")
create_tables()
query = """
        DELETE FROM TmpResults;
        """
execute_query(connection, query) #making sure tmpresults clear for testing

load_file_results("test.csv")

query = """
        SELECT*
        FROM TmpResults;
        """
testing = execute_read_query(connection, query)
print(testing)