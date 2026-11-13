# PressureIQ — Formal Mathematical Formulation & Technical Derivations

**System:** PressureIQ: AI-Powered Cricket Pressure Performance Analytics  
**Document:** Mathematical Formulation Reference Manual  
**Version:** 1.0.0  
**Target Submission:** SupeRR Selector Season 2 — Round 1

---

## 1. Overview & Mathematical Conventions

This document provides complete, transparent mathematical specifications for every analytical index, statistical baseline, empirical shrinkage estimator, and composite rating formula implemented in the PressureIQ engine.

### Notation Standards
- $\mathcal{M}$: Set of all evaluated cricket matches, where $m \in \mathcal{M}$.
- $\mathcal{D}_m$: Ordered sequence of legal and illegal deliveries in match $m$, where $d \in \mathcal{D}_m$.
- $\mathcal{P}$: Master player registry, where $p \in \mathcal{P}$.
- $\mathbb{I}(\cdot)$: Indicator function returning $1$ if the condition is true and $0$ otherwise.
- $\text{clip}(x, a, b)$: Clamping operator $\max(a, \min(x, b))$.
- $[a, b]$: Closed continuous interval.

---

## 2. Match State Reconstruction Equations

### 2.1 Innings Progression & Delivery Accounting
For any delivery $d = (m, \text{inn}, o, b)$ where $m$ is match ID, $\text{inn} \in \{1, 2\}$, $o \in [0, 19]$ is over index, and $b \in [1, 6+]$ is ball index within over:

- **Legal Delivery Indicator:**
  $$\mathcal{L}(d) = \mathbb{I}(\text{extras\_type} \notin \{\text{'wides'}, \text{'noballs'}\})$$
  *Units:* Dimensionless boolean.  
  *Source Module:* `src/match_state/delivery_processor.py`

- **Cumulative Legal Deliveries Bowled ($B_{\text{bowled}}$):**
  $$B_{\text{bowled}}(d) = \sum_{k=1}^{d} \mathcal{L}(k)$$
  *Units:* Balls ($0 \le B_{\text{bowled}} \le 120$).

- **Legal Balls Remaining ($B_{\text{rem}}$):**
  $$B_{\text{rem}}(d) = \max(0, B_{\text{available}} - B_{\text{bowled}}(d))$$
  Where $B_{\text{available}} = 120$ for standard 20-over matches or $6 \times \text{scheduled\_overs}$ for rain-reduced matches.  
  *Source Module:* `src/match_state/state_calculator.py`

- **Wickets in Hand ($W_{\text{rem}}$):**
  $$W_{\text{rem}}(d) = 10 - \sum_{k=1}^{d} \mathbb{I}(\text{is\_wicket}(k) = 1)$$
  *Units:* Wickets ($0 \le W_{\text{rem}} \le 10$).

---

### 2.2 Run Rates & Target Metrics

- **Current Run Rate ($CRR$):**
  $$CRR(d) = \begin{cases} 
  \frac{R_{\text{scored}}(d)}{B_{\text{bowled}}(d) / 6}, & \text{if } B_{\text{bowled}}(d) > 0 \\ 
  0.0, & \text{otherwise} 
  \end{cases}$$
  *Units:* Runs per over (rpo).

- **Required Run Rate ($RRR$) — Second Innings Chases Only:**
  $$RRR(d) = \begin{cases} 
  \frac{R_{\text{req}}(d)}{B_{\text{rem}}(d) / 6}, & \text{if } \text{inn} = 2 \text{ and } B_{\text{rem}}(d) > 0 \\ 
  \text{undefined (null)}, & \text{if } \text{inn} = 1 
  \end{cases}$$
  Where $R_{\text{req}}(d) = \max(0, T - R_{\text{scored}}(d))$ and $T$ is the target score.  
  *Critical Audit Check:* $RRR$ is strictly isolated to the second innings to prevent first-innings target leakage.

---

## 3. Dynamic Pressure Detection Engine (Phase 4)

Pressure at delivery $d$ is a multi-attribute continuous score bounded within $[0, 100]$.

### 3.1 Batting Pressure Score ($P_{\text{bat}}$)
In chasing innings ($\text{inn} = 2$):

$$P_{\text{bat}}(d) = w_{\text{rrr}} P_{\text{RRR}} + w_{\text{wkt}} P_{\text{Wicket}} + w_{\text{time}} P_{\text{Time}} + w_{\text{close}} P_{\text{Closeness}} + w_{\text{imp}} P_{\text{Importance}}$$

**Feature Weight Vector:**
$$\mathbf{w}_{\text{bat}} = [w_{\text{rrr}}, w_{\text{wkt}}, w_{\text{time}}, w_{\text{close}}, w_{\text{imp}}] = [0.35, 0.25, 0.15, 0.15, 0.10]$$

#### Component Formulations:
1. **Required Rate Pressure ($P_{\text{RRR}}$):**
   $$P_{\text{RRR}} = \text{clip}\left(\frac{RRR - 6.0}{14.0 - 6.0} \times 100, \; 0, \; 100\right)$$
   *Interpretation:* Scaled from par scoring ($6.0$ rpo $\to 0$) to steep leverage ($14.0+$ rpo $\to 100$).

2. **Wicket Depletion Pressure ($P_{\text{Wicket}}$):**
   $$P_{\text{Wicket}} = \text{clip}\left(\frac{10 - W_{\text{rem}}}{10 - 2} \times 100, \; 0, \; 100\right)$$
   *Interpretation:* Captures tail-end collapse risk; 10 wickets in hand $\to 0$, $\le 2$ wickets in hand $\to 100$.

3. **Time / Balls Remaining Leverage ($P_{\text{Time}}$):**
   $$P_{\text{Time}} = \left(1.0 - \frac{B_{\text{rem}}}{B_{\text{available}}}\right) \times 100$$
   *Interpretation:* Increases monotonically as overs expire.

4. **Match Closeness ($P_{\text{Closeness}}$):**
   $$P_{\text{Closeness}} = 100 \times \exp\left(-\frac{|R_{\text{req}} - B_{\text{rem}}|}{15.0}\right)$$
   *Interpretation:* Peaks when runs required equals balls remaining.

5. **Match Importance Multiplier ($P_{\text{Importance}}$):**
   $$P_{\text{Importance}} = \begin{cases} 
   100.0, & \text{if match is playoff/knockout} \\ 
   50.0, & \text{if regular league/bilateral fixture} 
   \end{cases}$$

### 3.2 First-Innings Batting Pressure ($P_{\text{bat, inn1}}$)
Because $RRR$ is undefined in the 1st innings, pressure is governed by par score deficit relative to phase par:

$$P_{\text{bat, inn1}}(d) = 0.40 P_{\text{ParDeficit}} + 0.30 P_{\text{Wicket}} + 0.20 P_{\text{PhaseLeverage}} + 0.10 P_{\text{Importance}}$$

Where $P_{\text{ParDeficit}}$ evaluates current score against historical stadium par at that legal ball count and wicket loss.

---

### 3.3 Bowling Pressure Score ($P_{\text{bowl}}$)
A bowling side experiences pressure under opposing momentum, defensive target defense, and boundary leaks:

$$P_{\text{bowl}}(d) = 0.30 P_{\text{Defend}} + 0.25 P_{\text{WktHazard}} + 0.20 P_{\text{DeathLeverage}} + 0.15 P_{\text{Closeness}} + 0.10 P_{\text{Importance}}$$

Where:
- $P_{\text{Defend}} = \text{clip}\left(\frac{12.0 - RRR}{12.0 - 5.0} \times 100, \; 0, \; 100\right)$ (inverse of batting rate cushion; low RRR means severe defensive pressure).
- $P_{\text{WktHazard}} = \text{clip}\left(\frac{W_{\text{rem}} - 2}{8} \times 100, \; 0, \; 100\right)$ (batting team has wickets to spare).
- $P_{\text{DeathLeverage}} = \mathbb{I}(o \ge 16) \times \text{clip}\left(\frac{B_{\text{bowled}} - 96}{24} \times 100, \; 0, \; 100\right)$.

---

### 3.4 Validated Pressure Category Tiers
Every delivery is categorized into five discrete ordinal tiers:

$$\text{Tier}(d) = \begin{cases} 
\text{Very Low}, & 0.0 \le P(d) < 20.0 \\ 
\text{Low}, & 20.0 \le P(d) < 40.0 \\ 
\text{Moderate}, & 40.0 \le P(d) < 60.0 \\ 
\text{High}, & 60.0 \le P(d) < 80.0 \\ 
\text{Extreme}, & 80.0 \le P(d) \le 100.0 
\end{cases}$$

**High-Pressure Qualification Threshold:**
$$\mathcal{H}(d) = \mathbb{I}(P(d) \ge 60.0)$$
All subsequent pressure-performance evaluations evaluate deliveries where $\mathcal{H}(d) = 1$.

---

## 4. Player Baseline Calculation & Empirical Bayes Shrinkage (Phase 5)

### 4.1 Unadjusted Historical Metrics
For player $i$ with $n_i$ sample deliveries:

- **Batting Strike Rate:**
  $$SR_i = \frac{\sum_{d \in \mathcal{D}_i} \text{runs\_scored}(d)}{n_i} \times 100$$

- **Batting Average:**
  $$Avg_i = \frac{\sum_{d \in \mathcal{D}_i} \text{runs\_scored}(d)}{\max\left(1, \; \sum_{d \in \mathcal{D}_i} \text{is\_dismissed}(d)\right)}$$

- **Bowling Economy Rate:**
  $$Econ_i = \frac{\sum_{d \in \mathcal{D}_i} \text{runs\_conceded}(d)}{n_i / 6}$$

### 4.2 Empirical Bayes Shrinkage
To guard against small-sample variance inflation, raw metrics $\bar{x}_i$ are shrunken toward the competition cohort prior $\mu_0$:

$$\theta_i^{\text{shrunk}} = (1 - B_i) \bar{x}_i + B_i \mu_0$$

Where the shrinkage weight $B_i \in [0, 1]$ is:

$$B_i = \frac{\sigma^2 / n_i}{\sigma^2 / n_i + \tau^2}$$

- $\sigma^2$: Within-player measurement variance.
- $\tau^2$: Between-player population variance across all eligible cohort peers.
- $n_i$: Delivery sample size for player $i$.
- *Asymptotic Behavior:* As $n_i \to \infty$, $B_i \to 0$ and $\theta_i^{\text{shrunk}} \to \bar{x}_i$. As $n_i \to 0$, $B_i \to 1$ and $\theta_i^{\text{shrunk}} \to \mu_0$.

---

## 5. Pressure Performance Indices (Phases 6 & 7)

### 5.1 Batter Pressure Performance Index ($BPPI$)
Evaluates a batter's ability to retain or exceed their baseline scoring under high pressure ($P \ge 60$):

$$BPPI_i = 0.40 S_{\text{SR\_Ret}} + 0.25 S_{\text{Avg\_Ret}} + 0.20 S_{\text{Bnd\_Eff}} + 0.15 S_{\text{Dot\_Ctrl}}$$

Where each subcomponent is normalized to $[0, 100]$:
1. **Strike Rate Retention ($S_{\text{SR\_Ret}}$):**
   $$Ret_{\text{SR}} = \frac{SR_{i, \text{HP}}}{SR_{i, \text{Base}}}$$
   $$S_{\text{SR\_Ret}} = \text{clip}\left(\frac{Ret_{\text{SR}} - 0.60}{1.40 - 0.60} \times 100, \; 0, \; 100\right)$$
2. **Average Retention ($S_{\text{Avg\_Ret}}$):**
   $$S_{\text{Avg\_Ret}} = \text{clip}\left(\frac{Avg_{i, \text{HP}} / Avg_{i, \text{Base}} - 0.50}{1.50 - 0.50} \times 100, \; 0, \; 100\right)$$
3. **Boundary Efficiency ($S_{\text{Bnd\_Eff}}$):**
   $$S_{\text{Bnd\_Eff}} = \text{clip}\left(\frac{\text{BndPct}_{i, \text{HP}} - 20.0}{70.0 - 20.0} \times 100, \; 0, \; 100\right)$$
4. **Dot Ball Control ($S_{\text{Dot\_Ctrl}}$):**
   $$S_{\text{Dot\_Ctrl}} = \text{clip}\left(\frac{60.0 - \text{DotPct}_{i, \text{HP}}}{60.0 - 20.0} \times 100, \; 0, \; 100\right)$$

---

### 5.2 Bowler Pressure Performance Index ($BPPI\text{-}B$)
Evaluates containment and wicket-taking under high pressure ($P \ge 60$):

$$BPPI\text{-}B_i = 0.35 S_{\text{Econ\_Ret}} + 0.30 S_{\text{Wkt\_Taking}} + 0.20 S_{\text{Dot\_Gen}} + 0.15 S_{\text{Bnd\_Prev}}$$

Where:
1. **Economy Retention ($S_{\text{Econ\_Ret}}$):**
   $$Ret_{\text{Econ}} = \frac{Econ_{i, \text{Base}}}{Econ_{i, \text{HP}}}$$
   $$S_{\text{Econ\_Ret}} = \text{clip}\left(\frac{Ret_{\text{Econ}} - 0.65}{1.35 - 0.65} \times 100, \; 0, \; 100\right)$$
2. **Wicket Taking ($S_{\text{Wkt\_Taking}}$):**
   $$S_{\text{Wkt\_Taking}} = \text{clip}\left(\frac{Wkts_i / B_i - 0.01}{0.10 - 0.01} \times 100, \; 0, \; 100\right)$$
3. **Dot Ball Generation ($S_{\text{Dot\_Gen}}$):**
   $$S_{\text{Dot\_Gen}} = \text{clip}\left(\frac{\text{DotPct}_{i, \text{HP}} - 20.0}{60.0 - 20.0} \times 100, \; 0, \; 100\right)$$
4. **Boundary Restriction ($S_{\text{Bnd\_Prev}}$):**
   $$S_{\text{Bnd\_Prev}} = \text{clip}\left(\frac{30.0 - \text{BndConcPct}_{i, \text{HP}}}{30.0 - 10.0} \times 100, \; 0, \; 100\right)$$

---

## 6. Unified Player Rating & Ranking Engine (Phase 8)

The Unified Rating models synthesize four foundational pillars:

### 6.1 Final Batter Pressure Rating ($FBPR$)
$$FBPR_i^{\text{raw}} = 0.35 S_{\text{Resilience}} + 0.30 S_{\text{Absolute}} + 0.20 S_{\text{Consistency}} + 0.15 S_{\text{Context}}$$

- **Resilience Score ($S_{\text{Resilience}}$):** Directly set to $BPPI_i$.
- **Absolute Performance Score ($S_{\text{Absolute}}$):**
  $$S_{\text{Absolute}} = 0.60 \times \text{clip}\left(\frac{SR_{\text{HP}} - 80}{200 - 80} \times 100, 0, 100\right) + 0.40 \times \text{clip}\left(\frac{\text{BndPct}_{\text{HP}} - 20}{70 - 20} \times 100, 0, 100\right)$$
- **Consistency Score ($S_{\text{Consistency}}$):**
  $$S_{\text{Consistency}} = 0.60 \times \text{clip}\left(\frac{150 - \sigma_{\text{SR}}}{150 - 10} \times 100, 0, 100\right) + 0.40 \times \text{clip}\left(\frac{M_i - 2}{15 - 2} \times 100, 0, 100\right)$$
- **Context Difficulty Score ($S_{\text{Context}}$):**
  $$S_{\text{Context}} = 0.60 \times \text{clip}\left(\frac{n_{\text{extreme}} / n_{\text{HP}}}{0.40} \times 100, 0, 100\right) + 0.40 \times \text{clip}\left(\frac{n_{\text{HP}} - 20}{150 - 20} \times 100, 0, 100\right)$$

#### Final Shrinkage Adjustment:
$$FBPR_i = (1 - \lambda_i) FBPR_i^{\text{raw}} + \lambda_i \mu_{\text{cohort}}$$
Where $\lambda_i = \text{clip}\left(1.0 - \frac{n_i}{100}, \; 0.0, \; 0.40\right)$ and $\mu_{\text{cohort}} = 50.0$.

---

### 6.2 Final Bowler Pressure Rating ($FBOR$)
$$FBOR_i^{\text{raw}} = 0.35 S_{\text{Resilience}} + 0.30 S_{\text{Absolute}} + 0.20 S_{\text{Consistency}} + 0.15 S_{\text{RoleLeverage}}$$

- **Resilience Score ($S_{\text{Resilience}}$):** Directly set to $BPPI\text{-}B_i$.
- **Absolute Score ($S_{\text{Absolute}}$):**
  $$S_{\text{Absolute}} = 0.45 \times \text{clip}\left(\frac{13.0 - Econ_{\text{HP}}}{13.0 - 6.0} \times 100, 0, 100\right) + 0.35 S_{\text{Dot\_Gen}} + 0.20 S_{\text{Wkt\_Taking}}$$
- **Consistency Score ($S_{\text{Consistency}}$):**
  $$S_{\text{Consistency}} = 0.60 \times \text{clip}\left(\frac{6.0 - \sigma_{\text{Econ}}}{6.0 - 0.5} \times 100, 0, 100\right) + 0.40 \times \text{clip}\left(\frac{M_i - 2}{15 - 2} \times 100, 0, 100\right)$$
- **Role Leverage Score ($S_{\text{RoleLeverage}}$):**
  $$S_{\text{RoleLeverage}} = 0.70 \times \text{clip}\left(\frac{\text{DeathBalls} / n_{\text{HP}}}{0.60} \times 100, 0, 100\right) + 0.30 \times \text{clip}\left(\frac{n_{\text{HP}} - 24}{120 - 24} \times 100, 0, 100\right)$$

#### Final Shrinkage Adjustment:
$$FBOR_i = (1 - \lambda_i) FBOR_i^{\text{raw}} + \lambda_i \mu_{\text{cohort}}$$
Where $\lambda_i = \text{clip}\left(1.0 - \frac{n_i}{120}, \; 0.0, \; 0.40\right)$ and $\mu_{\text{cohort}} = 50.0$.

---

## 7. Statistical Uncertainty & Bayesian Reliability (Phases 8 & 9)

### 7.1 Standard Error of Rating ($SE_i$)
The measurement standard error decreases monotonically with high-pressure delivery volume:

$$SE_i = \frac{\sigma_{\text{cohort}}}{\sqrt{n_i / n_0}}$$

Where $\sigma_{\text{cohort}} \approx 7.5$ points and $n_0 = 40$ balls.

### 7.2 95% Bayesian Confidence Intervals
$$CI_{95}(i) = [R_i - 1.96 \cdot SE_i, \quad R_i + 1.96 \cdot SE_i]$$
Where $R_i \in \{FBPR_i, FBOR_i\}$.

### 7.3 Reliability Classification
$$\text{Reliability Level}(i) = \begin{cases} 
\text{High}, & n_i \ge 80 \text{ balls and } CI_{95} \text{ width} \le 14.0 \\ 
\text{Medium}, & 40 \le n_i < 80 \text{ balls and } CI_{95} \text{ width} \le 20.0 \\ 
\text{Provisional}, & \text{otherwise} 
\end{cases}$$

---

## 8. Match-Level Block Bootstrap Formulations (Phase 9)

Let $\mathcal{M}$ be the set of $N = 883$ matches. For bootstrap iteration $b \in \{1, \dots, B\}$ where $B = 100$:

1. Resample matches with replacement:
   $$\mathcal{M}^{(b)} = \{m_1^{(b)}, m_2^{(b)}, \dots, m_N^{(b)}\}, \quad m_k^{(b)} \sim \text{Uniform}(\mathcal{M})$$
2. Compile player deliveries from the sampled matches:
   $$\mathcal{D}_i^{(b)} = \bigcup_{m \in \mathcal{M}^{(b)}} \{d \in \mathcal{D}_{i, m}\}$$
3. Re-estimate bootstrap ratings $R_i^{(b)}$ and ranks $\text{Rank}_i^{(b)}$.
4. **Top-10 Inclusion Probability:**
   $$P(\text{Rank}_i \le 10) = \frac{1}{B} \sum_{b=1}^{B} \mathbb{I}(\text{Rank}_i^{(b)} \le 10)$$
5. **Pairwise Dominance Probability:**
   $$P(R_i > R_j) = \frac{1}{B} \sum_{b=1}^{B} \mathbb{I}(R_i^{(b)} > R_j^{(b)})$$

