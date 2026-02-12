# VStats Endpoint Validation (Fase 0)

Este documento registra os testes *em runtime* feitos antes de alterar endpoints no código.

## Execução

Data: 2026-02-11

## Endpoints Validados e em Uso

### Match Preview
- `GET /stats/match/v1/preview?Fx={match_id}` → Usado para contexto pré-jogo (H2H, forma, standings)

### Standings  
- `GET /stats/standings/v1/season?tmcl={tournament_id}` → Classificação da competição

### Referee Stats
- `GET /stats/referees/v1/get-by-prsn?Prsn={referee_id}` → Estatísticas do árbitro

Estratégia:

1. Buscar um `match_id` futuro via:
   - `GET /stats/tournament/v1/calendar`
   - `GET /stats/tournament/v1/schedule/week` (fallback para `schedule/day`)
2. Validar endpoints candidatos:
   - Preview (primário): `GET /stats/matchpreview/v1/get-match-preview?Fx={match_id}`
   - Preview (secundário): `GET /stats/matchstats/v1/match-preview?Fx={match_id}`
   - Standings: `GET /stats/standings/v1/standings?tmcl={tmcl}&detailed=false`

## Resultado

Match usado:

- `match_id`: `e0j63vpd5i9tvum7lrxuv7das`
- `tournament_id (tmcl)`: `8v84l9nq3d5t0j4gb781i3llg`
- Competição: `Campeonato Argentino`

Preview:

- Primário (`/stats/matchpreview/v1/get-match-preview`): **HTTP 200**, retorna `matchInfo`, `previousMeetingsAnyComp`, `formAnyComp`.
- Secundário (`/stats/matchstats/v1/match-preview`): **HTTP 404**.

Standings:

- `GET /stats/standings/v1/standings`: **HTTP 200**, mas o formato variou:
  - para a competição testada, o ranking apareceu em `totalCup[0].ranking` (não em `total.ranking`).

Decisão:

- `fetch_match_preview()` deve usar o endpoint primário e o parser de standings deve ser robusto a múltiplos formatos.

