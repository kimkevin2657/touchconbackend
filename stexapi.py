import requests
import json
import time
import psycopg2 # driver 임포트


DB_NAME = 'touchcon'
DB_USER = 'touchcon'
DB_PASS = 'touchcon'
DB_HOST = 'localhost'
DB_PORT = '5432'





conn = psycopg2.connect(host='localhost', dbname=DB_NAME, user=DB_USER, password=DB_PASS, port='5432') # db에 접속
cur = conn.cursor()

url = "https://api3.stex.com/public/ticker"


while(True):
    r = requests.get(url)

    data = r.json()

    tempdata = data["data"]

    tocpriceusdt = ""

    ethprice2 = ""
    for q in range(0, len(tempdata)):
        if tempdata[q]["group_name"] == "TOC" or tempdata[q]["currency_code"] == "TOC":
            tocpriceusdt = (float(tempdata[q]["ask"])*0.5 + float(tempdata[q]["bid"])*0.5)

        if tempdata[q]["currency_code"] == "ETH" and tempdata[q]["group_name"] == "USDT":
            ethprice2 = (float(tempdata[q]["bid"])*0.5 + 0.5*float(tempdata[q]["ask"]))*float(tempdata[q]["fiatsRate"]["KRW"])

    print(tocpriceusdt, "   ", ethprice2)
    tocprice2 = tocpriceusdt*ethprice2
    print(tocprice2)
    
    ethprice = float("{:.0f}".format(ethprice2))
    tocprice = float("{:.0f}".format(tocprice2))

    try:
        cur.execute("UPDATE exchangerate SET rate = %s WHERE coin = %s", (ethprice, "Ethereum"))
    except:
        conn.rollback()
    else:
        conn.commit()

    try:
        cur.execute("UPDATE exchangerate SET rate = %s WHERE coin = %s", (tocprice, "TouchCon"))
    except:
        conn.rollback()
    else:
        conn.commit()

    time.sleep(120)
