import re
from bs4 import BeautifulSoup
import requests
import lxml
import os
import json
import urllib.parse
import pandas as pd
import time
from requests.sessions import session
import tqdm
import urllib
from multiprocessing import Pool


class Paper_downloader:
    def __init__(self, dst_folder):
        self.dst_folder = dst_folder
        self.headers = {
            'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
        }
        if not os.path.isdir(self.dst_folder):
            os.makedirs(self.dst_folder)

    def qurey(self, url, name):
        sess = requests.Session()
        basic_url = re.match(r"(.*//)?[^/]*", url).group(0)
        if basic_url.find("ieeexplore.ieee.org") != -1:
            doc_id = re.search(r'(?<=document/)\d+', url).group(0)
            doc_url = f"https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber={doc_id}"
            r = requests.get(doc_url, headers=self.headers)
            soup = BeautifulSoup(r.text, "lxml")
            pdf_url = soup.select_one("iframe")['src']
        elif basic_url.find("onlinelibrary.wiley.com") != -1:
            doc_id = re.search(r"(?<=doi/)[^/]*/[^/]*", url).group(0)
            pdf_url = f"https://onlinelibrary.wiley.com/doi/pdfdirect/{doc_id}"
        elif basic_url.find("dl.acm.org") != -1:
            r = requests.get(url, headers=self.headers)
            html = r.text
            # with open("tmp.html", "w", encoding='utf-8') as f:
            # f.write(html)
            soup = BeautifulSoup(html, 'lxml')
            pdf_url = basic_url + soup.select_one(".red")['href']
        print(pdf_url)
        r = sess.get(pdf_url, verify="cacert.pem")
        with open(self.dst_folder + os.sep + f"{name}.pdf", 'wb') as f2:
            f2.write(r.content)


if __name__ == "__main__":

    test_downloader = Paper_downloader(".\\test_folder")
    test_downloader.qurey(
        "https://onlinelibrary.wiley.com/doi/10.1111/cgf.12929", "test")
    # test_p = Pool(2)
    # test_p.starmap(test_downloader.qurey, [
    #     ["https://dl.acm.org/doi/10.1145/142750.142892", "1"],
    #     ["https://ieeexplore.ieee.org/document/1173157", "2"],
    #     ["https://dl.acm.org/doi/10.1145/142750.142892", "3"],
    #     ["https://ieeexplore.ieee.org/document/1173157", "4"],
    # ])
    # test_p.terminate()
    # test_p.join()
