from flask import Flask, request, logging, jsonify
from flask_cors import CORS, cross_origin
#from data import Articles
from passlib.hash import sha256_crypt
from functools import wraps
import json
from flask import jsonify
import flask_praetorian
import psycopg2
import requests
import base64
from passlib.hash import sha256_crypt
import jwt

from pyupbit import Upbit
import pyupbit

guard = flask_praetorian.Praetorian()
cors = CORS()

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["SECRET_KEY"] = "temp secret"
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}

cors.init_app(app)





DB_NAME = "pentaplant"
DB_USER = "pentaplant"
DB_PASS = "pentaplant_landingpage"
DB_HOST = "localhost"
DB_PORT = "5432" 
conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
cur = conn.cursor()







@app.route('/login', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def login():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  login error =========================== ")
            print(ex)
            pass
        print(data)

        query = False
        cur.execute("SELECT userid, password FROM users WHERE email = %s", (data["email"],))
        temp = cur.fetchall()
        if len(temp) != 0:
            if len(temp[0]) != 0:
                
                query = True


        if query:
            if sha256_crypt.verify(data["password"], temp[0][1]):
                key = "secret key"
                encoded = jwt.encode({"Username": data["email"]}, key, algorithm="HS256")
                return json.dumps(encoded), 200, {"contentType": "application/json"}
            else:
                return json.dumps({"success": "wrong password"}), 200, {"contentType": "application/json"}

        if not query:

            tempdict = dict()

            tempdict["email"] = data["email"]
            tempdict["password"] = data["password"]

            r = requests.post("https://api.pentaplant.com:8443/api/user/supportLogin", json=tempdict, verify=False)




            success = False
            userid = 0
            for key,items in r.json().items():
                if key == "userResult":
                    if items != None:
                        try:
                            userid = int(r.json()["userResult"]["userId"])
                            success = True
                        except Exception as ex:
                            print(" ======================  login error =========================== ")
                            print(ex)
                            pass

            if success:
                hashval = sha256_crypt.encrypt(data["password"])

                cur.execute("INSERT INTO users (userid, email, password) VALUES (%s, %s, %s)", (userid, data["email"], hashval))
                conn.commit()

                cur.execute("INSERT INTO botsdata (userid) VALUES (%s)", (userid,))
                conn.commit()

                tempjson = {
                    "active" : False,
                    "amount" : 10.63897028,
                    "entrynum" : 100,
                    "pricediff" : 312.0883,
                    "pyramiding": False,
                    "percentrange": 50,
                    "percentreturn": 2,
                    "currpyramiding": False,
                    "pyramidingexit": 3,
                    "entrynumpyramiding": 5,
                    "passedpyramidingexit": False,
                    "percentreturnpyramiding": 0.5
                }

                tupleval = (userid, json.dumps(tempjson), json.dumps(tempjson), json.dumps(tempjson), True)
                cur.execute("INSERT INTO bots (userid, botone, bottwo, botthree, firsttrading) VALUES (%s, %s, %s, %s, %s)",tupleval)
                conn.commit()

                key = "secret key"
                encoded = jwt.encode({"Username": data["email"]}, key, algorithm="HS256")
                return json.dumps(encoded), 200, {"contentType": "application/json"}

            if not success:
                return json.dumps({"success": "wrong login"}), 200, {"contentType": "application/json"}

        return json.dumps({"success": True}), 200, {"contentType": "application/json"}



@app.route("/totalbalance", methods=["GET","POST"])
@cross_origin(origin="*", headers=["Content- Type", "Authorization"])
def totalbalance():
    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  totalbalance error =========================== ")
            print(ex)
            pass
        print(data)

        sessionToken = ""
        sessionTokenbool = False
        try:
            sessionToken = data["sessionToken"]
        except Exception as ex:
            print(" ======================  totalbalance error =========================== ")
            print(ex)
            sessionTokenbool = True
            pass

        print(" ====== /totalbalance  sessiontokenbool   ", sessionTokenbool)
        if sessionTokenbool:
            return json.dumps({"USDT": 0, "BTC": 0}), 200, {"contentType": "application/json"}


        print(" =======  totalbalance sessionToken   ", sessionToken)

        key = "secret key"
        decoded = jwt.decode(sessionToken, key, algorithms="HS256")
        print( " ==========  totalbalance  decoded   ", decoded)
        email = decoded["Username"]
        
        print( " ==========  totalbalance  email   ", email)

        cur.execute("SELECT userid FROM users WHERE email = %s", (email,))
        tempuserid = cur.fetchall()
        print(" ============ totalbalance  userid fetchall  ", tempuserid)
        userid = tempuserid[0][0]

        print(" ============= totalbalance  userid  ", userid,)

        cur.execute("SELECT apikey, secretkey FROM users WHERE email = %s", (email,))
        temp = cur.fetchall()
        print(" =========  totalbalance temp  ", temp)
        print(" =========  totalbalance apikey  ", temp[0][0], "   ",type(temp[0][0]))
        print(" =========== totalbalance  secretkey  ", temp[0][1], "   ", type(temp[0][1]))
        if len(temp) != 0 and temp != None:
            if len(temp[0]) != 0 and temp[0] != None:
                if temp[0][0] != None:
                    print( " =========  totalbalance  execute fetch balance   ")
                    upbitobj = Upbit(temp[0][0], temp[0][1])

                    usdt = upbitobj.get_balance("USDT")
                    btc = upbitobj.get_balance("BTC")

                    print( "= =======  totalbalance usdt   ", usdt)

                    print( "= =======  totalbalance btc   ", btc)


                    print( "   totalbalance  btc and usdt    ", btc, "   ", usdt)
                    balance = json.dumps({"BTC": btc, "USDT": usdt})
                    cur.execute("UPDATE users SET balance = %s WHERE userid = %s", (usdt, userid))
                    conn.commit()
                    cur.execute("UPDATE bots SET totalbalance = %s WHERE userid = %s", (balance, userid))
                    conn.commit()
                    
                    return json.dumps({"USDT": usdt,"BTC": btc}), 200, {"contentType": "application/json"}

        balance = json.dumps({"BTC": 0, "USDT": 0})
        cur.execute("UPDATE users SET balance = %s WHERE userid = %s", (0, userid))
        conn.commit()
        cur.execute("UPDATE bots SET totalbalance = %s WHERE userid = %s", (balance, userid))
        conn.commit()

        return json.dumps({"USDT": 0, "BTC": 0}), 200, {"contentType": "application/json"}
        


@app.route("/firsttrading", methods=["GET","POST"])
@cross_origin(origin="*", headers=["Content- Type", "Authorization"])
def firsttrading():
    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  firsttrading error =========================== ")
            print(ex)
            pass
        print(data)

        sessionToken = ""
        sessionTokenbool = False
        try:
            sessionToken = data["sessionToken"]
        except Exception as ex:
            print(" ======================  firsttrading error =========================== ")
            print(ex)
            sessionTokenbool = True
            pass

        if sessionTokenbool:
            return json.dumps({"firsttrading": True}), 200, {"contentType": "application/json"}

        print(" ======= firsttrading sessionToken   ", sessionToken)

        key = "secret key"
        decoded = jwt.decode(sessionToken, key, algorithms="HS256")
        print( " ========== firsttrading decoded   ", decoded)
        email = decoded["Username"]

        cur.execute("SELECT userid FROM users WHERE email = %s", (email,))
        userid = cur.fetchall()[0][0]

        print(" ============  firsttrading  userid   ", userid)

        cur.execute("SELECT firsttrading FROM bots WHERE userid = %s",(userid,))
        boolval = cur.fetchall()[0][0]

        if boolval:
            return json.dumps({"firsttrading": True}), 200, {"contentType": "application/json"}
        else:
            return json.dumps({"firsttrading": False}), 200, {"contentType": "application/json"}



@app.route("/totalbalancetwo", methods=["GET","POST"])
@cross_origin(origin="*", headers=["Content- Type", "Authorization"])
def totalbalancetwo():
    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  totalbalance error =========================== ")
            print(ex)
            pass
        print(data)

        sessionToken = ""
        sessionTokenbool = False
        try:
            sessionToken = data["sessionToken"]
        except Exception as ex:
            print(" ======================  totalbalance error =========================== ")
            print(ex)
            sessionTokenbool = True
            pass

        print(" ====== /totalbalance  sessiontokenbool   ", sessionTokenbool)
        if sessionTokenbool:
            return json.dumps({"USDT": 0, "BTC": 0}), 200, {"contentType": "application/json"}


        print(" =======  totalbalance sessionToken   ", sessionToken)

        key = "secret key"
        decoded = jwt.decode(sessionToken, key, algorithms="HS256")
        print( " ==========  totalbalance  decoded   ", decoded)
        email = decoded["Username"]
        
        print( " ==========  totalbalance  email   ", email)

        cur.execute("SELECT userid FROM users WHERE email = %s", (email,))
        tempuserid = cur.fetchall()
        print(" ============ totalbalance  userid fetchall  ", tempuserid)
        userid = tempuserid[0][0]

        print(" ============= totalbalance  userid  ", userid,)

        cur.execute("SELECT apikey, secretkey FROM users WHERE email = %s", (email,))
        temp = cur.fetchall()
        print(" =========  totalbalance temp  ", temp)
        print(" =========  totalbalance apikey  ", temp[0][0], "   ",type(temp[0][0]))
        print(" =========== totalbalance  secretkey  ", temp[0][1], "   ", type(temp[0][1]))
        if len(temp) != 0 and temp != None:
            if len(temp[0]) != 0 and temp[0] != None:
                if temp[0][0] != None:
                    print( " =========  totalbalance  execute fetch balance   ")
                    upbitobj = Upbit(temp[0][0], temp[0][1])

                    usdt = upbitobj.get_balance("USDT")
                    btc = upbitobj.get_balance("BTC")

                    print( "= =======  totalbalance usdt   ", usdt)

                    print( "= =======  totalbalance btc   ", btc)


                    print( "   totalbalance  btc and usdt    ", btc, "   ", usdt)
                    balance = json.dumps({"BTC": btc, "USDT": usdt})
                    cur.execute("UPDATE users SET balance = %s WHERE userid = %s", (usdt, userid))
                    conn.commit()
                    cur.execute("UPDATE bots SET totalbalance = %s WHERE userid = %s", (balance, userid))
                    conn.commit()
                    
                    return json.dumps({"USDT": usdt,"BTC": btc}), 200, {"contentType": "application/json"}

        balance = json.dumps({"BTC": 0, "USDT": 0})
        cur.execute("UPDATE users SET balance = %s WHERE userid = %s", (0, userid))
        conn.commit()
        cur.execute("UPDATE bots SET totalbalance = %s WHERE userid = %s", (balance, userid))
        conn.commit()

        return json.dumps({"USDT": 0, "BTC": 0}), 200, {"contentType": "application/json"}
        


@app.route("/firsttradingtwo", methods=["GET","POST"])
@cross_origin(origin="*", headers=["Content- Type", "Authorization"])
def firsttradingtwo():
    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  firsttrading error =========================== ")
            print(ex)
            pass
        print(data)

        sessionToken = ""
        sessionTokenbool = False
        try:
            sessionToken = data["sessionToken"]
        except Exception as ex:
            print(" ======================  firsttrading error =========================== ")
            print(ex)
            sessionTokenbool = True
            pass

        if sessionTokenbool:
            return json.dumps({"firsttrading": True}), 200, {"contentType": "application/json"}

        print(" ======= firsttrading sessionToken   ", sessionToken)

        key = "secret key"
        decoded = jwt.decode(sessionToken, key, algorithms="HS256")
        print( " ========== firsttrading decoded   ", decoded)
        email = decoded["Username"]

        cur.execute("SELECT userid FROM users WHERE email = %s", (email,))
        userid = cur.fetchall()[0][0]

        print(" ============  firsttrading  userid   ", userid)

        cur.execute("SELECT firsttrading FROM bots WHERE userid = %s",(userid,))
        boolval = cur.fetchall()[0][0]

        if boolval:
            return json.dumps({"firsttrading": True}), 200, {"contentType": "application/json"}
        else:
            return json.dumps({"firsttrading": False}), 200, {"contentType": "application/json"}








@app.route("/updatebotsetting", methods=["GET","POST"])
@cross_origin(origin="*", headers=["Content- Type", "Authorization"])
def updatebotsetting():
    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  updatebotsetting error =========================== ")
            print(ex)
            pass
        print(data)

        inputdata = data["inputdata"]
        print()
        print("   inputdata    ", json.dumps(inputdata, indent=4))
        print()
        sessionToken = ""
        sessionTokenbool = False
        try:
            sessionToken = data["sessionToken"]
        except Exception as ex:
            print(" ======================  updatebotsetting error =========================== ")
            print(ex)
            sessionTokenbool = True
            pass

        if sessionTokenbool:
            json.dumps({"result": "wrong"}), 200, {"contentType": "application/json"}

        print(" ======= sessionToken   ", sessionToken)

        key = "secret key"
        decoded = jwt.decode(sessionToken, key, algorithms="HS256")
        print( " ==========  decoded   ", decoded)
        email = decoded["Username"]

        cur.execute("SELECT userid FROM users WHERE email = %s", (email,))
        userid = cur.fetchall()[0][0]

        cur.execute("SELECT botone, bottwo, botthree, firsttrading, totalbalance FROM bots WHERE userid = %s", (userid,))
        temp = cur.fetchall()[0]

        botone = temp[0]
        bottwo = temp[1]
        botthree = temp[2]
        firsttrading = temp[3]
        totalbalance = temp[4]["USDT"]

        print(" =======================================================   ", firsttrading, "    ", totalbalance)
        if not firsttrading:
            print(" =========== not firsttrading returned   ")
            return json.dumps({"result": "already"}), 200, {"contentType": "application/json"}

        inputtotal = 0.0
        for i in range(0, len(inputdata)):
            if inputdata[i]["active"] == True:
                inputtotal += float(inputdata[i]["StartingAmount"])
        print("   total balance  and inputtotal    ", totalbalance, "   ", inputtotal)
        if inputtotal > float(totalbalance):
            return json.dumps({"result": "insufficient"}), 200, {"contentType": "application/json"}
    
        
        if float(totalbalance) > 5 and firsttrading == True and float(totalbalance) >= float(inputtotal):
            print(" ================================   all triggered   ")
            if inputdata[0]["active"] == True:
                botone["active"] = True
                if inputdata[0]["UpPyramiding"] == True:
                    botone["pyramiding"] = True
                    botone["entrynumpyramiding"] = int(inputdata[0]["pyramidingEntry"])
                    botone["percentreturnpyramiding"] = float(inputdata[0]["pyramidingGain"])
                    botone["pyramidingexit"] = 10000000
                else:
                    botone["pyramiding"] = False
                    botone["entrynumpyramiding"] = 0
                    botone["percentreturnpyramiding"] = 0
                    botone["pyramidingexit"] = 10000000
                botone["entrynum"] = int(inputdata[0]["EntryNum"])
                botone["amount"] = float(inputdata[0]["StartingAmount"])
                botone["percentrange"] = float(inputdata[0]["PercentRange"])
                botone["percentreturn"] = float(inputdata[0]["PercentReturn"])
                botone["pricediff"] = 0
                botone["currpyramiding"] = False
                botone["passedpyramidingexit"] = False
            else:
                botone["active"] = False
                if inputdata[0]["UpPyramiding"] == True:
                    botone["pyramiding"] = True
                    botone["entrynumpyramiding"] = int(inputdata[0]["pyramidingEntry"])
                    botone["percentreturnpyramiding"] = float(inputdata[0]["pyramidingGain"])
                    botone["pyramidingexit"] = 10000000
                else:
                    botone["pyramiding"] = False
                    botone["entrynumpyramiding"] = 0
                    botone["percentreturnpyramiding"] = 0
                    botone["pyramidingexit"] = 10000000
                botone["entrynum"] = int(inputdata[0]["EntryNum"])
                botone["amount"] = float(inputdata[0]["StartingAmount"])
                botone["percentrange"] = float(inputdata[0]["PercentRange"])
                botone["percentreturn"] = float(inputdata[0]["PercentReturn"])
                botone["pricediff"] = 0
                botone["currpyramiding"] = False
                botone["passedpyramidingexit"] = False


            if inputdata[1]["active"] == True:
                bottwo["active"] = True
                if inputdata[1]["UpPyramiding"] == True:
                    bottwo["pyramiding"] = True
                    bottwo["entrynumpyramiding"] = int(inputdata[1]["pyramidingEntry"])
                    bottwo["percentreturnpyramiding"] = float(inputdata[1]["pyramidingGain"])
                    bottwo["pyramidingexit"] = 10000000
                else:
                    botone["pyramiding"] = False
                    botone["entrynumpyramiding"] = 0
                    botone["percentreturnpyramiding"] = 0
                    botone["pyramidingexit"] = 10000000
                bottwo["entrynum"] = int(inputdata[1]["EntryNum"])
                bottwo["amount"] = float(inputdata[1]["StartingAmount"])
                bottwo["percentrange"] = float(inputdata[1]["PercentRange"])
                bottwo["percentreturn"] = float(inputdata[1]["PercentReturn"])
                bottwo["pricediff"] = 0
                bottwo["currpyramiding"] = False
                bottwo["passedpyramidingexit"] = False
            else:
                bottwo["active"] = False
                if inputdata[0]["UpPyramiding"] == True:
                    bottwo["pyramiding"] = True
                    bottwo["entrynumpyramiding"] = int(inputdata[0]["pyramidingEntry"])
                    bottwo["percentreturnpyramiding"] = float(inputdata[0]["pyramidingGain"])
                    bottwo["pyramidingexit"] = 10000000
                else:
                    bottwo["pyramiding"] = False
                    bottwo["entrynumpyramiding"] = 0
                    bottwo["percentreturnpyramiding"] = 0
                    bottwo["pyramidingexit"] = 10000000
                bottwo["entrynum"] = int(inputdata[0]["EntryNum"])
                bottwo["amount"] = float(inputdata[0]["StartingAmount"])
                bottwo["percentrange"] = float(inputdata[0]["PercentRange"])
                bottwo["percentreturn"] = float(inputdata[0]["PercentReturn"])
                bottwo["pricediff"] = 0
                bottwo["currpyramiding"] = False
                bottwo["passedpyramidingexit"] = False

            if inputdata[2]["active"] == True:
                botthree["active"] = True
                if inputdata[2]["UpPyramiding"] == True:
                    botthree["pyramiding"] = True
                    botthree["entrynumpyramiding"] = int(inputdata[2]["pyramidingEntry"])
                    botthree["percentreturnpyramiding"] = float(inputdata[2]["pyramidingGain"])
                    botthree["pyramidingexit"] = 10000000
                else:
                    botthree["pyramiding"] = False
                    botthree["entrynumpyramiding"] = int(inputdata[0]["pyramidingEntry"])
                    botthree["percentreturnpyramiding"] = 0
                    botthree["pyramidingexit"] = 10000000
                botthree["entrynum"] = int(inputdata[2]["EntryNum"])
                botthree["amount"] = float(inputdata[2]["StartingAmount"])
                botthree["percentrange"] = float(inputdata[2]["PercentRange"])
                botthree["percentreturn"] = float(inputdata[2]["PercentReturn"])
                botthree["pricediff"] = 0
                botthree["currpyramiding"] = False
                botthree["passedpyramidingexit"] = False
            else:
                botthree["active"] = False
                if inputdata[0]["UpPyramiding"] == True:
                    botthree["pyramiding"] = True
                    botthree["entrynumpyramiding"] = int(inputdata[0]["pyramidingEntry"])
                    botthree["percentreturnpyramiding"] = float(inputdata[0]["pyramidingGain"])
                    botthree["pyramidingexit"] = 10000000
                else:
                    botthree["pyramiding"] = False
                    botthree["entrynumpyramiding"] = 0
                    botthree["percentreturnpyramiding"] = 0
                    botthree["pyramidingexit"] = 10000000
                botthree["entrynum"] = int(inputdata[0]["EntryNum"])
                botthree["amount"] = float(inputdata[0]["StartingAmount"])
                botthree["percentrange"] = float(inputdata[0]["PercentRange"])
                botthree["percentreturn"] = float(inputdata[0]["PercentReturn"])
                botthree["pricediff"] = 0
                botthree["currpyramiding"] = False
                botthree["passedpyramidingexit"] = False

        print(" =============   update bots userid    ", userid)
        print(" =============   update bots botone    ", json.dumps(botone, indent=4))
        print(" =============   update bots bottwo    ", json.dumps(bottwo, indent=4))
        print(" =============   update bots botthree    ", json.dumps(botthree, indent=4))

        tupleval = (json.dumps(botone), json.dumps(bottwo), json.dumps(botthree), userid)
        cur.execute("UPDATE bots SET (botone, bottwo, botthree) = (%s, %s, %s) WHERE userid = %s", tupleval)
        conn.commit()

        cur.execute("UPDATE users SET botactive = %s WHERE userid = %s", (True, userid))
        conn.commit()

        return json.dumps({"result": "success"}), 200, {"contentType": "application/json"}

        
@app.route("/updateapikey", methods=["GET","POST"])
@cross_origin(origin="*", headers=["Content- Type", "Authorization"])
def updateapikey():
    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  updateapikey error =========================== ")
            print(ex)
            pass
        print(data)

        sessionToken = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(sessionToken, key, algorithms="HS256")
        print(" ========  updateapikey   decoded   ", decoded)
        email = decoded["Username"]
        print(" ========  updateapikey   email   ", email)
        apikey = data["apikey"]
        secretkey = data["secretkey"]
        print(" ========  updateapikey   apikey   ", apikey,"    ",secretkey)
        cur.execute("SELECT userid FROM users WHERE email = %s", (email,))
        userid = cur.fetchall()[0][0]
        print(" ========  updateapikey   userid   ", userid)
        btc = 0
        usdt = 0
        successbool = False
        try:
            temp = Upbit(apikey, secretkey)
            btc = temp.get_balance("BTC")
            usdt = temp.get_balance("USDT")
            successbool = True
        except Exception as ex:
            print(" ======================  updateapikey error =========================== ")
            print(ex)
            pass

        print(" ========  updateapikey   btc   ", btc,"     ", usdt,"     ", successbool)

        cur.execute("SELECT apikey, secretkey FROM users", (email,))
        tempkeys = cur.fetchall()
        for q in range(0, len(tempkeys)):
            if apikey == tempkeys[q][0] or secretkey == tempkeys[q][1]:
                return json.dumps({"result": "already"}), 200, {"contentType": "application/json"}

        cur.execute("SELECT firsttrading FROM bots WHERE userid = %s", (userid,))
        firsttrading = cur.fetchall()[0][0]
        print(" ========  updateapikey   firsttrading   ", firsttrading)
        if not firsttrading:
            return json.dumps({"result": "alreadybot"}), 200, {"contentType": "application/json"}

        if btc != None and usdt != None and successbool:
            cur.execute("UPDATE users SET (apikey, secretkey, balance) = (%s, %s, %s) WHERE email = %s", (apikey, secretkey, usdt, email))
            conn.commit()
            inputjson = json.dumps({"BTC": btc, "USDT": usdt})
            cur.execute("UPDATE bots SET totalbalance = %s WHERE userid = %s", (inputjson, userid))
            conn.commit()
            cur.execute("UPDATE users SET botactive = %s WHERE userid = %s", (False, userid))
            conn.commit()
            return json.dumps({"result": "success"}), 200, {"contentType": "application/json"}
        if btc == None and usdt == None:
            return json.dumps({"result": "wrong"}), 200, {"contentType": "application/json"}



@app.route("/transactionhistory", methods=["GET", "POST"])
@cross_origin(origin="*", headers=["Content- Type", "Authorization"])
def transactionhistory():
    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  transactionhistory error =========================== ")
            print(ex)
            pass
        print(data)

        sessionToken = ""
        sessionTokenbool = False
        try:
            sessionToken = data["sessionToken"]
        except Exception as ex:
            print(" ======================  transactionhistory error =========================== ")
            print(ex)
            sessionTokenbool = True
            pass
        if sessionTokenbool:
            templist = []
            temptemp = {
					"no": 2,
					"date": '2021-05-03',
					"time": '14:00',
					"coin": 'BTC',
					"type": 'BTC',
					"amount": '200',
					"price": '400$',
					"worth": 'N/A'
			}
            templist.append(temptemp)

            return json.dumps({"data": templist}), 200, {"ContentType": "application/json"}
        sessionToken = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(sessionToken, key, algorithms="HS256")
        email = decoded["Username"]

        cur.execute("SELECT userid FROM users WHERE email = %s", (email,))
        userid = cur.fetchall()[0][0]

        cur.execute("SELECT id, entrytime, currency, amount, baseamount, entryprice, side FROM transaction WHERE userid = %s", (userid,))

        temp = cur.fetchall()
        print(temp)
        if len(temp) != 0:
            temp = sorted(temp)
            templist = []
            for i in range(0, len(temp)):
                temptype = "매수"
                if temp[i][6] == "sell":
                    temptype = "매도"
                temptemp = {
                    "no": i+1,
                    "date": temp[i][1][:10],
                    "time": temp[i][1][11:],
                    "coin": temp[i][2],
                    "type": temptype,
                    "amount": "{:.4f}".format(temp[i][3]),
                    "price": "{:.2f}".format(temp[i][5]),
                    "worth": "{:.2f}".format(temp[i][4])
                }
                templist.append(temptemp)


            return json.dumps({"data": templist}), 200, {"ContentType": "application/json"}
        else:
            templist = []
            temptemp = {
					"no": 2,
					"date": '2021-05-03',
					"time": '14:00',
					"coin": 'BTC',
					"type": 'BTC',
					"amount": '200',
					"price": '400$',
					"worth": 'N/A'
			}
            templist.append(temptemp)

            return json.dumps({"data": templist}), 200, {"ContentType": "application/json"}



@app.route('/healthcheck', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def healthcheck():
    if request.method == "GET":
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


if __name__ == '__main__':
#    app.config['SECRET_KEY'] = 'Gmc@1234!'
#    csrf = CSRFprotect()
#    csrf.init_app(app)
    app.secret_key='secret123'
#    app.run(host='0.0.0.0', port=80, debug=True)
    app.run(host='0.0.0.0', port=5055, debug=True)








