# NetMikuji 🎱

PWA em HTML/JS puro para gerar números para **Loto7**, **Loto6** e **Mini Loto** (loterias japonesas), com filtro de combinações já sorteadas e estatísticas históricas.

App em: **kamebug.github.io/net-mikuji/**

---

## Estrutura da pasta

```
Net Mikuji/
├── docs/                  <- GitHub Pages (branch main)
│   ├── index.html         <- App principal (PWA)
│   ├── manifest.json      <- PWA manifest
│   ├── sw.js              <- Service worker (offline)
│   ├── .nojekyll          <- Desabilita Jekyll
│   └── data/
│       ├── loto6.json     <- Historico Loto6
│       ├── loto7.json     <- Historico Loto7
│       └── miniloto.json  <- Historico Mini Loto
├── .github/
│   └── workflows/
│       └── update-data.yml  <- Atualizacao automatica (toda segunda)
├── scrape_mizuho.py       <- Scraper historico completo
├── update.py              <- Atualiza so sorteios novos
├── validate.py            <- Verifica integridade dos JSONs
├── deploy.ps1             <- Script de deploy
└── README.md
```

---

## Instalacao (primeira vez)

```powershell
py -m pip install requests beautifulsoup4 lxml selenium
```

---

## Capturar historico completo (primeira vez)

```powershell
py scrape_mizuho.py
py validate.py
powershell -ExecutionPolicy Bypass -File ".\deploy.ps1"
```

---

## Atualizar manualmente

```powershell
py update.py
py validate.py
powershell -ExecutionPolicy Bypass -File ".\deploy.ps1"
```

---

## Atualizacao automatica

O arquivo `.github/workflows/update-data.yml` roda o scraper automaticamente
toda segunda-feira as 21h JST via GitHub Actions — sem precisar abrir o PC.

Para rodar manualmente pelo GitHub:
1. Acesse github.com/kamebug/net-mikuji/actions
2. Clique em "Atualizar dados"
3. Clique em "Run workflow"

---

## Loterias suportadas

| Loteria   | Range | Numeros | Bonus |
|-----------|-------|---------|-------|
| Loto7     | 1-37  | 7       | 2     |
| Loto6     | 1-43  | 6       | 1     |
| Mini Loto | 1-31  | 5       | 1     |

---

## Estrategias de geracao

- Aleatorio uniforme: probabilidade igual para todos os numeros
- Ponderado por frequencia: favorece numeros mais frequentes historicamente
- Numeros atrasados: favorece numeros que nao saem ha mais tempo

Nenhuma estrategia aumenta a probabilidade real de ganhar.
As frequencias historicas sao informativas, nao preditivas.

---

## Fonte dos dados

Resultados raspados do site da Mizuho Bank
(mizuhobank.co.jp/takarakuji/check/loto/).
Nao ha API oficial.

---

## Licenca

MIT
