# Pricing d'options par simulation de Monte Carlo

Application Streamlit interactive pour la valorisation d'options vanille et exotiques
par simulation de Monte Carlo, avec calcul des sensibilités (grecques) et de la VaR du
portefeuille d'options.

## Contenu

| Fichier | Description |
|---|---|
| `Simulation_montecarlo.py` | Application Streamlit complète (~530 lignes) |
| `simulation_grecque.ipynb` | Notebook exploratoire sur les grecques |
| `Simulation de monte Carlo Djaname.pdf` | Rapport détaillant la méthodologie |

## Fonctionnalités

### Briques de simulation
- **Générateur normal** implémenté à la main par transformée de Box-Muller
  (`simulation_loinormal`), à partir de deux tirages uniformes — la loi normale n'est
  pas appelée en boîte noire.
- **Mouvement brownien** construit par accumulation d'incréments $\sqrt{\Delta t}\,Z$.
- **Quasi-Monte Carlo** : séquences de Sobol scramblées (`scipy.stats.qmc.Sobol`)
  transformées par $\Phi^{-1}$, pour comparer la convergence QMC / MC classique.
- **Variables antithétiques** : chaque payoff est moyenné sur les trajectoires
  $+W$ et $-W$, ce qui réduit la variance de l'estimateur.

### Options valorisées
| Type | Fonction | Payoff |
|---|---|---|
| Européenne | `prix_St_browm`, `prix_St_norm0`, `prix_St_norm` | $\max(S_T - K, 0)$ |
| Asiatique | `option_asiatique` | moyenne arithmétique du sous-jacent |
| Lookback | `option_lookback` | extremum de la trajectoire |
| Barrière | `option_barrier` | activation/désactivation au franchissement de $H$ |

Chaque prix est renvoyé avec son **intervalle de confiance**
$\pm z_\alpha \hat{\sigma}/\sqrt{n}$.

### Grecques
Delta, Gamma, Theta, Rho et Vega par différences finies sur le prix Monte Carlo,
déclinés pour chaque famille d'options (`delta_asiatique`, `gamma_lookback`, etc.).
Le module `black_scholes` et ses dérivées analytiques (`delta_BS`, `gamma_BS`,
`theta_BS`) servent de référence pour valider l'estimateur simulé sur le cas européen.

### Mesure de risque
- `var_montecarlo_europene` : VaR de la position optionnelle par simulation complète.
- `delta_gamma`, `delta_gamma_asiatique`, `delta_gamma_lookback`,
  `delta_gamma_barrier` : approximation Delta-Gamma de la VaR, plus rapide, à
  confronter à la VaR pleine simulation.

## Interface

L'application est organisée en une barre latérale de sélection du type d'option
(Européenne / Asiatique / Lookback / Barrière / Portefeuille), suivie de formulaires
Streamlit pour :

1. la simulation d'une loi normale et d'un mouvement brownien (pédagogique),
2. la saisie des paramètres $S_0$, $K$, $T$, $\sigma$, $r$, style call/put,
3. l'affichage du prix, des grecques et de la VaR.

## Dépendances

```
streamlit numpy scipy pandas matplotlib bokeh
```

## Utilisation

```bash
pip install streamlit numpy scipy pandas matplotlib bokeh
streamlit run Simulation_montecarlo.py
```

L'application s'ouvre sur `http://localhost:8501`.

## Remarques

- Le nombre de tirages QMC est fixé à $2^{11}$ dans `prix_St_norm` ; c'est un choix
  imposé par `random_base2`, à ajuster si l'on veut plus de précision.
- Les boucles Python sur les trajectoires rendent les grands nombres de simulations
  lents : une vectorisation NumPy complète est la première optimisation à envisager.
