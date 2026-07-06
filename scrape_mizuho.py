"""
scrape_mizuho.py
Captura o histórico completo de Loto6, Loto7 e Mini Loto do site da Mizuho Bank.
Usa Selenium (headless Chrome) para renderizar o JavaScript da página.
Usa busca por rótulo (<th> text) em vez de índice posicional para evitar
o bug clássico de datas trocadas entre a estrutura antiga (1–460) e nova (461+).

Uso:
    py scrape_mizuho.py              # raspa tudo
    py scrape_mizuho.py --type loto6 # raspa só Loto6
    py scrape_mizuho.py --resume     # continua de onde parou
"""

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import time
import random
import argparse
import re
from datetime import datetime
from pathlib import Path

# ==============================================================================
# CONFIGURAÇÃO
# ==============================================================================

OUTPUT_DIR = Path(__file__).parent / "docs" / "data"

LOTTERIES = {
    "loto6": {
        "label":    "Loto6",
        "max_num":  43,
        "pick":     6,
        "bonus":    1,
        "url_old":  "https://www.mizuhobank.co.jp/takarakuji/check/loto/backnumber/loto6{page:04d}.html",  # ex: loto60001.html
        "old_start": 1,
        "old_step":  20,
        "old_last":  441,
        "url_new":  "https://www.mizuhobank.co.jp/takarakuji/check/loto/backnumber/detail.html?fromto={start}_{end}&type=loto6",
        "new_start": 461,
        "main_url": "https://www.mizuhobank.co.jp/takarakuji/check/loto/loto6/index.html",
    },
    "loto7": {
        "label":    "Loto7",
        "max_num":  37,
        "pick":     7,
        "bonus":    2,
        "url_old":  None,
        "new_start": 1,
        "url_new":  "https://www.mizuhobank.co.jp/takarakuji/check/loto/backnumber/detail.html?fromto={start}_{end}&type=loto7",
        "main_url": "https://www.mizuhobank.co.jp/takarakuji/check/loto/loto7/index.html",
    },
    "miniloto": {
        "label":    "Mini Loto",
        "max_num":  31,
        "pick":     5,
        "bonus":    1,
        # Rodadas 1–520: formato antigo "loto" (Mini Loto era chamado só de "Loto")
        "url_old":  "https://www.mizuhobank.co.jp/takarakuji/check/loto/backnumber/loto{page:04d}.html",
        "old_start": 1,
        "old_step":  20,
        "old_last":  501,   # loto0001.html até loto0501.html (rodadas 1–520)
        # Rodadas 521+: formato novo
        "url_new":  "https://www.mizuhobank.co.jp/takarakuji/check/loto/backnumber/detail.html?fromto={start}_{end}&type=miniloto",
        "new_start": 521,
        "main_url": "https://www.mizuhobank.co.jp/takarakuji/check/loto/miniloto/index.html",
    },
}

DELAY_MIN = 2.0
DELAY_MAX = 4.0
JS_WAIT   = 10    # segundos para o JS carregar as tabelas
EMPTY_MAX = 5     # páginas vazias consecutivas antes de encerrar

# ==============================================================================
# SELENIUM
# ==============================================================================

def make_driver() -> webdriver.Chrome:
    """Cria driver Chrome headless."""
    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,900")
    opts.add_argument("--lang=ja")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    # Selenium Manager baixa o ChromeDriver automaticamente
    driver = webdriver.Chrome(options=opts)
    return driver


def fetch_page(driver: webdriver.Chrome, url: str, retries: int = 3) -> BeautifulSoup | None:
    """Carrega URL com Selenium, aguarda JS e retorna BeautifulSoup."""
    for attempt in range(retries):
        try:
            driver.get(url)
            # Aguarda até aparecer uma tabela com conteúdo de sorteio
            try:
                WebDriverWait(driver, JS_WAIT).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[contains(text(),'抽せん日') or contains(text(),'抽選日')]")
                    )
                )
            except Exception:
                pass  # continua mesmo sem o wait — pode estar em página antiga
            time.sleep(1.0)  # margem extra para renderização
            return BeautifulSoup(driver.page_source, "lxml")
        except Exception as e:
            print(f"  Erro Selenium (tentativa {attempt+1}): {e}")
            time.sleep(DELAY_MAX)
    return None


# ==============================================================================
# PARSING
# ==============================================================================

def extract_th_value(table, label_text: str) -> str | None:
    """
    Busca por <th> cujo texto contém label_text e retorna o texto do <td> irmão.
    Imune a mudanças de índice posicional.
    """
    for row in table.find_all("tr"):
        th = row.find("th")
        if th and label_text in th.get_text(strip=True):
            td = row.find("td")
            if td:
                return td.get_text(strip=True)
    return None


def parse_date(raw: str) -> str | None:
    raw = raw.strip()
    for fmt in ("%Y年%m月%d日", "%Y/%m/%d", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    m = re.search(r"(\d{4})[年/\-](\d{1,2})[月/\-](\d{1,2})", raw)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return None


def parse_numbers(raw: str) -> list[int]:
    return [int(n) for n in re.findall(r"\d+", raw)]


def parse_draw_table(table, lottery_key: str) -> dict | None:
    cfg = LOTTERIES[lottery_key]

    raw_round = extract_th_value(table, "回")
    if not raw_round:
        return None
    m = re.search(r"(\d+)", raw_round)
    if not m:
        return None
    round_num = int(m.group(1))

    raw_date = extract_th_value(table, "抽せん日") or extract_th_value(table, "抽選日")
    if not raw_date:
        return None
    date_str = parse_date(raw_date)
    if not date_str:
        print(f"  ⚠ Data não reconhecida: '{raw_date}' (rodada {round_num})")
        return None

    raw_nums = extract_th_value(table, "本数字")
    if not raw_nums:
        return None
    numbers = parse_numbers(raw_nums)
    if len(numbers) != cfg["pick"]:
        print(f"  ⚠ {len(numbers)} números (esperado {cfg['pick']}) rodada {round_num}")
        return None

    raw_bonus = extract_th_value(table, "ボーナス数字") or extract_th_value(table, "ボーナス")
    bonus_nums = parse_numbers(raw_bonus) if raw_bonus else []
    bonus_nums = bonus_nums[:cfg["bonus"]]

    return {
        "round":   round_num,
        "date":    date_str,
        "numbers": sorted(numbers),
        "bonus":   sorted(bonus_nums),
    }


def scrape_page(driver: webdriver.Chrome, url: str, lottery_key: str) -> list[dict]:
    soup = fetch_page(driver, url)
    if not soup:
        return []

    tables = soup.find_all("table", class_=re.compile(r"type(TK|01|02)", re.I))
    if not tables:
        tables = [t for t in soup.find_all("table")
                  if "抽せん日" in t.get_text() or "抽選日" in t.get_text()]

    draws = []
    for table in tables:
        draw = parse_draw_table(table, lottery_key)
        if draw:
            draws.append(draw)
    return draws


def get_latest_round(driver: webdriver.Chrome, lottery_key: str) -> int:
    url = LOTTERIES[lottery_key]["main_url"]
    soup = fetch_page(driver, url)
    if not soup:
        return 0
    matches = re.findall(r"第(\d+)回", soup.get_text())
    return max(int(x) for x in matches) if matches else 0


# ==============================================================================
# VALIDAÇÃO
# ==============================================================================

def validate_draws(draws: list[dict], lottery_key: str) -> list[dict]:
    valid, last_date, last_round, skipped = [], None, 0, 0
    for d in draws:
        rnd, dt = d["round"], d["date"]
        if rnd == last_round:
            print(f"  ⚠ DUPLICATA ignorada: rodada {rnd}")
            skipped += 1
            continue
        if last_date and dt < last_date:
            print(f"  ⚠ DATA RETROAGIU: rodada {rnd}, {dt} < {last_date}")
            skipped += 1
            continue
        valid.append(d)
        last_round, last_date = rnd, dt
    if skipped:
        print(f"  → {skipped} sorteio(s) descartado(s)")
    return valid


# ==============================================================================
# ORQUESTRAÇÃO
# ==============================================================================

def scrape_lottery(driver: webdriver.Chrome, lottery_key: str, start_from: int = 1) -> list[dict]:
    cfg = LOTTERIES[lottery_key]
    all_draws, seen_rounds = [], set()

    print(f"\n{'='*60}")
    print(f"  {cfg['label']} — início na rodada {start_from}")
    print(f"{'='*60}")

    # Fase 1: páginas antigas
    if cfg.get("url_old") and start_from < 461:
        page_start = cfg["old_start"]
        while page_start <= cfg["old_last"]:
            if page_start + cfg["old_step"] - 1 < start_from:
                page_start += cfg["old_step"]
                continue
            url = cfg["url_old"].format(page=page_start)
            print(f"  [antigo] rodadas {page_start}–{page_start+cfg['old_step']-1}")
            draws = scrape_page(driver, url, lottery_key)
            for d in draws:
                if d["round"] >= start_from and d["round"] not in seen_rounds:
                    all_draws.append(d)
                    seen_rounds.add(d["round"])
            print(f"    → {len(draws)} sorteios")
            time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
            page_start += cfg["old_step"]

    # Fase 2: páginas novas
    latest = get_latest_round(driver, lottery_key)
    if latest == 0:
        print("  ⚠ Não detectou sorteio mais recente — usando 9999")
        latest = 9999

    print(f"\n  Sorteio mais recente: {latest}")

    current = max(cfg.get("new_start", 461), start_from)
    consecutive_empty = 0

    while current <= latest:
        end = min(current + 19, latest)
        url = cfg["url_new"].format(start=current, end=end)
        print(f"  [novo] rodadas {current}–{end}")
        draws = scrape_page(driver, url, lottery_key)
        new_count = 0
        for d in draws:
            if d["round"] not in seen_rounds:
                all_draws.append(d)
                seen_rounds.add(d["round"])
                new_count += 1
        print(f"    → {new_count} novos")

        consecutive_empty = 0 if draws else consecutive_empty + 1
        if consecutive_empty >= EMPTY_MAX:
            print(f"  {EMPTY_MAX} páginas vazias consecutivas — encerrando.")
            break

        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))
        current += 20

    all_draws.sort(key=lambda d: d["round"])
    all_draws = validate_draws(all_draws, lottery_key)
    print(f"\n  Total: {len(all_draws)} sorteios válidos")
    return all_draws


# ==============================================================================
# SAVE / LOAD
# ==============================================================================

def save_json(lottery_key: str, draws: list[dict]):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    cfg = LOTTERIES[lottery_key]
    payload = {
        "lottery":      lottery_key,
        "label":        cfg["label"],
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "total_draws":  len(draws),
        "draws":        draws,
    }
    path = OUTPUT_DIR / f"{lottery_key}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\n  ✓ Salvo: {path} ({len(draws)} sorteios)")


def load_existing(lottery_key: str) -> tuple[list[dict], int]:
    path = OUTPUT_DIR / f"{lottery_key}.json"
    if not path.exists():
        return [], 0
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    draws = data.get("draws", [])
    return draws, max((d["round"] for d in draws), default=0)


# ==============================================================================
# ENTRY POINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Scraper NetMikuji — Mizuho Bank")
    parser.add_argument("--type", choices=["loto6", "loto7", "miniloto", "all"],
                        default="all")
    parser.add_argument("--resume", action="store_true",
                        help="Continua de onde parou")
    args = parser.parse_args()

    targets = ["loto6", "loto7", "miniloto"] if args.type == "all" else [args.type]

    print("Iniciando Chrome headless...")
    driver = make_driver()

    try:
        for key in targets:
            existing_draws, last_round, start_from = [], 0, 1

            if args.resume:
                existing_draws, last_round = load_existing(key)
                if last_round:
                    start_from = last_round + 1
                    print(f"\n  Retomando {key} da rodada {start_from} "
                          f"({len(existing_draws)} já salvas)")

            new_draws = scrape_lottery(driver, key, start_from)

            if existing_draws:
                existing_rounds = {d["round"] for d in existing_draws}
                merged = existing_draws + [d for d in new_draws
                                           if d["round"] not in existing_rounds]
                merged.sort(key=lambda d: d["round"])
                final = validate_draws(merged, key)
            else:
                final = new_draws

            save_json(key, final)
    finally:
        driver.quit()
        print("\n✓ Chrome encerrado.")

    print("\n✓ Concluído.")


if __name__ == "__main__":
    main()
