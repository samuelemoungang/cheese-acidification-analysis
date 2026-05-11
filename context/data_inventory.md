---
name: Data Inventory
description: Complete inventory of all data files from both sessions with temporal coverage and quality notes
type: project
---

# Data Inventory

## Session 1 — 28 April 2026
Folder: `data/`

| File | Instrument | Measurements | Resolution | Start | End | Valid points |
|---|---|---|---|---|---|---|
| `trace pH fromage 1_USB_28042026.csv` | USB logger | pH, mV | 1 min | 28/04 10:43 | 28/04 23:59* | 775 |
| `trace pH fromage 2_Server_28042026.csv` | Server | pH | ~1 s | 28/04 10:00 | 28/04 15:37 | 7 308 |
| `trace pH fromage 3_28042026_hannah.csv` | Hanna PHLOT001 | pH, mV, T°C | 1 min | 28/04 12:08 | 28/04 16:18 | 251 |

Temperature file for session 1 (stored in `data_5_mais/` — same physical logger):
| File | Instrument | Measurements | Resolution | Start | End | Points |
|---|---|---|---|---|---|---|
| `trace_temp_28042026.csv` (from `fromage 2026.txt`) | Elpro Ecolog TP4-L | T°C | 16 s | 28/04 07:12 | 28/04 14:31 | 1 646 |

**Critical note**: the temperature logger stops at 14:31 while Fromage 2 pH data runs until 15:37 and Fromage 1 until end of day. **Incomplete temperature coverage for session 1.**

*The USB logger recorded for 2+ days (until 30 April); the notebook filters to 28 April only.

## Session 2 — 5 May 2026
Folder: `data_5_mais/`

Raw source files:
- `PHLOT002.CSV` → Hanna edge, `;`-separated, comma decimal separator
- `Fromage 5 mai II.txt` → Elpro Ecolog, TSV, 8-line metadata header
- `fromage 2026.txt` → Elpro Ecolog, TSV, 8-line metadata header (contains **28 April** data — same logger, placed in wrong folder)

Clean CSV files produced by `convert_to_csv.py`:
| File | Source | Measurements | Resolution | Start | End | Points |
|---|---|---|---|---|---|---|
| `trace_pH_hannah_05052026.csv` | PHLOT002.CSV | pH, mV, T°C | 1 min | 05/05 11:23 | 05/05 16:08 | 286 |
| `trace_temp_05052026.csv` | Fromage 5 mai II.txt | T°C | 16 s | 05/05 07:14 | 06/05 07:05 | 5 368 |
| `trace_temp_28042026.csv` | fromage 2026.txt | T°C | 16 s | 28/04 07:12 | 28/04 14:31 | 1 646 |

## Standardised CSV Format (clean output)
- **pH + mV + temp**: `datetime,pH,mV,temp_C` — ISO 8601 datetime, dot decimal separator
- **Temperature only**: `datetime,temp_C`
- Loading: `pd.read_csv(..., index_col='datetime', parse_dates=True)`

## Observed pH Range Summary
| Source | Start pH | End pH | Measured duration |
|---|---|---|---|
| Fromage 1 USB (28 Apr) | ~6.15 | ~5.43 | ~13 h (28 Apr only) |
| Fromage 2 Server (28 Apr) | ~6.93 | ~4.72 | ~5.6 h |
| Fromage 3 Hannah (28 Apr) | 5.93 | ~5.02 | ~4 h |
| Hannah PHLOT002 (5 May) | 6.42 | 5.15 | ~4h45 |
