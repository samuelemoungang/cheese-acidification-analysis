"""Convert raw logger files in data_5_mais/ to clean, standardised CSVs."""
import re
from pathlib import Path
import pandas as pd

BASE = Path(__file__).parent


# ── 1. PHLOT002.CSV  (Hannah edge — pH + mV + temp, 5 mai 2026) ──────────────
# Semicolon-separated, 19 metadata lines + 1 header line → skiprows=20
# Decimal separator: comma  →  must replace before parsing

raw_path = BASE / "PHLOT002.CSV"
raw_text = raw_path.read_text(encoding="latin-1")

# Replace comma-decimals only inside numeric fields (not in metadata prose).
# Strategy: split on ';', strip spaces, replace ',' with '.' in each token,
# then rejoin — done per data line after skipping the header block.
lines = raw_text.splitlines()

# Find the data-start line (first line that starts with ';' and second token is
# a digit — i.e., the first data record, not the column header).
header_line = None
data_start = None
for i, line in enumerate(lines):
    stripped = line.lstrip()
    if stripped.startswith(";#Rec."):
        header_line = i
    elif header_line is not None and stripped.startswith(";"):
        tokens = stripped.split(";")
        if len(tokens) > 1 and tokens[1].strip().isdigit():
            data_start = i
            break

records = []
for line in lines[data_start:]:
    if not line.strip():
        continue
    tokens = line.split(";")
    # tokens: ['', rec, date, time, pH, 'pH', mV, 'mV', temp, '°C', '']
    if len(tokens) < 9:
        continue
    try:
        rec      = int(tokens[1].strip())
        date_str = tokens[2].strip()          # YYYY-MM-DD
        time_str = tokens[3].strip()          # HH:MM:SS
        ph_val   = float(tokens[4].strip().replace(",", "."))
        mv_val   = float(tokens[6].strip().replace(",", "."))
        temp_val = float(tokens[8].strip().replace(",", "."))
    except ValueError:
        continue
    records.append({
        "datetime": pd.to_datetime(f"{date_str} {time_str}"),
        "pH":       ph_val,
        "mV":       mv_val,
        "temp_C":   temp_val,
    })

df_ph = pd.DataFrame(records).set_index("datetime").sort_index()
out_ph = BASE / "trace_pH_hannah_05052026.csv"
df_ph.to_csv(out_ph)
print(f"[OK] {out_ph.name}  →  {len(df_ph):,} rows  |  {df_ph.index[0]} → {df_ph.index[-1]}")


# ── 2 & 3.  Ecolog TP4-L temperature files ────────────────────────────────────
# Format: 8-line metadata block ending with '@HEADER ENDS', then tab-separated
#   "DD.MM.YYYY"  "HH:MM:SS"  value  (optional trailing tab)

def parse_ecolog(path: Path) -> pd.DataFrame:
    lines = path.read_text(encoding="latin-1").splitlines()
    # Skip header: find '@HEADER ENDS' and start one line after
    data_start = 0
    for i, line in enumerate(lines):
        if "@HEADER ENDS" in line:
            data_start = i + 1
            break
    records = []
    for line in lines[data_start:]:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            date_str = parts[0].strip().strip('"')   # DD.MM.YYYY
            time_str = parts[1].strip().strip('"')   # HH:MM:SS
            temp_val = float(parts[2].strip().replace(",", "."))
        except ValueError:
            continue
        dt = pd.to_datetime(f"{date_str} {time_str}", format="%d.%m.%Y %H:%M:%S")
        records.append({"datetime": dt, "temp_C": temp_val})
    return pd.DataFrame(records).set_index("datetime").sort_index()


for src, dst_name in [
    ("Fromage 5 mai II.txt", "trace_temp_05052026.csv"),
    ("fromage 2026.txt",     "trace_temp_28042026.csv"),
]:
    df_t = parse_ecolog(BASE / src)
    out_t = BASE / dst_name
    df_t.to_csv(out_t)
    print(f"[OK] {out_t.name}  →  {len(df_t):,} rows  |  {df_t.index[0]} → {df_t.index[-1]}")
