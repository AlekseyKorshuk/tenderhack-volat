from dateutil.relativedelta import relativedelta
import datetime
from apps.app.models import Auctions
import pandas as pd
import requests
import json
import time

print("Parsing auctions.xlsx")
auctions = pd.read_excel("datasets/auctions.xlsx", sheet_name="Запрос1")
print("Parsing products.xlsx")
products = pd.read_excel("datasets/products.xlsx", sheet_name="Запрос1")
print("Parsing done")
with open('datasets/id_to_inn.txt', ) as f:
    id_to_inn = json.load(f)

datetime_format = "%d.%m.%Y %H:%M:%S"


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
            date = datetime.datetime.strptime(purchase['beginDate'], datetime_format)

            if now - relativedelta(months=12, days=now.day, hours=now.hour, minutes=now.minute,
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


def get_profiles_list():
    query_set = Auctions.objects.values('id')
    ids = []
    for profile in query_set:
        ids.append(profile['id'])
    return ids


def getProductByID(id):
    product = requests.get(
        f'https://old.zakupki.mos.ru/api/Cssp/Sku/GetEntity?id={str(id)}'
    ).json()
    image = 'https://zakupki.mos.ru/cms/Media/CompanyProfile/Images/logo_dummy.svg'
    if len(product['images']) != 0:
        image = f'https://zakupki.mos.ru/newapi/api/Core/Thumbnail/{product["images"][0]["fileStorage"]["id"]}/140/140'
    product_dict = {
        'id': str(id),
        'name': str(product['name']),
        'category': str(product['productionDirectoryName']),
        'minPrice': str(product['minPrice']) if product['minPrice'] is not None else "-",
        'maxPrice': str(product['maxPrice']) if product['maxPrice'] is not None else "-",
        'image': image
    }
    time.sleep(0.1)
    return product_dict


def getINNByID(id):
    return id_to_inn[str(id)]


def getCategoriesStats(id):
    user_auctions = auctions.loc[auctions['ИНН заказчика'] == int(getINNByID(id))]
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
    product_list = [1153130, 34879568, 19216453, 34751624]

    return product_list


def predictPurchases(inn):
    product_list = _predictPurchases(inn, auctions)
    result_list = []

    for item in product_list:
        temp_dict = {
            'date': item['date']
        }
        temp_dict.update(getProductByID(item['id']))
        result_list.append(temp_dict)

    return result_list


def _predictPurchases(inn, df):

    product_list = [
        {
            'id': 1153130,
            'date': "21.10.2021"
        },
        {
            'id': 18448990,
            'date': "21.10.2021"
        },
        {
            'id': 34879568,
            'date': "21.10.2021"
        },
        {
            'id': 19216453,
            'date': "21.10.2021"
        },
    ]

    return product_list