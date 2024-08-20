import requests
from bs4 import BeautifulSoup
import json
from requests.exceptions import RequestException


filename = 'proxylist.jdproxies'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' \
             '(KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'


def create_proxy_record(address, port, type, enabled):
    proxy_record = dict()
    proxy_preferences = dict()
    proxy_preferences["username"] = None
    proxy_preferences["password"] = None
    proxy_preferences["port"] = port
    proxy_preferences["address"] = address
    proxy_preferences["type"] = type
    proxy_preferences['preferNativeImplementation'] = False
    proxy_preferences['resolveHostName'] = False
    proxy_preferences['connectMethodPreferred'] = False
    proxy_record['proxy'] = proxy_preferences
    proxy_record['rangeRequestsSupported'] = True
    proxy_record['filter'] = None
    proxy_record['pac'] = False
    proxy_record['reconnectSupported'] = False
    proxy_record['enabled'] = enabled
    json_data = proxy_record
    return json_data

def check_socks_proxy(proxy_host, proxy_port, timeout=5):
    # Define the proxy in the format required by the requests library
    proxy = {
        'http': f'socks4://{proxy_host}:{proxy_port}',
        'https': f'socks4://{proxy_host}:{proxy_port}'
    }

    try:
        # Attempt to make a request through the proxy to check if it's active
        response = requests.get('http://httpbin.org/ip', proxies=proxy, timeout=timeout)
        if response.status_code == 200:
            return True
            # print(f"Proxy {proxy_host}:{proxy_port} is active.")
            # print("Response IP:", response.json()["origin"])
        else:
            # print(f"Proxy {proxy_host}:{proxy_port} is inactive.")
            return False
    except RequestException as e:
        # print(f"Proxy {proxy_host}:{proxy_port} is inactive. Error: {e}")
            return False



def create_json_structure(proxies):
    proxylist_json_structure = dict()
    proxylist_json_structure["customProxyList"] = proxies
    return proxylist_json_structure


def get_proxies_from_socks_proxy_net():
    proxy_site_url = 'https://socks-proxy.net/#list'
    res = requests.get(proxy_site_url, headers={'User-Agent': user_agent})
    soup = BeautifulSoup(res.text, "lxml")
    proxy_list = list()
    for items in soup.select("tbody tr"):
        proxy_definition = []
        for item in items.select("td")[:8]:
            proxy_definition.append(item.text)
        if check_socks_proxy(proxy_definition[0],proxy_definition[1]):
            print(f"✅ Proxy: {proxy_definition[0]}:{proxy_definition[1]} is active.")
            proxy_list.append(
                create_proxy_record(
                    type=proxy_definition[4].upper(), address=proxy_definition[0], port=int(proxy_definition[1]), enabled=True
                )
            )
        else:
            print(f"❌ Proxy: {proxy_definition[0]}:{proxy_definition[1]} is inactive.")
        
    return proxy_list

proxy_list = list([create_proxy_record(type="NONE", address=None, port=80, enabled=True)])
proxy_list = proxy_list + get_proxies_from_socks_proxy_net()
json_output = create_json_structure(proxy_list)
with open(filename, 'w') as f:
    json.dump(json_output, f, indent=2)
