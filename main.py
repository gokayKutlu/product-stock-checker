import requests
import json
import time

from discord import Webhook, RequestsWebhookAdapter
from bs4 import BeautifulSoup

# This determines the time in seconds we wait after each check.
DELAY = 3


def send_message(id, token, message, role_id, username):
    """
    Sends a message to the specified Discord channel in discord.json file
    """
    webhook = Webhook.partial(id, token, adapter=RequestsWebhookAdapter())
    webhook.send(f"{message} - <@&{role_id}>", username=username)


def check_existence(url, classname):
    """
    Checks if an HTML element with the given CSS selector exists. Returns true if it exists, otherwise returns false.
    """
    data = requests.get(url).text
    soup = BeautifulSoup(data, "lxml")

    class_content = soup.select(classname)
    if len(class_content) == 0:
        return False
    else:
        return True


def check_status_code(url, target_status_code):
    """
    Checks the status code of the page. Returns true if it matches our expectations in urls.json, otherwise returns false.
    """
    status_code = requests.get(url, allow_redirects=False).status_code

    if status_code == target_status_code:
        return True
    else:
        return False


def in_stock(product_name, website, url):
    """
    Here is what happens if the product is in stock.
    """
    message = f"{product_name} şimdi {website} sitesinde stokta!"
    print(message)

    with open("discord.json") as file:
            discord_data = json.load(file)

    webhook_id = discord_data[product_name]['webhook-id']
    webhook_token = discord_data[product_name]['webhook-token']
    role_id = discord_data[product_name]['role-id']
    role_name = discord_data[product_name]['role-name']

    send_message(webhook_id, webhook_token, f"{message} - {url}", role_id, role_name)


def out_of_stock(product_name, website):
    """
    Here is what happens if the product is NOT in stock.
    """
    print(f"{product_name} {website} sitesinde stokta yok.")


def error(exception):
    """
    Sends a message to the private channel that is being used to receive exceptions as messages by the developer.
    """
    with open("discord.json") as file:
            discord_data = json.load(file)

    webhook_id = discord_data['Error']['webhook-id']
    webhook_token = discord_data['Error']['webhook-token']
    role_id = discord_data['Error']['role-id']
    role_name = discord_data['Error']['role-name']

    print(str(exception))
    send_message(webhook_id, webhook_token, f"{exception}", role_id, role_name)


if __name__ == "__main__":
    """
    Main logic here.
    """
    urls_in_stock = []
    while True:
        try:
            with open("urls.json") as file:
                json_data = json.load(file)
            for row in json_data:
                website = row['website-name']
                mode = row['mode']

                if mode == "class-exists":
                    class_name = row['class']
                elif mode == "status-code":
                    target_status_code = row['target-status-code']

                for product in row['products']:
                    product_name = product['product-name']
                    url = product['url']

                    if mode == "class-exists":
                        instock = check_existence(url, class_name)
                    elif mode == "status-code":
                        instock = check_status_code(url, target_status_code)

                    if instock:
                        if url not in urls_in_stock:
                            in_stock(product_name, website, url)
                        urls_in_stock.append(url)
                    else:
                        if url in urls_in_stock:
                            urls_in_stock.remove(url)
                        else:
                            out_of_stock(product_name, website)
                    time.sleep(DELAY)
        except Exception as e:
            error(e)