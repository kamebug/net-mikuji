# CHANGELOG — NetMikuji

## [0.1.0] — 2026-07-06

### Adicionado
- Estrutura inicial do projeto
- `scrape_mizuho.py`: scraper histórico completo com busca por rótulo (`<th>` text) — imune ao bug de índice posicional que causa conflito de datas
- `update.py`: atualização incremental de novos sorteios
- `validate.py`: validação cruzada rodada × data, detecção de lacunas e duplicatas
- `deploy.ps1`: script de deploy para GitHub Pages
- Design base do PWA (HTML/JS) com suporte a Loto6, Loto7 e Mini Loto
- Três estratégias de geração: uniforme, ponderada por frequência, números atrasados
- Grade de frequência histórica por número
