

from eth_account import Account
import secrets

priv = secrets.token_hex(32)
private_key = "0x" + priv
acct = Account.from_key(private_key)

print(acct.address)
print(private_key)



import psycopg2
import time
import requests
import json

from decimal import Decimal
from web3 import Web3

temp = "ethereum"

r = requests.get("https://ethgasstation.info/api/ethgasAPI.json?api-key=3502f4f4e22ce930b268de8fea9c5a25a9674a8e98c700225936665566d4")

gwei = r.json()["average"]/10.0

gaslimit = 0
if temp == "erc20":
    gaslimit = 100000
if temp == "ethereum":
    gaslimit = 30000


gaslimit = 27000

wei = Decimal(gwei) * (Decimal(10) ** 9)

print(gwei)
print(wei)

eth_amount = Web3.fromWei(wei * gaslimit,'ether')

print(eth_amount)



"""
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


qrcode = "12452"
userid = 24

temp = []
try:
    cur.execute("SELECT id FROM transactions WHERE (userid, couponid) = (%s, %s)", (userid, int(qrcode)))
except:
    conn.rollback()
else:
    temp = cur.fetchall()

print(temp)

"""











"""

import requests

temp = requests.get("http://localhost:3000/balance?address=0x69203F5c49cb15c03d60820113C12EaDA2b5Ed67&contract_address=0x549905519f9e06d55d7dfcd4d54817780f6b93e8")

print(temp.json())

"""

"""
import psycopg2

DB_NAME = "touchcon"
DB_USER = "touchcon"
DB_PASS = "touchcon"
DB_HOST = "localhost"
DB_PORT = "5432" 
conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
cur = conn.cursor()

for i in range(0, 5):
    userid = ""
    try:
        if i < 4:
            cur.execute("SELECT useri FROM users WHERE email = %s", ("ssar@naver.com",))
        else:
            cur.execute("SELECT userid FROM users WHERE email = %s", ("ssar@naver.com",))
    except:
        conn.rollback()
    else:
        userid = cur.fetchall()

    print(userid)


"""