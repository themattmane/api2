# -- https://pypi.python.org/pypi/geolocation-python/0.2.0 -- geolocation
#############################
##!flask/bin/python
##################################
## IMPORTED PACKAGES & EXTENSIONS
##################################

from flask import Flask, jsonify, request, abort, render_template
import datetime
import pymysql
import string
import random
import uuid

app = Flask(__name__)

@app.route('/loaderio-5ba8750e61b62f1aa52fe9d3db5a8e11/', methods=['GET'])
def loaderio():
    return render_template('loaderio-5ba8750e61b62f1aa52fe9d3db5a8e11.txt')

###############################
#     TIMESTAMPING LOGIC
###############################

def utctime():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")  # Variable is set to current time it is pulling from

###############################
#     RANDOM VALUE GENERATORS
###############################

def id_generator(size=32, chars=string.ascii_lowercase + string.digits): #Specifices to only use random upper case & #s
    return ''.join(random.choice(chars) for _ in range(size)) #FInds size worth of random values using parameters set

def uuid_generator(): #Can be used globally to return a random uuid
    return uuid.uuid4() #Reutrns a 32 digit random uuid code.

#############################
#     SQL DATABASE SETTINGS
#############################

connection = pymysql.connect(

host='db4free.net',
user='eightypiusername',
password='Bisnet123',
db='eightypidatabase',
charset='utf8mb4',
cursorclass=pymysql.cursors.DictCursor,
autocommit=True,

)

#############################
#     EXTERNAL API KEYS
#############################

#Weather Data API Key
weather_key = "894eb3084dd61ab649bf20494bd3cacb"

#############################
#     API SERVICES
#############################
@app.route('/core/<key>', methods=['POST','GET'])
def create_task(key):
    # Cursor
    cur = connection.cursor(pymysql.cursors.DictCursor)
    liveutctime = utctime() #converts global function to a callabale variable
    #Request headers
    secret_req = request.headers['secretid'] #requests secretid in header
    #Request parameters
    latlng = request.args["latlng"]  # Requests the user's current latlng (location) in a string format Ex. "123,784"
    userid = request.args["userid"]  # Request the user's unique id in a string format
    sessionid = request.args["sessionid"]  # Request the session id of user
    # Authentication
    sql = "SELECT `secretid` FROM `auth2` WHERE `keyid` = %s"
    cur.execute(sql, (key,))
    json_result = cur.fetchone().values()  # secretid/query result in JSON format
    raw_secret = str(json_result[0])  # raw secretid
    confirm_secret = raw_secret  # secret from database
    # secret requested by user in body of request

    if secret_req != confirm_secret:  # if the secret from the db and secrect request dont match the service will abort
        abort(401)

    if request.method == 'POST':
        ###############################################
        #CORE REQUESTED DATA FROM BODY IN JSON POST CALL
        ################################################
        raw_sessionopen = request.json.get("sessionopen", "")  #Optional request of the time the session began
        #########################
        #Session ID Time Stamping
        #########################
        #If a sessioon open time is not supplied in the body of the request, then system sets sessionoppen to UTC time/date
        if raw_sessionopen == "": #The session open request is empty
            sessionopen = liveutctime
        else: #he session open request has data
            sessionopen = raw_sessionopen

        ###################
        # SAVE DATA TO MYSQL
        ###################
        query = "INSERT INTO `users` (`userid`, `keyid`, `latlng`, `sessionid`, `sessionopen`, `lastupdate`) VALUES (%s, %s, %s, %s, %s, %s)"
        cur.execute(query, (userid, key, latlng, sessionid, sessionopen, liveutctime))
        # connection is not autocommit by default. So you must commit to save your changes.
        connection.commit()
        print("Succesfully registered user at " + liveutctime)
        ##############
        #RESPONSE DATA
        ##############
        core = {
            ### Uid auto generated  'uid': coredata[-1]['uid'] + 1,
            # 'temperature': temp,
            'key': key,
            'userid': userid,
            'latlng': latlng,
            'session_data': {'sessionopen': '55',
                             'sessionid': sessionid}

        }
        coredata.append(
            core)  # VERY IMPORTANT...coredata (preset response) #append attaches new data #(core) new data above

        return jsonify({'core': core}), 201
    elif request.method == 'GET':
        sql = "SELECT * FROM `users` WHERE `keyid` = %s"
        cur.execute(sql, (key,))
        get_jsonresult = cur.fetchall()

        return jsonify(get_jsonresult), 200

coredata = [
    {
        'uid': 100,
        'userid': 543
    }
]

@app.route('/core', methods=['GET'])
def get_core():

    core = {
        'key': key,
        'userid': userid,
        'latlng': latlng,
        'session_data': { 'sessionopen': sessionopen,
                         'sessionid': sessionid }

    }
    return jsonify({'core': core})

@app.route('/preregister', methods=['GET'])
def preregister():
    utctime()
    return render_template('preregister.html',time=utctime)

@app.route('/register', methods=['GET','POST'])
def register():
    liveutctime = str(utctime()) #run utctime global function
    regiser_key = str(id_generator()) #run idgenerator global function
    register_secretid = str(uuid_generator()) #run uuid global function
    try:
        with connection.cursor() as cursor:
        # Create a new record
            sql = "INSERT INTO `auth2` (`dbid`, `keyid`, `secretid`, `lastupdate`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (regiser_key, regiser_key, register_secretid, liveutctime))

    # connection is not autocommit by default. So you must commit to save
    # your changes.
        connection.commit()
        #connection.close()

        return ("Succesfully registered user at " + liveutctime)

    except:
        print("failure")
    return str(regiser_key), str(register_secretid)


if __name__ == '__main__':
    app.run(debug=True)