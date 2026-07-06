# Teste rápido — cole no terminal Python
import requests
from bs4 import BeautifulSoup

url = "https://www.mizuhobank.co.jp/takarakuji/check/loto/backnumber/detail.html?fromto=461_480&type=loto6"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
r = requests.get(url, headers=headers, timeout=15)
print(r.status_code)
print(r.text[:3000])