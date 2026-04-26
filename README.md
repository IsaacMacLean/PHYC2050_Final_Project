# PHYC 2050 Final Project — Traffic at Intersections

Simulation of car flow through a four-arm intersection controlled either by a **roundabout** or by **traffic lights**, written for the PHYC 2050 / MATH 2052 final project (Spring 2026).

The car-following model is the Lennard–Jones brake from the project handout: each vehicle accelerates toward a target speed with relaxation time `τ = 2 s` and is decelerated by an interaction `η v` with

`η = (σ / R)^12`,

where `R` is the gap to the obstacle ahead (a leading car or a stop line) and `σ = 7 m`. Time integration is forward-Euler.

## Layout

```
PHYC2050_TrafficSim/
├── README.md
├── report.tex                             full LaTeX report with appendix code listings
├── code/                                  all source
│   ├── sim_core.py                        1D vehicle, signal, single-lane simulator
│   ├── round_core.py                      polar-coordinate roundabout: state-machine
│   │                                      vehicle (approach/circle/exit/done),
│   │                                      four-arm support, ring registry, yield rule
│   ├── step1_two_cars.py                  two-vehicle following test (stop-and-go)
│   ├── step2_pedestrian_light.py          fleet of cars at one pedestrian light
│   ├── step3_intersection_lights.py       two perpendicular roads, opposing-phase lights
│   ├── step4_roundabout_demo.py           four-arm roundabout snapshot
│   ├── analysis1_roundabout_baseline.py            passing-time histogram (Q1)
│   ├── analysis2_roundabout_density.py             passing time vs spawn rate, roundabout (Q2)
│   ├── analysis3_roundabout_asymmetric.py          heatmap <t>(rate_h, rate_v) (Q3)
│   ├── analysis4_roundabout_hv_difference.py       H-V passing-time bias heatmap (Q4)
│   ├── analysis5_lights_density_and_cycle.py       lights density and cycle sweeps (Q5)
│   ├── analysis6_roundabout_vs_lights.py           head-to-head comparison (Q6)
│   ├── analysis7_lights_asymmetric.py              lights asymmetric heatmap (Q5 follow-up)
│   ├── analysis8_lights_hv_difference.py           lights H-V bias (Q5 follow-up)
│   └── analysis9_flow_rate_comparison.py           throughput comparison
└── figures/                               generated PNGs (committed)
    ├── fig_step1_two_vehicles.png
    ├── ...
    └── fig_analysis9_flow_rate_comparison.png
```

## How to run

```
pip install numpy matplotlib
cd code
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
python analysis7_lights_asymmetric.py
python analysis8_lights_hv_difference.py
python analysis9_flow_rate_comparison.py
```

Each script prints a small summary table and saves its figure into `../figures/`.

## Compiling the report

```
pdflatex report.tex
pdflatex report.tex   # twice for the table of contents
```

The `\graphicspath{{figures/}}` directive points to the figures folder, and code listings are included via `\lstinputlisting{code/...}`.

## Model summary

**Roundabout.** Polar coordinates, ring radius `R = 15 m`, arm length `L = 95 m`, exit length `35 m`. Each vehicle has a state from {approach, circle, exit, done}. A vehicle in the approach state may transition to circle only if no other vehicle in the ring is within angular distance `~ π/3` counter-clockwise of its entry point (yield-to-the-left rule for CCW traffic). Inside the ring vehicles cruise at `5.5 m/s` and follow each other with the same Lennard–Jones interaction in arc-length space. They exit the ring once they have travelled the angular distance to their assigned exit, then continue onto the outgoing arm.

**Traffic light.** Two perpendicular one-lane roads, same arm length as the roundabout. A binary signal at the intersection (red half the cycle, green half the cycle), with horizontal and vertical signals 180° out of phase. A red light is treated as a stationary obstacle at the stop line.

Spawning is a Poisson process at the road entrance with rate `r` cars/s/road, plus a 10 m minimum-gap rejection to avoid unphysical pile-ups.

## Headline result

In this configuration the traffic light is faster than the roundabout at every density tested. But the roundabout shows a strong direction-dependent bias from the yield-to-the-left rule: vertical-arm cars wait up to ~38 s longer than horizontal-arm cars at heavy load. This is the "Armdale Roundabout bias" the project introduction mentions, made visible.
