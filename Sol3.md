# building model

we model the building as a graph $G = (V, E)$.

## nodes (v)

each node $v \in V$ is one of:

- rooms $r \in R$
- hallway junctions
- stair landings
- exits to outside
- one staging area where responders start

## edges (e)

each edge $e = (u, v) \in E$ is one of:

- doorways
- corridor segments
- stair flights

each edge $e$ has:

- length $l_e$ (meters)
- cross-sectional area $A_e$
- optional physical parameters (door open/closed, width, etc.)

---

# hazard model: reaction–diffusion on the graph

the continuous hazard lives on nodes:

- $\phi_v(t) \in \mathbb{R}^+$: hazard intensity at node $v$ at time $t$

the dynamics follow a reaction–diffusion ODE:

- $\dfrac{d\phi_v(t)}{dt} = D \sum_{w \in \mathcal{N}(v)} W_{vw} \left(\phi_w(t) - \phi_v(t)\right) + R_v(\phi_v(t), t)$

where:

- $D$: diffusion coefficient  
- $\mathcal{N}(v)$: neighbors of $v$  
- $W_{vw}$: conductance on edge $(v, w)$

for edge $e = (v, w)$:

- $W_{vw} = \kappa \dfrac{A_{vw}}{L_{vw}}$

with $L_{vw} = l_e$ and $A_{vw} = A_e$, and $\kappa$ a scaling constant.

reaction term $R_v(\cdot)$:

- rooms with fire: non-linear growth (e.g. $t^2$-type HRR mapped into $\phi_v$)
- corridors / non-sources: decay unless $\phi_v$ exceeds ignition threshold $\phi_{\text{ign}}$, then switch to a growth mode

---

# from node hazard to edge hazard

for edge $e = (u, v)$:

- continuous edge hazard: $\phi_e(t) = H(\phi_u(t), \phi_v(t))$

simple choices:

- $\phi_e(t) = \max\{\phi_u(t), \phi_v(t)\}$
- $\phi_e(t) = \dfrac{\phi_u(t) + \phi_v(t)}{2}$

discrete hazard level:

- thresholds $0 = \tau_0 < \tau_1 < \tau_2 < \tau_3 < \tau_4 = \infty$
- $h_e(t) = \Psi(\phi_e(t))$, with $h_e(t) = k$ if $\tau_k \le \phi_e(t) < \tau_{k+1}$, $k \in \{0,1,2,3\}$

---

# precomputing the hazard field

we pre-solve the ODE before routing:

- choose horizon $[0, T_{\max}]$ and time step $\Delta t_{\text{RD}}$
- integrate $\dfrac{d\boldsymbol{\phi}(t)}{dt} = D L_W \boldsymbol{\phi}(t) + \mathbf{R}(\boldsymbol{\phi}(t), t)$  
  where $\boldsymbol{\phi}(t)$ stacks all $\phi_v(t)$ and $L_W$ is the weighted Laplacian
- store $\phi_v(t_k)$ for all nodes and time points $t_k$
- at query time:
  - interpolate $\phi_v(t)$ for arbitrary $t$
  - compute $\phi_e(t)$ and $h_e(t)$ via $H$ and $\Psi$

---

# responder traversal time

a responder who starts traversing edge $e$ at time $t_{\text{start}}$ has traversal time:

- $t_e(t_{\text{start}}) = \dfrac{l_e}{v_{\text{base}}} \cdot \gamma\big(h_e(t_{\text{start}})\big) \cdot \delta_{\text{carry}}$

where:

- $v_{\text{base}}$: base walking speed  
- $h_e(t_{\text{start}}) = \Psi\big(H(\phi_u(t_{\text{start}}), \phi_v(t_{\text{start}}))\big)$  
- hazard multiplier $\gamma(h)$, e.g. $\gamma = [1, 2, 4, \infty]$ for $h = [0,1,2,3]$
- load multiplier $\delta_{\text{carry}}$:
  - $\delta_{\text{carry}} = 1/\eta_{\text{carry}}$, $\eta_{\text{carry}} \approx 0.6$, if carrying
  - $\delta_{\text{carry}} = 1$ otherwise

assumption: $h_e(t)$ is evaluated once at departure and held constant over the traversal.

---

# responder state + oxygen

responder $i$ has state:

- $s_i(t) = (\text{position}_i(t), \text{cargo}_i(t), o_i(t))$

components:

- $\text{position}_i(t)$: node or edge  
- $\text{cargo}_i(t)$: empty / carrying  
- $o_i(t)$: remaining oxygen  

oxygen model:

- $o_i(t) = o_{\max} - \alpha t - \beta \displaystyle \int_0^t g\big(\phi(\text{pos}_i(s), s)\big)\, ds$

parameters:

- $o_{\max} \approx 1200\,\text{L}$
- buffer $o_{\text{buffer}} \approx 300\,\text{L}$
- $\alpha$: base consumption rate
- $\beta$: extra consumption factor
- $g(\cdot)$: maps local hazard (continuous $\phi$ or discrete $h$) to an exposure factor

in discrete simulation, along a route, for each time segment of length $\Delta t$ with hazard level $h$:

- $\Delta o = \alpha \Delta t + \beta \, g(h) \Delta t$

constraint: any route with $o_i(t_i) < o_{\text{buffer}}$ at completion time $t_i$ is infeasible.

---

# room properties

each room $r$ has:

- $t_r^{\text{check}}$: sweep time (e.g. 2 min, 5 min, 10 min)
- $w_r \in \{1,\dots,10\}$: risk weight
- $y_r \in \{0,1\}$: victim present indicator

$y_r$ behavior:

- before sweep: modeled as Bernoulli with scenario-specific probability
- after sweep: actual value revealed

---

# objective function

let $p_i$ be the ordered rooms visited by responder $i$.

objective:

- $j = \displaystyle \sum_{r \in R} w_r c_r + \lambda \max_i t_i + \mu \sum_i \sum_{r \in p_i} I(r) \, t_{\text{unsafe}}(r)$

where:

- $c_r$: time when room $r$ is declared clear
- $t_i$: completion time of responder $i$
- $I(r)$: critical-room indicator
  - $I(r) = 1$ if $w_r > w_{\text{critical}}$, else $I(r) = 0$
- $t_{\text{unsafe}}(r)$: time a responder is alone in critical room $r$
- $\lambda \approx 0.3 \langle w_r \rangle$
- $\mu$: scenario-dependent

---

# victim transport logic

when sweep of room $r$ finishes and $y_r = 1$:

- extend the responder’s route by the TDSP path from $r$ to the nearest exit
- compute traversal times with $\delta_{\text{carry}} = 1/\eta_{\text{carry}}$
- after drop-off, continue with remaining tasks

if this extra travel causes $o_i(t_i) < o_{\text{buffer}}$:

- reassign remaining rooms from that responder, or
- defer them to a later wave

---

# solution approach: large-neighborhood search (LNS)

we solve the multi-vehicle routing problem with time-dependent edge costs and oxygen constraints via LNS.

## step 1: greedy initialization

- sort rooms by descending $w_r$
- for each room $r$:
  - for each responder $i$ and each insertion position in route $p_i$:
    - use TDSP to recompute affected paths
    - update arrival times, sweeps, transport legs, and oxygen
    - discard infeasible insertions (oxygen or other constraints)
  - choose feasible insertion with minimal $\Delta j$

## step 2: destroy

- remove $k = \lceil 0.3 |R| \rceil$ rooms using:
  - random
  - Shaw (nearby / similar rooms)
  - worst-cost (highest $w_r c_r$)

## step 3: repair

for each removed room $r$:

- consider all responders $i$ and all insertion positions in $p_i$
- for each candidate:
  - rerun TDSP where needed
  - propagate timings
  - recompute oxygen and full objective
- pick the feasible insertion with smallest $\Delta j$
- insert $r$ there

## step 4: acceptance

- if $j_{\text{new}} < j_{\text{current}}$: accept
- else accept with probability $\exp(-\Delta j / T)$
- temperature schedule: $T_k = T_0 \alpha^k$ with $T_0 \approx 0.1 \, j_{\text{initial}}$ and $\alpha \approx 0.95$

## step 5: termination

stop when:

- 200 iterations without improving $j_{\text{best}}$, or
- 1000 total iterations, or
- time limit reached

---

# time-dependent shortest path (TDSP)

edge cost depends on departure time, so we use a label-setting TDSP algorithm under FIFO.

## state

- labels $(v, t_v)$: earliest known arrival at node $v$
- priority queue keyed by $t_v$

## relaxation

when popping $(i, t_{\text{current}})$, for each outgoing edge $e = (i, j)$:

- interpolate $\phi_i(t_{\text{current}})$ and $\phi_j(t_{\text{current}})$
- compute $\phi_e(t_{\text{current}}) = H(\phi_i(t_{\text{current}}), \phi_j(t_{\text{current}}))$
- compute $h_e(t_{\text{current}}) = \Psi(\phi_e(t_{\text{current}}))$
- compute $t_e(t_{\text{current}}) = \dfrac{l_e}{v_{\text{base}}} \cdot \gamma(h_e(t_{\text{current}})) \cdot \delta_{\text{carry}}$
- set $t_{\text{arrival}} = t_{\text{current}} + t_e(t_{\text{current}})$
- if $t_{\text{arrival}} < t_j$, update $t_j$ and predecessor, and push $(j, t_j)$

## complexity

single-source TDSP:

- $O\big((|V| + |E|)\log |V|\big)$

static all-pairs shortest paths are not valid for exact time-dependent costs; they can only be used as heuristics based on baseline (hazard-free) travel times.
