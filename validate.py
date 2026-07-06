"""
validate.py
Verifica a integridade dos JSONs gerados.
Detecta: lacunas de rodada, datas fora de ordem, números fora do range,
duplicatas e combinações repetidas.

Uso:
    python validate.py
    python validate.py --type loto6
"""

import json
import argparse
from pathlib import Path
from collections import Counter

OUTPUT_DIR = Path(__file__).parent / "docs" / "data"

LOTTERIES = {
    "loto6":    {"max_num": 43, "pick": 6, "bonus": 1},
    "loto7":    {"max_num": 37, "pick": 7, "bonus": 2},
    "miniloto": {"max_num": 31, "pick": 5, "bonus": 1},
}


def validate_file(lottery_key: str):
    path = OUTPUT_DIR / f"{lottery_key}.json"
    if not path.exists():
        print(f"  [{lottery_key}] Arquivo não encontrado: {path}")
        return

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    draws = data.get("draws", [])
    cfg   = LOTTERIES[lottery_key]
    errors = []
    warnings = []

    seen_rounds  = set()
    seen_combos  = set()
    last_date    = None
    last_round   = 0

    for d in draws:
        rnd = d.get("round")
        dt  = d.get("date", "")
        nums = d.get("numbers", [])
        bon  = d.get("bonus", [])

        # Rodada duplicada
        if rnd in seen_rounds:
            errors.append(f"Rodada {rnd}: DUPLICATA")
        seen_rounds.add(rnd)

        # Lacuna de rodada
        if last_round and rnd != last_round + 1:
            warnings.append(f"Rodada {rnd}: lacuna após {last_round} "
                            f"({rnd - last_round - 1} faltando)")

        # Data retroagindo
        if last_date and dt < last_date:
            errors.append(f"Rodada {rnd}: data {dt} < anterior {last_date}")

        # Quantidade de números
        if len(nums) != cfg["pick"]:
            errors.append(f"Rodada {rnd}: {len(nums)} números (esperado {cfg['pick']})")

        # Números fora do range
        for n in nums:
            if not (1 <= n <= cfg["max_num"]):
                errors.append(f"Rodada {rnd}: número {n} fora do range 1–{cfg['max_num']}")

        # Números duplicados dentro do sorteio
        if len(set(nums)) != len(nums):
            errors.append(f"Rodada {rnd}: números duplicados em {nums}")

        # Combinação já sorteada antes
        combo = tuple(sorted(nums))
        if combo in seen_combos:
            warnings.append(f"Rodada {rnd}: combinação {list(combo)} já apareceu antes")
        seen_combos.add(combo)

        last_round = rnd
        last_date  = dt

    # Resumo
    print(f"\n  [{lottery_key}] {len(draws)} sorteios — "
          f"rodada {draws[0]['round'] if draws else '?'} "
          f"até {draws[-1]['round'] if draws else '?'}")
    print(f"    Atualizado em: {data.get('last_updated','?')}")

    if errors:
        print(f"    ✗ {len(errors)} ERRO(S):")
        for e in errors[:10]:
            print(f"      • {e}")
        if len(errors) > 10:
            print(f"      ... (+{len(errors)-10} mais)")
    else:
        print(f"    ✓ Sem erros")

    if warnings:
        print(f"    ⚠ {len(warnings)} aviso(s):")
        for w in warnings[:5]:
            print(f"      • {w}")
        if len(warnings) > 5:
            print(f"      ... (+{len(warnings)-5} mais)")
    else:
        print(f"    ✓ Sem lacunas de rodada")


def main():
    parser = argparse.ArgumentParser(description="Valida integridade dos JSONs")
    parser.add_argument("--type", choices=["loto6", "loto7", "miniloto", "all"],
                        default="all")
    args = parser.parse_args()

    targets = (list(LOTTERIES.keys()) if args.type == "all" else [args.type])
    print("Validando JSONs...\n")
    for key in targets:
        validate_file(key)
    print("\n✓ Validação concluída.")


if __name__ == "__main__":
    main()
