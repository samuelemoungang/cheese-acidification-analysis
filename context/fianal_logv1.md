# Journal des modifications — Notebooks d'acidification fromagère

**Date :** juin 2026  
**Auteurs du code :** Lilandra Albert-Lavault & Samuele Moungang  
**Contexte :** Modifications apportées suite aux retours du professeur Hanik Nils

---

## Contexte général

Le projet comporte deux sessions expérimentales :
- **S1 — 28 avril 2026** : sur-inoculation (MFR38 974g + MFR32 282g, ratio 3.45:1)
- **S2 — 5 mai 2026** : protocole normal (MFR38 + MFR32, ratio 1:2)

Trois notebooks ont été modifiés :
1. `acidification_analysis_28avril.ipynb`
2. `acidification_analysis_05052026.ipynb`
3. `comparison_sessions.ipynb`

---

## 1. Refocalisation du notebook de comparaison

### Problème
Le notebook contenait des corrélations entre paramètres des modèles et indicateurs de qualité (rendement, texture, croûte). Avec seulement 2 sessions, ces corrélations n'ont aucune signification statistique.

### Modification
- Suppression de tous les graphiques de corrélation paramètre / qualité.
- Remplacement par une **analyse quantitative des différences S1 vs S2** : ΔL, Δk, Δt₀, Δμ, Δα, Δβ.
- Ajout d'une **analyse des résidus** (graphiques 2×2 fit + résidus) pour évaluer la qualité de chaque modèle.
- Ajout d'une **table de comparaison R²** entre modèle logistique et LP ODE pour chaque session.

---

## 2. Lissage du capteur Server (Fromage 2) — filtre Savitzky-Golay

### Problème
Le capteur Server produit des données à ~1 mesure/seconde avec un bruit haute fréquence important. Le rééchantillonnage à 1 min (médiane) ne suffisait pas à lisser la courbe.

### Modification — dans les deux notebooks individuels

**Section 3 — Rééchantillonnage :**
```python
SG_WINDOW = 21
df2_res   = resample_data(df2_interp['pH'])
_sg_vals  = savgol_filter(df2_res.values, window_length=SG_WINDOW, polyorder=3)
df2_smooth = pd.Series(_sg_vals, index=df2_res.index, name='pH')
```

- Filtre **Savitzky-Golay** (fenêtre = 21 pts, ordre polynomial = 3) appliqué après le rééchantillonnage 1 min.
- Filtre **centré** → aucun décalage temporel introduit.
- Les graphiques de rééchantillonnage affichent maintenant : courbe brute (gris clair) + courbe lissée SG (couleur).

**Correction du double lissage :**  
La correction Nernst et le fit logistique utilisaient ensuite un `rolling(window=5)` supplémentaire sur le capteur Server, ce qui créait un double lissage. Ce rolling a été remplacé par un simple `.dropna()` :
```python
# Avant
pH2_corr_vis = pH2_corr.rolling(window=5, center=True).median()
# Après
pH2_corr_vis = pH2_corr.dropna()
```

---

## 3. Correction de la forme en S artificielle — modèle LP ODE

### Problème
Le modèle Luedeking-Piret présentait une **forme en S anormale** au début de la courbe A(t). Cause : X₀ (fraction de biomasse initiale) était fixée à 0.01. Comme la fenêtre de mesure commence après le vrai début de la fermentation, l'optimiseur était forcé d'utiliser des valeurs de μ irréalistes (μ = 24–55 h⁻¹, contre 0.3–2.0 h⁻¹ attendus pour des bactéries lactiques) pour rattraper rapidement le niveau réel de biomasse. Cela produisait une phase de latence artificielle suivie d'une accélération brutale, absente des données réelles.

### Modification — dans les trois notebooks

**X₀ devient un paramètre libre**, optimisé avec un multi-start sur `[0.01, 0.3, 0.7, 0.95]` pour éviter les minima locaux :

```python
def fit_lp_ode(ph_series, fit_start, fit_end):
    def residuals(params):
        mu, alpha, beta, X0 = params
        if mu <= 0 or alpha < 0 or beta < 0 or not (0 < X0 < 1):
            return 1e10
        sol = solve_ivp(lp_ode, [t[0], t[-1]], [X0, 0.0], ...)
        ...

    best_res = None
    for x0_init in [0.01, 0.3, 0.7, 0.95]:
        res = minimize(residuals, x0=[2.0, 0.3, 0.1, x0_init],
                       method='Nelder-Mead',
                       options={'xatol': 1e-7, 'fatol': 1e-9, 'maxiter': 12000})
        if best_res is None or res.fun < best_res.fun:
            best_res = res

    mu_f, alpha_f, beta_f, X0_f = best_res.x
```

**Interprétation de X₀ :**
| Valeur de X₀ | Phase bactérienne |
|---|---|
| X₀ < 0.2 | Début de croissance exponentielle |
| 0.2 ≤ X₀ < 0.6 | Croissance active |
| X₀ ≥ 0.6 | Phase stationnaire (fermentation déjà avancée au début de la fenêtre) |

Un X₀ élevé pour S1 confirme directement la sur-inoculation : les bactéries étaient déjà en phase stationnaire au moulage.

**Mises à jour des graphiques :**
- X₀ affiché dans la boîte de paramètres sur le graphique LP ODE.
- Ligne horizontale pointillée sur la courbe X(t) indiquant le niveau X₀.
- Le tableau récapitulatif inclut une colonne "X₀ (phase)".

---

## 4. Mises à jour du notebook de comparaison — détail des cellules

### Cellule `c4c2148b` — Comparaison qualité modèles + paramètres LP
- Tous les textes imprimés sont maintenant **dynamiques** (calculés à partir des résultats de fit, pas de valeurs codées en dur).
- X₀ affiché en premier avec son label de phase.
- Contrôle de plausibilité biologique de μ (flag ⚠ si μ > 5 h⁻¹).
- Section "Differences S2 − S1" inclut ΔX₀ avec interprétation automatique.

### Cellule `3a1ae2ae` — Graphiques résidus LP ODE
- La boîte d'annotation affiche désormais `X₀ = ... (phase)` en premier, avant μ, α, β.

### Cellule `9b8a10d1` — Graphique en barres des paramètres
- Layout changé de **2×3 à 2×4** :
  - Ligne 0 : L, k, t₀ + case cachée (4ème colonne vide)
  - Ligne 1 : **X₀**, μ, α, β
- Labels "Logistic" / "LP ODE" ajoutés à gauche de la figure.
- Note explicative sur X₀ : seuils > 0.6 (phase stationnaire) et < 0.3 (début de croissance).

### Cellule `69c665ec` — Observations et interprétation
- Tableau LP ODE mis à jour : ajout d'une ligne **X₀ (fraction de biomasse initiale)**.
- Les valeurs R² LP ODE ne sont plus codées en dur (elles dépendent du fit) — renvoi à la sortie de la Section 7.
- Conclusion enrichie : X₀ comme **diagnostic unifié** qui explique à la fois le t₀ négatif (logistique) et les résidus systématiques (LP) — les deux sont des symptômes de la même cause biologique (sur-inoculation S1).

---

## Résumé des fichiers modifiés

| Fichier | Sections modifiées |
|---|---|
| `acidification_analysis_28avril.ipynb` | Section 3 (lissage SG), Section 6 (LP ODE avec X₀ libre) |
| `acidification_analysis_05052026.ipynb` | Section 3 (lissage SG), Section 6 (LP ODE avec X₀ libre) |
| `comparison_sessions.ipynb` | Section 5 (résidus logistique), Section 6 (LP ODE), Section 7 (résidus LP + X₀), Section 8 (tableau récap), Section 9 (observations) |
