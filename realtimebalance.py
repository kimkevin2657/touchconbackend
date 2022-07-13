import psycopg2
import time
import requests

DB_NAME = "touchcon"
DB_USER = "touchcon"
DB_PASS = "touchcon"
DB_HOST = "localhost"
DB_PORT = "5432" 
conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
cur = conn.cursor()



contract_address = "0x549905519f9e06d55d7dfcd4d54817780f6b93e8"

while(True):

    templist = []
    try:
        cur.execute("SELECT userid, wallet FROM users WHERE registered = %s", (True,))
    except:
        conn.rollback()
    else:
        templist = cur.fetchall()

    for k in range(0, len(templist)):
        if templist[k][1] == None:
            continue
        if isinstance(templist[k][1], str):

            res = requests.get("http://localhost:3000/balance?address="+templist[k][1]+"&contract_address="+contract_address)
            resjson = res.json()
            try:
                cur.execute("UPDATE users SET touchcon = %s WHERE userid = %s", (float(resjson["balance"]), templist[k][0]))
            except:
                conn.rollback()
            else:
                conn.commit()
            try:
                cur.execute("UPDATE users SET ethereum = %s WHERE userid = %s", (float(resjson["eth_balance"]), templist[k][0]))
            except:
                conn.rollback()
            else:
                conn.commit()
            print(" === userid, ether, touchcon     ", templist[k][0], "   ", resjson["eth_balance"], "    ", resjson["balance"])

    templist = []
    try:
        cur.execute("SELECT id, wallet FROM adminwallet")
    except:
        conn.rollback()
    else:
        templist = cur.fetchall()

    templist = sorted(templist)
    templist = templist[::-1]

    res = requests.get("http://localhost:3000/balance?address="+templist[0][1]+"&contract_address="+contract_address)
    resjson = res.json()

    try:
        cur.execute("UPDATE adminwallet SET (ethereum, touchcon) = (%s, %s) WHERE id = %s", (float(resjson["eth_balance"]), float(resjson["balance"]), templist[0][0]))
    except:
        conn.rollback()
    else:
        conn.commit()
    print(" ==== admin     ", resjson["eth_balance"], "   ", resjson["balance"])


    time.sleep(180)
