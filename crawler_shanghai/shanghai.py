import pymongo
import json
import urllib.parse
from bs4 import BeautifulSoup
import requests
import lxml
from tqdm import tqdm
import re
import pymongo
import datetime
from multiprocessing import Pool
from threading import Thread
import html5lib

mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
dbClient = mongoClient["shanghai_help"]
db = dbClient['db']


class pageScraper:
    def __init__(self):
        self.base_url = "https://www.daohouer.com/index.php?page={}&hdid=&cjtype=&address=#"
        self.basic_header = {
            'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
        }
        self.table_keys = ['id', 'time', 'emergency',
                           'category', 'abstract', 'location']

    def get_page(self, page_index):
        # print(page_index)
        page_url = self.base_url.format(page_index)
        r = requests.get(page_url, headers=self.basic_header)
        soup = BeautifulSoup(r.content, 'html5lib')
        table = soup.select("#table_id_example > tbody")[0]

        result = []
        for item in table.select("tr"):
            tds = item.select('td')
            data_item = {}
            for i in range(len(self.table_keys)):
                if i == 1:
                    data_item[self.table_keys[i]] = '2022-' + \
                        re.sub(r'\s+', 'T', tds[1].get_text().strip())
                else:
                    data_item[self.table_keys[i]] = tds[i].get_text().strip()
            data_item['status'] = tds[1].select('img')[0].get('src')[-5]
            # print() # id
            # print('2022-' + re.sub(r'\s+', 'T', tds[1].get_text().strip())) # date
            # print(tds[2].get_text()) # emergency
            # print(tds[3].get_text()) # category
            # print(tds[4].get_text()) # abstract
            # print(tds[5].get_text()) # location

            page_try = [0, 1, -1, 2, -2]
            for i in page_try:
                content_url = self.base_url.format(
                    page_index + i) + "#open-modal" + data_item['id']
                r = requests.get(content_url)
                content_soup = BeautifulSoup(r.content, 'lxml')
                content_div = content_soup.select(
                    "#open-modal{} > div".format(data_item['id']))
                if len(content_div) > 0:
                    content_div = content_div[0]
                    start_flag = False
                    acc_str = ""
                    content_strs = []
                    for i in content_div.children:
                        if (i.name == 'h4'):
                            start_flag = True
                        if start_flag and i.name == None:
                            acc_str += i.strip()
                        if start_flag and i.name == 'br':
                            content_strs.append(acc_str)
                            acc_str = ""
                    if acc_str != '':
                        content_strs.append(acc_str)
                    if len(content_strs) > 0:
                        data_item['content'] = content_strs[0]
                    for i in content_strs[1:]:
                        if re.match(r"^联系人", i):
                            data_item['person'] = i[4:]
                        if re.match(r"^联系电话", i):
                            data_item['phone'] = i[5:]
                        if re.match(r"^联系地址", i):
                            data_item['address'] = i[5:]
                    break
            # print(data_item)
            result.append(data_item)

        now = datetime.datetime.now(datetime.timezone.utc)
        for i in result:
            i['crawl_time'] = now
            db.find_one_and_update(
                {"id": i['id']},
                {
                    "$set": i
                },
                upsert=True
            )
        print("...", page_index)
        return result


def update_recent():
    scraper = pageScraper()
    scraper_pool = Pool(8)
    scraper_pool.map(scraper.get_page, list(range(1, 10)))
    scraper_pool.terminate()
    scraper_pool.join()


def update_all():
    scraper = pageScraper()
    r = requests.get("https://www.daohouer.com/index.php",
                     headers=scraper.basic_header)
    soup = BeautifulSoup(r.content, 'html5lib')
    page = soup.select(
        "body > div > div.help_info__PSQ5C > div > div:nth-child(8) > div:nth-child(3)")
    if len(page) > 0:
        mr = re.search(r'共\s*(\d+)\s*页', page[0].get_text())
        if mr:
            page_number = int(mr.group(1))
            scraper_pool = Pool(8)
            scraper_pool.map(scraper.get_page, list(range(1, page_number + 1)))
            scraper_pool.terminate()
            scraper_pool.join()
            return
    print("error")


if __name__ == "__main__":
    scraper = pageScraper()
    # scraper.get_page(1)
    update_all()
