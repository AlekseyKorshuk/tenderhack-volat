import requests


profile_url = 'https://zakupki.mos.ru/newapi/api/CompanyProfile/GetByCompanyId?companyId={USER_ID}'
pear_page = 1000
import time

def get_purchase(customer_id):
    items = []
    count = -1
    skip = 0
    while len(items) != count:
        response = requests.get(
            'https://old.zakupki.mos.ru/api/Cssp/Purchase/Query?queryDto={%22filter%22:{%22customerCompanyId%22:' + str(customer_id) + ',%22auctionSpecificFilter%22:{%22stateIdIn%22:[19000002,19000005,19000003,19000004,19000008]},%22needSpecificFilter%22:{},%22tenderSpecificFilter%22:{}},%22order%22:[{%22field%22:%22relevance%22,%22desc%22:true}],%22withCount%22:true,%22take%22:1000,%22skip%22:' + str(skip) + '}'
        ).json()
        count = response['count']
        items = items + response['items']
        skip += pear_page
    items_clear = []
    for item in items:
        if item['auctionId'] is not None:
            items_clear.append(item)
    return items_clear


def get_profile(customer_id):
    response = requests.get(
        profile_url.format(USER_ID=str(customer_id))
    ).json()
    response['items'] = get_purchase(customer_id)
    return response


def _get_purchase_detailed(auction_id):
    response = requests.get(
        f'https://zakupki.mos.ru/newapi/api/Auction/Get?auctionId={str(auction_id)}'
    ).json()

    return response


def get_purchases_detailed(purchases):

    items = []
    i = 0
    while i < len(purchases):
        print(i)
        items.append(
            _get_purchase_detailed(
                purchases[i]['auctionId']

            )
        )
        if 'message' in items[-1] and items[-1]['message'] == "Необходимо пройти проверку":
            items.pop()
            input("ERRRR")
        elif 'message' in items[-1]:
            print(items[-1]['message'])
        else:
            i += 1
        time.sleep(1)
    return items


def get_achievements(customer_id):

    response = requests.get(
        f'https://zakupki.mos.ru/newapi/api/CompanyProfile/GetAchievementsByCompanyId?companyId={str(customer_id)}'
    ).json()

    return response