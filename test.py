import requests
import json


class Proxies:
    proxies = []
    index = 0

    def __init__(self):
        response = requests.get(
            'https://proxylist.geonode.com/api/proxy-list?limit=50&page=1&sort_by=speed&sort_type=asc&speed=fast&protocols=socks4'
        )
        self.proxies = response.json()['data']

    def get(self):
        proxy = self.proxies[self.index % len(self.proxies)]
        self.index += 1
        return {
            'http': f"{proxy['protocols'][0]}://{proxy['ip']}:{proxy['port']}",
            'https': f"{proxy['protocols'][0]}://{proxy['ip']}:{proxy['port']}",
        }




proxies = Proxies()

print(len(proxies.proxies))

for i in range(1000):

    while True:
        try:
            proxy = proxies.get()
            print(proxy)
            response = requests.get('https://zakupki.mos.ru/newapi/api/Auction/Get?auctionId=9146382', proxies=proxy)
            break
        except:
            pass

    if "message" in response.json() and response.json()['message'] == "Необходимо пройти проверку":
        print(i, "Необходимо пройти проверку")
    else:
        print("DONE")


