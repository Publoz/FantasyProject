from os import name
import sqlite3
import json
from sqlite3 import Error
from sqlite3.dbapi2 import Connection
from flask import Flask, render_template, url_for, redirect, jsonify, request, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = "MrWorldWideMr305Pitbull"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
bootstrap = Bootstrap(app)


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

def execute_read_query_one(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        if(result is None):
            print("Read was null")
            return ""
        
        print("Read successful")
        return result[0]
    except Error as e:
        print(f"The error '{e}' occurred")

def execute_read_query_one_row(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchone()
        if(result is None):
            print("Read for row was null")
            return ""
        
        print("Read successful")
        return result
    except Error as e:
        print(f"The error '{e}' occurred")

class LoginForm(FlaskForm):
    gmName = StringField('Club Name', validators=[InputRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=80)])
    remember = BooleanField('Remember me')

class RegisterForm(FlaskForm):
    gmName = StringField('Club Name', validators=[InputRequired(), Length(min=3, max=20)])
    name = StringField('Name', validators=[InputRequired(), Length(min=3, max=30)])
    email = StringField('Email', validators=[InputRequired(), Length(min=3, max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=80)])

class User(UserMixin):
    def __init__(self, id, gmName, email, password):
         self.id = id
         self.gmName = gmName
         self.email = email
         self.password = password
         self.authenticated = False
    def is_active(self):
         return self.is_active()
    def is_anonymous(self):
         return False
    def is_authenticated(self):
         return self.authenticated
    def is_active(self):
         return True
    def get_id(self):
         return self.id
    def get_gmName(self):
        return self.gmName
    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)



@app.route('/')
def init():
    return redirect('/home')

@app.route('/home')
def hello_world():
    return render_template('index.html', name="")

@app.route('/get_players', methods=['POST'])
def get_players(): 
    print('you are here')
    return redirect('/home')

@app.route('/players.html')
def changeToPlayers():
    return render_template('players.html')

@app.route('/debug')
def debug():
    print('-------------------------------------DEBUG------------')
    if "user" in session:
        print(session["user"])
    
    return redirect('/home')

#-------------------------------------------------LOGIN---------------------------
@app.route('/login', methods = ['GET', 'POST'])
def changeToLogin():
    form = LoginForm()
    message = ""
    
    if(form.validate_on_submit()):
        if(getUser(form.gmName.data,  (form.password.data)) == "" or not str(form.gmName.data).isalnum()
        or not str(form.password.data).isalnum()):
            message = "Invalid Username or password"
            render_template('login.html', form=form, message=message)
        else:
            user = load_user(form.gmName.data)
            #login_user(user, form.remember.data)
            #session['user'] = user.toJson()
            session['user'] = user.get_gmName()
            return render_template('index.html', name="Welcome " + session['user'])

    return render_template('login.html', form=form, message=message)

@app.route('/signup', methods =['GET', 'POST'])
def signup():
    form = RegisterForm()

    if(form.validate_on_submit()):
        hashed = generate_password_hash(form.password.data, method='sha256')
        registerUser(form.gmName.data, form.name.data, form.email.data, hashed)
        return "<h1>New User created</h1>"  

    return render_template('signup.html', form=form)
# @app.route('/loginData', methods = ['POST'])
# def validate():
#     gmName = request.form['gmName']
#     password = request.form['password']

@login_manager.user_loader
def load_user(gmName):
    connection = create_connection("fantasyDatabase.sqlite")
    query = """
            SELECT *
            FROM USERS
            WHERE gmName = '{}'
            """.format(gmName)

    user = execute_read_query_one_row(connection, query)
    if(user == ""): #TODO No idea why this started triggering on load - this is to stop crash
        return None
    connection.close()
    print(user)
    print("done")
    return User(user[0], user[1], user[2], user[3])

@app.route('/logout') #TODO Not working - could not build url endpoint
def logout(): #Login required not working got rid of tag
    if "user" in session:
        session.pop("user", None)
   # logout_user()
    return redirect('/home')


def getUser(gmName, password):
    connection = create_connection("fantasyDatabase.sqlite")

    query = """
            SELECT* 
            FROM Users
            """
    print(execute_read_query(connection, query))

    query = """
            SELECT password
            FROM USERS
            WHERE gmName = '{}'
            """.format(gmName)

    hashed = execute_read_query_one(connection, query)
    if(hashed == ""):
        print("User dont exist")
        return ""

    if(not(check_password_hash(hashed, password))):
        print("hash wrong")
        return ""

    query = """
            SELECT gmName
            FROM Users
            WHERE gmName = '{}' AND password = '{}'
            """.format(gmName, hashed)

    return execute_read_query_one(connection, query)

def registerUser(gmName, name, email, password):
    connection = create_connection("fantasyDatabase.sqlite")

    query = """
            INSERT INTO Users
            VALUES (NULL, '{}', '{}', '{}', '{}');
            """.format(gmName, name, email, password)

    execute_query(connection, query)

def create_tables():
    connection = create_connection("fantasyDatabase.sqlite")
    #Get rid of GK field and just have a general goalie for each team?
    #PlayerName and club are used to distinguish between players - the year determines which
    #year this player is playing


    query = """
            DROP TABLE IF EXISTS GMs
            """
    execute_query(connection, query)
    query = """
            DROP TABLE IF EXISTS TempResults
            """
    execute_query(connection, query)
    query = """
            DROP TABLE IF EXISTS Results
            """
    execute_query(connection, query)
    query = """
            DROP TABLE IF EXISTS Players
            """
    execute_query(connection, query)
    query = """
            DROP TABLE IF EXISTS Users
            """
    execute_query(connection, query)



    query = """
            CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            gmName TEXT UNIQUE,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT);
            """
    execute_query(connection, query)

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
		FOREIGN KEY(playerName, club, year, round) REFERENCES results(playerName, club, year, round),
        FOREIGN KEY(gmName) REFERENCES Users(gmName)
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


    passw = generate_password_hash('abcabc')

    query = """
            INSERT Into USERS
            VALUES (NULL, 'Sauls boys', 'Paulie I', 'publoz123@gmail.com', '{}'),
                    (NULL, 'Dave', 'Master David', 'suh@asdasdsds', '{}');

            """.format(passw, passw)
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

