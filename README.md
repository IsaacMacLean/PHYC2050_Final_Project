# PHYC 2050 Final Project — Traffic at Intersections

Simulation of car flow through a four-arm intersection controlled either by a **roundabout** or by **traffic lights**, written for the PHYC 2050 / MATH 2052 final project (Spring 2026).

The car-following model is the Lennard–Jones brake from the project handout: each vehicle accelerates toward a target speed with relaxation time `τ = 2 s` and is decelerated by an interaction `η v` with

`η = (σ / R)^12`,

where `R` is the gap to the obstacle ahead (a leading car or a stop line) and `σ = 15 m`. Time integration is forward-Euler with `dt ∈ [0.01, 0.05] s`.

## Layout

```
sim_core.py     1D vehicle, traffic-signal, single-lane simulator
round_core.py   Polar-coordinate roundabout: ring + four approach/exit arms
step1_two_cars.py                  two-vehicle following test (stop-and-go)
step2_pedestrian_light.py          fleet of cars at one pedestrian light
step3_intersection_lights.py       two perpendicular roads, opposing-phase lights
step4_roundabout_demo.py           four-arm roundabout snapshot
analysis1_roundabout_baseline.py             passing-time histogram (Q1)
analysis2_roundabout_density.py              <t>(spawn rate) on roundabout (Q2)
analysis3_roundabout_asymmetric.py           heatmap <t>(rate_h, rate_v) (Q3)
analysis4_roundabout_hv_difference.py        H-V passing-time bias heatmap (Q4)
analysis5_lights_density_and_cycle.py        light density and cycle sweeps (Q5)
analysis6_roundabout_vs_lights.py            head-to-head comparison (Q6)
```

## How to run

```
pip install numpy matplotlib
python step1_two_cars.py
python step2_pedestrian_light.py
python step3_intersection_lights.py
python step4_roundabout_demo.py
python analysis1_roundabout_baseline.py
python analysis2_roundabout_density.py
python analysis3_roundabout_asymmetric.py
python analysis4_roundabout_hv_difference.py
python analysis5_lights_density_and_cycle.py
python analysis6_roundabout_vs_lights.py
```

Each script prints a small summary table and writes a PNG into the working directory.

## Model summary

**Roundabout.** Polar coordinates with ring radius `R = 20 m`. Each arm is `L = 200 m`. Cars are spawned at the far end of an arm with speed 10 m/s. At the stop line (`s = L`) a vehicle may enter the ring only if no other vehicle in the ring lies within an angular distance `π/3` counter-clockwise of the entry point — the "yield-to-the-left" rule for CCW-flowing traffic. Inside the ring vehicles travel at a target tangential speed of 9 m/s (with the same Lennard-Jones car-following), and exit when they reach their target angle, joining a one-lane exit arm. The "horizontal" stream enters at θ = π and exits at θ = 0 (going east); the "vertical" stream enters at θ = 3π/2 and exits at θ = π/2 (going north).

**Traffic light.** Two perpendicular one-lane roads cross at the origin. Each direction has a binary signal (red half the cycle, green half the cycle). The horizontal and vertical signals are 180° out of phase. A red light is treated as a stationary obstacle at the stop line.

Spawning is a Poisson process with rate `r` cars/s/road, plus a minimum-gap rejection of 25 m at the entry to avoid unphysical pile-ups.

## What the analyses answer

1. Mean roundabout passing time at moderate density.
2. Roundabout passing time and exit flow as functions of spawn rate.
3. Asymmetric traffic: the contour `<t>(rate_h, rate_v)` is *not* symmetric — V-cars yield to H-cars in this CCW model, so heavy H-traffic penalises V-traffic but not the reverse.
4. The H − V passing-time bias as a function of `(rate_h, rate_v)` makes the asymmetry quantitative.
5. The same density sweep for traffic lights, plus the dependence on cycle period.
6. Direct comparison of roundabout and lights at matched spawn rates.

`fig_step*.png` and `fig_analysis*.png` files contain the figures.
