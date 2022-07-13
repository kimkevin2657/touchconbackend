import psycopg2
import pytz
from time import gmtime, strftime
import datetime
import json

DB_NAME = "touchcon"
DB_USER = "touchcon"
DB_PASS = "touchcon"
DB_HOST = "localhost"
DB_PORT = "5432" 
conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
cur = conn.cursor()

cur.execute("SELECT id FROM users")
temp = cur.fetchall()

for i in range(0, len(temp)):
    try:
        cur.execute("UPDATE users SET (touchconpointlockupjson, stakingstartjson, stakingendjson) = (%s, %s, %s) WHERE id = %s", (json.dumps({"ALL": []}), json.dumps({"ALL": []}), json.dumps({"ALL": []}), temp[i][0]))
    except:
        conn.rollback()
    else:
        conn.commit()