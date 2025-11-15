we model the building as a graph $g(v, e)$.

## nodes (v)

- rooms $r$
- hallway junctions
- stair landings
- exits to outside
- one staging area where responders start

## edges (e)

- everything thats walkable:
  - doorways
  - corridor segments
  - stair flights
- each edge $e$ carries:
  - length $l_e$ (meters)
  - time-varying hazard level $h_e(t) \in \{0,1,2,3\}$, updated every minute by cellular automaton:
    - fire in a room at $t$ ⇒ adjacent edges become $h=1$ (light smoke) at $t+1$
    - $h=1$ edge becomes $h=2$ (heavy smoke) at $t+2$
    - $h=2$ edge becomes $h=3$ (impassable fire) at $t+3$
    - vertical spread: one floor per minute
    - horizontal spread: one edge per minute
    - (we should prob define these as variables, idt the spread is that fast b/c then we would be going through all possible states of h in 4 minutes)

## responder traversal time

a responder who starts traversing edge $e$ at calendar time $t_{start}$ experiences:

$$
t_e(t_{start}) = \frac{l_e}{v_{base}} \cdot \gamma(h_e(t_{start})) \cdot \delta_{carry}
$$

the total time, $t_e(t_{start})$, required for a responder to traverse a specific path segment (edge $e$) starting at time $t_{start}$ is calculated by first determining the nominal travel time (ie the segment's length ($l_e$)) divided by the base speed ($v_{base}$) and then inflating this baseline by two factors that account for operational challenges.

- the first factor is the Hazard Multiplier, $\gamma(h_e(t_{start}))$, which dramatically increases the transit time (up to effectively $\infty$) based on the current hazard level ($h$) of the edge, forcing responders to slow down significantly in dangerous areas.
- the second factor, the Load Multiplier, $\delta_{carry}$, further penalizes the transit time by approximately $1.67$ if the responder is currently carrying a victim, reflecting the decreased speed efficiency ($\eta_{carry} \approx 0.6$) associated with transporting a load.

- $\gamma = [1, 2, 4, \infty]$ for $h = [0,1,2,3]$
- $\delta_{carry} = 1 / \eta_{carry}$ ($\eta_{carry} \approx 0.6$) if carrying a victim, else 1

the same corridor can take 15 s at $t=19$ or 50 s at $t=21$ if smoke arrives between the two departure instants.

## responder state vector

$s_i(t) = (position, cargo, o_2)$

- **cargo**: toggles empty -> carrying when a victim is discovered; reverts only when an exit node is reached.
- **oxygen** decays as:

  $$o_i(t) = o_{max} - \alpha \cdot t - \beta \cdot \sum_{s=0}^{t} h_{exposure}(s)$$

  - $\alpha$: base consumption
  - $\beta$: extra in hazard
  - $o_{max} \approx 1200L$
  - buffer = 300L
  - (we prob should do more research on this as well)
- any route that forecasts $o_i(t_i) < $ buffer is infeasible and discarded during search.

## room properties

every room $r$ has:

- $t_r^{check}$: deterministic sweep time (e.g., small bedroom 2 min, icu 5 min, warehouse 10 min)
- $w_r$: risk weight 1…10 (combining occupancy probability and vulnerability)
- $y_r$: 1 if a victim is actually inside
  - $y_r$ is revealed only when the room check finishes; until then, treat as a bernoulli draw if from (stats!) distribution, prob need research to find which one we should use

## objective function

$j$ balances three competing terms:

$$
j = \sum_{r \in r} w_r c_r + \lambda \max_i t_i + \mu \sum_i \sum_{r \in p_i} i(r) t_{unsafe}(r)
$$

- $c_r$: clock time when room $r$ is declared clear (risk-weighted completion)
- $t_i$: total time responder $i$ spends until her last task (makespan load-balancing)
- $i(r) = 1$ iff $w*r > w_{critical}$
- $t_{unsafe}(r)$: interval the responder is alone inside $r$ (safety penalty for solo sweeping of critical rooms)
- $\lambda \approx 0.3 \langle w_r \rangle$
- $\mu$: scenario-dependent (e.g., high in hospital fire, low in empty warehouse)

## victim transport logic

- if $y_r = 1$ is discovered, the responder’s route is immediately extended by the shortest path from `r` to the nearest exit, computed with $\delta*{carry} = 1/\eta_{carry}$
- only after dropping off the victim then the responder can continue sweeping.
- extra travel consumes oxygen and may push the route beyond the buffer; if so, reassign the room to another responder or leave for a later wave.

## solution approach: large-neighborhood search (lns)

we solve the multi-vehicle routing problem with time-dependent edge costs via lns, a heuristic (approximation)that repeatedly destroys and rebuilds chunks of a feasible assignment (as the problem is too hard to solve-NP Hard)

### step 1: greedy

- sort rooms by descending $w_r$
- for each room, evaluate insertion cost at every legal position of every responder route (time-dependent shortest path + o₂ check)
- pick the cheapest feasible insertion
- result: always feasible, but typically 20–40% above (worse) the best known.

### step 2: destroy

- remove $k = \lceil 0.3 |r| \rceil$ rooms using one of:
  - random
  - shaw (geographically and risk-similar rooms assigned to the same responder)
  - worst-cost (rooms with highest $w_r c_r$ contribution)
- leaves partial routes feasible.

### step 3: repair

- for each removed room $r$, enumerate every responder $i$ and every possible insertion slot $p$ in $i$’s current route
- compute new arrival times with time-dependent dijkstra
- propagate delays to downstream tasks
- recompute all three objective terms
- keep the $(i,p)$ pair that yields the smallest $\delta j$
- insert $r$ at that position only if $o_i(t_i) \geq$ buffer
- repair is expensive: per removed room, perform $o(m \cdot |r|/m) = o(|r|)$ shortest-path queries.

### step 4: acceptance

- if $j_{new} < j_{current}$: accept and update best if improved
- else: accept with probability $\exp(-\delta j / t)$, where $t$ follows geometric cooling: $t_k = t_0 \alpha^k$, $t_0 \approx 0.1 j_{initial}$, $\alpha \approx 0.95$
- occasional uphill moves escape local minima.

### step 5: termination

- stop after 200 consecutive iterations without improving $j_{best}$, or 1000 total iterations (create and calculate loss function) or just stop based on time elapsed

## time-dependent shortest path subroutine

standard dijkstra fails because edge cost $c_e$ depends on arrival time. use a label-setting algorithm on states $(node, arrival_time)$:

- priority queue keyed by `arrival_time`
- relax outgoing edge $e$ by evaluating $h_e(t_{current})$ and computing $t_{arrival} = t_{current} + t_e(t_{current})$
- complexity: $o((|v| + |e|) \log |v|)$ with binary heap
- optimization: pre-compute all-pairs shortest paths
