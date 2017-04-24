from flask import Flask, abort
app = Flask(__name__)
import pymysql
import pymysql
from pymysql.cursors import DictCursor

##JSON
import json

    ##Connect to the database
connection = pymysql.connect(host='db4free.net',
user='eightypiusername',
password='Bisnet123',
db='eightypidatabase',
charset='utf8mb4',
cursorclass=DictCursor)

cur = pymysql.cursors.DictCursor

@app.route('/', methods=['POST','GET'])
def index():
    try:
        with connection.cursor() as cursor:
        # Create a new record
            sql = "INSERT INTO `auth` (`dbid`, `keyid`, `secretid`, `lastupdate`) VALUES (%s,%s,%s, %s)"
            cursor.execute(sql, ('44','1234', 'very-secret', '12-22-09'))

    # connection is not autocommit by default. So you must commit to save
    # your changes.
        connection.commit()
        x = 'success'
        print("success")
    except:
        print("failure")
    return x
import string
import random
def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
import uuid
def uuid_generator():
    return uuid.uuid4()

@app.route('/get/', methods=['POST','GET'])
def get():
    print(id_generator())
    print(uuid_generator())
    key = "1234"
    try:
        with connection.cursor() as cursor:
        # Read a single record
            sql = "SELECT `secretid` FROM `auth` WHERE `keyid` = %s"
            cursor.execute(sql, (key,))
            #result = cursor.fetchall()
            json_result = cursor.fetchone().values()
            solve = str(json_result[0])

    finally:
        connection.close()
    return solve
if __name__ == '__main__':
    app.run(debug=True)


#SQL SETTINGS FOR CREATING DB
#CREATE TABLE `auth`(secretid TEXT,
#  dbid INT AUTO_INCREMENT,
#  keyid VARCHAR(100) UNIQUE,
#  lastupdate TEXT,
#  PRIMARY KEY (dbid));
