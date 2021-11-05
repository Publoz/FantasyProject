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

#Executes SQL that changes database
def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except Error as e:
        print(f"The error '{e}' occurred")

#Returns the result of a read/select query
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

#Creates the tables for this database
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


def update_results(): #CHANGE TO RESULTS
    query = """ 
    UPDATE TmpResults
    SET points = goals - (twoMins*2) + (win);
    """
    execute_query(connection, query)

#Removes annoying end line and commas
def rem(value):
    value = str(value)
    return value.strip('\n').strip(',')

#Reads a CSV file of a rounds results into tmpResults table which will need to 
#transferred to actual results
def load_file_results(path): #Goes into tmpResults
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

#Gm's leaderboard - returns rank, name and points
def leaderboard():
    query = """"
            SELECT RANK() OVER (ORDER BY "Points" DESC) AS 'Rank', G.gmName AS 'GM', SUM(R.points) AS "Points"
            FROM Gms G JOIN Results R
            ON G.playerName = R.playerName AND G.club = R.club AND G.year = R.year
            GROUP BY G.gmName
            ORDER BY "Points" DESC;
            """
    return execute_read_query(connection, query)

#Overall player stats leaderboard
def player_stats(sorting):
    query = """
            SELECT P.playerName AS "Name", p.price AS "Price", p.club || ' ' || p.team AS "Team", sum(r.points) AS "Points", sum(r.points) * 1.0 / (count(R.playerName) * 1.0) AS "AVG", sum(r.twoMins) AS "2 mins"  
            FROM Results R JOIN Players P
            ON P.playerName = R.playerName AND p.year = r.year AND p.club = r.club
            GROUP BY P.playerName, P.club
            ORDER BY {} DESC; /* ORDER BY Can change based on param */
            """.format(sorting)
    return execute_read_query(connection, query)

#Add a player to the players database
def add_player(name, club, year, price, team, gk):
    query = """
            INSERT INTO Players
            VALUES ('{}', '{}', {}, {}, '{}', {});
            """.format(name, club, year, price, team, gk)
    execute_query(connection, query)

#Get a gm's squad for a round
def get_squad(gmName, round): #Need to get average too
    query = """
            SELECT playerName, price, gk
            FROM Players
            WHERE gmName = '{}' AND round = {}  
            """.format(gmName, round)
    return execute_read_query(connection, query)

#Get the average amount of points for a player
def get_avg(name, club, year):
    query = """
            SELECT sum(points) / count(playerName)
            FROM TmpResults
            WHERE playerName = '{}' AND club = '{}' AND year = {}
            GROUP BY playerName, club;
            """.format(name, club, year)
    return execute_read_query(connection, query)

#Get a team - specify club, team and year
#Returns [(PlayerName, price)]
def get_team(club, team, year):
    query = """
            SELECT playerName, price
            FROM Players
            WHERE club = '{}' AND team = '{}' AND year = {}; 
            """.format(club, team, year)

    return execute_read_query(connection, query)

#Returns the cost of a gms squad for a round
def compute_cost(gmName, round):
    query = """
            SELECT SUM(price)
            FROM Players P JOIN Gms G
            ON P.playerName = G.playerName AND P.club = G.club AND P.year = G.year
            WHERE G.gmName = '{}' AND round = {}; 
            """.format(gmName, round)
    return execute_read_query(connection, query)

#--------------------------------START----------------------------------------------
connection = create_connection("fantasyDatabase.sqlite")
create_tables()
query = """
        DELETE FROM TmpResults;
        """
execute_query(connection, query) #making sure tmpresults clear for testing
query = """
        DELETE FROM Players;
        """
execute_query(connection, query)
query = """
        DELETE FROM Gms;
        """
execute_query(connection, query)
query = """
        DELETE FROM Results;
        """
execute_query(connection, query)

load_file_results("test.csv")

query = """
        SELECT*
        FROM TmpResults;
        """
update_results()
testing = execute_read_query(connection, query) #Testing select all from tmpResults
print(testing)


#print(get_avg("Paul Ireland", "Vikings", 2022)) #returns [(7,)]
#avg = int(get_avg("Paul Ireland", "Vikings", 2022)[0][0]) #How to get value from query
