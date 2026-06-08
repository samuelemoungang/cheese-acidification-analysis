# Evaluation of Acidification Profiles in Cheese Making

## Introduction

This project monitors and models the pH acidification curves during Raclette-type cheese production. Two experimental sessions were conducted to compare the effect of different starter culture ratios on the acidification dynamics. The analysis extracts quantitative parameters using two mathematical models and evaluates their biological plausibility.

**Sessions:**
- **S1 — 28 April 2026:** MFR38 (974g) + MFR32 (282g) — ratio 3.45:1 (over-inoculation)
- **S2 — 5 May 2026:** MFR38 + MFR32 — ratio 1:2 (normal protocol)

---

## Notebooks

| Notebook | Description |
|---|---|
| `acidification_analysis_28avril.ipynb` | Full analysis of Session 1 (28 Apr) |
| `acidification_analysis_05052026.ipynb` | Full analysis of Session 2 (5 May) |
| `comparison_sessions.ipynb` | Cross-session comparison — parameters, models, residuals |

---

## Data Pipeline

Each session notebook follows the same 6-step pipeline:

1. **Load & interpolation** — raw CSV data from 3 probes (Hannah, USB, Server)
2. **Resampling** — 1-minute median resampling; Server probe additionally filtered with a Savitzky-Golay filter (window=21, polyorder=3) to suppress high-frequency noise without temporal shift
3. **Nernst temperature correction** — applied to USB and Server probes (T=35°C assumed); Hannah has internal ATC and requires no correction
4. **Logistic decline fit** — `pH(t) = L + (pH₀ − L) / (1 + exp(k·(t − t₀)))`
5. **Luedeking-Piret ODE fit** — `dX/dt = μX(1−X)`, `dA/dt = α·dX/dt + β·X` on acid proxy A(t) = pH₀ − pH(t)
6. **Residual analysis** — R² and RMSE, residual plots to assess model quality

---

## Models

### Logistic Decline

Empirical sigmoid model fitting the pH drop directly.

| Parameter | Meaning |
|---|---|
| **L** | Asymptotic minimum pH (final acidity plateau) |
| **k** (h⁻¹) | Acidification rate constant |
| **t₀** (h) | Inflection time — moment of maximum acidification rate |

> Note: t₀(S1) = −2.87h (negative) is an artefact of over-inoculation — the peak acidification rate occurred before the measurement window started.

### Luedeking-Piret ODE

Mechanistic model linking bacterial growth to acid production.

| Parameter | Meaning |
|---|---|
| **X₀** | Initial biomass fraction — indicates bacterial phase at window start |
| **μ** (h⁻¹) | Specific growth rate (biologically valid range: 0.3–2.0 h⁻¹ for lactic acid bacteria) |
| **α** | Growth-associated acid production coefficient |
| **β** | Non-growth-associated coefficient (stationary phase) |

**Important:** X₀ is fitted as a **free parameter** (multi-start optimization on [0.01, 0.3, 0.7, 0.95]) to avoid an artificial S-shape in A(t). Fixing X₀ = 0.01 when the measurement window starts after the true fermentation onset forces unrealistically high μ values (μ >> 5 h⁻¹). The fitted X₀ directly indicates the fermentation phase at the start of the measurement window:
- X₀ < 0.2 → early growth phase
- 0.2 ≤ X₀ < 0.6 → active growth
- X₀ ≥ 0.6 → stationary phase (fermentation already advanced)

---

## Key Results

| | S1 — 28 Apr | S2 — 5 May |
|---|---|---|
| **pH at moulage** | 5.93 | 6.42 |
| **ΔpH total** | 0.89 | 1.27 |
| **L (logistic)** | 5.078 | 5.196 |
| **k (logistic, h⁻¹)** | 0.920 | 1.693 |
| **t₀ (logistic, h)** | −2.87 ⚠ | +1.77 ✓ |
| **X₀ (LP ODE)** | 0.752 (stationary phase) | 0.097 (early growth) |
| **Fresh yield** | 12.17% | 11.80% |

---

## Experimental Notes

- **S1 over-inoculation:** Excess starter bacteria caused fermentation to be in late/stationary phase at moulage. This explains the negative t₀, high X₀, and higher yield. S1 results are not representative of the standard process.
- **LP model validity:** The Luedeking-Piret model requires both the exponential and stationary phases to be present in the measurement window. For S1 (X₀ = 0.752), the exponential phase was already complete before measurement began, making LP parameters less identifiable. For S2 (X₀ = 0.097), the full fermentation arc is captured and LP is reliable.
- **Only 2 sessions:** Statistical correlations between model parameters and quality indicators (yield, texture) are not meaningful with 2 data points. Results are qualitative and exploratory.

---

**Supervisor:** Dimitri Bocquel  
**Authors:** Lilandra Albert-Lavault & Samuele Moungang  
**Course:** TP Fromage — EPFL / HEIG-VD, 2026
