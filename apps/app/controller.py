from dateutil.relativedelta import relativedelta
import datetime

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
        'price': 0
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
            if purchase['stateName'] == 'Активная':
                active['count'] += 1
                active['price'] += purchase['startPrice']

    return months, purchase_stats, total_spent, active

