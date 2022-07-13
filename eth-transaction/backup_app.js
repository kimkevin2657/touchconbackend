const express = require('express')
var ethers = require('ethers');
var crypto = require('crypto');
var axios = require('axios');

fs = require('fs');
const app = express()
require('dotenv').config()
const port = 3000

const Web3 = require('web3');
const web3 = new Web3(new Web3.providers.HttpProvider("https://mainnet.infura.io/v3/d3636135d8fd41a68bc2348d7ee7a72b"));

console.log("process.env.NODE_ENV", process.env.NODE_ENV);

if (process.env.NODE_ENV == "dev") {
  var abi = fs.readFileSync('./erc20_abi.json', 'utf-8');
} else {
  var abi = fs.readFileSync('/var/www/erc20_api/erc20_abi.json', 'utf-8');
}

var GBC_Contract_Address = "0xb7447364ef42cff09425a0feae703ee0b72647f9";
var contract = new web3.eth.Contract(JSON.parse(abi), GBC_Contract_Address);

app.get('/', (req, res) => {
  try {
    if (req.query !== {} && req.query.address) {
      var walletAddress = req.query.address;

      web3.eth.getBalance(walletAddress).then(function (eth_balance) {
        // console.log("eth_balance",Web3.utils.fromWei(eth_balance.toString(), 'ether'));

        contract.methods.balanceOf(walletAddress).call().then(function (balance) {
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({
            "code": 200, "message": "Balance retrived.", data: {
              balance: Web3.utils.fromWei(balance.toString(), 'ether'),
              eth_balance: Web3.utils.fromWei(eth_balance.toString(), 'ether'),
            }
          }));
        });
      })


    } else {
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ "code": 500, "message": "Invalid request." }));
    }

  } catch (e) {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ "code": 500, "message": e.message }));
  }
});

app.get('/addNewAddress', (req, res) => {
  try {
    if (req.headers !== {} && req.headers.authtoken && req.headers.authtoken == "fDd024823e04Aa328f6c7917321B331147dA8d2b") {




      var id = crypto.randomBytes(32).toString('hex');
      var privateKey = "0x" + id;

      var wallet = new ethers.Wallet(privateKey);
      res.setHeader('Content-Type', 'application/json');
      res.send(JSON.stringify({
        "code": 200,
        "message": "New address generated.",
        data: {
          "privateKey": id,
          "address": wallet.address
        }
      }));

    } else {
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ "code": 500, "message": "Invalid Token." }));
    }
  } catch (e) {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ "code": 500, "message": e.message }));
  }
});

app.get('/transactions', (req, res) => {
  try {
    var filter = {}
    var pastTransferEvents = contract.getPastEvents('Transfer', filter, { fromBlock: 0, toBlock: 'latest' })
    pastTransferEvents.then(events => {
      res.setHeader('Content-Type', 'application/json');
      res.end(JSON.stringify({ "code": 200, "message": "Transaction History.", data: events }));
    })
  } catch (e) {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ "code": 500, "message": e.message }));
  }
});

app.get('/send-transaction', (req, res) => {
  var Tx = require("ethereumjs-tx").Transaction;

  var myAddress = req.query.from_address;
  var toAddress = req.query.to_address;
  var amount = parseInt(req.query.amount);

  var config = {
    method: 'get',
    url: 'https://ethgasstation.info/api/ethgasAPI.json?api-key=3502f4f4e22ce930b268de8fea9c5a25a9674a8e98c700225936665566d4',
    headers: {}
  };

  axios(config)
    .then(function (response) {

      // var gasPrice = web3.utils.toHex(20 * 1e9);
      // var gasLimit = web3.utils.toHex(1000000);

      var gasPrice = web3.utils.toHex(response.data.average / 10 * 1e9);
      var gasLimit = web3.utils.toHex(100000);
      //var gasLimit = web3.utils.toHex(50000);



      console.log("gas * price + value", gasPrice * gasLimit);

      console.log("wei to eth", web3.utils.fromWei((gasPrice * gasLimit).toString(), 'ether'))

      // var amount = req.query.amount;
      // "2faa3d1a6e3077928380a2c15a61692b458b5ca8b334c2e0f18d699e6f0e8c34"
      var privateKey = Buffer.from(req.query.privateKey, 'hex');

      console.log("amount", amount);

      // get transaction count, later will used as nonce

      try {

        web3.eth.getTransactionCount(myAddress).then(function (v) {
          count = v

          var contract = new web3.eth.Contract(JSON.parse(abi), GBC_Contract_Address, { from: myAddress })

          var rawTransaction = {
            "from": myAddress,
            "gasPrice": gasPrice,
            "gasLimit": gasLimit,
            "to": GBC_Contract_Address,
            "value": "0x0",
            "data": contract.methods.transfer(toAddress, amount).encodeABI(),
            "nonce": web3.utils.toHex(count),
            "chainId": 0x01
          }

          console.log("rawTransaction", rawTransaction);

          const privateKey1Buffer = Buffer.from(privateKey, 'hex')

          var transaction = new Tx(rawTransaction)
          transaction.sign(privateKey1Buffer)

          console.log("transaction.serialize().toString('hex')", transaction.serialize().toString('hex'));

          web3.eth.sendSignedTransaction('0x' + transaction.serialize().toString('hex'), function (err, hash) {
            if (!err) {
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({
                //"code": 200, "message": "Transaction succefully", "data": {
		 "code": 200, "message": "트랜잭션 성공하였습니다", "data": {
                  "tx": hash,
                  "raw": rawTransaction,
                  "gas_fees_in_eth": web3.utils.fromWei((gasPrice * gasLimit).toString(), 'ether')
                }
              }));
            } else {
              console.log(err.message);
              res.setHeader('Content-Type', 'application/json');
              res.end(JSON.stringify({
               // "code": 500, "message": err.message, "data": rawTransaction,
		"code": 500, "message": "이더리움이 부족합니다", "data": rawTransaction,
                "gas_fees_in_eth": web3.utils.fromWei((gasPrice * gasLimit).toString(), 'ether')
              }));
            }
          });
        })


      } catch (e) {
        res.setHeader('Content-Type', 'application/json');
        res.end(JSON.stringify({ "code": 500, "message": e.message }));
      }

    });
});

app.listen(port, () => {
  console.log(`app listening at http://localhost:${port}`)
});
