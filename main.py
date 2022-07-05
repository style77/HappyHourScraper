from bs4 import BeautifulSoup
import urllib

import discord
import time

URL = 'https://www.x-kom.pl/goracy-strzal'  # morele coming soon
WEBHOOK_URL = ''
INTERVAL = 1800  # 30min

url_contents = urllib.request.urlopen(URL).read()
soup = BeautifulSoup(url_contents, "html.parser")


def get_data(classes_info):
    data = {
        'sold_out': False
    }

    for find, text in classes_info['classes'].items():
        div = soup.find(classes_info['type'], {"class": text})

        z = str(div)
        z = z.replace(f'<span class="{text}">', '', 1)
        z = z.replace('</span>', '', 1)

        data[find] = z
    else:
        if data['discount_price'] == 'None':
            data['sold_out'] = True

        if data['sold_out']:
            data['image'] = data['soldout_image']
            del data['soldout_image']

        z = data['image'].replace(f'<img alt="{data["name"]}" class="sc-1tblmgq-1 fsblMa" loading="lazy" src="', '', 1)
        data['image'] = z.replace('"/>', '', 1)

    return data


def send_webhook(data):
    webhook = discord.Webhook.from_url(WEBHOOK_URL, adapter=discord.RequestsWebhookAdapter())
    e = discord.Embed(title="Gorący Strzał", description=f"[{data['name']}]({URL})")
    if data['sold_out']:
        e.add_field(name="Cena", value=f"Przed: Wyprzedano\nPo: Wyprzedano")
    else:
        e.add_field(name="Cena", value=f"Przed: {data['price']}\nPo: {data['discount_price']}")
    e.add_field(name="Oszczędasz", value=f"{data['discount']}")
    e.set_thumbnail(url=f"{data['image']}")
    webhook.send(embed=e)


xkom_classes = {
    "type": "span",
    "classes": {
        "name": "sc-1bb6kqq-10 bCbKaT m80syu-0 gQYnjo",
        "price": "sc-1bb6kqq-5 kZBxOq",
        "discount_price": "sc-1bb6kqq-4 dxMCAZ",
        "discount": "sc-18w91q-4 hzAGMh",
        "image": "sc-1tblmgq-0 sc-18w91q-5 duwgih sc-1tblmgq-3 iQxnQh",
        "soldout_image": "sc-1tblmgq-0 sc-18w91q-5 ewYAjT sc-1tblmgq-3 iQxnQh"
    }
}

while True:
    data = get_data(xkom_classes)

    with open('last.txt', 'r+') as f:
        if f.read() != data['name']:
            send_webhook(data)
            f.write(data['name'])
            print(f"Sent webhook with {data['name']}")
        else:
            print("Not sending, because last offer is current.")
    time.sleep(INTERVAL)

