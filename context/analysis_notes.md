---
name: Analysis Notes
description: Data quality observations, additional parameters to consider, and modelling ideas
type: project
---

# Analysis Notes

## Data Quality — Points of Attention

1. **Session 1**: three pH meters active simultaneously — likely on different pieces from the same batch, but this needs confirmation with the team. If from the same batch, inter-probe discrepancies are scientifically interesting (Nernst correction already applied in the notebook).

2. **Incomplete temperature coverage (Session 1)**: the Elpro logger covers only 07:12–14:31, while Fromage 1 USB fermentation continues until end of day. Fromage 3 Hannah has its own embedded temperature sensor (coverage 12:08–16:18).

3. **USB logger recorded 2+ days**: data beyond 28 April already discarded in `acidification_analysis.ipynb`.

4. **Session 2 — single pH meter**: PHLOT002 final pH is 5.15 — fermentation was likely not yet complete when the logger was stopped.

5. **Yield gap**: 12.17% (Session 1) vs 11.8% (Session 2) — ~0.4 percentage point difference. To be correlated with acidification profiles.

## Existing Pipeline (`acidification_analysis.ipynb`)
1. Load & inspect raw data
2. Interpolation onto a regular grid (Server signal has gaps)
3. 1-min resampling (median) + Savitzky-Golay smoothing (window 11 min, degree 3)
4. Nernst temperature correction
5. Aligned profile comparison (t = 0)

## Parameters Already Available
| Parameter | Sources |
|---|---|
| pH | All loggers |
| mV (electrode potential) | USB, Hanna |
| Product temperature | Hanna (embedded), Elpro (ambient) |
| Time | Derivable from datetime indices |
| Fresh yield | Measured post-session (12.17% / 11.8%) |

## Additional Parameters Worth Considering
| Parameter | Currently available? | Relevance to quality |
|---|---|---|
| **dpH/dt** (acidification rate) | Computable from existing data | Rate shape — max speed, inflection point, area under curve |
| **Titratable acidity (°Dornic / TA)** | To be measured | Direct lactic acid concentration, complementary to pH |
| **Starter culture type & dose** | To be documented | Drives acidification speed and final profile shape |
| **Milk composition** (fat %, protein %) | To be collected | Direct impact on yield and texture |
| **Rennet dose & type + curd-cut timing** | To be documented | Controls syneresis and final texture |
| **Moisture / dry matter (final)** | To be measured | Industry-standard quality metric |
| **Whey volume drained** | To be measured | Linked to moisture content and yield |
| **Sensory scores** (texture, taste, aroma) | To be collected | Subjective quality ground truth |

## Modelling Ideas
- Fit a **modified Gompertz** or **logistic model** to the pH(t) curve — classical predictive microbiology approach
- Extract curve features: initial pH, final pH, maximum acidification rate, inflection point time, area under the curve
- Regress extracted features against fresh yield (and future quality measures)
- Session 1 provides multiple overlapping sensors → useful for internal cross-validation
- Long-term goal: given a real-time pH + temperature profile, predict final yield and quality class before unmolding
