import re
from bs4 import BeautifulSoup
import requests
import lxml
import os
import json
import urllib.parse
import pandas as pd
import time
import tqdm


class Google_scholar_scaper:
    def __init__(self):
        self.headers = {
            'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582",
            "Cookie":
            "CONSENT=YES+SE.zh-CN+V15+BX; GSP=LM=1620720736:S=gad5vCw-zhBdkVfF; ANID=AHWqTUnZE6t0D_2VSDA4nKw2CQvZJPBCuLlaZCxXgIBJ-mK4E6ecXxjxBLxuhoyS; HSID=AegSa6cynsFLs4vmx; SSID=AVsybvSBkQGLyCe_g; APISID=nT2GNOo2F7x8GrZH/Axjx6IGPApgVVpoSb; SAPISID=Vc8ihJCphpMmzVoq/AuJHuMNJzvN0afAB8; __Secure-3PAPISID=Vc8ihJCphpMmzVoq/AuJHuMNJzvN0afAB8; OGPC=19022591-1:; __Secure-1PAPISID=Vc8ihJCphpMmzVoq/AuJHuMNJzvN0afAB8; SEARCH_SAMESITE=CgQIqpMB; SID=BAhvIbY6TICfJgRpXNJqZeVfeh_pKX2pQJtC_0Op-oKA1gzbXuS-ZhwmDKwTbpOx98wWjw.; __Secure-1PSID=BAhvIbY6TICfJgRpXNJqZeVfeh_pKX2pQJtC_0Op-oKA1gzbkhEpwPKoLMjI-5lfs7uXwQ.; __Secure-3PSID=BAhvIbY6TICfJgRpXNJqZeVfeh_pKX2pQJtC_0Op-oKA1gzbnZsVVhs7p_CRSDu5wmIZYQ.; NID=221=hfrbAgsgvMMUPULlRjkZpBE55rpSiLE1D01B5xk1mDQK3joRuHINMkwd9GSP4f4VGLaxj7TU_uljRHFsKdbqILCEC8SaObSkRIdQtQZri6LmDOIMO-yIxSYvTSfDmeFC7GNWtsn7w-XpaOJrLElLPgG12HODWZe8yV0nXUUQaeh0-FPVZsXVBG1RvP_SYHIn3VkzPoFV833I-XTnHIr1jV30dAHcLTZQcGEEdSklY5BZgoO7QoWFea997iEEHmczXdXlsA0YvhnyzsFpfgA6zmhoRnL_RDd16mAIfQ; 1P_JAR=2021-08-21-09; __Secure-1PSIDCC=AJi4QfEguhE6al1psfUW_6rcvi-rie1ALE-eTcWm95PtxkVWR1gwhSaFHItPtBfebVfCoVBkKw; SIDCC=AJi4QfE4M_TILehdAjiAqYH5cuKZByKX5W2hjVFkUIfG5ofpTOpr5wsv6CVOTlq1zf2PXJcF5c0; __Secure-3PSIDCC=AJi4QfHBaf3bEtBiYRMX0rYl5ZNYbcf0yF9KMSMkjcaebGOvLBnFNmNla6hvObnT-UUJ2lHytwA"
        }
        self.proxies = {
            'http': "socks5://127.0.0.1:7890",
            'https': "socks5://127.0.0.1:7890",
        }

    def query(self, title="", author="", publication="", clbk=lambda x: None):
        q = urllib.parse.quote
        query_url = f"&as_q={q(title)}&as_publication={q(publication)}&as_sauthors={q(author)}"
        html = requests.get("https://scholar.lanfanshu.cn/scholar?" + f"{query_url}",
                            headers=self.headers, proxies=self.proxies).text
        # with open("tmp.html", "w", encoding='utf-8') as f:
        # f.write(html)
        soup = BeautifulSoup(html, 'lxml')
        data = []
        # Container where all needed data is located
        for result in soup.select('.gs_ri')[:1]:
            title = result.select_one('.gs_rt').text
            # title_link = result.select_one('.gs_rt a')['href']
            publication_info = result.select_one('.gs_a').text
            snippet = result.select_one('.gs_rs').text
            # cited_by = result.select_one('#gs_res_ccl_mid .gs_nph+ a')['href']
            # citation = int((result.select_one(
            # '#gs_res_ccl_mid .gs_nph+ a').text).split(" ")[-1])
            citation = int(re.search(r'\d+', (result.select_one(
                '.gs_or_cit+ a').text).strip()).group(0))
            # related_articles = result.select_one('a:nth-child(4)')['href']
            data.append({
                'title': title,
                # 'title_link': title_link,
                'publication_info': publication_info,
                'snippet': snippet,
                # 'cited_by': f'https://scholar.google.com{cited_by}',
                'citation': citation,
                'query_succeed': True,
                # 'related_articles': f'https://scholar.google.com{related_articles}',
            })
        clbk(data)


# scaper = Google_scholar_scaper()
# def clbk(data):
    # print(json.dumps(data, indent=2, ensure_ascii=False))
# scaper.query("Visualizing Expanded Query Results", clbk=clbk)


class Journal_scaper:
    def __init__(self):
        self.headers = {
            'User-agent':
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }
        self.proxies = {
            'http': "socks5://127.0.0.1:7890",
            'https': "socks5://127.0.0.1:7890",
        }

    def export_func(self, name, data):
        result = pd.DataFrame(
            columns=["title", "first_author", "citation", "publication_info", "snippet", "query_succeed"])
        for i in data:
            result = result.append([i], ignore_index=True)
        result.to_csv(f"{name}_pubinfo.csv")


class EuroVis_scaper(Journal_scaper):
    def __init__(self):
        super().__init__()

    def get_pub_list(self, name="", url="https://onlinelibrary.wiley.com/toc/14678659/2018/37/3"):
        html = requests.get(url,
                            headers=self.headers, proxies=self.proxies).text
        soup = BeautifulSoup(html, 'lxml')
        data = []
        for result in soup.select(".bulkDownloadWrapper+ .bulkDownloadWrapper .issue-item"):
            title = re.sub(
                r'<[^>]*>', "", result.select_one("h2").text).strip()
            author = re.sub(r'<[^>]*>', "", result.select_one(
                ".comma__item:nth-child(1) .author-style").text).strip()
            data.append({
                "title": title,
                "first_author": author
            })
        # data = data[:3]
        scholar_scaper = Google_scholar_scaper()
        complete_entries = 0

        def collector(entry, scholar_data):
            nonlocal complete_entries
            entry['query_succeed'] = scholar_data[0]['query_succeed']
            if entry['query_succeed']:
                entry["citation"] = scholar_data[0]['citation']
                entry['publication_info'] = scholar_data[0]['publication_info']
                entry['snippet'] = scholar_data[0]['snippet']
            complete_entries += 1
            if complete_entries == len(data):
                self.export_func(name, data)
        for i in tqdm.tqdm(data):
            fail_cnt = 0
            while True:
                try:
                    # scholar_scaper.query(
                        # title=i['title'], author=i["first_author"], publication="Computer Graphics Forum", clbk=lambda x: collector(i, x))
                    scholar_scaper.query(
                        title=i['title'], clbk=lambda x: collector(i, x))
                    break
                except Exception:
                    fail_cnt += 1
                    if fail_cnt >= 5:
                        collector(i, [{"query_succeed": False}])
                        break
                    pass
                time.sleep(5)


# evscaper = EuroVis_scaper()
# evscaper.get_pub_list(name="EuroVis2018",
#                       url="https://onlinelibrary.wiley.com/toc/14678659/2018/37/3")
