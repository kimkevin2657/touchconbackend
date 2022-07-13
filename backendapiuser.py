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

from PIL import Image
import base64
import io
import cv2
import numpy as np
import imutils


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



@app.route('/popular', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def popular():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass


        coupons2 = []
        try:
            cur.execute("SELECT id, title, amount, image, couponid, company, number FROM coupons WHERE (active, individualsend) = (%s, %s)", (True, False))
        except:
            conn.rollback()
        else:
            coupons2 = cur.fetchall()

        print(" ==== coupons " , coupons2)

        if len(coupons2) == 0:
            return json.dumps({"Result": []}), 200, {'ContentType':'application/json'}

        coupons = []
        for q in range(0, len(coupons2)):
            if coupons2[q][6] == 0:
                continue
            else:
                coupons.append(coupons2[q])
        

        coupons = sorted(coupons)

        temppopular = [[0, coupons[i][0], coupons[i][2], coupons[i][5], coupons[i][1], coupons[i][4]] for i in range(0, len(coupons))]
        for k in range(0, len(coupons)):
            trans = []
            try:
                cur.execute("SELECT id FROM transactions WHERE couponid = %s", (coupons[k][4],))
            except:
                conn.rollback()
            else:
                trans = cur.fetchall()
            temppopular[k][0] = len(trans)
    
        temppopular = sorted(temppopular)
        temppopular = temppopular[::-1]

        print(" === temppopular   ", temppopular)

        resultlist = []
        maxidx = min(8, len(temppopular))
        for i in range(0, maxidx):
            currcompany = temppopular[i][3]

            currcompanyinfo = []
            try:
                cur.execute("SELECT logo, userid FROM companies WHERE company = %s", (currcompany,))
            except:
                conn.rollback()
            else:
                currcompanyinfo = cur.fetchall()[0]

            print(currcompanyinfo[0])

            print(" =====   ",i, "    ",currcompanyinfo[0][len(currcompanyinfo[0])-4:len(currcompanyinfo[0])] )


            currlogo = cv2.imread(currcompanyinfo[0], cv2.IMREAD_UNCHANGED)

            currimg2 = ""
            if currcompanyinfo[0][len(currcompanyinfo[0])-5:len(currcompanyinfo[0])] == ".jpeg":
                print(" ====  ", currcompanyinfo[0])
                _, imagebytes = cv2.imencode(".png", currlogo)
                currimg = str(base64.b64encode(imagebytes))[2:]
                currimg2 = currimg[:-1]

            if currcompanyinfo[0][len(currcompanyinfo[0])-4:len(currcompanyinfo[0])] == ".png":
                print(" ====  ", currcompanyinfo[0])
                _, imagebytes = cv2.imencode(".png", currlogo)
                currimg = str(base64.b64encode(imagebytes))[2:]
                currimg2 = currimg[:-1]


            tempdict = dict()
            tempdict["Title"] = temppopular[i][4]
            tempdict["Companyid"] = currcompanyinfo[1]
            tempdict["Amount"] = temppopular[i][2]
            tempdict["Logo"] = currimg2
            tempdict["Company"] = currcompany
            tempdict["Couponid"] = temppopular[i][5]

            resultlist.append(tempdict)


        # Result= [ {"Logo": 기업 로고 이미지, "Title": 쿠폰 제목, "Amount": 쿠폰 금액, "Companyid" 기업 id } , { ... } ] 

        return json.dumps({"Result": resultlist}), 200, {'ContentType':'application/json'}


@app.route('/company', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def company():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        companies = []
        try:
            cur.execute("SELECT id, userid, logo, company FROM companies WHERE registered = %s", (True,))
        except:
            conn.rollback()
        else:
            companies = cur.fetchall()

        if len(companies) == 0:
            return json.dumps({"Result": []}), 200, {'ContentType':'application/json'}

        companies = sorted(companies)

        resultlist = []
        for k in range(0, len(companies)):
            tempdict = dict()
            tempdict["Company"] = companies[k][3]
            tempdict["Companyid"] = companies[k][1]

            currlogo = cv2.imread(companies[k][2], cv2.IMREAD_UNCHANGED)

            _, imagebytes = cv2.imencode(".png", currlogo)
            currimg = str(base64.b64encode(imagebytes))[2:]
            currimg2 = currimg[:-1]
    
            tempdict["Logo"] = currimg2

            resultlist.append(tempdict)

        # Result=[ {"Logo": 기업 로고 이미지, "Company": 기업명, "Companyid": 기업id }, { ... } ]

        return json.dumps({"Result": resultlist}), 200, {'ContentType':'application/json'}



@app.route('/coupon', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def coupon():
    if request.method == "POST":

        # "Companyid" : 기업id 

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        companyid = int(data["Companyid"])
        companyval = ""
        try:
            cur.execute("SELECT company FROM companies WHERE userid = %s", (companyid,))
        except:
            conn.rollback()
        else:
            companyval = cur.fetchall()[0][0]

        print(" ==== companyval  ", companyval)

        coupons2 = []
        try:
            cur.execute("SELECT id, image, title, amount, couponid, number FROM coupons WHERE (company, individualsend) = (%s, %s)", (companyval,False))
        except:
            conn.rollback()
        else:
            coupons2 = cur.fetchall()

        if len(coupons2) == 0:
             return json.dumps({"Result": []}), 200, {'ContentType':'application/json'}

        coupons = []
        for q in range(0, len(coupons2)):
            if coupons2[q][5] == 0:
                continue
            else:
                coupons.append(coupons2[q])

        coupons = sorted(coupons)

        print(" ==== coupons   ", coupons)

        resultlist = []
        for k in range(0, len(coupons)):
            tempdict = dict()
            
            currlogo = cv2.imread(coupons[k][1], cv2.IMREAD_UNCHANGED)

            _, imagebytes = cv2.imencode(".png", currlogo)
            currimg = str(base64.b64encode(imagebytes))[2:]
            currimg2 = currimg[:-1]

            tempdict["Image"] = currimg2
            tempdict["Company"] = companyval
            tempdict["Title"] = coupons[k][2]
            tempdict["Amount"] = coupons[k][3]
            tempdict["Couponid"] = coupons[k][4]
            resultlist.append(tempdict)

        # Result=[ {"Image": 쿠폰 이미지, "Company": 기업명, "Title": 제목, "Amount": 쿠폰금액, "Couponid": 쿠폰id} , {... } ]

        return json.dumps({"Result": resultlist}), 200, {'ContentType':'application/json'}



@app.route('/coupondetail', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def coupondetail():
    if request.method == "POST":

        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(" ======================  emailverification error =========================== ")
            print(ex)
            pass

        # "Couponid" : 쿠폰id


        couponid = int(data["Couponid"])
    
        couponinfo = []
        try:
            cur.execute("SELECT id, title, subject, amount, number, company, image FROM coupons WHERE (couponid, individualsend) = (%s, %s)", (couponid, False))
        except:
            conn.rollback()
        else:
            couponinfo = cur.fetchall()

        if len(couponinfo) == 0:
            return json.dumps({"Result": "failed"}), 200, {'ContentType':'application/json'}


        couponinfo = sorted(couponinfo)


        currlogo = cv2.imread(couponinfo[0][6], cv2.IMREAD_UNCHANGED)

        _, imagebytes = cv2.imencode(".png", currlogo)
        currimg = str(base64.b64encode(imagebytes))[2:]
        currimg2 = currimg[:-1]


        temp = {"Title": couponinfo[0][1], "Subject": couponinfo[0][2], "Amount": couponinfo[0][3], "Couponid": couponid, "Number": couponinfo[0][4], "Company": couponinfo[0][5], "Image": currimg2}


        # "Title" = 쿠폰 제목,  "Subject": 쿠폰 내용    "Amount": 쿠폰금액, "Couponid" : 쿠폰id, "Number": 발행갯수, "Company": 기업명, 
        return json.dumps({"Result": temp}), 200, {'ContentType':'application/json'}


@app.route('/noticesweb', methods=['GET', 'POST'])
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
                    cur.execute("SELECT id, title, subject, date, adminid FROM webnotice WHERE active = %s", (True,))
                except:
                    conn.rollback()
                else:
                    temp = cur.fetchall()

                if len(temp) == 0:
                    return json.dumps({'Result': []}), 200, {'ContentType':'application/json'}

                temp = sorted(temp)

                temp = temp[::-1]

                templist = []
                for i in range(0, len(temp)):
                    tempdict = dict()
                    tempdict["Id"] = temp[i][0]
                    tempdict["Title"] = temp[i][1]
                    tempdict["Subject"] = temp[i][2]
                    tempdict["Date"] = temp[i][3][:10]
                    tempdict["Admin"] = temp[i][4]
                    templist.append(tempdict)

                return json.dumps({'Result': templist}), 200, {'ContentType':'application/json'}
        return json.dumps({'Result': "failed"}), 200, {'ContentType':'application/json'}


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
                cur.execute("UPDATE webnotice SET (title, subject, date) = (%s, %s, %s) WHERE id = %s", (title, subject, currdate, idval))
            except:
                conn.rollback()
            else:
                conn.commit()


            return json.dumps({'Result': "success"}), 200, {'ContentType':'application/json'}



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
    app.run(host='0.0.0.0', port=5500, debug=True)