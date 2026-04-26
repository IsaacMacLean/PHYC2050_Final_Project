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
