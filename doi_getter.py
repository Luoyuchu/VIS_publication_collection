import pymongo
import json
import urllib.parse
from bs4 import BeautifulSoup
import requests
import lxml


class Doi_getter:
    def __init__(self):
        self.headers = {
            'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
        }
        self.proxies = {
            'http': "socks5://127.0.0.1:7890",
            'https': "socks5://127.0.0.1:7890",
        }


class Doi_getter_dblp(Doi_getter):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://dblp.org/search/publ/api?format=json&q='

    def query(self, title, authors, year, venue):
        q_url = self.base_url + urllib.parse.quote(title)
        print(q_url)
        r = requests.get(q_url)
        print(r.content)


a = Doi_getter_dblp().query("Visual Cascade Analytics of Large-scale Spatiotemporal Data",
                            ["Zikun Deng", "Di Weng"], 2021, "VIS")
