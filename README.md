# NetMikuji 🎱

PWA em HTML/JS puro para gerar números para **Loto7**, **Loto6** e **Mini Loto** (loterias japonesas), com filtro de combinações já sorteadas e estatísticas históricas.

Hospedado em **GitHub Pages** (`kamebug.github.io/net-mikuji/`) — acessível de qualquer dispositivo sem instalação.

---

## Estrutura

```
loto-pwa/
├── docs/                  ← GitHub Pages (branch main)
│   ├── index.html         ← App principal (PWA)
│   ├── manifest.json      ← PWA manifest
│   ├── sw.js              ← Service worker (offline)
│   └── data/
│       ├── loto6.json     ← Histórico Loto6
│       ├── loto7.json     ← Histórico Loto7
│       └── miniloto.json  ← Histórico Mini Loto
├── scraper/
│   ├── scrape_mizuho.py   ← Captura histórico completo
│   ├── update.py          ← Atualiza só sorteios novos
│   ├── validate.py        ← Verifica integridade dos JSONs
│   └── requirements.txt
├── deploy.ps1
└── README.md
```

---

## Primeiro uso — capturar histórico

```powershell
cd scraper
pip install -r requirements.txt

# Raspa todo o histórico (demora ~30 min por loteria)
python scrape_mizuho.py

# Valida os JSONs gerados
python validate.py
```

## Atualizações periódicas

```powershell
cd scraper
python update.py   # só baixa sorteios novos
python validate.py
```

## Deploy

```powershell
powershell -ExecutionPolicy Bypass -File ".\deploy.ps1"
```

---

## Loterias suportadas

| Loteria   | Range  | Números | Bônus |
|-----------|--------|---------|-------|
| Loto7     | 1–37   | 7       | 2     |
| Loto6     | 1–43   | 6       | 1     |
| Mini Loto | 1–31   | 5       | 1     |

---

## Estratégias de geração

- **Aleatório uniforme** — probabilidade igual para todos os números
- **Ponderado por frequência** — favorece números mais frequentes historicamente
- **Números atrasados** — favorece números que não saem há mais tempo

> ⚠️ Nenhuma estratégia aumenta a probabilidade real de ganhar. As frequências históricas são informativas, não preditivas.

---

## Fonte dos dados

Resultados históricos raspados do site da **Mizuho Bank**
(`mizuhobank.co.jp/takarakuji/check/loto/`).
Não há API oficial — atualização manual via `update.py`.

---

## Licença

MIT
