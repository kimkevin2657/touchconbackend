###  web3 version = 5.24.0
### homepage = https://github.com/ethereum/web3.py
### requires = websockets, jsonschema, eth-abi, aiohttp, hexbytes, protobuf, ipfshttpclient, eth-hash, lru-dict, pywin32, eth-utils, eth-account, eth-typing, requests


from web3 import Web3
import json
import requests

from flask import Flask, request, logging, jsonify, redirect
from flask_cors import CORS, cross_origin

cors = CORS()

app = Flask(__name__)

CORS(app)

app.config['CORS_HEADERS'] = 'Content-Type'
app.config["SECRET_KEY"] = "temp secret"

cors.init_app(app)


#infura = "https://mainnet.infura.io/v3/d3636135d8fd41a68bc2348d7ee7a72b"


infura = "https://mainnet.infura.io/v3/29cf0d783a5b4f219c0a18f59b4402e8"


w3 = Web3(Web3.HTTPProvider(infura))

#latest_block = w3.eth.get_block("latest")
#gas_limit = int(latest_block.gasLimit / (1 if len(latest_block.transactions) == 0 else len(latest_block.transactions)))
#print(gas_limit)


contract_address = "0x549905519f9e06d55d7dfcd4d54817780f6b93e8"

abi = json.load(open("touchconabi.json"))


#############################################################################################################
#############################################################################################################
#############################################################################################################
import psycopg2
DB_NAME = "touchcon"
DB_USER = "touchcon"
DB_PASS = "touchcon"
DB_HOST = "localhost"
DB_PORT = "5432" 
conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
cur = conn.cursor()

import pytz
import datetime
from time import gmtime, strftime
def currenttime():
    tz1 = pytz.timezone("UTC")
    tz2 = pytz.timezone("Asia/Seoul")
    dt = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt
#############################################################################################################
#############################################################################################################
#############################################################################################################


@app.route('/balance', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def balance():
    if request.method == "GET":

        from_address = request.args.get("address")
        ### ethereum balance
        check_sum = w3.toChecksumAddress(from_address)
        balance = w3.eth.get_balance(check_sum)
        ether_value  = w3.fromWei(balance, 'ether')



        ### erc20 balance
        token = w3.eth.contract(address=w3.toChecksumAddress(contract_address), abi=abi["abi"]) # declaring the token contract
        token_balance = token.functions.balanceOf(w3.toChecksumAddress(from_address)).call() # returns int with balance, without decimals
        print(" token_balance    ", token_balance)
        token_balance = w3.fromWei(token_balance, "ether")
        print(" token_balance  fromWei   ", token_balance)

        #############################################################################################################
        tempuserid = 0
        try:
            cur.execute("SELECT userid FROM users WHERE wallet = %s", (from_address,))
        except:
            conn.rollback()
        else:
            tempuserid = cur.fetchall()[0][0]
        try:
            cur.execute("INSERT INTO transactions (type, date, userid) VALUES (%s, %s, %s)",("balance", currenttime(), tempuserid))
        except:
            conn.rollback()
        else:
            conn.commit()
        #############################################################################################################

        return json.dumps({"eth_balance": float(ether_value), "balance": float(token_balance)}), 200, {'ContentType':'application/json'}


    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(ex)

        from_address = data["from_address"] 

        ### ethereum balance
        check_sum = w3.toChecksumAddress(from_address)
        balance = w3.eth.get_balance(check_sum)
        ether_value  = w3.fromWei(balance, 'ether')

        ### erc20 balance
        token = w3.eth.contract(address=w3.toChecksumAddress(contract_address), abi=abi["abi"]) # declaring the token contract
        token_balance = token.functions.balanceOf(w3.toChecksumAddress(from_address)).call() # returns int with balance, without decimals
        token_balance = w3.fromWei(token_balance, "ether")

        #############################################################################################################
        tempuserid = 0
        try:
            cur.execute("SELECT userid FROM users WHERE wallet = %s", (from_address,))
        except:
            conn.rollback()
        else:
            tempuserid = cur.fetchall()[0][0]
        try:
            cur.execute("INSERT INTO transactions (type, date, userid) VALUES (%s, %s, %s)",("balance", currenttime(), tempuserid))
        except:
            conn.rollback()
        else:
            conn.commit()
        #############################################################################################################

        return json.dumps({"Ethereum": float(ether_value), "TouchCon": float(token_balance)}), 200, {'ContentType':'application/json'}

        
@app.route('/sendeth', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def sendeth():
    if request.method == "GET":
        from_address = request.args.get("from_address")
        from_address_private_key = request.args.get("from_address_private_key")
        to_address = request.args.get("to_address")
        amount = float(request.args.get("amount"))


        ### send ethereum 
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

        print(" ======   /senderc     gastype    ", gastype)
        print(" ======   /senderc     waittime    ", waittime)



        nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(from_address))
        print(" ========= send erc20.py   sendeth initial  nonce   ",nonce)

        tx_hash = 1
        error_message = ""
        nonce_count = 0
        whilebool = False
        whilecount = 0
        while not whilebool:
            whilecount += 1
            if whilecount > 10:
                whilebool = True
            tx = {
                'nonce': w3.toHex(nonce),
                'to': w3.toChecksumAddress(to_address),
                'value': w3.toWei(amount, 'ether'),
                'gas': 30000,
                'gasPrice': w3.toWei(gasprice, 'gwei'),
            }
            signed_tx = w3.eth.account.sign_transaction(tx, from_address_private_key)
            try:
                tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
                whilebool = True
            except ValueError as ex:
                if "message" in ex.args[0]:
                    if ex.args[0].get("message") == 'replacement transaction underpriced':
                        if nonce_count == 0:
                            nonce += 1
                            nonce_count = 1
                        gasprice *= 1.1
                        error_message = ex.args[0].get("message")
                    if ex.args[0].get("message") == 'insufficient funds for gas * price + value':
                        error_message = ex.args[0].get("message")
                        whilebool = True
                pass
                    
                    

        """
        nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(from_address))
        tx = {
            'nonce': nonce,
            'to': w3.toChecksumAddress(to_address),
            'value': w3.toWei(amount, 'ether'),
            'gas': 30000,
            'gasPrice': w3.toWei(gasprice, 'gwei'),
        }
        signed_tx = w3.eth.account.sign_transaction(tx, from_address_private_key)

        tx_hash = ""
        try:
            tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        except ValueError as ex:
            print(" =====   /senderc   tx_hash error     ", ex)
            print(" =====   /senderc   tx_hash error  type   ", type(ex))
            gasprice *= 1.4
            tx = {
                'nonce': nonce,
                'to': w3.toChecksumAddress(to_address),
                'value': w3.toWei(amount, 'ether'),
                'gas': 30000,
                'gasPrice': w3.toWei(gasprice, 'gwei'),
            }
            signed_tx = w3.eth.account.sign_transaction(tx, from_address_private_key)
            tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            pass
        """

        #############################################################################################################
        #############################################################################################################

        #return json.dumps({"transaction": w3.toHex(tx_hash), "Waittime": waittime}), 200, {'ContentType':'application/json'}
        if error_message == "":
            return json.dumps({"transaction": w3.toHex(tx_hash), "Waittime": waittime}), 200, {'ContentType':'application/json'}
        if error_message == "insufficient funds for gas * price + value":
            return json.dumps({"transaction": "insufficient funds for gas * price + value", "Waittime": waittime}), 200, {'ContentType':'application/json'}

    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(ex)

        from_address = data["from_address"] 
        from_address_private_key = data["from_address_private_key"]
        to_address = data["to_address"]
        amount = data["amount"]


        ### send ethereum 
        r = requests.get("https://ethgasstation.info/api/ethgasAPI.json?api-key=3502f4f4e22ce930b268de8fea9c5a25a9674a8e98c700225936665566d4")
        gasprice = r.json()["average"]/10.0
        nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(from_address))
        tx = {
            'nonce': nonce,
            'to': w3.toChecksumAddress(to_address),
            'value': w3.toWei(amount, 'ether'),
            'gas': 30000,
            'gasPrice': w3.toWei(gasprice, 'gwei'),
        }
        signed_tx = w3.eth.account.sign_transaction(tx, from_address_private_key)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        #############################################################################################################
        #############################################################################################################

        return json.dumps({"transaction": w3.toHex(tx_hash)}), 200, {'ContentType':'application/json'}


@app.route('/senderc', methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
def senderc():
    if request.method == "GET":

        
        from_address = request.args.get("from_address")
        from_address_private_key = request.args.get("from_address_private_key")
        to_address = request.args.get("to_address")
        amount = float(request.args.get("amount"))

        print(" /senderc   input params     ", from_address, "   ", from_address_private_key, "   ", to_address, "   ", amount)

        ### send erc20
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

        print(" ======   /senderc     gastype    ", gastype)
        print(" ======   /senderc     waittime    ", waittime)

        print(" /senderc   gasprice    ", gasprice)

        

        unicorns = w3.eth.contract(w3.toChecksumAddress(contract_address), abi=abi["abi"])

        nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(from_address))
        print(" /senderc   nonce   ", nonce)

        tx_hash = 1
        error_message = ""
        nonce_count = 0
        whilebool = False
        whilecount = 0
        tempcount = 0
        while not whilebool:
            whilecount += 1
            if whilecount > 10:
                whilebool = True
            tempcount += 1
            print(" =====================  current while loop count     ", tempcount)
            print(" current gasprice   ", gasprice)
            print(" current nonce   ", nonce)
            print(" w3.toWei(amount, 'ether')   value    ", w3.toWei(amount, 'ether'))
            print(" w3.toWei(amount, 'ether')   type    ", type(w3.toWei(amount, 'ether')))

            unicorn_txn = unicorns.functions.transfer(w3.toChecksumAddress(to_address), w3.toWei(amount, 'ether')).buildTransaction({
                'gas': 80000,
                'gasPrice': w3.toWei(gasprice, 'gwei'),
                'nonce': w3.toHex(nonce),
                'value': 0
            })

            signed_tx = w3.eth.account.sign_transaction(unicorn_txn, from_address_private_key)

            try:
                #tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
                tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
                whilebool = True
            except ValueError as ex:
                print(" senderc  ValueError   ", ex)
                if "message" in ex.args[0]:
                    if ex.args[0].get("message") == 'replacement transaction underpriced':
                        print(" failed transaction ===  replacement transaction underpriced  ")
                        if nonce_count == 0:
                            nonce += 1
                            nonce_count = 1
                        gasprice *= 1.1
                        error_message = ex.args[0].get("message")
                    if ex.args[0].get("message") == 'insufficient funds for gas * price + value':
                        print(" failed transaction ===  insufficient funds  ")
                        error_message = ex.args[0].get("message")
                        whilebool = True
                pass

        print()
        print(" tx_hash    ", w3.toHex(tx_hash))
        print(" error_message   ", error_message)

        """
        print(" /senderc   unicorns    ", unicorns)

        unicorn_txn = unicorns.functions.transfer(w3.toChecksumAddress(to_address), w3.toWei(amount, "ether")).buildTransaction({
            'gas': 80000,
            'gasPrice': w3.toWei(gasprice, 'gwei'),
            'nonce': nonce
        })
        print(" /senderc    unicorn_txn    ", unicorn_txn)

        signed_tx = w3.eth.account.sign_transaction(unicorn_txn, from_address_private_key)

        print(" /senderc   signed_tx    ", signed_tx)

        tx_hash = ""
        try:
            tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        except Exception as ex:
            print(" =====   /senderc   tx_hash error     ", ex)
            gasprice *= 1.4
            unicorn_txn = unicorns.functions.transfer(w3.toChecksumAddress(to_address), w3.toWei(amount, "ether")).buildTransaction({
                'gas': 80000,
                'gasPrice': w3.toWei(gasprice, 'gwei'),
                'nonce': nonce
            })
            signed_tx = w3.eth.account.sign_transaction(unicorn_txn, from_address_private_key)
            tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
            pass


        print(" /senderc   tx_hash     ", w3.toHex(tx_hash))
        """

        #############################################################################################################
        #############################################################################################################

        #return json.dumps({"transaction": w3.toHex(tx_hash), "Waittime": waittime}), 200, {'ContentType':'application/json'}
        if error_message == "":
            return json.dumps({"transaction": w3.toHex(tx_hash), "Waittime": waittime}), 200, {'ContentType':'application/json'}
        if error_message == "insufficient funds for gas * price + value":
            return json.dumps({"transaction": "insufficient funds for gas * price + value", "Waittime": waittime}), 200, {'ContentType':'application/json'}


    if request.method == "POST":
        data = dict()
        try:
            data = request.get_json()
        except Exception as ex:
            print(ex)

        from_address = data["from_address"] 
        from_address_private_key = data["from_address_private_key"]
        to_address = data["to_address"]
        amount = data["amount"]

        ### send erc20
        r = requests.get("https://ethgasstation.info/api/ethgasAPI.json?api-key=3502f4f4e22ce930b268de8fea9c5a25a9674a8e98c700225936665566d4")
        gasprice = r.json()["average"]/10.0
        nonce = w3.eth.getTransactionCount(w3.toChecksumAddress(from_address))

        unicorns = w3.eth.contract(w3.toChecksumAddress(contract_address), abi=abi["abi"])

        unicorn_txn = unicorns.functions.transfer(w3.toChecksumAddress(to_address), w3.toWei(amount, "ether")).buildTransaction({
            'gas': 80000,
            'gasPrice': w3.toWei(gasprice, 'gwei'),
            'nonce': nonce
        })

        signed_tx = w3.eth.account.sign_transaction(unicorn_txn, from_address_private_key)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

        #############################################################################################################
        #############################################################################################################

        return json.dumps({"transaction": w3.toHex(tx_hash)}), 200, {'ContentType':'application/json'}


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
    app.run(host='0.0.0.0', port=3000, debug=True)






