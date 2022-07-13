from web3 import Web3
import psycopg2
import json

DB_NAME = "touchcon"
DB_USER = "touchcon"
DB_PASS = "touchcon"
DB_HOST = "localhost"
DB_PORT = "5432"
conn = psycopg2.connect(database=DB_NAME,user=DB_USER,password=DB_PASS,host=DB_HOST,port=DB_PORT)
cur = conn.cursor()


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

print(" adminwallets    ", temp_adminwallets)

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
