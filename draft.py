from os import name
import sqlite3
from sqlite3 import Error
from sqlite3.dbapi2 import Connection
from flask import Flask, render_template, url_for, redirect, jsonify, request

app = Flask(__name__)

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



@app.route('/')
def init():
    return redirect('/home')

@app.route('/home')
def hello_world():
    return render_template('index.html')

@app.route('/get_players', methods=['POST'])
def get_players(): 
    print('you are here')
    return redirect('/home')

@app.route('/players.html')
def changeToPlayers():
    return render_template('players.html')


def create_tables():
    connection = create_connection("fantasyDatabase.sqlite")
    #Get rid of GK field and just have a general goalie for each team?
    #PlayerName and club are used to distinguish between players - the year determines which
    #year this player is playing
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
    #Might need to incorporate score for players points
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

    #Is it worth storing gms total points
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

    #Clearing tables
    query = """
            DELETE FROM Gms;
            """
    execute_query(connection, query)
    query = """
            DELETE FROM Results;
            """
    execute_query(connection, query)
    query = """
            DELETE FROM TmpResults;
            """
    execute_query(connection, query)
    query = """
            DELETE FROM Players;
            """
    execute_query(connection, query)

    query = """
            INSERT INTO Players
        VALUES ('Paul Ireland', 'Vikings', 2022, 25, 'A', 0),
	   ('Ben Potaka', 'Victoria', 2022, 20, 'A', 0),
	   ('Thomas Roxburgh', 'Spartanz', 2022, 10, 'A', 1),
	   ('Willy Makea', 'Spartanz', 2022, 20, 'A', 0),
	   ('Paul Ireland', 'Vikings', 2021, 25, 'A', 0);
       """
    execute_query(connection, query)

    query = """
    INSERT INTO Results 
    VALUES ('Paul Ireland', 'Vikings', 2022, 1, 6, 0, 1, NULL),
	   ('Willy Makea', 'Spartanz', 2022, 1, 3, 1, 0, NULL),
	   ('Ben Potaka', 'Victoria', 2022, 1, 5, 2, 0, NULL),
	   ('Thomas Roxburgh', 'Spartanz', 2022, 1, 0, 0, 0, NULL),
	   ('Paul Ireland', 'Vikings', 2022, 2, 1, 0, 0, NULL),
	   ('Willy Makea', 'Spartanz', 2022, 2, 5, 2, 1, NULL),
	   ('Ben Potaka', 'Victoria', 2022, 2, 5, 2, 0, NULL),
	   ('Thomas Roxburgh', 'Spartanz', 2022, 2, 0, 0, 0, NULL),
	   ('Paul Ireland', 'Vikings', 2021, 1, 20, 3, 1, NULL)
	   ;
       """
    execute_query(connection, query)

    query = """
    INSERT INTO Gms
    VALUES ('Paul Ireland', 'Vikings', 2022, 1, 'Sauls boys'),
	   ('Willy Makea', 'Spartanz', 2022, 1, 'Sauls boys'),
	   ('Ben Potaka', 'Victoria', 2022, 1, 'Dave'),
	   ('Thomas Roxburgh', 'Spartanz', 2022, 1, 'Dave'), 
	   ('Paul Ireland', 'Vikings', 2022, 2, 'Sauls boys'),
	   ('Willy Makea', 'Spartanz', 2022, 2, 'Sauls boys'),
	   ('Ben Potaka', 'Victoria', 2022, 2, 'Dave'),
	   ('Thomas Roxburgh', 'Spartanz', 2022, 2, 'Dave') 
	   ;
	   
       """
    execute_query(connection, query)

    query = """
    UPDATE Results
    SET points = goals - (twoMins*2) + (win);   
       """
    execute_query(connection, query)

    connection.close()

@app.route('/players/<col>', methods = ['GET'])
def getPlayers(col):
    connection = create_connection("fantasyDatabase.sqlite")
    query = """
            SELECT P.playerName AS "Name", p.price AS "Price", p.club || ' ' || p.team AS "Team", sum(r.points) AS "Points",
            round(sum(r.points) * 1.0 / (count(R.playerName) * 1.0),2) AS "AVG", sum(r.twoMins) AS "2 mins"  
            FROM Results R JOIN Players P
            ON P.playerName = R.playerName AND p.year = r.year AND p.club = r.club
            WHERE R.year = {}
            GROUP BY P.playerName, P.club
            ORDER BY "{}" DESC
            """.format(year, col)
    data = execute_read_query(connection, query)

    cols = ['Name', 'Price', 'Team', 'Points', 'AVG', '2 mins']

    connection.close()

    dic = {"cols" : cols, "data" : data}
    return jsonify(dic)

@app.route('/allTime/<col>', methods = ['GET'])
def getAllTime(col):
    connection = create_connection("fantasyDatabase.sqlite")

    query =  """
            SELECT playerName AS "Name", SUM(goals) AS "Goals", sum(twoMins) AS "2 minutes", sum(win) AS "Wins"
            FROM Results
            GROUP BY playerName
            ORDER BY "{}" DESC;
             """.format(col)
    data = execute_read_query(connection, query)
    connection.close()

    cols = ['Name', 'Goals', '2 minutes', 'Wins']

    dic = {"cols" : cols, "data" : data}
    return jsonify(dic)

@app.route('/topPlayers', methods = ['GET'])
def getTop():
    connection = create_connection("fantasyDatabase.sqlite")

    query = """
            SELECT playerName, points
            FROM Results
            WHERE round = {} AND year = {}
            ORDER BY points DESC
            LIMIT 3;
            """.format(round, year)
    data = execute_read_query(connection, query)
    connection.close()
    return jsonify(data)

    
@app.route('/topGms', methods = ['GET'])
def getGms():
   
    connection = create_connection("fantasyDatabase.sqlite")

    query = """
            SELECT RANK() OVER (ORDER BY "Points" DESC) AS 'Rank', G.gmName AS 'GM',SUM(R.points) AS "Points"
            FROM Gms G JOIN Results R
            ON G.playerName = R.playerName AND G.club = R.club AND G.year = R.year AND G.round = R.round
            WHERE R.year = {}
            GROUP BY G.gmName
            ORDER BY "Points" DESC;    
            """.format(year)
    data = execute_read_query(connection, query)

    cols = ['Rank', 'Gm name', 'Points']
    dic = {"cols" : cols, "data" : data}

    connection.close()
    return jsonify(dic)

#  @app.route('/topPlayers', methods = ['GET'])
#  def getTop():
#     connection = create_connection("fantasyDatabase.sqlite")

#     query = """

#              """
#     data = execute_read_query(connection, query)
#     connection.close()
#     return jsonify(data)

round = 1
year = 2022

create_tables()

if __name__ == '__main__':
    app.run(debug=True)

