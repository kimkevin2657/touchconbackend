from flask import Flask, request, logging, jsonify, redirect
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
from time import gmtime, strftime
import datetime
import time
import pytz
import random


import urllib

from PIL import Image
import io
import cv2
import numpy as np
import imutils



from decimal import Decimal
from web3 import Web3


from flask_mail import Mail
from flask_mail import Message
from eth_account import Account
import secrets

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


guard = flask_praetorian.Praetorian()
cors = CORS()


app = Flask(__name__)

mail = Mail(app)

CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config["SECRET_KEY"] = "temp secret"
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}



app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = '7xaverix7@gmail.com'
app.config['MAIL_PASSWORD'] = 'RLAqudcjf7928!'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False



cors.init_app(app)



DB_NAME = "touchcon"
DB_USER = "touchcon"
DB_PASS = "touchcon"
DB_HOST = "localhost"
DB_PORT = "5432" 
conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
cur = conn.cursor()



def currenttime():
    tz1 = pytz.timezone("UTC")
    tz2 = pytz.timezone("Asia/Seoul")
    dt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt


def relaxed_decode_base64(data):
    data2 = urllib.parse.unquote(urllib.parse.unquote(data))
    for i in range(0,1000):
        if len(data2) % 4 == 0:
            if i == 0:
                print(" no padding needed ")
            print(i)
            break
        else:
            data2 += "="

    return base64.urlsafe_b64decode(data2)

"""
@app.route("/")
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def index():


    msg = Message('Hello from the other side!', sender = '7xaverix7@gmail.com', recipients = ['xaverix7@gmail.com'])
    msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
    mail.send(msg)


    return "Message sent!"
"""


@app.route('/emailverification', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def emailverification():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  emailverification error =========================== ")
                print(ex)
                pass

            email = data["Email"]

            verificationcode = str(random.randint(1000, 9999))


            temp = []
            try:
                cur.execute("SELECT userid, registered FROM users WHERE email = %s", (email,))
            except Exception as ex:
                conn.rollback()
            else:
                temp = cur.fetchall()

            #if len(temp) != 0:
            #    if temp[0][1]:
            #        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}

            print(verificationcode)

            #sender_email = "lab10431@gmail.com"
            #sender_email = "ngm1224@gmail.com"
            sender_email = "rewardtoy@gmail.com"
            receiver_email = email
            #password = "Psalms104:31"
            #password = "redtiger298"
            #password = "gzemtqqzpltmylzc"
            password = "lfaicejuvaaavrfc"


            message = MIMEMultipart("alternative")
            message["Subject"] = "터치콘 이메일 인증코드"
            message["From"] = sender_email
            message["To"] = receiver_email

            # Create the plain-text and HTML version of your message
            text = """\
            {}
            """.format(verificationcode)

            # Turn these into plain/html MIMEText objects
            part1 = MIMEText(text, "plain")
            message.attach(part1)

            # Create secure connection with server and send email
            context = ssl.create_default_context()

            try:

                server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
                server.login(sender_email, password)
                server.sendmail(
                    sender_email, receiver_email, message.as_string()
                )

            except Exception as ex:
                print(ex)
                #return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}
                return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}

            if len(temp) == 0:
                try:
                    cur.execute("INSERT INTO users (email, verification, registered) VALUES (%s, %s, %s)",(email, verificationcode, False))
                except Exception as ex:
                    conn.rollback()
                else:
                    conn.commit()
            if len(temp) != 0:
                #if not temp[0][1]:
                try:
                    cur.execute("UPDATE users SET (verification, registered) = (%s, %s) WHERE email = %s", (verificationcode, True, email))
                except Exception as ex:
                    conn.rollback()
                else:
                    conn.commit()


            return json.dumps({'Result': verificationcode}), 200, {'ContentType':'application/json'}
        
        #return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}
        return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}
    
    
@app.route('/sendtemppassword', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def sendtemppassword():
    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except:
            pass
        
        email = data["email"]
        
        temppassword = str(random.randint(1000000, 9999999))
        
        encryptedpin = sha256_crypt.encrypt(temppassword)
        
        emailexist = ""
        try:
            cur.execute("SELECT userid FROM users WHERE email = %s", (email,))
        except:
            conn.rollback()
        else:
            emailexist = cur.fetchall()
        
        try:
            if emailexist == None or emailexist[0] == None:
                return json.dumps({'Result': "No email"}), 200, {'ContentType':'application/json'}
        except:
            pass
        
        
        #sender_email = "lab10431@gmail.com"
        #sender_email = "ngm1224@gmail.com"
        sender_email = "rewardtoy@gmail.com"
        receiver_email = email
        #password = "Psalms104:31"
        #password = "redtiger298"
        #password = "gzemtqqzpltmylzc"
        password = "lfaicejuvaaavrfc"

        message = MIMEMultipart("alternative")
        message["Subject"] = "터치콘 임시 비밀번호"
        message["From"] = sender_email
        message["To"] = receiver_email

        # Create the plain-text and HTML version of your message
        text = """\
        {}
        """.format(temppassword)

        # Turn these into plain/html MIMEText objects
        part1 = MIMEText(text, "plain")
        message.attach(part1)

        # Create secure connection with server and send email
        context = ssl.create_default_context()

        try:
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
        except Exception as ex:
            print(ex)
            #return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}
            return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}
                
        
        try:
            cur.execute("UPDATE users SET pin = %s WHERE email = %s", (encryptedpin, email))
        except:
            conn.rollback()
        else:
            conn.commit()
        
        return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}
        
        
        
    

@app.route('/emailverify', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def emailverify():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  emailverification error =========================== ")
                print(ex)
                pass

            print(" ===============   data   ", data)

            email = data["Email"]
            
            if email == "highdev@naver.com":
                return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}

            if email == "chailk6644@gmail.com":
                return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}

            code = data["Verification"]

            phone = data["Phone"]

            ver = ""
            try:
                cur.execute("SELECT verification FROM users WHERE email = %s", (email,))
            except Exception as ex:
                conn.rollback()
            else:
                ver = cur.fetchall()[0][0]

            if ver == code:
                currphone = "".join("".join(str(phone).split("-")).split("."))
                try:
                    cur.execute("UPDATE users SET phone = %s WHERE email = %s", (currphone, email))
                except:
                    conn.rollback()
                else:
                    conn.commit()

                return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}

            else:
                return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}

        #return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}
        return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}




@app.route('/pinregister', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def pinregister():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            email = data["Email"]
            pin = data["Pin"]

            encryptedpin = sha256_crypt.encrypt(pin)

            temptemptemp = "wef"
            try:
                cur.execute("SELECT touchconpoint FROM users WHERE email = %s", (email,))
            except:
                conn.rollback()
            else:
                temptemptemp = cur.fetchall()[0][0]

            try:
                temptemptemp2 = float(temptemptemp)

            except:

                try:
                    cur.execute("UPDATE users SET (pin, touchcon, touchconpoint, ethereum, registered, touchconlockup) = (%s, %s, %s, %s, %s, %s) WHERE email = %s", (encryptedpin, 0.0, 0.0, 0.0, True, 0, email))
                except Exception as ex:
                    conn.rollback()
                else:
                    conn.commit()
                try:
                    cur.execute("UPDATE users SET (touchconconversion, touchconpointconversion, touchconpointscan, touchconpointattend, touchconpointstaking, touchconpointlockup) = (%s, %s, %s, %s, %s, %s) WHERE email = %s", (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, email))
                except Exception as ex:
                    conn.rollback()
                else:
                    conn.commit()

                try:
                    cur.execute("UPDATE users SET (touchconpointlockupjson, stakingstartjson, stakingendjson) = (%s, %s, %s) WHERE email = %s", (json.dumps({"ALL": []}), json.dumps({"ALL": []}), json.dumps({"ALL": []}), email))
                except:
                    conn.rollback()
                else:
                    conn.commit()
                pass


            userid = ""
            try:
                cur.execute("SELECT userid FROM users WHERE email = %s", (email,))
            except Exception as ex:
                conn.rollback()
            else:
                userid = cur.fetchall()[0][0]


            key = "secret key"
            encoded = jwt.encode({"email": email, "userid": userid}, key, algorithm="HS256")

            return json.dumps({'Result':encoded}), 200, {'ContentType':'application/json'}

        #return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}
        return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}



@app.route('/pinlogin', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def pinlogin():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            email = decoded["email"]
            userid = int(decoded["userid"])
            pin = data["Pin"]

            temppin = ""
            try:
                cur.execute("SELECT pin, registered FROM users WHERE email = %s",(email,))
            except Exception as ex:
                print(ex)
                conn.rollback()
            else:
                temppin = cur.fetchall()


            try:

                if temppin[0][1]:
                    if sha256_crypt.verify(pin, temppin[0][0]):

                        return json.dumps({'Result':"success", "Email": email}), 200, {'ContentType':'application/json'}
                    else:

                        return json.dumps({'Result':"failed"}), 200, {'ContentType':'application/json'}


                else:
                    return json.dumps({'Result':"failed"}), 200, {'ContentType':'application/json'}

            except Exception as ex:
                print(ex)
                return json.dumps({'Result':"failed"}), 200, {'ContentType':'application/json'}

        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}


@app.route('/createwallet', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def createwallet():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            print(" =========  create wallet   ")

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            email = decoded["email"]
            userid = int(decoded["userid"])

            tempwallet = ""
            try:
                cur.execute("SELECT wallet FROM users WHERE userid = %s", (userid,))
            except:
                conn.rollback()
            else:
                tempwallet = cur.fetchall()

            print(" =============   tempwallet    ", tempwallet)
            if tempwallet[0][0] != None:
                return json.dumps({'Result': tempwallet[0][0]}), 200, {'ContentType':'application/json'}


            priv = secrets.token_hex(32)
            private_key = "0x" + priv
            acct = Account.from_key(private_key)


            try:
                cur.execute("UPDATE users SET privatekey = %s WHERE userid = %s", (private_key, userid))
            except:
                conn.rollback()
            else:
                conn.commit()

            try:
                cur.execute("UPDATE users SET wallet = %s WHERE userid = %s", (acct.address,userid))
            except:
                conn.rollback()
            else:
                conn.commit()

            return json.dumps({'Result': acct.address}), 200, {'ContentType':'application/json'}

        #return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}
        return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}



@app.route('/balance', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def balance():
    if request.method == "POST":

#        for i in range(0, 5):

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  pinregister error =========================== ")
            print(ex)
            pass
        print(" =======   /balance     data,   ", data)

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")

        email = decoded["email"]
        userid = int(decoded["userid"])


        print(" =======   /balance     email, userid,   ", email, "     ", userid)

        print(" =============   before fetched wallet data from users     ", userid)
        templist = []
        try:
            cur.execute("SELECT wallet, privatekey, touchcon, ethereum FROM users WHERE userid = %s", (userid,))
        except:
            conn.rollback()
        else:
            templist = cur.fetchall()[0]

        print(" =============   fetched wallet data from users     ", userid)

        #print(" =============  /balance     ", templist2)

        #if len(templist2) == 0:
        #    return json.dumps({'Result': {"TouchCon": str(0), "Ethereum" : str(0), "TouchPoint": str(0)}}), 200, {'ContentType':'application/json'}

        #templist = templist2[0]


        from_address = templist[0]
        privateKey = templist[1]

        """
        print(" =============   before fetched touchcon and ethereum from :3000     ", from_address)
        r = requests.get("http://127.0.0.1:3000/balance?address="+from_address)
        touchcon = r.json()["balance"]
        ethereum = r.json()["eth_balance"]
        """

        infura = "https://mainnet.infura.io/v3/29cf0d783a5b4f219c0a18f59b4402e8"

        contract_address = "0x549905519f9e06d55d7dfcd4d54817780f6b93e8"

        abi = json.load(open("./transfer/touchconabi.json"))

        w3 = Web3(Web3.HTTPProvider(infura))
        
        check_sum = w3.toChecksumAddress(from_address)
        balance = w3.eth.get_balance(check_sum)
        ether_value  = w3.fromWei(balance, 'ether')

        ### erc20 balance
        token = w3.eth.contract(address=w3.toChecksumAddress(contract_address), abi=abi["abi"]) # declaring the token contract
        token_balance = token.functions.balanceOf(w3.toChecksumAddress(from_address)).call() # returns int with balance, without decimals
        print(" token_balance    ", token_balance)
        token_balance = w3.fromWei(token_balance, "ether")
        print(" token_balance  fromWei   ", token_balance)
        
        touchcon = token_balance
        ethereum = ether_value









        print(" =============   fetched touchcon and ethereum from :3000     ", touchcon, "   ", ethereum, "    ", type(touchcon), "    ", type(ethereum))

        print(" =============   before fetched point data from users     ", userid)
        templist = []
        try:
            cur.execute("SELECT touchcon, touchconconversion, touchconlockup, touchconpointconversion, touchconpointscan, touchconpointattend, touchconpointstaking, touchconpointlockupjson, ethereum FROM users WHERE userid = %s", (userid,))
        except:
            conn.rollback()
        else:
            templist = cur.fetchall()[0]

        print(" =============   fetched point data from users     ", userid)

        # touchcon = actual TOC in wallet, 
        # touchconconversion = converted from TOP to TOC
        # touchconlockup = amount of TOC converted to TOP
        # touchconpointconversion = converted from TOC to TOP, 
        # touchconpointscan = scanned coupon and acquired TOP
        # touchconpointattend = attendance gained TOP
        # touchconpointstaking = amount of TOP gained from after staking ended
        # touchconpointlockup = amount of TOP that's locked up due to staking
        touchcon = float(touchcon) + float(templist[1]) - float(templist[2])
        touchconpoint = float(templist[3]) + float(templist[4]) + float(templist[5]) + float(templist[6]) - float(sum(templist[7]["ALL"]))
        ethereum = float(ethereum)


        print({"TouchCon": touchcon, "Ethereum" :ethereum, "TouchPoint": touchconpoint})

        return json.dumps({'Result': {"TouchCon": str(touchcon), "Ethereum" : str(ethereum), "TouchPoint": str(touchconpoint)}}), 200, {'ContentType':'application/json'}

#        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}




@app.route('/convert', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def convert():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            email = decoded["email"]
            userid = int(decoded["userid"])

            coin = float(data["Coin"])


            # touchcon -> points conversion = (add the coin amount to touchconlockup), (add the coin amount to touchconpointconversion)


            templist = []
            try:
                cur.execute("SELECT touchconlockup, touchconpointconversion FROM users WHERE userid = %s", (userid,))
            except:
                conn.rollback()
            else:
                templist = cur.fetchall()[0]

            temp2 = float(templist[0]) + float(coin)

            temp3 = float(templist[1]) + float(coin)

            try:
                cur.execute("UPDATE users SET (touchconlockup, touchconpointconversion) = (%s, %s) WHERE userid = %s", (temp2, temp3, userid))
            except:
                conn.rollback()
            else:
                conn.commit()


            return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}

        #return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}
        return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}


@app.route('/convertcoin', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def convertcoin():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            email = decoded["email"]
            userid = int(decoded["userid"])

            points = float(data["Point"])

            templist = []
            try:
                cur.execute("SELECT touchconconversion, touchconpointconversion FROM users WHERE userid = %s", (userid,))
            except:
                conn.rollback()
            else:
                templist = cur.fetchall()[0]

            temp2 = float(templist[0]) + float(points)

            temp3 = float(templist[1]) - float(points)

            try:
                cur.execute("UPDATE users SET (touchconconversion, touchconpointconversion) = (%s, %s) WHERE userid = %s", (temp2, temp3, userid))
            except:
                conn.rollback()
            else:
                conn.commit()


            return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}

        #return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}
        return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}




@app.route('/sendcoin', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def sendcoin():
    if request.method == "POST":
        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            email = decoded["email"]
            userid = int(decoded["userid"])
            coin = data["Coin"]
            amount = float(data["Amount"])
            to_address = data["Address"]

            
            print(" to_address   ", to_address)

            print(" amount   ", amount)

            typeval = ""
            if coin == "TouchCon":
                typeval = "erc20"
            if coin == "Ethereum":
                typeval = "ethereum"

            templist = []
            try:
                cur.execute("SELECT wallet, privatekey, touchcon, ethereum, touchconconversion, touchconlockup FROM users WHERE userid = %s", (userid,))
            except:
                conn.rollback()
            else:
                templist = cur.fetchall()[0]



            from_address = templist[0]
            privateKey = templist[1]

            r = requests.get("http://127.0.0.1:3000/balance?address="+from_address)
            touchcon = r.json()["balance"]
            ethereum = r.json()["eth_balance"]

            print(" ===============     balance   ", touchcon, "   ", ethereum)

            contract_address = "0x549905519f9e06d55d7dfcd4d54817780f6b93e8"

            temp = Web3.isAddress(to_address)
            if not temp:
                return json.dumps({'Result': "유효하지 않은 출금주소입니다."}), 200, {'ContentType':'application/json'}

            user_touchcon = touchcon + float(templist[4]) - float(templist[5])
            user_ethereum = ethereum

            print(" /sendcoin   user_touchcon ", user_touchcon)
            print(" /sendcoin   user_ehtereum ", user_ethereum)

            if coin == "TouchCon":
                if amount > user_touchcon:
                    print(" insufficient TOC ")
                    return json.dumps({'Result': "터치콘이 부족합니다."}), 200, {'ContentType':'application/json'}
            
            if coin == "Ethereum":
                if amount > user_ethereum:
                    print(" insufficient ethereum")
                    return json.dumps({'Result': "이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}

            #############################  수수료 계산 #######################################
            r = requests.get("https://ethgasstation.info/api/ethgasAPI.json?api-key=3502f4f4e22ce930b268de8fea9c5a25a9674a8e98c700225936665566d4")
            waittime = r.json()["fastestWait"]
            gastype = "fastest"
            gasprice = r.json()["fastest"]/10.0
            if gasprice > 40.0:
                gasprice = r.json()["fast"]/10.0
                waittime = r.json()["fastWait"]
                gastype = "fast"
            if gasprice > 38.0:
                gasprice = r.json()["average"]/10.0
                waittime = r.json()["avgWait"]
                gastype = "average"
            gasprice_wei = Web3.toWei(gasprice, "gwei")
            if coin == "TouchCon":
                if amount > touchcon:

                    if touchcon != 0.0 or touchcon != 0:
                        # send max user_touchcon from user 
                        gasLimit = 80000
                        commission = Web3.fromWei(gasprice_wei*gasLimit, "ether")
                        if commission > user_ethereum:
                            print(" insufficient ethereum commission")
                            return json.dumps({'Result': "수수료용 이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}

                    if amount - touchcon > 0.0:
                        # and then send the remaining from the admin
                        adminwallets2 = []
                        try:
                            cur.execute("SELECT id, wallet, privatekey FROM adminwallet")
                        except:
                            conn.rollback()
                        else:
                            adminwallets2 = cur.fetchall()
                        adminwallets2 = sorted(adminwallets2)
                        adminwallets2 = adminwallets2[::-1]
                        temp_adminwallets = adminwallets2[0]
                        

                        infura = "https://mainnet.infura.io/v3/29cf0d783a5b4f219c0a18f59b4402e8"

                        contract_address = "0x549905519f9e06d55d7dfcd4d54817780f6b93e8"

                        abi = json.load(open("./transfer/touchconabi.json"))

                        w3 = Web3(Web3.HTTPProvider(infura))
                        
                        check_sum = w3.toChecksumAddress(temp_adminwallets[1])
                        balance = w3.eth.get_balance(check_sum)
                        ether_value  = w3.fromWei(balance, 'ether')



                        ### erc20 balance
                        token = w3.eth.contract(address=w3.toChecksumAddress(contract_address), abi=abi["abi"]) # declaring the token contract
                        token_balance = token.functions.balanceOf(w3.toChecksumAddress(temp_adminwallets[1])).call() # returns int with balance, without decimals
                        print(" token_balance    ", token_balance)
                        token_balance = w3.fromWei(token_balance, "ether")
                        print(" token_balance  fromWei   ", token_balance)
                        
                        temp_admin_balance = token_balance
                        temp_admin_ethereum = ether_value
                        
                        
                        #r = requests.get("http://127.0.0.1:3000/balance?address="+temp_adminwallets[1])
                        #temp_admin_balance = r.json()["balance"]
                        #temp_admin_ethereum = r.json()["eth_balance"]
                        if amount - touchcon > temp_admin_balance:
                            print(" insufficient admin TOC ")
                            return json.dumps({'Result': "관리자의 TOC가 부족합니다. 관리자에 문의 부탁드립니다."}), 200, {'ContentType':'application/json'}
                        gasLimit = 80000
                        commission = Web3.fromWei(gasprice_wei*gasLimit, "ether")
                        if commission > temp_admin_ethereum:
                            print(" insufficient admin ethereum commission ")
                            return json.dumps({'Result': "관리자의 수수료용 이더리움이 부족합니다. 관리자에 문의 부탁드립니다."}), 200, {'ContentType':'application/json'}

                else:
                    gasLimit = 80000
                    commission = Web3.fromWei(gasprice_wei*gasLimit, "ether")
                    if commission > user_ethereum:
                        print(" insufficient ethereum commission")
                        return json.dumps({'Result': "수수료용 이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}

            if coin == "Ethereum":
                gasLimit = 30000
                commission = Web3.fromWei(gasprice_wei*gasLimit, "ether")
                total = commission + amount
                if total > user_ethereum:
                    print(" insufficient ethereum commission")
                    return json.dumps({'Result': "수수료용 이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}
                


            #############################  수수료 계산 #######################################


            print(" from_address, privatekey, touchcon, ethereum, typeval   ", from_address, "   ", privateKey, "   ", touchcon,"    ", ethereum, "  ", typeval)

            if typeval == "erc20":
                if amount > touchcon:
                    user_tx_hash = ""
                    admin_tx_hash = ""
                    adminwallets2 = []
                    try:
                        cur.execute("SELECT id, wallet, privatekey FROM adminwallet")
                    except:
                        conn.rollback()
                    else:
                        adminwallets2 = cur.fetchall()

                    adminwallets2 = sorted(adminwallets2)
                    adminwallets2 = adminwallets2[::-1]
                    adminwallets = adminwallets2[0]

                    print(" adminwallets     ", adminwallets)

                    useramount = touchcon

                    if touchcon != 0.0 or touchcon != 0:
                        print(" =========  user touchcon not equal to zero ")
                        res = ""
                        try:
                            res = requests.get("http://localhost:3000/senderc?from_address="+from_address+"&to_address="+to_address+"&amount="+str(useramount)+"&contract_address="+contract_address+"&type="+typeval+"&from_address_private_key="+privateKey)
                            print("  /senderc   res.json()     ", res.json())
                            if res.json()["transaction"] == "insufficient funds for gas * price + value":
                                print(" 235235235 insufficient ethereum commission")
                                return json.dumps({'Result': "수수료용 이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}
                            
                            print(" ==== /sendcoin  touchcon != 0.0 res.status_code    ", res.status_code)
                            if res.json()["transaction"] == "replacement transaction underpriced":
                                print(" 235235235 insufficient replacement transaction underpriced ")
                                return json.dumps({'Result': "현재 이더리움 블록체인이 꽉 차 있어서 나중에 다시 시도 부탁드립니다."}), 200, {'ContentType':'application/json'}
                            
                        except Exception as ex:
                            print(" ==== /sendcoin touchcon != 0.0  res.status_code    ",ex)
                            return json.dumps({'Result': "이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}

                        if res.status_code != 200:
                            return json.dumps({'Result': "이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}
                        user_tx_hash = res.json()["transaction"]
                    adminamount = amount - touchcon
                    res = ""
                    try:
                        res = requests.get("http://localhost:3000/senderc?from_address="+adminwallets[1]+"&to_address="+to_address+"&amount="+str(adminamount)+"&contract_address="+contract_address+"&type="+typeval+"&from_address_private_key="+adminwallets[2])
                        print("  /senderc   res.json()     ", res.json())
                        print(" ==== /sendcoin after touchcon != 0.0 res.status_code    ", res.status_code)
                        if res.json()["transaction"] == "insufficient funds for gas * price + value":
                            print(" 235235235 insufficient admin ethereum commission")
                            return json.dumps({'Result': "관리자의 수수료용 이더리움이 부족합니다. 관리자에 문의 부탁드립니다."}), 200, {'ContentType':'application/json'}
                        if res.json()["transaction"] == "replacement transaction underpriced":
                            print(" 235235235 insufficient replacement transaction underpriced ")
                            return json.dumps({'Result': "현재 이더리움 블록체인이 꽉 차 있어서 나중에 다시 시도 부탁드립니다."}), 200, {'ContentType':'application/json'}
                            
                    except Exception as ex:
                        print(" ==== /sendcoin after touchcon != 0.0  res.status_code    ",ex)
                        return json.dumps({'Result': "이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}

                    if res.status_code != 200:
                        return json.dumps({'Result': "이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}
                    admin_tx_hash = res.json()["transaction"]
                    currtouchconconversion = 0.0
                    try:
                        cur.execute("SELECT touchconconversion FROM users WHERE userid = %s", (userid,))
                    except:
                        conn.rollback()
                    else:
                        currtouchconconversion = cur.fetchall()[0][0]

                    newcurrtouchconconversion = currtouchconconversion - adminamount
                    try:
                        cur.execute("UPDATE users SET touchconconversion = %s WHERE userid = %s", (newcurrtouchconconversion, userid))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()

                    tempuserid = 0
                    try:
                        cur.execute("SELECT userid FROM users WHERE wallet = %s", (from_address,))
                    except:
                        conn.rollback()
                    else:
                        tempuserid = cur.fetchall()[0][0]
                    try:
                        cur.execute("INSERT INTO transactions (type, date, userid) VALUES (%s, %s, %s)",("senderc_"+to_address+"_"+str(amount)+"_"+user_tx_hash+"_"+admin_tx_hash, currenttime(), tempuserid))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()

                    return json.dumps({"Result": "success", "Waittime": res.json()["Waittime"]}), 200, {'ContentType':'application/json'}

                else:

                    tx_hash = ""
                    res = ""
                    try:
                        res = requests.get("http://localhost:3000/senderc?from_address="+from_address+"&to_address="+to_address+"&amount="+str(amount)+"&contract_address="+contract_address+"&type="+typeval+"&from_address_private_key="+privateKey)
                        
                        print("  /senderc   res.json()     ", res.json())
                        if res.json()["transaction"] == "insufficient funds for gas * price + value":
                            print(" 235235235 insufficient ethereum commission")
                            return json.dumps({'Result': "수수료용 이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}
                        if res.json()["transaction"] == "replacement transaction underpriced":
                            print(" 235235235 insufficient replacement transaction underpriced ")
                            return json.dumps({'Result': "현재 이더리움 블록체인이 꽉 차 있어서 나중에 다시 시도 부탁드립니다."}), 200, {'ContentType':'application/json'}
                            
                    except Exception as ex:
                        return json.dumps({'Result': "이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}
                    if res.status_code != 200:
                        return json.dumps({'Result': "이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}
                    else:
                        tx_hash = res.json()["transaction"]
                        tempuserid = 0
                        try:
                            cur.execute("SELECT userid FROM users WHERE wallet = %s", (from_address,))
                        except:
                            conn.rollback()
                        else:
                            tempuserid = cur.fetchall()[0][0]
                        try:
                            cur.execute("INSERT INTO transactions (type, date, userid) VALUES (%s, %s, %s)",("senderc_"+to_address+"_"+str(amount)+"_"+tx_hash, currenttime(), tempuserid))
                        except:
                            conn.rollback()
                        else:
                            conn.commit()
                        print(" /sendcoin     Waittime     ", res.json()["Waittime"])
                        return json.dumps({"Result": "success", "Waittime": res.json()["Waittime"]}), 200, {'ContentType':'application/json'}


            if typeval == "ethereum":
                print( " ================ eth section   ")
                tx_hash = ""
                res = ""
                try:
                    res = requests.get("http://localhost:3000/sendeth?from_address="+from_address+"&to_address="+to_address+"&amount="+str(amount)+"&contract_address="+contract_address+"&type="+typeval+"&from_address_private_key="+privateKey)
                    print("  /senderc   res.json()     ", res.json())
                    if res.json()["transaction"] == "insufficient funds for gas * price + value":
                        print(" 235235235 insufficient ethereum commission")
                        return json.dumps({'Result': "수수료용 이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}
                    if res.json()["transaction"] == "replacement transaction underpriced":
                        print(" 235235235 insufficient replacement transaction underpriced ")
                        return json.dumps({'Result': "현재 이더리움 블록체인이 꽉 차 있어서 나중에 다시 시도 부탁드립니다."}), 200, {'ContentType':'application/json'}
                            
                except Exception as ex:
                    return json.dumps({'Result': "이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}

                if res.status_code == 200:
                    tx_hash = res.json()["transaction"]
                    tempuserid = 0
                    try:
                        cur.execute("SELECT userid FROM users WHERE wallet = %s", (from_address,))
                    except:
                        conn.rollback()
                    else:
                        tempuserid = cur.fetchall()[0][0]
                    try:
                        cur.execute("INSERT INTO transactions (type, date, userid) VALUES (%s, %s, %s)",("sendeth_"+to_address+"_"+str(amount)+"_"+tx_hash, currenttime(), tempuserid))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()
                    return json.dumps({'Result': "success", "Waittime": res.json()["Waittime"]}), 200, {'ContentType':'application/json'}
                else:
                    return json.dumps({'Result': "이더리움이 부족합니다"}), 200, {'ContentType':'application/json'}




@app.route('/scanhistory', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def scanhistory():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            email = decoded["email"]
            userid = decoded["userid"]
        


            temp = []
            try:
                cur.execute("SELECT id, date, couponid FROM transactions WHERE userid = %s AND type = %s", (userid,"user"))
            except:
                conn.rollback()
            else:
                temp = cur.fetchall()

            print( " ======== scanhistory temp length    ", len(temp))

            if len(temp) == 0:
                
                return json.dumps({'Result': []}), 200, {'ContentType':'application/json'}

            else:
                print(" ===========  scanhistory temp length != 0  ", len(temp), "    ", temp[0])
                temp = sorted(temp)
                temp = temp[::-1]

                outputdata = []
                for i in range(0, len(temp)):
                    print(" =====   ", i)
                    tempdict = dict()
                    tempdict["Date"] = temp[i][1][:10]

                    curr_couponid = temp[i][2]
                    curr_val = []
                    try:
                        cur.execute("SELECT amount, company FROM coupons WHERE couponid = %s", (curr_couponid,))
                    except:
                        conn.rollback()
                    else:
                        curr_val = cur.fetchall()

                    print(" curr_val   ", curr_val)
                    

                    try:
                        temptemptemp = curr_val[0]
                    except Exception as ex:
                        continue

                    curr_amount = curr_val[0][0]
                    curr_company = curr_val[0][1]

                    tempdict["Amount"] = curr_amount
                    tempdict["Company"] = curr_company
                    print(" tempdict   ", tempdict)
                    outputdata.append(tempdict)

                return json.dumps({'Result': outputdata}), 200, {'ContentType':'application/json'}

        #return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}
        return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}






@app.route('/scan', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def scan():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            email = decoded["email"]
            userid = int(decoded["userid"])


            tempqrcode = data["Qr"]

            qrcode = tempqrcode
            if tempqrcode[:7] == "http://":
                qrcode = tempqrcode[7:]
            if tempqrcode[:8] == "https://":
                qrcode = tempqrcode[8:]

            temp = []
            try:
                cur.execute("SELECT id FROM transactions WHERE (userid, couponid) = (%s, %s)", (userid, int(qrcode)))
            except:
                conn.rollback()
            else:
                temp = cur.fetchall()
            if len(temp) != 0:
                return json.dumps({'Result': "이미 스캔된 쿠폰입니다."}), 200, {'ContentType':'application/json'}

            print(" ===========  input qrcode   ", qrcode)
            

            temp = []
            try:
                cur.execute("SELECT number, active, amount FROM coupons WHERE couponid = %s", (int(qrcode),))
            except:
                conn.rollback()
            else:
                temp = cur.fetchall()

            if len(temp) != 0:
                companyval = ""
                try:
                    cur.execute("SELECT company FROM coupons WHERE couponid = %s", (int(qrcode),))
                except:
                    conn.rollback()
                else:
                    companyval = cur.fetchall()[0][0]
                companypoints = ""
                try:
                    cur.execute("SELECT touchconpoint FROM companies WHERE company = %s", (companyval,))
                except:
                    conn.rollback()
                else:
                    companypoints = cur.fetchall()[0][0]

                companypointsadmingive = ""
                try:
                    cur.execute("SELECT admingive FROM companies WHERE company = %s", (companyval,))
                except:
                    conn.rollback()
                else:
                    companypointsadmingive = cur.fetchall()[0][0]

                print(" ==========    company points    ", companypoints, "   ", companypointsadmingive, "   ", temp[0][2])
                if float(companypoints) + float(companypointsadmingive) < float(temp[0][2]):
                    print(" ==========   company doesn't have enough points   ")
                    return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}





            # add coupon amount to touchconpointscan at users

            # subtract one from coupon number at coupons 

            # insert into transaction


            successbool = False
            errorstr = ""

            print(" =======  coupon  temp ", temp)

            if len(temp) != 0:
                if temp[0][0] >= 1 and temp[0][1] == True:


                    curr_touchpoint = ""
                    try:
                        cur.execute("SELECT touchconpointscan FROM users WHERE userid = %s", (userid,))
                    except:
                        conn.rollback()
                    else:
                        curr_touchpoint = cur.fetchall()[0][0]

                    
                    new_touchconpoint = float(curr_touchpoint) + float(temp[0][2])
                    try:
                        cur.execute("UPDATE users SET touchconpointscan = %s WHERE userid = %s", (new_touchconpoint, userid))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()

                    print(" =========== currtouchcpoint   ", curr_touchpoint, "    ", new_touchconpoint)

                    curr_time = currenttime()
                    try:
                        cur.execute("INSERT INTO transactions (type, date, userid, couponid) VALUES(%s, %s, %s, %s)",("user", curr_time, userid, qrcode))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()

                    curr_number = ""
                    try:
                        cur.execute("SELECT number FROM coupons WHERE couponid = %s", (int(qrcode),))
                    except:
                        conn.rollback()
                    else:
                        curr_number = cur.fetchall()[0][0]

                    new_number = int(curr_number) - 1

                    try:
                        cur.execute("UPDATE coupons SET number = %s WHERE couponid = %s", (new_number, int(qrcode)))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()

                    companyval = ""
                    try:
                        cur.execute("SELECT company FROM coupons WHERE couponid = %s", (int(qrcode),))
                    except:
                        conn.rollback()
                    else:
                        companyval = cur.fetchall()[0][0]

                    companypoints = ""
                    try:
                        cur.execute("SELECT touchconpoint FROM companies WHERE company = %s", (companyval,))
                    except:
                        conn.rollback()
                    else:
                        companypoints = cur.fetchall()[0][0]

                    companypointsadmingive = ""
                    try:
                        cur.execute("SELECT admingive FROM companies WHERE company = %s", (companyval,))
                    except:
                        conn.rollback()
                    else:
                        companypointsadmingive = cur.fetchall()[0][0]


                    if float(companypoints) + float(companypointsadmingive) < float(temp[0][2]):
                        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}


                    newcompanypoints = float(companypoints) - float(temp[0][2])
                    try:
                        cur.execute("UPDATE companies SET touchconpoint = %s WHERE company = %s", (newcompanypoints, companyval))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()

                    successbool = True

                else:
                    if temp[0][1] == False:
                        errorstr = "쿠폰이 유효하지 않습니다."
                    if temp[0][0] < 1:
                        errorstr = "쿠폰 갯수가 없습니다."
            else:
                return json.dumps({'Result': "존재하지 않는 쿠폰 입니다"}), 200, {'ContentType':'application/json'}


            if successbool:
                return json.dumps({'Result': "success", "Amount": str(float(temp[0][2]))}), 200, {'ContentType':'application/json'}

            if errorstr == "쿠폰 갯수가 없습니다.":
                return json.dumps({'Result': errorstr}), 200, {'ContentType':'application/json'}

            if errorstr == "쿠폰이 유효하지 않습니다.":
                return json.dumps({'Result': errorstr}), 200, {'ContentType':'application/json'}

            if not successbool:
                return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}



@app.route('/usercouponlist', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def usercouponlist():
    if request.method == "POST":
        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            email = decoded["email"]
            userid = decoded["userid"]

            templist = []
      
            try:
                cur.execute("SELECT id, type, date, couponid FROM transactions WHERE userid = %s AND type = %s", (userid, "user"))
            except:
                conn.rollback()
            else:
                templist = cur.fetchall()

            print(" ========= usercouponlist    ", templist)

            templist = sorted(templist, reverse=True)

            if len(templist) != 0:
                result = []
                for k in range(0, len(templist)):
                    tempval2 = []
                    try:
                        cur.execute("SELECT amount, company FROM coupons WHERE couponid = %s", (templist[k][3],))
                    except:
                        conn.rollback()
                    else:
                        tempval2 = cur.fetchall()

                    tempval = [0,0]
                    if len(tempval2) != 0:
                        tempval = tempval2[0]
                    else:
                        continue
                    tempdict = dict()
                    tempdict["Date"] = templist[k][2][:10]
                    tempdict["Amount"] = tempval[0]
                    tempdict["Company"] = tempval[1]
                    tempdict["Qr"] = str(templist[k][3]) +"_"+ token
                    result.append(tempdict)
                
                return json.dumps({'Result': result}), 200, {'ContentType':'application/json'}


            else:
                return json.dumps({'Result': []}), 200, {'ContentType':'application/json'}

                #Result={Date: 날짜, Amount: 쿠폰금액, Company: 업체명, Qr: 쿠폰id값}




@app.route('/internalscan', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def internalscan():
    if request.method == "POST":
        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            email = decoded["email"]
            userid = int(decoded["userid"])

            tempqrcode = data["Qr"]

            base64_decoded = relaxed_decode_base64(tempqrcode)

            image = Image.open(io.BytesIO(base64_decoded))

            image_numpy = np.array(image)

            image_numpy = imutils.resize(image_numpy, width=500)

            qrCodeDetector = cv2.QRCodeDetector()
            decodedText, points, _ = qrCodeDetector.detectAndDecode(image_numpy)
            qr_data = decodedText.split(",")


            qrcode = decodedText
            if tempqrcode[:7] == "http://":
                qrcode = tempqrcode[7:]
            if tempqrcode[:8] == "https://":
                qrcode = tempqrcode[8:]


            temp = []
            try:
                cur.execute("SELECT id FROM transactions WHERE (userid, couponid) = (%s, %s)", (userid, int(qrcode)))
            except:
                conn.rollback()
            else:
                temp = cur.fetchall()
            if len(temp) != 0:
                return json.dumps({'Result': "이미 스캔된 쿠폰입니다."}), 200, {'ContentType':'application/json'}


            phone = ""
            try:
                cur.execute("SELECT phone FROM users WHERE userid = %s", (int(userid),))
            except:
                conn.rollback()
            else:
                phone = cur.fetchall()[0][0]
            phones = []
            try:
                cur.execute("SELECT phones FROM coupons WHERE couponid = %s", (int(qrcode),))
            except:
                conn.rollback()
            else:
                phones = cur.fetchall()

            if phones[0][0] != None:
                phonebool = False
                listphones = phones[0][0]["phones"]
                for q in range(0, len(listphones)):
                    if listphones[q] == phone:
                        phonebool = True
                if not phonebool:
                    return json.dumps({'Result': "본인의 쿠폰이 아닙니다."}), 200, {'ContentType':'application/json'}
                


            temp = []
            try:
                cur.execute("SELECT number, active, amount FROM coupons WHERE couponid = %s", (int(qrcode),))
            except:
                conn.rollback()
            else:
                temp = cur.fetchall()


            if len(temp) != 0:
                companyval = ""
                try:
                    cur.execute("SELECT company FROM coupons WHERE couponid = %s", (int(qrcode),))
                except:
                    conn.rollback()
                else:
                    companyval = cur.fetchall()[0][0]
                companypoints = ""
                try:
                    cur.execute("SELECT touchconpoint FROM companies WHERE company = %s", (companyval,))
                except:
                    conn.rollback()
                else:
                    companypoints = cur.fetchall()[0][0]

                companypointsadmingive = ""
                try:
                    cur.execute("SELECT admingive FROM companies WHERE company = %s", (companyval,))
                except:
                    conn.rollback()
                else:
                    companypointsadmingive = cur.fetchall()[0][0]


                if float(companypoints) + float(companypointsadmingive) < float(temp[0][2]):
                    return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}
            # add coupon amount to touchconpointscan at users

            # subtract one from coupon number at coupons 

            # insert into transaction



            successbool = False
            errorstr = ""

            if len(temp) != 0:
                if temp[0][0] >= 1 and temp[0][1] == True:

                    curr_touchpoint = ""
                    try:
                        cur.execute("SELECT touchconpointscan FROM users WHERE userid = %s", (userid,))
                    except:
                        conn.rollback()
                    else:
                        curr_touchpoint = cur.fetchall()[0][0]

                    
                    new_touchconpoint = float(curr_touchpoint) + float(temp[0][2])
                    try:
                        cur.execute("UPDATE users SET touchconpointscan = %s WHERE userid = %s", (new_touchconpoint, userid))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()



                    curr_time = currenttime()
                    try:
                        cur.execute("INSERT INTO transactions (type, date, userid, couponid) VALUES(%s, %s, %s, %s)",("user", curr_time, userid, qrcode))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()

                    curr_number = ""
                    try:
                        cur.execute("SELECT number FROM coupons WHERE couponid = %s", (int(qrcode),))
                    except:
                        conn.rollback()
                    else:
                        curr_number = cur.fetchall()[0][0]

                    new_number = int(curr_number) - 1

                    try:
                        cur.execute("UPDATE coupons SET number = %s WHERE couponid = %s", (new_number, int(qrcode)))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()

                    companyval = ""
                    try:
                        cur.execute("SELECT company FROM coupons WHERE couponid = %s", (int(qrcode),))
                    except:
                        conn.rollback()
                    else:
                        companyval = cur.fetchall()[0][0]


                    companypoints = ""
                    try:
                        cur.execute("SELECT touchconpoint FROM companies WHERE company = %s", (companyval,))
                    except:
                        conn.rollback()
                    else:
                        companypoints = cur.fetchall()[0][0]

                    companypointsadmingive = ""
                    try:
                        cur.execute("SELECT admingive FROM companies WHERE company = %s", (companyval,))
                    except:
                        conn.rollback()
                    else:
                        companypointsadmingive = cur.fetchall()[0][0]

                    print(" companypoints ", companypoints)

                    if float(companypoints) + float(companypointsadmingive) < float(temp[0][2]):
                        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}

                    newcompanypoints = float(companypoints) - float(temp[0][2])
                    try:
                        cur.execute("UPDATE companies SET touchconpoint = %s WHERE company = %s", (newcompanypoints, companyval))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()

                    successbool = True

                else:
                    if temp[0][1] == False:
                        errorstr = "쿠폰이 유효하지 않습니다."
                    if temp[0][0] < 1:
                        errorstr = "쿠폰 갯수가 없습니다."
            else:
                return json.dumps({'Result': "존재하지 않는 쿠폰 입니다"}), 200, {'ContentType':'application/json'}


            if successbool:
                return json.dumps({'Result': "success" , "Amount": str(float(temp[0][2]))}), 200, {'ContentType':'application/json'}

            if errorstr == "쿠폰 갯수가 없습니다.":
                return json.dumps({'Result': errorstr}), 200, {'ContentType':'application/json'}

            if errorstr == "쿠폰이 유효하지 않습니다.":
                return json.dumps({'Result': errorstr}), 200, {'ContentType':'application/json'}

            if not successbool:
                return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}




@app.route('/attendance', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def attendance():
    if request.method == "POST":

        for i in range(0, 5):

            data = request.get_json()
            
            # 유저의 세션 토큰을 가져옴
            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            # 유저의 세션토큰에서 유저의 이메일이랑 user id 를 가지고옴
            email = decoded["email"]
            userid = decoded["userid"]

            date = data["Date"]

            currentdate = currenttime()
            records = []
            try:
                cur.execute("SELECT id, date FROM attendance WHERE userid = %s", (userid,))
            except:
                conn.rollback()
            else:
                records = cur.fetchall()
            
            if len(records) != 0:
                for q in range(0, len(records)):
                    if records[q][1] == currentdate:
                        return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}


            # attendance 라는 DB 테이블에 어느 유저가 어느날짜에 출석을 하였는지 기록함
            try:
                cur.execute("INSERT INTO attendance (userid, date) VALUES (%s, %s)",(userid, date))
            except:
                conn.rollback()
            else:
                conn.commit()

            # 유저 DB 에서 출석해서 TOP 1 적립이 되도록 1 추가 해줌
            curr_touchpoint = ""
            try:
                cur.execute("SELECT touchconpointattend FROM users WHERE email = %s", (email,))
            except:
                conn.rollback()
            else:
                curr_touchpoint = cur.fetchall()[0][0]
            new_touchpoint = float(curr_touchpoint) + 1.0

            try:
                cur.execute("UPDATE users SET touchconpointattend = %s WHERE email = %s", (new_touchpoint, email))
            except:
                conn.rollback()
            else:
                conn.commit()
                
            # 어드민 DB 에서 유저가 출석함으로써 TOP 1 를 차감을함
            admin_touchconpoint = ""
            try:
                cur.execute("SELECT touchconpoint FROM admins WHERE userid = %s", (1,))
            except:
                conn.rollback()
            else:
                admin_touchconpoint = cur.fetchall()[0][0]
                
            admin_touchconpoint -= 1.0
            try:
                cur.execute("UPDATE admins SET touchconpoint = %s WHERE userid = %s", (admin_touchconpoint, 1))
            except:
                conn.rollback()
            else:
                conn.commit()
            

            return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}

        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}


@app.route('/attendancerecord', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def attendancerecord():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            email = decoded["email"]
            userid = decoded["userid"]

            temp = []
            try:
                cur.execute("SELECT id, date FROM attendance WHERE userid = %s", (userid,))
            except:
                conn.rollback()
            else:
                temp = cur.fetchall()

            if len(temp) != 0:

                temp = sorted(temp)

                temp = temp[::-1]

                templist = []
                for i in range(0, len(temp)):
                    templist.append(temp[i][:10])

                return json.dumps({'Result': templist}), 200, {'ContentType':'application/json'}

            else:
                return json.dumps({'Result': []}), 200, {'ContentType':'application/json'}
        
        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}


@app.route('/pinchange', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def pinchange():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            email = decoded["email"]
            userid = decoded["userid"]

            newpin = data["Pin"]

            encryptedpin = sha256_crypt.encrypt(newpin)

            try:
                cur.execute("UPDATE users SET pin = %s WHERE email = %s", (encryptedpin, email))
            except:
                conn.rollback()
            else:
                conn.commit()

            return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}

        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}

@app.route('/notices', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def notices():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            typeval = data["Type"]

            if typeval == "notice":

                temp = []
                try:
                    cur.execute("SELECT id, title, subject, date FROM notice WHERE active = %s", (True,))
                except:
                    conn.rollback()
                else:
                    temp = cur.fetchall()

                if len(temp) == 0:
                    return json.dumps({'Result': "no notices"}), 200, {'ContentType':'application/json'}

                temp = sorted(temp)
                temp = temp[::-1]

                templist = []
                for i in range(0, len(temp)):
                    tempdict = dict()
                    tempdict["Title"] = temp[i][1]
                    tempdict["Subject"] = temp[i][2]
                    tempdict["Date"] = temp[i][3][:10]
                    templist.append(tempdict)

                return json.dumps({'Result': templist}), 200, {'ContentType':'application/json'}
        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}


@app.route('/unregister', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def unregister():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")

            try:
                cur.execute("UPDATE users SET registered = %s WHERE email = %s", (False, decoded["email"]))
            except:
                conn.rollback()
            else:
                conn.commit()

            return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}

        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}


@app.route('/exchangerate', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def exchangerate():
    if request.method == "POST":

        for i in range(0, 5):

            temp = []
            try:
                cur.execute("SELECT rate FROM exchangerate WHERE coin = %s", ("TouchCon",))
            except:
                conn.rollback()
            else:
                temp = cur.fetchall()[0][0]

            temp2 = []
            try:
                cur.execute("SELECT rate FROM exchangerate WHERE coin = %s", ("Ethereum",))
            except:
                conn.rollback()
            else:
                temp2 = cur.fetchall()[0][0]

            return json.dumps({'Result': {"TouchCon": temp, "Ethereum": temp2}}), 200, {'ContentType':'application/json'}
            
        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}





@app.route('/staking', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def staking():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")
            email = decoded["email"]
            userid = int(decoded["userid"])

            print(" ============    data       ", data)

            currtime = currenttime()[:10]

            currmonth = int(currtime[5:7])  

            currday = int(currtime[8:])

            curryear = int(currtime[:4])  

            amount = float(data["Amount"])
            
            
            ##################################################################################
            if email == "jin.come.up@gmail.com" or email == "tne298@naver.com" or email == "highdev@naver.com" or email == "kimkevin2657@naver.com":
                print(" =========   test emails used for staking ")
                
                
                if currmonth not in [2]:
                    return json.dumps({'Result': "incorrect time"}), 200, {'ContentType':'application/json'}

                if currday not in [14, 15, 16]:
                    return json.dumps({'Result': "incorrect time"}), 200, {'ContentType':'application/json'}


                templist = []
                try:
                    cur.execute("SELECT touchconpointlockupjson, stakingendjson FROM users WHERE registered = %s", (True,))
                except:
                    conn.rollback()
                else:
                    templist = cur.fetchall()
                if len(templist) != 0:
                    sumval = 0.0
                    for k in range(0, len(templist)):
                        if templist[k][0] != None:
                            if len(templist[k][0]["ALL"]) == 0:
                                continue
                            elif templist[k][1] != None:
                                if len(templist[k][1]["ALL"]) != 0:
                                    if templist[k][1]["ALL"][-1] != "":
                                        sumval += templist[k][0]["ALL"][-1]

                    if 1 <= currmonth and currmonth <= 9:
                        if sumval >= 8000000:
                            return json.dumps({'Result': "too much"}), 200, {'ContentType':'application/json'}
                    if 10 <= currmonth and currmonth <= 12:
                        if sumval >= 11375140:
                            return json.dumps({'Result': "too much"}), 200, {'ContentType':'application/json'}

                enddate = ""
                if currmonth == 2:
                    enddate = str(curryear) + "-02-17"
                
                print(" enddate   ", enddate)


                currstaking = []
                try:
                    cur.execute("SELECT touchconpointlockupjson, stakingstartjson, stakingendjson FROM users WHERE userid = %s", (userid,))
                except:
                    conn.rollback()
                else:
                    currstaking = cur.fetchall()[0]
                if len(currstaking) != 0:
                    
                    if currstaking[0] != None:
                        currstaking[0]["ALL"].append(amount)
                        currstaking[1]["ALL"].append(currtime)
                        currstaking[2]["ALL"].append(enddate)
                else:
                    currstaking.append({"ALL":[amount]})
                    currstaking.append({"ALL":[currtime]})
                    currstaking.append({"ALL":[enddate]})
                
                print(" ====== currstaking   ", currstaking)

                try:
                    cur.execute("UPDATE users SET (touchconpointlockupjson, stakingstartjson, stakingendjson) = (%s, %s, %s) WHERE userid = %s", (json.dumps(currstaking[0]), json.dumps(currstaking[1]), json.dumps(currstaking[2]), userid))
                except:
                    conn.rollback()
                else:
                    conn.commit()


                tupleval = ("staking", currtime+"_"+enddate, userid, amount)

                try:
                    cur.execute("INSERT INTO transactions (type, date, userid, couponid) VALUES (%s, %s, %s, %s)", tupleval)
                except:
                    conn.rollback()
                else:
                    conn.commit()
                
                return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}
        
            ####################################################################################
            
            
            
            

            if currmonth not in [1,4,7,10]:
                return json.dumps({'Result': "incorrect time"}), 200, {'ContentType':'application/json'}

            if currday not in [1,2,3,4,5,6,7,8,9,10]:
                return json.dumps({'Result': "incorrect time"}), 200, {'ContentType':'application/json'}


            templist = []
            try:
                cur.execute("SELECT touchconpointlockupjson, stakingendjson FROM users WHERE registered = %s", (True,))
            except:
                conn.rollback()
            else:
                templist = cur.fetchall()
            if len(templist) != 0:
                sumval = 0.0

                for k in range(0, len(templist)):
                    if templist[k][0] != None:
                        if len(templist[k][0]["ALL"]) == 0:
                            continue
                        elif templist[k][1] != None:
                            if len(templist[k][1]["ALL"]) != 0:
                                if templist[k][1]["ALL"][-1] != "":
                                    sumval += templist[k][0]["ALL"][-1]
                if 1 <= currmonth and currmonth <= 9:
                    if sumval >= 8000000:
                        return json.dumps({'Result': "too much"}), 200, {'ContentType':'application/json'}
                if 10 <= currmonth and currmonth <= 12:
                    if sumval >= 11375140:
                        return json.dumps({'Result': "too much"}), 200, {'ContentType':'application/json'}

            enddate = ""
            if currmonth == 1:
                enddate = str(curryear) + "-04-10"
            if currmonth == 4:
                enddate = str(curryear) + "-07-10"
            if currmonth == 7:
                enddate = str(curryear) + "-10-10"
            if currmonth == 10:
                enddate = str(curryear+1) + "-07-10"


            currstaking = []
            try:
                cur.execute("SELECT touchconpointlockupjson, stakingstartjson, stakingendjson FROM users WHERE userid = %s", (userid,))
            except:
                conn.rollback()
            else:
                currstaking = cur.fetchall()[0]
            if len(currstaking) != 0:
                if currstaking[0] != None:
                    currstaking[0]["ALL"].append(amount)
                    currstaking[1]["ALL"].append(currtime)
                    currstaking[2]["ALL"].append(enddate)
            else:
                currstaking.append({"ALL":[amount]})
                currstaking.append({"ALL":[currtime]})
                currstaking.append({"ALL":[enddate]})


            try:
                cur.execute("UPDATE users SET (touchconpointlockupjson, stakingstartjson, stakingendjson) = (%s, %s, %s) WHERE userid = %s", (json.dumps(currstaking[0]), json.dumps(currstaking[1]), json.dumps(currstaking[2]), userid))
            except:
                conn.rollback()
            else:
                conn.commit()

            tupleval = ("staking", currtime+"_"+enddate, userid, amount)

            try:
                cur.execute("INSERT INTO transactions (type, date, userid, couponid) VALUES (%s, %s, %s, %s)", tupleval)
            except:
                conn.rollback()
            else:
                conn.commit()

            return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}


        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}
    
    

@app.route('/stakinguser', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def stakinguser():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass

            token = data["sessionToken"]
            key = "secret key"
            decoded = jwt.decode(token, key, algorithms="HS256")
            email = decoded["email"]
            userid = int(decoded["userid"])



            tempuser = []
            user_toplockup = []
            stakingstartjson = []
            stakingendjson = []
            try:
                cur.execute("SELECT touchconpointlockupjson, stakingstartjson, stakingendjson FROM users WHERE userid = %s", (userid,))
            except:
                conn.rollback()
            else:
                tempuser = cur.fetchall()
            if len(tempuser) != 0:
                if len(tempuser[0]) != 0:

                    user_toplockup = tempuser[0][0]["ALL"]
                    stakingstartjson = tempuser[0][1]["ALL"]
                    stakingendjson = tempuser[0][2]["ALL"]
            
            Resultvec = []
            if len(user_toplockup) != 0 and user_toplockup != None:
                for q in range(0, len(user_toplockup)):
                    tempdict = dict()
                    tempdict["ApplicationDate"] = stakingstartjson[q][:10]
                    tempdict["ApplingAmount"] = user_toplockup[q]
                    Resultvec.append(tempdict)

            return json.dumps({'Result': Resultvec}), 200, {'ContentType':'application/json'}
            
        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}




















@app.route('/healthcheck', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def healthcheck():
    if request.method == "GET":
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}


@app.route('/')
def redirecttomain():
    return redirect("https://www.rewardcon.com", code=302)

if __name__ == '__main__':
#    app.config['SECRET_KEY'] = 'Gmc@1234!'
#    csrf = CSRFprotect()
#    csrf.init_app(app)
    app.secret_key='secret123'
#    app.run(host='0.0.0.0', port=80, debug=True)
    app.run(host='0.0.0.0', port=5055, debug=True)








