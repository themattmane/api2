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

#now = datetime.datetime.now() #retrieve the current time from datetime module
#utctime = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") #Variable is set to current time it is pulling from

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

    ########################
    #SECURITY/AUTHENTICATION
    ########################

    try:
        with connection.cursor() as cursor: #begin connection
        # Read the secret id from the database
            sql = "SELECT `secretid` FROM `auth2` WHERE `keyid` = %s"
            cursor.execute(sql, (key,))
            #result = cursor.fetchall()
            json_result = cursor.fetchone().values() #secretid/query result in JSON format
            raw_secret = str(json_result[0]) #raw secretid
    finally:
        connection.cursor()

    confirm_secret = raw_secret #secret from database
    # secret requested by user in body of request
    secret_req = request.json.get("secretid", "")

    if secret_req != confirm_secret: #if the secret from the db and secrect request dont match the service will abort
        abort(400)


    ###############################################
    #CORE REQUESTED DATA FROM BODY IN JSON POST CALL
    ################################################

    latlng = request.json.get("latlng", "") #Requests the user's current latlng (location) in a string format Ex. "123,784"
    userid = request.json.get("userid", "")  #Request the user's unique id in a string format
    sessionid = request.json.get("userid", "") #Request the session id of user
    raw_sessionopen = request.json.get("sessionopen", "")  #Optional request of the time the session began

    #########################
    #Session ID Time Stamping
    #########################

    liveutctime = utctime() #converts global function to a callabale variable
    #If a sessioon open time is not supplied in the body of the request, then system sets sessionoppen to UTC time/date
    if raw_sessionopen == "": #The session open request is empty
        sessionopen = liveutctime
    else: #he session open request has data
        sessionopen = raw_sessionopen

    ####################
    #BODY REQUEST ERRORS
    ####################

    #if latlng or userid or sessionid is None:
    if latlng and userid and sessionid == "":
        abort(400) #400 error did not supply latlng or sessionid or userid

    #WEATHER DATA
    #current_lng = latlng.rsplit(',', 1)[0]
    #current_lat = latlng.rsplit(',', 1)[1]
    #response = requests.get("http://api.openweathermap.org/data/2.5/weather?lat="
    #                        + current_lat + "&lon=" + current_lng + "&appid=" + weather_key + "")
    #json_object = response.json()
    #temp = round(float(json_object['main']['temp']))

    #RESPONSE DATA

    core = {
        'uid': coredata[-1]['uid'] + 1,
        #'temperature': temp,
        'userid': userid,
        'latlng': latlng,
        'session_data': { 'sessionopen': sessionopen,
                         'sessionid': sessionid },
        'key': key
    }
    # append data to actual response VERY IMPORTANT
    coredata.append(core)  #coredata (preset response) #append attaches new data #(core) new data above


    ###################
    #SAVE DATA TO MYSQL
    ###################

    try:
        with connection.cursor() as cursor:
        # Create a new record
            sql = "INSERT INTO `users` (`userid`, `keyid`, `latlng`, `sessionid`, `sessionopen`, `lastupdate`) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (userid,key,latlng,sessionid,sessionopen,liveutctime))

    # connection is not autocommit by default. So you must commit to save
    # your changes.
        connection.commit()
        #connection.close()

    finally:
        print("Succesfully registered user at " + liveutctime)


    return jsonify({'core': core}), 201


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