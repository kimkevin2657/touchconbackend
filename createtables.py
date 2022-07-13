import psycopg2 # driver 임포트
import json

from backendapi import currenttime

DB_NAME = 'touchcon'
DB_USER = 'touchcon'
DB_PASS = 'touchcon'
DB_HOST = 'localhost'
DB_PORT = '5432'





conn = psycopg2.connect(host='localhost', dbname=DB_NAME, user=DB_USER, password=DB_PASS, port='5432') # db에 접속
cur = conn.cursor()


cur.execute("SELECT id FROM coupons WHERE phones = %s", (None,))
temp = cur.fetchall()
print(temp)

#cur.execute("ALTER TABLE users ADD COLUMN touchconversion DOUBLE PRECISION")


#conn.commit()


# SUBJECT VARCHAR(10485760),