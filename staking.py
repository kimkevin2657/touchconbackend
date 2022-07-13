
import json
import psycopg2
import requests
from time import gmtime, strftime
import datetime
import time
import pytz
import random


def currenttime():
    tz1 = pytz.timezone("UTC")
    tz2 = pytz.timezone("Asia/Seoul")
    dt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt

DB_NAME = "touchcon"
DB_USER = "touchcon"
DB_PASS = "touchcon"
DB_HOST = "localhost"
DB_PORT = "5432" 
conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
cur = conn.cursor()

while(True):

    currtime = currenttime()[:10]

    currmonth = int(currtime[5:7])  

    currday = int(currtime[8:])

    curryear = int(currtime[:4])  


    """
    if currmonth in [1,4,7,10] and currday == 10:

        print(" ===========================     staking hit  ========================   ")

        templist = []
        try:
            cur.execute("SELECT id, userid, stakingend, touchconpointlockup FROM users")
        except:
            conn.rollback()
        else:
            templist = cur.fetchall()

        if len(templist) != 0:

            for k in range(0, len(templist)):
                if templist[k][2] == currtime:
                    pointlockup = templist[k][3]
                    pointlockup *= 0.07
                    try:
                        cur.execute("UPDATE users SET (touchconpointstaking, touchconpointlockup) = (%s, %s) WHERE userid = %s", (pointlockup, 0.0, templist[k][1]))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()
    """
    
    
    templist = []
    try:
        cur.execute("SELECT id, userid, stakingendjson, touchconpointlockupjson, stakingstartjson FROM users")
    except:
        conn.rollback()
    else:
        templist = cur.fetchall()

    if len(templist) != 0:

        for k in range(0, len(templist)):
            if templist[k][2] == None:
                continue
            if len(templist[k][2]["ALL"]) == 0:
                continue
            for q in range(0, len(templist[k][2]["ALL"])):
                if templist[k][2]["ALL"][q] == currtime:
                    userstaked = 0
                    try:
                        cur.execute("SELECT touchconpointstaking FROM users WHERE userid = %s", (templist[k][1],))
                    except:
                        conn.rollback()
                    else:
                        userstaked = cur.fetchall()[0][0]
                    
                    pointlockup = templist[k][3]["ALL"][q]
                    pointlockup *= 1.07
                    singlepayout = pointlockup
                    pointlockup += userstaked
                    
                    currobj = templist[k][2]
                    currobj["ALL"][q] = ""

                    try:
                        cur.execute("UPDATE users SET (touchconpointstaking, stakingendjson) = (%s, %s) WHERE userid = %s", (pointlockup, json.dumps(currobj), templist[k][1]))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()

                    tupleval = ("staking", templist[k][4]["ALL"][q]+"_"+templist[k][3]["ALL"][q], templist[k][1], singlepayout)
                    try:
                        cur.execute("INSERT INTO transactions (type, date, userid, couponid) VALUES (%s, %s, %s, %s)", tupleval)
                    except:
                        conn.rollback()
                    else:
                        conn.commit()

    print(" =================  ")

    hours = 12
    hours *= 60
    hours *= 60
    time.sleep(hours)
    
    
    
        
