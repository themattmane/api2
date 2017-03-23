# -- https://pypi.python.org/pypi/geolocation-python/0.2.0 -- geolocation
#############################
##!flask/bin/python
##################################
## IMPORTED PACKAGES & EXTENSIONS
##################################

from flask import Flask, jsonify, request, abort, render_template
import requests
import datetime
import pymysql
import string
import random
import uuid

app = Flask(__name__)

###############################
#     TIMESTAMPING LOGIC
###############################

now = datetime.datetime.now()
utctime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") #Variable is set to current time it is pulling from

###############################
#     RANDOM VALUE GENERATORS
###############################

def id_generator(size=32, chars=string.ascii_uppercase + string.digits): #Specifices to only use random upper case & #s
    return ''.join(random.choice(chars) for _ in range(size)) #FInds size worth of random values using parameters set

def uuid_generator(): #Can be used globally to return a random uuid
    return uuid.uuid4() #Reutrns a 32 digit random uuid code.

#############################
#     SQL DATABASE SETTINGS
#############################
connection = pymysql.connect(host='wackystat2.cpdisqlre7yl.us-west-2.rds.amazonaws.com',
user='manning1234',
password='Bisnet1234',
db='wackystat2',
charset='utf8mb4',
cursorclass=pymysql.cursors.DictCursor)
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
    ###
    #SECURITY/AUTHENTICATION
    ###
    #

    #
    ###
    #CORE REQUESTED DATA FROM BODY IN JSON POST CALL
    ###
    #
    latlng = request.json.get("latlng", "") #Requests the user's current latlng (location) in a string format Ex. "123,784"
    userid = request.json.get("userid", "")  #Request the user's unique id in a string format
    sessionid = request.json.get("userid", "") #Request the session id of user
    raw_sessionopen = request.json.get("sessionopen", "")  #Optional request of the time the session began

    ####
    #Session ID Time Stamping
    ####
    #If a sessioon open time is not supplied in the body of the request, then system sets sessionoppen to UTC time/date
    if raw_sessionopen == "": #The session open request is empty
        sessionopen = utctime
    else: #he session open request has data
        sessionopen = raw_sessionopen

    ###
    #BODY REQUEST ERRORS
    ###

    #if latlng or userid or sessionid is None:
    if latlng and userid and sessionid == "":
        abort(400) #410 error did not supply latlng or sessionid or userid

    #WEATHER DATA
    current_lng = latlng.rsplit(',', 1)[0]
    current_lat = latlng.rsplit(',', 1)[1]
    response = requests.get("http://api.openweathermap.org/data/2.5/weather?lat="
                            + current_lat + "&lon=" + current_lng + "&appid=" + weather_key + "")
    json_object = response.json()
    temp = round(float(json_object['main']['temp']))

    #RESPONSE DATA
    task = {
        'id': tasks[-1]['id'] + 1,
        'userid': userid,
        'sessionid': sessionid,
        'latlng': latlng,
        'done': False,
        'key': key
    }
    core = {
        'uid': coredata[-1]['uid'] + 1,
        'temperature': temp,
        'userid': userid,
        'latlng': latlng,
        'session_data': { 'sessionopen': sessionopen,
                         'sessionid': sessionid },
        'key': key
    }
    tasks.append(task)
    coredata.append(core)
    #return jsonify({'task': task}), 200
    return jsonify({'core': core}), 201

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },

]

coredata = [
    {
        'uid': 100,
        'userid': 543
    }
]

@app.route('/', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})

@app.route('/preregister', methods=['GET'])
def preregister():
    utctime
    return render_template('preregister.html',time=utctime)

@app.route('/register', methods=['GET','POST'])
def register():
    regiser_key = str(id_generator())
    register_secretid = str(uuid_generator())
    try:
        with connection.cursor() as cursor:
        # Create a new record
            sql = "INSERT INTO `auth` (`dbid`, `keyid`, `secretid`, `lastupdate`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (regiser_key, regiser_key, register_secretid, utctime))

    # connection is not autocommit by default. So you must commit to save
    # your changes.
        connection.commit()

        print("Succesfully registered user at " + utctime)
    except:
        print("failure")
    return str(regiser_key), str(register_secretid)


if __name__ == '__main__':
    app.run(debug=True)