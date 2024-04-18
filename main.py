from web3 import Web3
from web3.middleware import geth_poa_middleware
from contractinfo import abi, contract_address

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

def main():
    print(f"Первый акк: {w3.eth.get_balance('0x1d0957FF516DC0C01f83D2c722A6c966750449ee')}\n"
          f"Второй акк: {w3.eth.get_balance('0x35E5323167651d0aC486Df1c3E626448aBb9Ed80')}\n"
          f"Третий акк: {w3.eth.get_balance('0x82A384050DD27b5239eA08400F7934Eb2869AC57')}\n"
          f"Четвертый акк: {w3.eth.get_balance('0xc55384a6Db1d37f57B720B69630E003b1fB58C6F')}\n"
          f"Пятый акк: {w3.eth.get_balance('0x7117897f9C9F402B0a48D06Ab8A29f0e98d9CcE1')}\n")

if __name__ == '__main__':
    main()