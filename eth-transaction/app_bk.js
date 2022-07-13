const express = require('express')
fs = require('fs');
const app = express()
require('dotenv').config()
const port = 3000

const Web3 = require('web3');
const web3 = new Web3(new Web3.providers.HttpProvider("https://mainnet.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161"));

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
  var amount = web3.utils.toHex(req.query.amount);
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
        "gasPrice": web3.utils.toHex(2 * 1e9),
        "gasLimit": web3.utils.toHex(210000),
        "to": GBC_Contract_Address,
        "value": "0x0",
        "data": contract.methods.transfer(toAddress, amount).encodeABI(),
        "nonce": web3.utils.toHex(count)
      }

      console.log("rawTransaction", rawTransaction);

      var transaction = new Tx(rawTransaction)
      transaction.sign(privateKey)

      web3.eth.sendSignedTransaction('0x' + transaction.serialize().toString('hex'), function (err, hash) {
        if (!err) {
          console.log(hash);
        } else {
          console.log(err.message);
          res.setHeader('Content-Type', 'application/json');
          res.end(JSON.stringify({ "code": 500, "message": err.message, "data": rawTransaction }));
        }
      });
    })


  } catch (e) {
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ "code": 500, "message": e.message }));
  }
});

app.listen(port, () => {
  console.log(`app listening at http://localhost:${port}`)
});