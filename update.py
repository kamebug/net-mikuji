"""
update.py
Atualiza os JSONs com sorteios novos desde o último salvo.
Roda após o scrape_mizuho.py inicial — muito mais rápido (poucos requests).

Uso:
    python update.py              # atualiza os três
    python update.py --type loto6
"""

import argparse
from scrape_mizuho import (
    LOTTERIES, load_existing, scrape_lottery,
    save_json, validate_draws, get_latest_round
)


def update_lottery(lottery_key: str):
    existing, last_round = load_existing(lottery_key)

    if not existing:
        print(f"  Nenhum dado local para {lottery_key}. "
              f"Execute scrape_mizuho.py primeiro.")
        return

    latest = get_latest_round(lottery_key)
    if latest <= last_round:
        print(f"  {lottery_key}: já atualizado (local={last_round}, remoto={latest})")
        return

    print(f"  {lottery_key}: {latest - last_round} sorteio(s) novo(s) "
          f"(rodadas {last_round+1}–{latest})")

    new_draws = scrape_lottery(lottery_key, start_from=last_round + 1)

    existing_rounds = {d["round"] for d in existing}
    merged = existing + [d for d in new_draws if d["round"] not in existing_rounds]
    merged.sort(key=lambda d: d["round"])
    final = validate_draws(merged, lottery_key)
    save_json(lottery_key, final)


def main():
    parser = argparse.ArgumentParser(description="Atualização incremental")
    parser.add_argument("--type", choices=["loto6", "loto7", "miniloto", "all"],
                        default="all")
    args = parser.parse_args()

    targets = (["loto6", "loto7", "miniloto"]
               if args.type == "all" else [args.type])

    for key in targets:
        print(f"\n--- {LOTTERIES[key]['label']} ---")
        update_lottery(key)

    print("\n✓ Atualização concluída.")


if __name__ == "__main__":
    main()
