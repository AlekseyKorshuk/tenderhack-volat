from dateutil.relativedelta import relativedelta as reldelta
import datetime
from apps.app.models import Auctions
import pandas as pd
import requests
import json
import time
from ml.controller import *

auctions = None
products = None

# print("Parsing auctions.xlsx")
# auctions = pd.read_excel("datasets/auctions.xlsx", sheet_name="Запрос1", converters={'ИНН заказчика': str, 'ИНН поставщика': str})
# print("Parsing done")
# print("Parsing products.xlsx")
# products = pd.read_excel("datasets/products.xlsx", sheet_name="Запрос1")
# print("Parsing done")
#
# print("Preloading")
# Preloaded().load_everything(auctions, products)
# print("Preloading done")


with open('datasets/id_to_inn.txt', ) as f:
    id_to_inn = json.load(f)

datetime_format = "%Y-%m-%d %H:%M:%S.%f"
datetime_format_api = "%d.%m.%Y %H:%M:%S"
datetime_predict_format = "%d.%m.%Y"


def get_purchase_stats(profile):
    now = datetime.datetime.now()

    months_dict = {
        9: "Сентябрь",
        10: "Октябрь",
        11: "Ноябрь",
        12: "Декабрь",
        1: "Январь",
        2: "Февраль",
        3: "Март",
        4: "Апрель",
        5: "Май",
        6: "Июнь",
        7: "Июль",
        8: "Август",
    }

    months = []
    purchase_stats = {}
    for i in range(now.month - 1, now.month - 13, -1):
        months.append(
            months_dict[i % 12 + 1]
        )
        purchase_stats[i % 12 + 1] = {
            'count': 0,
            'end_price': 0.0,
            'start_price': 0.0
        }

    months.reverse()
    total_spent = 0
    active = {
        'count': 0,
        'price': 0,
        'price_display': ""
    }

    for purchase in profile['items']:
        if purchase['beginDate']:
            date = datetime.datetime.strptime(purchase['beginDate'], datetime_format_api)

            if now - reldelta(months=12, days=now.day, hours=now.hour, minutes=now.minute,
                                   seconds=now.second) <= date <= now:
                purchase_stats[date.month]['count'] += 1
                if 'auctionCurrentPrice' in purchase and purchase['auctionCurrentPrice']:
                    purchase_stats[date.month]['end_price'] += purchase['auctionCurrentPrice']
                    purchase_stats[date.month]['start_price'] += purchase['startPrice']
                    total_spent += purchase['auctionCurrentPrice']
            if purchase['stateName'] == 'Активная':
                active['count'] += 1
                active['price'] += purchase['startPrice']

    active['price_display'] = f"{int(active['price']):,}".replace(',', ' ')
    return months, purchase_stats, int(total_spent), active


def get_contract_stats(profile):
    now = datetime.datetime.now()

    months_dict = {
        9: "Сентябрь",
        10: "Октябрь",
        11: "Ноябрь",
        12: "Декабрь",
        1: "Январь",
        2: "Февраль",
        3: "Март",
        4: "Апрель",
        5: "Май",
        6: "Июнь",
        7: "Июль",
        8: "Август",
    }

    months = []
    purchase_stats = {}
    for i in range(now.month - 1, now.month - 13, -1):
        months.append(
            months_dict[i % 12 + 1]
        )
        purchase_stats[i % 12 + 1] = {
            'count': 0,
            'price': 0.0,
        }

    months.reverse()
    total_spent = 0
    active = {
        'count': 0,
        'price': 0,
        'price_display': ""
    }

    for purchase in profile['items']:
        if purchase['conclusionDate']:
            date = datetime.datetime.strptime(purchase['conclusionDate'], datetime_format_api)
            if now - reldelta(months=12, days=now.day, hours=now.hour, minutes=now.minute,
                                   seconds=now.second) <= date <= now:
                purchase_stats[date.month]['count'] += 1
                purchase_stats[date.month]['price'] += purchase['rubSum']
                total_spent += purchase['rubSum']
            if purchase['state']['name'] == 'Заключен':
                active['count'] += 1
                active['price'] += purchase['rubSum']

    active['price_display'] = f"{int(active['price']):,}".replace(',', ' ')
    return months, purchase_stats, int(total_spent), active


def get_profiles_list():
    query_set = Auctions.objects.values('id')
    ids = []
    for profile in query_set:
        ids.append(profile['id'])
    return ids


def getProductByID(id):
    product = requests.get(
        f'https://old.zakupki.mos.ru/api/Cssp/Sku/GetEntity?id={str(id)}'
    )
    try:
        product = product.json()
        image = 'https://zakupki.mos.ru/cms/Media/CompanyProfile/Images/logo_dummy.svg'
        if len(product['images']) != 0:
            if product["images"][0]["fileStorage"]["id"] > 0:
                image = f'https://zakupki.mos.ru/newapi/api/Core/Thumbnail/{product["images"][0]["fileStorage"]["id"]}/140/140'
        product_dict = {
            'id': str(id),
            'name': str(product['name']),
            'category': str(product['productionDirectoryName']),
            'minPrice': str(product['minPrice']) if product['minPrice'] is not None else "-",
            'maxPrice': str(product['maxPrice']) if product['maxPrice'] is not None else "-",
            'image': image
        }
    except:
        product = None
        for index, row in (products.loc[products['ID СТЕ'] == int(id)]).iterrows():
            product = row
        product_dict = {
            'id': str(id),
            'name': product['Название СТЕ'],
            'category': product['Категория'],
            'minPrice': '-',
            'maxPrice': '-',
            'image': 'https://zakupki.mos.ru/cms/Media/CompanyProfile/Images/logo_dummy.svg'
        }

    time.sleep(0.1)
    return product_dict


def getINNByProfile(profile):
    return str(profile['company']['inn'])


def getCategoriesStats(id, is_supplier, inn):
    print('ИНН заказчика' if not is_supplier else 'ИНН поставщика')
    user_auctions = auctions.loc[auctions['ИНН заказчика' if not is_supplier else 'ИНН поставщика'] == str(inn)]
    products_dict = {}
    for index, row in user_auctions.iterrows():
        products_list = row['СТЕ']
        products_list = json.loads(products_list)
        for item in products_list:
            if item['Id'] is None:
                continue
            if item['Id'] not in products_dict:
                products_dict[str(item['Id'])] = int(item['Quantity'])
            else:
                products_dict[str(item['Id'])] += int(item['Quantity'])

    categories_stats = {}
    total_sum = 0
    for product_id in products_dict.keys():
        product = products.loc[products['ID СТЕ'] == int(product_id)]
        for index, row in product.iterrows():
            category = str(row['Категория'])
            if category not in categories_stats:
                categories_stats[category] = products_dict[product_id]
            else:
                categories_stats[category] += products_dict[product_id]
            total_sum += products_dict[product_id]

    categories_stats = dict(sorted(categories_stats.items(), key=lambda x: x[1], reverse=True)[:5])

    titles = []
    values = []
    result_list = []

    for category in categories_stats.keys():
        titles.append(category)
        values.append(int(categories_stats[category] / total_sum * 100))

    titles.append("Остальное")
    values.append(int(100 - sum(values)))

    for i in range(len(titles)):
        result_list.append(
            {
                'title': titles[i],
                'value': values[i]
            }
        )
    return {
        'categories_stats': {
            'titles': titles,
            'values': values,
            'list': result_list
        }
    }


def predictSuggestions(inn):
    product_list = _predictSuggestions(inn, auctions)
    result_list = []

    for id in product_list:
        result_list.append(getProductByID(id))

    return result_list


def _predictSuggestions(inn, df):
    product_list = items_user_did_not_try(str(inn), auctions, products)
    print(product_list)
    return product_list



def predictPurchases(inn):
    product_dict = _predictPurchases(str(inn), auctions)

    result_list = []

    for key in product_dict.keys():
        cat_period, demiseason_len, season_quantity, current_quantity, \
        last_buy, last_item, is_enough, next_buy = product_dict[key]
        temp_dict = {
            'period': cat_period,
            'date': datetime.datetime(next_buy.year, next_buy.month, next_buy.day).strftime("%d.%m.%Y"),
        }
        temp_dict.update(getProductByID(last_item))
        result_list.append(temp_dict)

    return result_list


def _predictPurchases(inn, df):
    product_dict = periods_info(inn, df)

    today = datetime.date.today()
    product_dict = sorted(product_dict.items(), key=lambda k: k[-1])
    product_dict_clear = {}
    for item in product_dict:
        if item[1][-1] >= today:
            product_dict_clear[item[0]] = item[1]

    return product_dict_clear


def start():
    global auctions, products

    if auctions is None:
        print("Parsing auctions.xlsx")
        auctions = pd.read_excel("datasets/auctions.xlsx", sheet_name="Запрос1")
        print("Parsing done")

    # if products is None:
    #     print("Parsing products.xlsx")
    #     products = pd.read_excel("datasets/products.xlsx", sheet_name="Запрос1")
    #     print("Parsing done")


def getNotifications(predictions, is_supplier):

    if not is_supplier:
        title = 'Запланируйте закупку на {DATE}'
    else:
        title = 'Подготовьтесь к продажам с {DATE}'

    notifications = []
    period = 7
    now = datetime.datetime.now()
    for item in predictions:
        try:
            date = datetime.datetime.strptime(str(item['date']), datetime_predict_format)
        except:
            date = datetime.datetime.strptime(str(item['date']), '%Y-%m-%d')
        delta = (date - now).days
        if delta <= period:
            notifications.append(
                {
                    'title': title.format(DATE=item["date"]),
                    'name': item['name'],
                    'date': item['date'],
                    'delta': period - delta
                }
            )

    notifications = sorted(notifications, key=lambda k: k['delta'])
    notifications = notifications[:min(len(notifications), 4)]
    return notifications


def predictTrand(inn):
    result_list = [
        {
            'name': 'Название категории',
            'quantity': 100,
            'sum': 100500,
            'trend': 32.8,
            'date': '21.10.2002',
        }
    ]

    return result_list
