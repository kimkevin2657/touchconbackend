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

import urllib

import random

import qrcode

from PIL import Image
import base64
import io
import cv2
import numpy as np
import imutils
from web3 import Web3


from sdk.api.message import Message
from sdk.exceptions import CoolsmsException



guard = flask_praetorian.Praetorian()
cors = CORS()

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["SECRET_KEY"] = "temp secret"
app.config['JWT_ACCESS_LIFESPAN'] = {'hours': 24}
app.config['JWT_REFRESH_LIFESPAN'] = {'days': 30}

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

@app.route('/isadmin', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def isadmin():
    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        print(" ========   couponlist  =============   ", data)

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]

        tempbool = ""
        try:
            cur.execute("SELECT id FROM companies WHERE login = %s", (email,))
        except:
            conn.rollback()
        else:
            tempbool = cur.fetchall()
        if len(tempbool) == 0:
            return json.dumps({"Result": "failed"}), 200, {'ContentType':'application/json'}

        temp = []
        try:
            cur.execute("SELECT id FROM companies WHERE login = %s", (email,))
        except:
            conn.rollback()
        else:
            temp = cur.fetchall()
        if len(temp) != 0:
            if len(temp[0]) != 0:
                return json.dumps({"Result": "company"}), 200, {'ContentType':'application/json'}
        
        temp = []
        try:
            cur.execute("SELECT id FROM admins WHERE login = %s", (email,))
        except:
            conn.rollback()
        else:
            temp = cur.fetchall()
        if len(temp) != 0:
            if len(temp[0]) != 0:
                return json.dumps({"Result": "admin"}), 200, {'ContentType':'application/json'}
        


@app.route('/login', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def login():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        loginval = data["Id"]
        password = data["Pass"]
        typeval = data["Type"]

        print(" ==========   login  data    ", data)

        tempbool = ""
        if typeval == "company":
            try:
                cur.execute("SELECT id FROM companies WHERE login = %s", (loginval,))
            except:
                conn.rollback()
            else:
                tempbool = cur.fetchall()
        if typeval == "admin":
            try:
                cur.execute("SELECT id FROM admins WHERE login = %s", (loginval,))
            except:
                conn.rollback()
            else:
                tempbool = cur.fetchall()

        if len(tempbool) == 0:
            return json.dumps({"Result": "failed"}), 200, {'ContentType':'application/json'}

        if typeval == "admin":
            curr_password = ""
            try:
                cur.execute("SELECT password FROM admins WHERE login = %s", (loginval,))
            except:
                conn.rollback()
            else:
                curr_password = cur.fetchall()[0][0]
            if sha256_crypt.verify(password, curr_password):
                key = "secret key"
                userid = ""
                try:
                    cur.execute("SELECT userid FROM admins WHERE login = %s", (loginval,))
                except:
                    conn.rollback()
                else:
                    userid = cur.fetchall()[0][0]
                encoded = jwt.encode({"email": loginval, "userid": userid }, key, algorithm="HS256")
                return json.dumps({"sessionToken": encoded}), 200, {'ContentType':'application/json'}
            else:
                return json.dumps({"Result": "비밀번호가 틀렸습니다."}), 200, {'ContentType':'application/json'}


        if typeval == "company":
            curr_password = ""
            try:
                cur.execute("SELECT password, registered FROM companies WHERE login = %s", (loginval,))
            except:
                conn.rollback()
            else:
                curr_password = cur.fetchall()[0]
            if sha256_crypt.verify(password, curr_password[0]) and curr_password[1]:
                key = "secret key"
                userid = ""
                try:
                    cur.execute("SELECT userid FROM companies WHERE login = %s", (loginval,))
                except:
                    conn.rollback()
                else:
                    userid = cur.fetchall()[0][0]
                encoded = jwt.encode({"email": loginval, "userid": userid }, key, algorithm="HS256")
                return json.dumps({"sessionToken": encoded}), 200, {'ContentType':'application/json'}
            else:
                return json.dumps({"Result": "비밀번호가 틀렸습니다."}), 200, {'ContentType':'application/json'}
            if not curr_password[1]:
                return json.dumps({"Result": "not approved"}), 200, {'ContentType':'application/json'}


@app.route('/adminregister', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def adminregister():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        login = data["Id"]
        password = data["Pass"]
        try:
            cur.execute("INSERT INTO admins (login, password) VALUES (%s, %s)",(login, sha256_crypt.encrypt(password)))
        except:
            conn.rollback()
        else:
            conn.commit()

        return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'}




@app.route('/register', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def register():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        name = data["Name"]
        phone = data["Phone"]
        ceo = data["CEO"]
        regis = data["Regis"]
        password = data["Pass"]

        encoded_image2 = data["Logo"]

        encoded_image = ""
        extension = ""
        if encoded_image2[:22] == "data:image/png;base64,":
            encoded_image = encoded_image2[22:]
            extension = ".png"
        if encoded_image2[:23] == "data:image/jpeg;base64,":
            encoded_image = encoded_image2[23:]
            extension = ".jpeg"


        imgid = str(random.randint(100000, 999999))

        base64_decoded = relaxed_decode_base64(encoded_image)

        image = Image.open(io.BytesIO(base64_decoded))

        image_numpy = np.array(image)

        image_numpy = imutils.resize(image_numpy, width=800)

        im = Image.fromarray(image_numpy)
        im.save("./coupons/"+str(currenttime()[:10])+"_"+str(imgid)+".png")

        temp = []
        try:
            cur.execute("SELECT company, registered FROM companies WHERE login = %s", (name,))
        except:
            conn.rollback()
        else:
            temp = cur.fetchall()

        if len(temp) == 0:

            try:
                cur.execute("INSERT INTO companies (login, password, company, phone, ceo, regis, registered, date, touchconpoint, admingive, logo) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",(name, sha256_crypt.encrypt(password), name, phone, ceo, regis, False, currenttime(), 0.0, 0.0, "./coupons/"+str(currenttime()[:10])+"_"+str(imgid)+".png"))
            except:
                conn.rollback()
            else:
                conn.commit()

            return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'}

        else:
            if temp[0][1] == True:
                return json.dumps({"Result": "failed"}), 200, {'ContentType':'application/json'}
            else:
                return json.dumps({"Result": "failed"}), 200, {'ContentType':'application/json'}


@app.route('/couponlist', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def couponlist():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        print(" ========   couponlist  =============   ", data)

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]

        curlist = []
        try:
            cur.execute("SELECT id, title, number, date, active, phones FROM coupons WHERE (company, active) = (%s, %s)", (email, True))
        except:
            conn.rollback()
        else:
            curlist = cur.fetchall()

        if len(curlist) != 0:

            curlist2 = []
            for q in range(0, len(curlist)):
                if curlist[q][5] == None:
                    curlist2.append(curlist[q])

            curlist = sorted(curlist2)

            curlist = curlist[::-1]

            templist = []
            for i in range(0, len(curlist)):
                if curlist[i][4] == False:
                    continue
                tempdict = dict()
                tempdict["Subject"] = curlist[i][1]
                tempdict["Amount"] = curlist[i][2]
                tempdict["Date"] = curlist[i][3][:10]
                templist.append(tempdict)

            return json.dumps({"Result": templist}), 200, {'ContentType':'application/json'} 
        else:
            return json.dumps({"Result": []}), 200, {'ContentType':'application/json'} 


@app.route('/couponuselist', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def couponuselist():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]

        curlist = []
        try:
            cur.execute("SELECT id, title, number, date, couponid, active, phones FROM coupons WHERE (company, active) = (%s, %s)", (email, True))
        except:
            conn.rollback()
        else:
            curlist = cur.fetchall()

        if len(curlist) != 0:

            curlist2 = []
            for q in range(0, len(curlist)):
                if curlist[q][6] != None:
                    curlist2.append(curlist[q])

            curlist = sorted(curlist2)

            curlist = curlist[::-1]

            couponidlist = [0 for x in range(0, len(curlist))]
            for i in range(0, len(curlist)):
                if curlist[i][5] == False:
                    continue
                trans = []
                try:
                    cur.execute("SELECT id, type, date, userid FROM transactions WHERE couponid = %s", (curlist[i][4],))
                except:
                    conn.rollback()
                else:
                    trans = cur.fetchall()

                couponidlist[i] = len(trans)

            templist = []
            for i in range(0, len(curlist)):
                if curlist[i][5] == False:
                    continue
                tempdict = dict()
                tempdict["Subject"] = curlist[i][1]
                tempdict["Amount"] = int(curlist[i][2]) - int(couponidlist[i])
                tempdict["Date"] = curlist[i][3][:10]
                tempdict["Boolean"] = "전송 성공"
                if curlist[i][6] == None:
                    tempdict["Phone"] = []
                else:
                    tempdict["Phone"] = curlist[i][6]
                templist.append(tempdict)

            return json.dumps({"Result": templist}), 200, {'ContentType':'application/json'} 
        else:
            return json.dumps({"Result": []}), 200, {'ContentType':'application/json'} 



@app.route('/createcoupon', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def createcoupon():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        print(" ==========   decoded   ", decoded)
        email = decoded["email"]
        userid = decoded["userid"]
        amount = data["Amount"]
        number = data["Number"]
        subject = data["Subject"]
        title = data["Title"]

        admingive = ""
        try:
            cur.execute("SELECT admingive, touchconpoint FROM companies WHERE userid = %s", (userid,))
        except:
            conn.rollback()
        else:
            admingive = cur.fetchall()[0]

        pointbalance = float(admingive[0]) + float(admingive[1])


        if pointbalance < float(amount) * float(number):
            return json.dumps({"Result": "터치포인트가 부족합니다. 어드민한테서 구매 부탁드립니다."}), 200, {'ContentType':'application/json'} 


        encoded_image2 = data["Image"]

        print(" =============   create coupon extension    ", encoded_image2[:50])
        print(encoded_image2[:22])
        print(encoded_image2[:23])

        encoded_image = ""
        extension = ""
        if encoded_image2[:22] == "data:image/png;base64,":
            encoded_image = encoded_image2[22:]
            extension = ".png"
        if encoded_image2[:23] == "data:image/jpeg;base64,":
            encoded_image = encoded_image2[23:]
            extension = ".jpeg"


        extension = ".png"

        couponid = str(random.randint(100000, 999999))

        base64_decoded = relaxed_decode_base64(encoded_image)

        image = Image.open(io.BytesIO(base64_decoded))

        image_numpy = np.array(image)

        image_numpy = imutils.resize(image_numpy, width=800)

        im = Image.fromarray(image_numpy)
        im.save("./coupons/"+str(currenttime()[:10])+"_"+str(couponid)+extension)

        tupleval = (couponid, email, number, amount, "./coupons/"+str(currenttime()[:10])+"_"+str(couponid)+extension, title, subject, currenttime(), True, False)

        try:
            cur.execute("INSERT INTO coupons (couponid, company, number, amount, image, title, subject, date, active, individualsend) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tupleval)
        except:
            conn.rollback()
        else:
            conn.commit()

        return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'} 


@app.route('/couponimages', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def couponimages():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]

        imglocations = []
        try:
            cur.execute("SELECT image, active FROM coupons WHERE company = %s", (email,))
        except:
            conn.rollback()
        else:
            imglocations = cur.fetchall()

        if len(imglocations) != 0:

            imgs = []
            for i in range(0, len(imglocations)):
                if imglocations[i][1] == False:
                    continue
                imgs.append(cv2.imread(imglocations[i][0], cv2.IMREAD_UNCHANGED))


            imgsbase64 = []
            for i in range(0, len(imgs)):
                _, imagebytes = cv2.imencode(".png", imgs[i])
                currimg = str(base64.b64encode(imagebytes))[2:]
                currimg2 = currimg[:-1]
                imgsbase64.append(currimg2)


            return json.dumps({"Result": imgsbase64}), 200, {'ContentType':'application/json'} 

        else:
            return json.dumps({"Result": []}), 200, {'ContentType':'application/json'} 

@app.route('/deletecoupon', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def deletecoupon():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]
        title = data["Subject"]

        for i in range(0, len(title)):

            try:
                cur.execute("UPDATE coupons SET active = %s WHERE title = %s", (False, title[i]))
            except:
                conn.rollback()
            else:
                conn.commit()

        return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'} 


@app.route('/pointcompanygive', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def pointcompanygive():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
            print(" ==============     ", data)
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]
        
        typeval = ""    
        try:
            cur.execute("SELECT id FROM admins WHERE login = %s", (email,))
        except:
            conn.rollback()
        else:
            typeval = cur.fetchall()

        if len(typeval) != 0:
            # sessionToken= 토큰, Company=기업명, Amount= 포인트
            companyname = data["Company"]
            amount = data["Amount"]
            curramount = ""
            try:
                cur.execute("SELECT admingive FROM companies WHERE company = %s", (companyname,))
            except:
                conn.rollback()
            else:
                curramount = cur.fetchall()

            if len(curramount) == 0:
                return json.dumps({"Result": "없는 기업명입니다"}), 200, {'ContentType':'application/json'} 
            else:
                newamount = float(curramount[0][0]) + float(amount)
                try:
                    cur.execute("UPDATE companies SET admingive = %s WHERE company = %s", (newamount,companyname))
                except Exception as ex:
                    print(ex)
                    conn.rollback()
                else:
                    conn.commit()


                """

                curradmingive = ""
                try:
                    cur.execute("SELECT admingive FROM companies WHERE company = %s", (companyname,))
                except:
                    conn.rollback()
                else:
                    curradmingive = cur.fetchall()[0][0]
                newcurradmingive = float(curradmingive) + float(amount)
                try:
                    cur.execute("UPDATE companies SET admingive = %s WHERE company = %s", (newcurradmingive, companyname))
                except:
                    conn.rollback()
                else:
                    conn.commit()
                """

                companyuserid = ""
                try:
                    cur.execute("SELECT userid FROM companies WHERE company = %s", (companyname,))
                except:
                    conn.rollback()
                else:
                    companyuserid = cur.fetchall()[0][0]

                try:
                    cur.execute("INSERT INTO transactions (type, date, userid, couponid) VALUES (%s, %s, %s, %s)",("admin", str(currenttime()[:10]), companyuserid, float(amount)))
                except:
                    conn.rollback()
                else:
                    conn.commit()

                return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'} 

        if len(typeval) == 0:
            return json.dumps({"Result": "권한 없습니다"}), 200, {'ContentType':'application/json'} 




@app.route('/getcoupons', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def getcoupons():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]

        typeval = ""

        tempval = []
        try:
            cur.execute("SELECT id FROM admins WHERE login = %s", (email,))
        except:
            conn.rollback()
        else:
            tempval = cur.fetchall()

        if len(tempval) == 0:
            typeval = "company"
        else:
            typeval = "admin"



        if typeval == "company":
            tpoints2 = ""
            try:
                cur.execute("SELECT touchconpoint, admingive FROM companies WHERE login = %s", (email,))
            except:
                conn.rollback()
            else:
                tpoints2 = cur.fetchall()

            tpoints = tpoints2[0][0] + tpoints2[0][1]
            
            
            resultlist = []
            try:
                cur.execute("SELECT couponid, number, title, date FROM coupons WHERE company = %s", (email,))
            except:
                conn.rollback()
            else:
                resultlist = cur.fetchall()
            totalused = []
            if len(resultlist) != 0:
                for k in range(0, len(resultlist)):
                    resultlist2 = []
                    try:
                        cur.execute("SELECT id FROM transactions WHERE couponid = %s", (int(resultlist[k][0]),))
                    except:
                        conn.rollback()
                    else:
                        resultlist2 = cur.fetchall()
                    totalused.append(len(resultlist2))

                finallist = []
                for k in range(0, len(resultlist)):
                    tempdict = dict()
                    tempdict["Company"] = email
                    tempdict["Title"] = resultlist[k][2]
                    tempdict["Points"] = int(resultlist[k][1]) + int(totalused[k])
                    tempdict["Used"] = int(totalused[k])
                    tempdict["Date"] = resultlist[k][3][:10]
                    finallist.append(tempdict)
                
                return json.dumps({"TouchConPoint": tpoints, "Result": finallist}), 200, {'ContentType':'application/json'} 
                # Result= [ {Company: 기업명, Points: 포인트, Date: 전송일} ] , "TouchConPoint" = 터치콘 포인트

            else:
                return json.dumps({"TouchConPoint": tpoints, "Result": []}), 200, {'ContentType':'application/json'} 

        if typeval == "admin":
            tpoints2 = 0.0
            totalpoints = []
            try:
                cur.execute("SELECT touchconpoint, admingive FROM companies WHERE registered = %s", (True,))
            except:
                conn.rollback()
            else:
                totalpoints = cur.fetchall()
            if len(totalpoints) != 0:
                for k in range(0, len(totalpoints)):
                    tpoints2 += totalpoints[k][1]
            tpoints = tpoints2

            admingive = ""
            try:
                cur.execute("SELECT admingive FROM companies WHERE login = %s", (email,))
            except:
                conn.rollback()
            else:
                admingive = cur.fetchall()[0][0]
            
            resultlist = []
            try:
                cur.execute("SELECT couponid, number, title, date, company FROM coupons WHERE active = %s", (True,))
            except:
                conn.rollback()
            else:
                resultlist = cur.fetchall()
            totalused = []
            if len(resultlist) != 0:
                for k in range(0, len(resultlist)):
                    resultlist2 = []
                    try:
                        cur.execute("SELECT id FROM transactions WHERE couponid = %s", (int(resultlist[k][0]),))
                    except:
                        conn.rollback()
                    else:
                        resultlist2 = cur.fetchall()
                    totalused.append(len(resultlist2))

                finallist = []
                for k in range(0, len(resultlist)):
                    tempdict = dict()
                    tempdict["Company"] = resultlist[k][4]
                    tempdict["Title"] = resultlist[k][2]
                    tempdict["Points"] = int(resultlist[k][1]) + int(totalused[k])
                    tempdict["Used"] = int(totalused[k])
                    tempdict["Date"] = resultlist[k][3][:10]
                    finallist.append(tempdict)
                
                return json.dumps({"TouchConPoint": tpoints, "TouchConPointAdmin" : admingive ,"Result": finallist}), 200, {'ContentType':'application/json'} 
                # Result= [ {Company: 기업명, Points: 포인트, Date: 전송일} ] , "TouchConPoint" = 터치콘 포인트

            else:
                return json.dumps({"TouchConPoint": tpoints, "TouchConPointAdmin" : admingive , "Result": []}), 200, {'ContentType':'application/json'} 



@app.route('/companylist', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def companylist():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]

        templsit = []
        try:
            cur.execute("SELECT company, regis, registered, date FROM companies")
        except:
            conn.rollback()
        else:
            templsit = cur.fetchall()

        if len(templsit) != 0:

            resultlist = []
            for i in range(0, len(templsit)):
                tempdict = dict()
                tempdict["Company"] = templsit[i][0]
                tempdict["Regis"] = templsit[i][1]
                tempdict["Status"] = templsit[i][2]
                tempdict["Date"] = templsit[i][3]
                resultlist.append(tempdict)


            return json.dumps({"Result": resultlist}), 200, {'ContentType':'application/json'} 

        else:
            return json.dumps({"Result": []}), 200, {'ContentType':'application/json'} 


@app.route('/deletecompany', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def deletecompany():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]

        companylist = data["Company"]

        print(" ==========  companylist     ", companylist)

        for i in range(0, len(companylist)):
            try:
                cur.execute("DELETE FROM companies WHERE company = %s", (companylist[i],))
            except:
                conn.rollback()
            else:
                conn.commit()

            tempcoupons = []
            try:
                cur.execute("SELECT id FROM coupons WHERE company = %s", (companylist[i],))
            except:
                conn.rollback()
            else:
                tempcoupons = cur.fetchall()
            if len(tempcoupons) != 0:
                for q in range(0, len(tempcoupons)):
                    try:
                        cur.execute("DELETE FROM coupons WHERE id = %s", (tempcoupons[q],))
                    except:
                        conn.rollback()
                    else:
                        conn.commit()
            

        return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'} 



@app.route('/approvecompany', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def approvecompany():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]

        companylist = data["Company"]

        print(" ==========  companylist     ", companylist)

        for i in range(0, len(companylist)):
            try:
                cur.execute("UPDATE companies SET registered = %s WHERE company = %s", (True, companylist[i],))
            except:
                conn.rollback()
            else:
                conn.commit()

        return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'} 


@app.route('/pointcompanylist', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def pointcompanylist():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
            print(" ==============     ", data)
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]

        typeval = ""

        tempval = []
        try:
            cur.execute("SELECT id FROM admins WHERE login = %s", (email,))
        except:
            conn.rollback()
        else:
            tempval = cur.fetchall()

        if len(tempval) == 0:
            typeval = "company"
        else:
            typeval = "admin"

        print(" ======= pointcompanylist  data     ", data)

        if typeval == "company":
            tpoints = ""
            try:
                cur.execute("SELECT touchconpoint FROM companies WHERE login = %s", (email,))
            except:
                conn.rollback()
            else:
                tpoints = cur.fetchall()[0][0]

            admingive = ""
            try:
                cur.execute("SELECT admingive FROM companies WHERE login = %s", (email,))
            except:
                conn.rollback()
            else:
                admingive = cur.fetchall()[0][0]

            print(" ====================     ", tpoints, "      ", admingive)
            
            resultlist = []
            try:
                cur.execute("SELECT couponid, number, title, date FROM coupons WHERE company = %s", (email,))
            except:
                conn.rollback()
            else:
                resultlist = cur.fetchall()
            totalused = []
            if len(resultlist) != 0:

                resultlist = sorted(resultlist)
                resultlist = resultlist[::-1]
                for k in range(0, len(resultlist)):

                    resultlist2 = []
                    try:
                        cur.execute("SELECT id FROM transactions WHERE couponid = %s", (int(resultlist[k][0]),))
                    except:
                        conn.rollback()
                    else:
                        resultlist2 = cur.fetchall()
                    totalused.append(len(resultlist2))

                finallist = []
                for k in range(0, len(resultlist)):
                    tempdict = dict()
                    tempdict["Company"] = email
                    tempdict["Title"] = resultlist[k][2]
                    tempdict["Points"] = int(resultlist[k][1]) + int(totalused[k])
                    tempdict["Used"] = int(totalused[k])
                    tempdict["Date"] = resultlist[k][3][:10]
                    finallist.append(tempdict)
                
                print( " ====== result    ", {"TouchConPoint": tpoints, "TouchConPointAdmin": admingive, "Result": finallist})

                return json.dumps({"TouchConPoint": tpoints, "TouchConPointAdmin": admingive, "Result": finallist}), 200, {'ContentType':'application/json'} 
                # Result= [ {Company: 기업명, Points: 포인트, Date: 전송일} ] , "TouchConPoint" = 터치콘 포인트

            else:
                return json.dumps({"TouchConPoint": tpoints, "TouchConPointAdmin": admingive, "Result": []}), 200, {'ContentType':'application/json'} 

        print(" ==============    ", data, "   ", typeval)

        if typeval == "admin":
            tpoints = 0.0
            totalpoints = []
            try:
                cur.execute("SELECT admingive FROM companies WHERE registered = %s", (True,))
            except:
                conn.rollback()
            else:
                totalpoints = cur.fetchall()
            if len(totalpoints) != 0:
                for k in range(0, len(totalpoints)):
                    tpoints += totalpoints[k][0]



            resultlist = []
            try:
                cur.execute("SELECT company, date, admingive, touchconpoint, userid FROM companies WHERE registered = %s", (True,))
            except:
                conn.rollback()
            else:
                resultlist = cur.fetchall()
            
            if len(resultlist) != 0:
                resultlist = sorted(resultlist)
                resultlist = resultlist[::-1]
                finallist = []
                for k in range(0, len(resultlist)):
                    tempdict = dict()
                    tempdict["Company"] = resultlist[k][0]
                    tempdict["Points"] = resultlist[k][2]
                    tempdict["Admingive"] = resultlist[k][3]
                    tempdates = []
                    print(" =============  tempdates data     ", resultlist[k][4])
                    try:
                        cur.execute("SELECT id, date FROM transactions WHERE (type, userid) = (%s, %s)", ("admin", resultlist[k][4]))
                    except Exception as ex:
                        print(ex)
                        conn.rollback()
                    else:
                        tempdates = cur.fetchall()
                    print(" ==========   tempdates   ", tempdates)
                    latestdate = ""
                    if len(tempdates) != 0:
                        tempdates = sorted(tempdates)
                        tempdates = tempdates[::-1]
                        latestdate = tempdates[0][1]
                    tempdict["Date"] = latestdate
                    finallist.append(tempdict)

                print({"TouchConPoint": tpoints, "Result": finallist})
                return json.dumps({"TouchConPoint": tpoints, "Result": finallist}), 200, {'ContentType':'application/json'} 
                # Result= [ {Company: 기업명, Points: 포인트, Date: 전송일} ] , "TouchConPoint" = 터치콘 포인트

            else:
                return json.dumps({"TouchConPoint": tpoints, "Result": []}), 200, {'ContentType':'application/json'} 




@app.route('/notices', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def notices():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]

        templist = []
        try:
            cur.execute("SELECT id, title, subject, adminid, date, active FROM notice")
        except:
            conn.rollback()
        else:
            templist = cur.fetchall()

        resultlist = []
        if len(templist) != 0:
            templist = sorted(templist)
            templist = templist[::-1]
            for i in range(0, len(templist)):
                if templist[i][5] == False:
                    continue
                tempdict = dict()
                tempdict["Id"] = templist[i][0]
                tempdict["Title"] = templist[i][1]
                tempdict["Admin"] = templist[i][3]
                tempdict["Date"] = templist[i][4]
                tempdict["Subject"] = templist[i][2]
                resultlist.append(tempdict)
        
        return json.dumps({"Result": resultlist}), 200, {'ContentType':'application/json'} 


@app.route('/noticesmodify', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def noticesmodify():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass



            title = data["Title"]
            subject = data["Subject"]
            idval = data["Id"]

            currdate = currenttime()[:10]

            print(idval)
            print(" ==========  ")
            print(title)
            print(" ===========  ")
            print(subject)
            print(" ==========  ")
            print(currdate)


            cur.execute("UPDATE notice SET (title, subject) = (%s, %s) WHERE id = %s", (title, subject, idval))
            conn.commit()

            return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}

@app.route('/noticeswebmodify', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def noticeswebmodify():
    if request.method == "POST":

        for i in range(0, 5):

            data = dict()
            try:
                data = request.get_json()
            except Exception as ex:
                print(" ======================  pinregister error =========================== ")
                print(ex)
                pass



            title = data["Title"]
            subject = data["Subject"]
            idval = data["Id"]

            currdate = currenttime()[:10]

            try:
                cur.execute("UPDATE webnotice SET (title, subject) = (%s, %s) WHERE id = %s", (title, subject, idval))
            except:
                conn.rollback()
            else:
                conn.commit()


            return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}


@app.route('/uploadnotice', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def uploadnotice():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]
        title = data["Title"]
        subject = data["Subject"]
        date = data["Date"]

        print(" ============== uploadnotice     ",data)
        try:
            cur.execute("INSERT INTO notice (title, subject, date, adminid, active) VALUES (%s, %s, %s, %s, %s)", (title, subject, date, "TouchCon", True))
        except:
            conn.rollback()
        else:
            conn.commit()

        return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'} 



@app.route('/uploadnoticeweb', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def uploadnoticeweb():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]
        title = data["Title"]
        subject = data["Subject"]
        date = data["Date"]

        print(" ============== uploadnotice     ",data)
        try:
            cur.execute("INSERT INTO webnotice (title, subject, date, adminid, active) VALUES (%s, %s, %s, %s, %s)", (title, subject, date, "TouchCon", True))
        except:
            conn.rollback()
        else:
            conn.commit()

        return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'} 




@app.route('/deletenoticeweb', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def deletenoticeweb():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]
        title = data["Title"]

        try:
            cur.execute("UPDATE webnotice SET active = %s WHERE title = %s", (False, title))
        except:
            conn.rollback()
        else:
            conn.commit()

        return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'} 


@app.route('/deletenotice', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def deletenotice():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]
        title = data["Title"]

        try:
            cur.execute("UPDATE notice SET active = %s WHERE title = %s", (False, title))
        except:
            conn.rollback()
        else:
            conn.commit()


        return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'} 


@app.route('/getadminwallet', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def getadminwallet():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]


        temp = []
        try:
            cur.execute("SELECT id FROM admins WHERE login = %s", (email,))
        except:
            conn.rollback()
        else:
            temp = cur.fetchall()

        if len(temp) != 0:

            temp1 = []
            try:
                cur.execute("SELECT id, wallet, privatekey FROM adminwallet")
            except:
                conn.rollback()
            temp1 = cur.fetchall()

            temp1 = sorted(temp1)
            temp1 = temp1[::-1]

            wallet = temp1[0][1]
            privatekey = temp1[0][2]

            return json.dumps({"Wallet": wallet, "Privatekey": privatekey}), 200, {'ContentType':'application/json'} 

        if len(temp) == 0:

            return json.dumps({"Result": "어드민이 아니십니다."}), 200, {'ContentType':'application/json'} 




@app.route('/addadminwallet', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def addadminwallet():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        email = decoded["email"]

        wallet = data["Wallet"]
        privatekey = data["Privatekey"]

        temp = Web3.isAddress(wallet)
        if not temp:
            return json.dumps({'Result': "유효하지 않은 출금주소입니다."}), 200, {'ContentType':'application/json'}

        temp = []
        try:
            cur.execute("SELECT id FROM admins WHERE login = %s", (email,))
        except:
            conn.rollback()
        else:
            temp = cur.fetchall()

        if len(temp) != 0:

            try:
                cur.execute("INSERT INTO adminwallet (wallet, privatekey) VALUES (%s, %s)", (wallet, privatekey))
            except:
                conn.rollback()
            else:
                conn.commit()

            return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'} 

        if len(temp) == 0:

            return json.dumps({"Result": "어드민이 아니십니다."}), 200, {'ContentType':'application/json'} 




@app.route('/sendsms', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def sendsms():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass


        # sessionToken=토큰,  Amount=str 금액, Image=이미지, Subject=내용, Title=제목, Phone=["폰번호", "폰번호"]

        # Result="success"  ||   Result=["실패한 번호", "실패한 번호", "실패한 번호"]

        token = data["sessionToken"]
        key = "secret key"
        decoded = jwt.decode(token, key, algorithms="HS256")
        print(" ==========   decoded   ", decoded)
        email = decoded["email"]
        userid = decoded["userid"]
        amount = data["Amount"]
        number = data["Number"]
        subject = data["Subject"]
        title = data["Title"]
        phone2 = data["Phone"]

        phone = ["".join("".join(x.split("-")).split(".")) for x in phone2]

        number = len(phone)

        admingive = ""
        try:
            cur.execute("SELECT admingive, touchconpoint FROM companies WHERE userid = %s", (userid,))
        except:
            conn.rollback()
        else:
            admingive = cur.fetchall()[0]

        pointbalance = float(admingive[0]) + float(admingive[1])


        if pointbalance < float(amount) * float(number):
            return json.dumps({"Result": "터치포인트가 부족합니다. 어드민한테서 구매 부탁드립니다."}), 200, {'ContentType':'application/json'} 


        encoded_image2 = data["Image"]

        print(" =============   create coupon extension    ", encoded_image2[:50])
        print(encoded_image2[:22])
        print(encoded_image2[:23])

        encoded_image = ""
        extension = ""
        if encoded_image2[:22] == "data:image/png;base64,":
            encoded_image = encoded_image2[22:]
            extension = ".png"
        if encoded_image2[:23] == "data:image/jpeg;base64,":
            encoded_image = encoded_image2[23:]
            extension = ".png"


        couponid = str(random.randint(100000, 999999))

        print(" ================   couponid    ", couponid)

        base64_decoded = relaxed_decode_base64(encoded_image)

        image = Image.open(io.BytesIO(base64_decoded))

        image_numpy = np.array(image)

        image_numpy = imutils.resize(image_numpy, width=400)

        im = Image.fromarray(image_numpy)

        imgfilename = "./coupons/"+str(currenttime()[:10])+"_"+str(couponid)

        im.save(imgfilename+extension)

        qrimgfilename = imgfilename + "_qr"
        

        img = qrcode.make(couponid)

        img.save(qrimgfilename+".png")
        

        ########################################################################################################
        ########################################## send SMS function ###########################################


        #api_key = "NCS2RPCUQIIMMB5C"
        #api_secret = "AEAURWLHQMUGPP2PAJ2NMYTKOJPU1YZD"
        api_key = "NCSTANMZJG9LHJSS"
        api_secret = "G4LQRMA7JFRHW3LPXOEPJGAL12AGDM9Y"
        cool = Message(api_key, api_secret)

        missedphone = []
        nobalance = False
        for q in range(0, len(phone)):

            if len(phone[q]) > 11:
                missedphone.append(phone[q])
                continue
            if phone[q][:3] != "010":
                missedphone.append(phone[q])
                continue


            ## 4 params(to, from, type, text) are mandatory. must be filled
            params = dict()
            params['type'] = 'mms' # Message type ( sms, lms, mms, ata )
            params['to'] = phone[q] # Recipients Number '01000000000,01000000001'
            params['from'] = '025583805' # Sender number
            params['text'] = "" # Message

            params["image"] = qrimgfilename+".png"
            #params["image"] = imgfilename+extension


            sendtempbool = False

            try:
                response = cool.send(params)
                print(json.dumps(response, indent=4))
                for key, value in response.items():
                    if key == "code" and value == "FileUploadFail":
                        missedphone.append(phone[q])
                    if key == "errorCode" and value == "NotEnoughBalance":
                        missedphone.append(phone[q])
                        nobalance = True
                    if key == "success_count" and value == 0:
                        missedphone.append(phone[q])
            except CoolsmsException as ex:
                print(ex)
                sendtempbool = True
                missedphone.append(phone[q])
            ## 4 params(to, from, type, text) are mandatory. must be filled

            if not sendtempbool:
                params = dict()
                params['type'] = 'mms' # Message type ( sms, lms, mms, ata )
                params['to'] = phone[q] # Recipients Number '01000000000,01000000001'
                params['from'] = '025583805' # Sender number
                params['text'] = "[터치콘] "+ subject # Message
                params["image"] = imgfilename+extension

                try:
                    response = cool.send(params)
                    print(json.dumps(response, indent=4))
                    for key, value in response.items():
                        if key == "code" and value == "FileUploadFail":
                            missedphone.append(phone[q])
                        if key == "errorCode" and value == "NotEnoughBalance":
                            missedphone.append(phone[q])
                            nobalance = True
                        if key == "success_count" and value == 0:
                            missedphone.append(phone[q])

                except CoolsmsException as ex:
                    print(ex)
                    missedphone.append(phone[q])

        if nobalance:
            return json.dumps({"Result": "coolsms.co.kr 에서 크레딧 잔고가 부족합니다."}), 200, {'ContentType':'application/json'} 

        print(" ========   phone      ", phone)
        print(" ========   missedphone    ", missedphone)


        if len(missedphone) == len(phone):
            return json.dumps({"Result": phone}), 200, {'ContentType':'application/json'} 


        successphone = []
        for q in range(0, len(phone)):
            if phone[q] in missedphone:
                continue
            if phone[q] not in missedphone:
                successphone.append(phone[q])


        ########################################################################################################
        ########################################################################################################

        thejsonb = dict()
        thejsonb["phones"] = successphone

        number = len(phone)

        tupleval = (couponid, email, number, amount, imgfilename+".png", title, subject, currenttime(), True, True, json.dumps(thejsonb))

        try:
            cur.execute("INSERT INTO coupons (couponid, company, number, amount, image, title, subject, date, active, individualsend, phones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", tupleval)
        except Exception as ex:
            conn.rollback()
        else:
            conn.commit()

        if len(missedphone) == 0:

            return json.dumps({"Result": "success"}), 200, {'ContentType':'application/json'} 
        else:
            return json.dumps({"Result": missedphone}), 200, {'ContentType':'application/json'} 





@app.route('/companyinfo', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def companyinfo():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        company = data["Company"]

        temp = []
        try:
            cur.execute("SELECT phone, ceo, regis, logo FROM companies WHERE company = %s", (company,))
        except:
            conn.rollback()
        else:
            temp = cur.fetchall()[0]


        templogo = cv2.imread(temp[3], cv2.IMREAD_UNCHANGED)
        _, imagebytes = cv2.imencode(".png", templogo)
        currimg = str(base64.b64encode(imagebytes))[2:]
        currimg2 = currimg[:-1]
        imgsbase64 = currimg2

        return json.dumps({"Company": company, "Ceo": temp[1], "Phone": temp[0], "Regis": temp[2], "Logo": imgsbase64}), 200, {'ContentType':'application/json'} 




@app.route('/assigndetail', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def assigndetail():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        
        company = data["Company"]

        companyid = ""
        try:
            cur.execute("SELECT userid FROM companies WHERE company = %s", (company,))
        except:
            conn.rollback()
        else:
            companyid = cur.fetchall()[0][0]

        temp = []
        try:
            cur.execute("SELECT id, date, couponid FROM transactions WHERE userid = %s", (companyid,))
        except:
            conn.rollback()
        else:
            temp = cur.fetchall()

        if len(temp) == 0:
            return json.dumps({"Result": temp}), 200, {'ContentType':'application/json'}

        else:
            temp = sorted(temp)
            temp = temp[::-1]
            result = []
            for i in range(0, len(temp)):
                tempdict = dict()
                tempdict["Admin"] = "TouchCon"
                tempdict["Date"] = temp[i][1]
                tempdict["Amount"] = temp[i][2]
                result.append(tempdict)

            return json.dumps({"Result": result}), 200, {'ContentType':'application/json'}


@app.route('/givedetail', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def givedetail():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        
        company = data["Company"]

        temp = []
        try:
            cur.execute("SELECT id, date, title, amount, number FROM coupons WHERE company = %s", (company,))
        except:
            conn.rollback()
        else:
            temp = cur.fetchall()

        if len(temp) == 0:
            return json.dumps({"Result": temp}), 200, {'ContentType':'application/json'}

        else:

            temp = sorted(temp)
            temp = temp[::-1]

            result = []
            for i in range(0, len(temp)):
                tempdict = dict()
                tempdict["Date"] = temp[i][1]
                tempdict["Title"] = temp[i][2]
                tempdict["Amount"] = temp[i][3]
                tempdict["Number"] = temp[i][4]
                result.append(tempdict)

            return json.dumps({"Result": result}), 200, {'ContentType':'application/json'}




@app.route('/scanuserdetail', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def scanuserdetail():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        title = data["Title"]
        couponid = ""
        try:
            cur.execute("SELECT couponid FROM coupons WHERE title = %s", (title,))
        except:
            conn.rollback()
        else:
            couponid = cur.fetchall()[0][0]

        temp = []
        try:
            cur.execute("SELECT id, date, userid FROM transactions WHERE couponid = %s", (couponid,))
        except:
            conn.rollback()
        else:
            temp = cur.fetchall()

        if len(temp) == 0:
            return json.dumps({"Result": temp}), 200, {'ContentType':'application/json'}

        else:

            temp = sorted(temp)
            temp = temp[::-1]

            result = []
            for i in range(0, len(temp)):
                temptemp = []
                try:
                    cur.execute("SELECT email, phone FROM users WHERE userid = %s", (temp[i][2],))
                except:
                    conn.rollback()
                else:
                    temptemp = cur.fetchall()[0]

                
                tempdict = dict()
                tempdict["Date"] = temp[i][1]
                tempdict["Email"] = temptemp[0]
                tempdict["Phone"] = temptemp[1]
                result.append(tempdict)

            return json.dumps({"Result": result}), 200, {'ContentType':'application/json'}



@app.route('/')
def redirecttomain():
    return redirect("https://www.rewardcon.com", code=302)



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
    app.run(host='0.0.0.0', port=5000, debug=True)








