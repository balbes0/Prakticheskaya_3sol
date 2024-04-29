from web3 import Web3
from web3.middleware import geth_poa_middleware
from contract_info import abi, address_contract
import re
from datetime import datetime

w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
contract = w3.eth.contract(address=address_contract, abi=abi)

def check_password_complexity(password):
    if len(password) >= 12 and re.search(r'[A-Z]', password) and re.search(r'[a-z]', password) and re.search(r'[0-9]', password):
        return True
    else:
        return False

def login():
    try:
        public_key = input("Введите публичный ключ: ")
        password = input("Введите пароль: ")
        w3.geth.personal.unlock_account(public_key, password)
        print("Авторизация проведена успешно")
        return public_key
    except Exception as e:
        print(f"Ошибка авторизации: {e}")
        return None
    
def register():
    try:
        password = input("Введите пароль: ")
        if check_password_complexity(password):
            account = w3.geth.personal.new_account(password)
            print(f"Публичный ключ: {account}. Данные были записаны в текстовый файл.")
            with open('info.txt', 'a', encoding="utf-8") as f:
                f.write('\nПубличный ключ: {}, пароль: {}'.format(account, password))
        else:
            print("Пароль не соответствует требованиям безопасноти! Придумайте новый.")
            register()
    except Exception as e:
        print(f"Ошибка при регистрации: {e}")

def createEstate(account):
    address = input("Введите название улицы: ")
    square = int(input("Введите номер улицы: "))
    type = int(input("Выберите тип недвижимости:\n1. Дом\n2. Квартира\n3. Промышленный объект\n4. Дача\nВыш выбор: "))
    if type < 1 or type > 4:
        type = input("Некорретный выбор! Повторите попытку: ")
    elif square <= 2:
        square = input("Номер улицы должен быть больше двух! Повторите попытку: ")
    elif len(address) < 2:
        address = input("Адрес слишком короткий! Повторите попытку: ")
    elif (type >= 1 and type <= 4) and square > 2 and len(address) >= 2:
        try:
            tx_hash = contract.functions.createEstate(address, square, type-1).transact({
                "from": account
            })
            print(f"Транзакция отправлена: {tx_hash.hex()}")
        except Exception as e:
            print(f"Ошибка при создании недвижимости: {e}")
 
def getEstates():
    try:
        estates = contract.functions.getEstates().call()
        if len(estates) > 0:
            for estate in estates:
                if estate[2] == 0:
                    estate_type = "Дом"
                elif estate[2] == 1:
                    estate_type = "Квартира"
                elif estate[2] == 2:
                    estate_type = "Промышленный объект"
                elif estate[2] == 3:
                    estate_type = "Дача"
                if estate[4] == True:
                    status = "Активный"
                elif estate[4] == False:
                    status = "Неактивный"
                print(f"Адрес: {estate[0]}, номер: {estate[1]}, тип: {estate_type}, создатель: {estate[3]}, статус: {status}, ID: {estate[5]}")
        else:
            print("Список недвижимостей пуст")
    except Exception as e:
        print(f"Ошибка при посмотре недвижимостей: {e}")

def createAd(account):
    try:
        GetMyEstates(account)
        price = int(input("Введите цену продажи: "))
        estateid = int(input("Введите ID недвижимости: "))
        date = int(datetime.now().strftime("%d%m%Y"))
        tx_hash = contract.functions.createAd(price, estateid, date).transact({
            "from": account
        })
        print(f"Транзакция отправлена: {tx_hash.hex()}")
    except Exception as e:
        print(f"Ошибка при создании объявления: {e}")

def GetMyEstates(account):
    try:
        estates = contract.functions.getEstates().call()
        myestates = []
        for estate in estates:
            if estate[3] == account:
                myestates.append(estate)
        if len(myestates) > 0:
            for estate in myestates:
                if estate[2] == 0:
                    type = "Дом"
                elif estate[2] == 1:
                    type = "Квартира"
                elif estate[2] == 2:
                    type = "Промышленный объект"
                elif estate[2] == 3:
                    type = "Дача"
                if estate[4] == True:
                    status = "Активный"
                elif estate[4] == False:
                    status = "Неактивный"
                print(f"Адрес: {estate[0]}, номер: {estate[1]}, тип: {type}, создатель: {estate[3]}, статус: {status}, ID: {estate[5]}")
        elif len(myestates) == 0:
            print("Список ваших недвижимостей пуст")
    except Exception as e:
        print(f"Ошибка при просмотре своих недвижимостей: {e}") 

def getAds():
    try:
        ads = contract.functions.getAds().call()
        if len(ads) > 0:
            for ad in ads:
                if ad[4] == "0x0000000000000000000000000000000000000000":
                    buyer = "Отсутствует"
                else:
                    buyer = ad[4]
                if ad[6] == 0:
                    status = "Открыт"
                elif ad[6] == 1:
                    status = "Закрыт"
            print(f"ID объявления: {ad[0]}, цена: {ad[1]}, ID недвижимости: {ad[2]}, создатель: {ad[3]}, покупатель: {buyer}, дата: {ad[5]}, статус: {status}")
        else:
            print("Объявлений на данный момент нет")
    except Exception as e:
        print(f"Ошибка при просмотре своих объявлений: {e}")

def updateEstateStatus(account):
    try:
        GetMyEstates(account)
        estates = contract.functions.getEstates().call()
        myestatesID = []
        for estate in estates:
            if estate[3] == account:
                myestatesID.append(estate[5])
        id = int(input("Введите ID недвижимости, который вы хотите изменить: "))
        if id in myestatesID:
            choice = input("Выберите действие:\n1. Изменить статус на <активное>\n2. Изменить статус на <неактивное>\nВыш выбор: ")
            match choice:
                case "1":
                    status = True
                case "2":
                    status = False

            contract.functions.updateEstateActive(id, status).transact({
                "from": account
            })
        else:
            print("Такой недвижимости не существует или вы не его владелец!")
             
    except Exception as e:
        print(f"Ошибка при изменени статуса недвижимости: {e}")

def GetMyAds(account):
    ads = contract.functions.getAds().call()
    myAds = []
    for ad in ads:
        if ad[3] == account:
            myAds.append(ad)
    if len(myAds) > 0:
        for ad in myAds:
            if ad[4] == "0x0000000000000000000000000000000000000000":
                buyer = "Отсутствует"
            else:
                buyer = ad[4]
            if ad[6] == 0:
                status = "Открыт"
            elif ad[6] == 1:
                status = "Закрыт"
            print(f"ID объявления: {ad[0]}, цена {ad[1]}, ID недвижимости: {ad[2]}, создатель: {ad[3]}, покупатель: {buyer}, дата: {ad[5]}, статус: {status}")
            return myAds
    else:
        print("У вас пока нет объявлений!")

def updateAdStatus(account):
    try:
        myAds = GetMyAds(account)
        myAdsID = []
        for myAd in myAds:
            myAdsID.append(myAd[3])
        id = int(input("Введите ID недвижимости, статус объявления которого вы хотите изменить: "))
        if account in myAdsID:
            choice = input("Выберите действией:\n1. Открыть объявление\n2. Закрыть объявление\nВыш выбор: ")
            match choice:
                case "1":
                    status = 0
                case "2":
                    status = 1
                case _:
                    print("Некорректный выбор!")
            contract.functions.updateAdType(id, status).transact({
                "from": account
            })
            print("Статус объявления был успешно изменен")
        else:
            print("Данных объявлений не существует или вы не его владелец!")
    except Exception as e:
        print(f"Ошибка при изменении статуса объявления: {e}")
    
def GetBalanceOnContract(account):
    try:
        balance = contract.functions.getBalance().call({
            "from": account
        })
        print(f"Баланс на контракте: {balance}")
        return balance
    except Exception as e:
        print(f"Ошибка при просмотре баланса: {e}")

def deposit(account):
    try:
        amount = int(input("Введите сумму пополнения: "))
        tx_hash = contract.functions.deposit().transact({
            "from": account,
            "value": amount
        })
        print(f"Транзакция отправлена: {tx_hash.hex()}, счет: {account}")
    except Exception as e:
        print(f"Ошибка при депозите средств на контракт: {e}")

def WithDraw(account):
    try:
        amount = int(input("Введите сумму вывода: "))
        tx_hash = contract.functions.withdraw(amount).transact({
            "from": account
        })
        print(f"Транзакция отправлена: {tx_hash.hex()}")
    except Exception as e:
        print(f"Ошибка при выводе средств: {e}")

def GetBalanceOnAccount(account):
    try:
        balance = w3.eth.get_balance(account)
        print(f"Баланс вашего аккаунта: {balance}")
    except Exception as e:
        print(f"Ошибка при выводе средств: {e}")

def BuyEstate(account):
    try:
        getAds()
        id = int(input("Введите ID недвижимости для покупки: "))
        tx_hash = contract.functions.buyEstate(id).transact({
            "from": account
        })
        print(f"Недвижимость было успешно куплена, транзакция отправлена: {tx_hash.hex()}")
    except Exception as e:
        print(f"Ошибка при покупке недвижимости: {e}")

if __name__ == '__main__':
    account = ""
    is_auth = False
    while True:
        if not is_auth:
            choice = input("1. Авторизация\n2. Регистрация\n3. Выход\nВыш выбор: ")
            match choice:
                case "1":
                    account = login()
                    if account != "" and account != None:
                        is_auth = True
                case "2":
                    register()
                case "3":
                    break
                case _:
                    print("Некорректный выбор!")
        elif is_auth:
            choice = input("Выберите действие:\n1. Пополнить баланс контракта\n2. Вывод средств с контракта\n3. Создать новую запись о недвижимости\n4. Создать объявление о продаже недвижимости\n5. Изменить статус недвижимости\n6. Изменить статус объявления\n7. Купить недвижимость\n8. Получить информацию о доступных недвижимостях\n9. Посмотреть объявления о текущих продажах недвижимости\n10. Посмотреть свой баланс на контракте\n11. Посмотреть свой баланс на аккаунте\n12. Посмотреть свои объявления\n13. Посмотреть свои недвижимости\n14. Посмотреть свой публичный адрес\n15. Выход из аккаунта\nВыш выбор: ")
            match choice:
                case "1":
                    deposit(account)
                case "2":
                    WithDraw(account)
                case "3":
                    createEstate(account)
                case "4":
                    createAd(account)
                case "5":
                    updateEstateStatus(account)
                case "6":
                    updateAdStatus(account)
                case "7":
                    BuyEstate(account)
                case "8":
                    getEstates()
                case "9":
                    getAds()
                case "10":
                    GetBalanceOnContract(account)
                case "11":
                    GetBalanceOnAccount(account)
                case "12":
                    GetMyAds(account)
                case "13":
                    GetMyEstates(account)
                case "14":
                    print(account)
                case "15":
                    account = ""
                    account = login()
                case _:
                    print("Некорректный выбор!")