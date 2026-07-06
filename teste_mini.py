from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

opts = Options()
# sem headless — abre o Chrome normal
driver = webdriver.Chrome(options=opts)

driver.get("https://www.mizuhobank.co.jp/takarakuji/check/loto/backnumber/")
time.sleep(8)

import re
links = re.findall(r'href="([^"]*)"', driver.page_source)
loto_links = [l for l in links if "loto" in l.lower() or "mini" in l.lower() or "backnumber" in l.lower()]
for l in sorted(set(loto_links)):
    print(l)

input("Pressione Enter para fechar...")
driver.quit()