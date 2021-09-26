import requests

profile_url = 'https://zakupki.mos.ru/newapi/api/CompanyProfile/GetByCompanyId?companyId={USER_ID}'
pear_page = 1000
import time

def get_purchase_customer(customer_id):
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

def get_purchase_supplier(customer_id):
    items = []
    count = -1
    skip = 0
    while len(items) != count:
        response = requests.get(
            'https://zakupki.mos.ru/newapi/api/Contract/Query?queryFilter={"filter":{"number":{"contains":true},"type":{},"beginEndDate":{},"conclusionDate":{},"conclusionReason":{},"customerKeyword":{"contains":true},"customerRegionTreePathId":{},"federalLaw":{},"offer":{},"supplierId":' + str(customer_id) + ',"offerRegisterNumber":{"contains":true},"okpdTreePathId":{},"placingOrder":{},"productionTreePathId":{},"registerNumber":{"contains":true},"rubSum":{},"sku":{},"state":{},"subject":{"contains":true},"supplierKeyword":{"contains":true},"purchaseRegisterNumber":{"contains":true}},"order":[{"field":"relevance","desc":true}],"withCount":true,"take":1000,"skip":' + str(skip) + '}'
        )
        # print(response.text)
        response = response.json()
        count = response['count']
        items = items + response['items']
        skip += pear_page
    items_clear = []
    for item in items:
        if item['auctionId'] is not None:
            items_clear.append(item)
    return items_clear


def get_profile(user_id):

    response = requests.get(
        'https://zakupki.mos.ru/newapi/api/CompanyProfile/GetByCompanyId?companyId={USER_ID}'.format(USER_ID=str(user_id))
    ).json()

    response_temp = requests.get(f'https://zakupki.mos.ru/newapi/api/Company/GetIdBySupplierId?supplierId={user_id}')
    is_supplier = False
    result_user_id = None
    if response_temp.status_code != 204:
        is_supplier = True
        result_user_id = int(response_temp.text)
    else:
        response_temp = requests.get(f'https://zakupki.mos.ru/newapi/api/Company/GetIdByCustomerId?customerId={user_id}')
        if response_temp.status_code != 204:
          result_user_id = int(response_temp.text)
        else:
          if response['company']['supplierId'] is not None:
            user_id = response['company']['supplierId']
            is_supplier = True
          elif response['company']['customerId'] is not None:
            result_user_id = response['company']['customerId']

    if not is_supplier:
        response['items'] = get_purchase_customer(user_id)
    else:
        response['items'] = get_purchase_supplier(user_id)

    response['isSupplier'] = is_supplier
    return response, is_supplier, result_user_id


def _get_purchase_detailed(auction_id):
    response = requests.get(
        f'https://zakupki.mos.ru/newapi/api/Auction/Get?auctionId={str(auction_id)}'
    ).json()

    return response


def get_purchases_detailed(purchases, data):
    items = []
    i = 0
    if data is not None:
        items = data['data']
        i = len(items)

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