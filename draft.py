from os import name
import sqlite3
import json
from sqlite3 import Error
from sqlite3.dbapi2 import Connection
from flask import Flask, render_template, url_for, redirect, jsonify, request, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm, RecaptchaField
from flask_bootstrap import Bootstrap
from flask_recaptcha import ReCaptcha
#from flask_uploads import DATA, configure_uploads, IMAGES, UploadSet
from wtforms import StringField, PasswordField, BooleanField, FileField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
# from werkzeug.datastructures import  FileStorage
#clea

app = Flask(__name__)

app.config['RECAPTCHA_PUBLIC_KEY'] = '6LfvVIIdAAAAAEdT5AFV-P0lTlzV1B5dgNI71M_a' # <-- Add your site key
app.config['RECAPTCHA_PRIVATE_KEY'] = '6LfvVIIdAAAAAOum0uXsTy4yzhT7r_Hv4I_og6B_' # <-- Add your secret key
app.config['TESTING'] = True
app.config['UPLOAD_FOLDER'] = 'static/'

#files = UploadSet('files', DATA)
#configure_uploads(app, files)
#6Le4Jn8dAAAAAH9qVnm2aocUvelNKQmDXf4t9phZ - site key
#6Le4Jn8dAAAAAFfh4315mHd2h5ljUA2V1dYoRoo - sec

recaptcha = ReCaptcha(app)

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
    recap = RecaptchaField()

class ResultsForm(FlaskForm):
    results = FileField('results')
    

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
    if( "user" in session):
        return render_template('index.html', name="Welcome " + session['user'])
    return render_template('index.html', name="")

@app.route('/get_players', methods=['POST'])
def get_players(): 
    print('you are here')
    return redirect('/home')

@app.route('/players.html')
def changeToPlayers():
    return render_template('players.html')


@app.route('/myTeam')
def changeToMyTeam():
    if "user" in session:
        return render_template('myteam.html', round=round, name = session["user"])
    else:
        return redirect('/login')

@app.route('/choose')
def changeToChoose():
    if "user" in session:
        return render_template('choose.html', round=round)
    else:
        return redirect('/login')

@app.route('/admin', methods = ['GET', 'POST'])
def changeToAdmin():

    form = ResultsForm()
    if session["user"] == "Master":
        if(form.validate_on_submit()):
            # filename = files.save(form.results.data)
            f = form.results.data
            filename = secure_filename(f.filename)
            f.save(app.config['UPLOAD_FOLDER'] + filename)
            readResults(filename)
            print(filename)
            return redirect('/home')
        else:
            return render_template('admin.html', form=form)
    else:
        return redirect('/home')


def readResults(filename):
    file = open(app.config['UPLOAD_FOLDER'] + filename, "r")
    print(file.readline())
    print(file.readline())

@app.route('/debug')
def debug():
    print('-------------------------------------DEBUG------------')
    if "user" in session:
        print(session["user"])
    
    return redirect('/home')

#-------------------------------------------------LOGIN---------------------------
@app.route('/login', methods = ['GET', 'POST'])
def changeToLogin():

    if("user" in session):
        logout()

    form = LoginForm()
    message = ""
     
    if(form.validate_on_submit()):
        if (form.gmName.data == 'Master'): #TODO Check if admin login secure?
            print("admin")
            if(check_password_hash(ps, form.password.data)):
                print("ADMIN LOGIN")
                session['user'] = 'Master'
                return render_template('index.html', name="Welcome Admin")

        elif(getUser(form.gmName.data,  form.password.data) == "" or not str(form.gmName.data).isalnum()): 
            #or not str(form.password.data).isalnum() # SQL Injection threat
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

        if recaptcha.verify(): # Use verify() method to see if ReCaptcha is filled out
            pass
        else:
            message = 'Please fill out the ReCaptcha!' # Send error message
            return render_template('signup.html', form=RegisterForm(), message=message)

        if(checkValidSignup(form) == 1 or form.gmName.data == 'Master'): #admin login name not in db
            return render_template('signup.html', form=RegisterForm(), message="Club or email exists")

        hashed = generate_password_hash(form.password.data, method='sha256')
        registerUser(form.gmName.data, form.name.data, form.email.data, hashed)
        return redirect('/home')
 
    #https://www.youtube.com/watch?v=VrH0eH4nE-c 
    return render_template('signup.html', form=form)
# @app.route('/loginData', methods = ['POST'])
# def validate():
#     gmName = request.form['gmName']
#     password = request.form['password']

def checkValidSignup(form):
     connection = create_connection("fantasyDatabase.sqlite")
     query = """
            SELECT EXISTS(SELECT gmName, email
                            FROM Users
                            WHERE gmName = '{}' OR email = '{}')
             """.format(form.gmName.data, form.email.data)
     return(execute_read_query_one(connection, query))

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
            DROP TABLE IF EXISTS Years
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

    query = """
    CREATE TABLE IF NOT EXISTS Players(
        pid INTEGER PRIMARY KEY AUTOINCREMENT,
        playerName TEXT
    );
            """
    execute_query(connection, query)

    players = """
    CREATE TABLE IF NOT EXISTS Years (
        pid INTEGER,
        club TEXT,
        year INTEGER,
		price INTEGER,
		team TEXT,
        PRIMARY KEY(pid, year)
        FOREIGN KEY(pid) REFERENCES Players(pid)
	);
    """
    #Might need to incorporate score for players points
    results = """
    CREATE TABLE IF NOT EXISTS Results (
        pid INTEGER,
        year INTEGER,
		round INTEGER,
		goals INTEGER,
		twoMins INTEGER,
		win INTEGER NOT NULL,
		points INTEGER,
		PRIMARY KEY(pid, year, round),
		FOREIGN KEY(pid, year) REFERENCES Years(pid, year)
        FOREIGN KEY(pid) REFERENCES Players(pid)
	);
    """

    tmp_results = """
     CREATE TABLE IF NOT EXISTS TmpResults (
        pid INTEGER,
        year INTEGER,
		round INTEGER,
		goals INTEGER,
		twoMins INTEGER,
		win INTEGER NOT NULL,
		points INTEGER,
		PRIMARY KEY(pid, year, round),
		FOREIGN KEY(pid, year) REFERENCES Years(pid, year)
        FOREIGN KEY(pid) REFERENCES Players(pid)
	);
    """

    #Is it worth storing gms total points
    gms = """
    CREATE TABLE IF NOT EXISTS Gms (
        pid INTEGER,
        year INTEGER,
        round INTEGER,
        gmName TEXT,
		PRIMARY KEY(pid, year, round, gmName)
		FOREIGN KEY(pid, year) REFERENCES years(pid, year),
		FOREIGN KEY(pid, year, round) REFERENCES results(pid, year, round),
        FOREIGN KEY(gmName) REFERENCES Users(gmName)
        FOREIGN KEY (pid) REFERENCES Players(pid)
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
        VALUES(NULL, 'Paul Ireland'),
            (NULL, 'Ben Potaka'),
            (NULL, 'Thomas Roxburgh'),
            (NULL, 'Willy Makea');
            """
    execute_query(connection, query)


    query = """
            INSERT INTO Years
        VALUES (1, 'Vikings', 2022, 25, 'A'),
	   (2, 'Victoria', 2022, 20, 'A'),
	   (3, 'Spartanz', 2022, 10, 'A'),
	   (4, 'Spartanz', 2022, 20, 'A'),
	   (1 ,'Vikings', 2021, 25, 'A');
       """
    execute_query(connection, query)

    #Paul Ireland = 1
    #Ben Potaka = 2
    #Thomas Roxburgh = 3
    #Willy makea = 4


    query = """
    INSERT INTO Results 
    VALUES (1, 2022, 1, 6, 0, 1, NULL),
	   (4,  2022, 1, 3, 1, 0, NULL),
	   (2,  2022, 1, 5, 2, 0, NULL),
	   (3,  2022, 1, 0, 0, 0, NULL),
	   (2, 2022, 2, 1, 0, 0, NULL),
	   (4,  2022, 2, 5, 2, 1, NULL),
	   (1,  2022, 2, 5, 2, 0, NULL),
	   (3, 2022, 2, 0, 0, 0, NULL),
	   (1, 2021, 1, 20, 3, 1, NULL)
	   ;
       """
    execute_query(connection, query)

    query = """
    INSERT INTO Gms
    VALUES (1, 2022, 1, 'Sauls boys'),
	   (4, 2022, 1, 'Sauls boys'),
	   (2, 2022, 1, 'Dave'),
	   (3, 2022, 1, 'Dave'), 
	   (1, 2022, 2, 'Sauls boys'),
	   (4, 2022, 2, 'Sauls boys'),
	   (2, 2022, 2, 'Dave'),
	   (3, 2022, 2, 'Dave') 
	   ;
	   
       """
    execute_query(connection, query)

    #  ('Paul Ireland', 'Vikings', 2022, 1, 'Dave'),
	#    ('Willy Makea', 'Spartanz', 2022, 1, 'Dave'),

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
            SELECT P.playerName AS "Name", Y.price AS "Price", y.club || ' ' || Y.team AS "Team", sum(r.points) AS "Points",
            round(sum(r.points) * 1.0 / (count(R.pid) * 1.0),2) AS "AVG", sum(r.twoMins) AS "2 mins"  
            FROM Results R JOIN Players P JOIN Years Y
            ON R.pid = p.pid AND r.year = y.year AND P.pid = y.pid AND R.pid = y.pid 
            WHERE R.year = {}
            GROUP BY P.pid
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
            SELECT p.playerName AS "Name", SUM(goals) AS "Goals", sum(twoMins) AS "2 minutes", sum(win) AS "Wins"
            FROM Results R JOIN Players P
            ON r.pid = p.pid
            GROUP BY p.pid
            ORDER BY "{}" DESC;
             """.format(col)
    data = execute_read_query(connection, query)
    connection.close()

    cols = ['Name', 'Goals', '2 minutes', 'Wins']

    dic = {"cols" : cols, "data" : data}
    return jsonify(dic)

#TODO will probably need to make this round-1
@app.route('/topPlayers', methods = ['GET'])
def getTop():
    connection = create_connection("fantasyDatabase.sqlite")

    query = """
            SELECT P.playerName, R.points
            FROM Results R JOIN Players P
            ON R.pid = P.pid 
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
            ON G.pid = R.pid AND G.year = r.year AND g.round = r.round
            WHERE R.year = {}
            GROUP BY G.gmName
            ORDER BY "Points" DESC;    
            """.format(year)
    data = execute_read_query(connection, query)

    cols = ['Rank', 'Gm name', 'Points']
    dic = {"cols" : cols, "data" : data}

    connection.close()
    return jsonify(dic)

@app.route('/squad', methods=['GET'])
def getSquad():
    connection = create_connection("fantasyDatabase.sqlite")

    query = """
            SELECT p.PlayerName, y.price, p.pid, y.club || ' ' ||y.team
            FROM Gms G JOIN Players P join Years y
            ON G.pid = P.pid AND Y.pid = P.pid AND y.year = g.year
            WHERE g.year = {} AND Round = {} AND gmName = '{}';
            """.format(year, round, session['user'])

    #dic = {"players": ["players"], "data":execute_read_query(connection, query) }
    dic = execute_read_query(connection, query)
   #print(dic.data)
    return jsonify(dic)


#TODO Make post, print out error message and don't save
#Check for number of players from a club - will also need GK
@app.route('/saveSquad/<jsdata>')
def saveSquad(jsdata):
    data = json.loads(jsdata)

    total = 0
    ids = []
    if(len(data) < 1 or len(data) > 4):
        dic = {"reason": "Wrong number of people", "success": "failure"}
        return jsonify(dic)

    for player in data:
        id = player.get("id")
        if(id in ids):
            dic = {"reason": "Duplicate player", "success": "failure"}
            return jsonify(dic)
        ids.append(id)
        name = player.get("name")
        clubTeam = player.get("clubTeam")
        price = player.get("price")
        if(price < 10 or price > 25 or price % 5 != 0): 
            dic = {"reason": "The price of a player was invalid", "success": "failure"}
            return jsonify(dic)
        total += price



    if(total > maxSquadCost):
        print('Too EXPENSIVE!!')
        error = "Too much money"
        dic = {"reason": "Too expensive", "success": "failure"}
        return jsonify(dic)
        #return render_template('choose.html', round=round, error=error)#render_template('choose.html', round=round, error="Too Expensive")

    #return "SUCCESS"
    connection = create_connection("fantasyDatabase.sqlite") 
    query = """
            DELETE FROM Gms
            WHERE gmName = '{}' AND year = {} AND round = {} 
            """.format(session['user'], year, round)
    execute_query(connection, query)

   
    for i in ids:
         query = """
                INSERT INTO Gms
                VALUES ({}, {}, {}, '{}');
                """ .format(i, year, round, session["user"])
         execute_query(connection, query)
       
    connection.close()
    print(data)
    dic = {"reason": "N/A", "success": "Saved!"}
    return jsonify(dic)
    #return jsonify("Saved!")
# @app.route('/squadPrice', methods=['GET'])
# def getSquadPrice():
#     connection = create_connection("fantasyDatabase.sqlite")

#     query = """
#             SELECT P.PlayerName, y.Price
#             FROM Gms G JOIN Years y JOIN Players P
#             ON P.pid = y.pid AND g.pid = y.pid AND y.year = G.year
#             WHERE Round = {} AND gmName = '{}';
#             """.format(round, session['user'])

#     #dic = {"players": ["players"], "data": }
#     return jsonify(execute_read_query(connection, query))


@app.route('/getTeam/<club>')
def getTeam(club):
    connection = create_connection("fantasyDatabase.sqlite")

    data = club.split()

    query = """
            SELECT y.pid, playerName, price
            FROM Players P JOIN Years Y
            ON P.pid = y.pid
            WHERE y.club = '{}' AND y.team = '{}' AND y.year = {};
            """.format(data[0], data[1], year)

    return jsonify(execute_read_query(connection, query))

@app.route('/getTeams')
def getTeams():
    connection = create_connection("fantasyDatabase.sqlite")

    query = """
            SELECT DISTINCT club || ' ' || team AS "team"
            FROM Years 
            WHERE year = {}
            """.format(year)

    return jsonify(execute_read_query(connection, query))

@app.route('/getSquadCost')
def getSquadCost():
    connection = create_connection("fantasyDatabase.sqlite")
    query = """
            SELECT SUM(y.price)
            FROM Gms G JOIN Years Y
            ON G.pid = y.pid
            WHERE G.gmName = '{}' AND y.year = {} AND g.round = {}
            """.format(session['user'], year, round)

    return jsonify(execute_read_query_one(connection, query))

@app.route('/getSquadAve')
def getSquadAve():
     connection = create_connection("fantasyDatabase.sqlite")
     query = """
           SELECT SUM(T.Ave)
            FROM (SELECT y.pid AS "pid", SUM(r.points) / COUNT(r.points) AS "Ave"
			 FROM Years Y JOIN Results R
			 ON Y.pid = R.pid AND Y.year = R.year 
			 WHERE y.year = 2022
			 GROUP BY R.pid) T JOIN Gms G
			 ON T.pid = G.pid
            WHERE g.year = {} AND g.round = {} AND G.gmName = '{}'; 
            """.format(year, round, session['user'])

     return jsonify(execute_read_query_one(connection, query))
        
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
maxSquadCost = 70
error = ""
ps = generate_password_hash("WellyFantasy2021", method="sha256") #TODO should this be more securely initiated



create_tables()



if __name__ == '__main__':
    app.run(debug=True)

