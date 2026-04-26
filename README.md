# PHYC2050 / MATH2052 -- Traffic at Intersections

Simulation code for the 2026 PHYC2050 / MATH2052 final project: comparing a
four-arm **roundabout** against a two-phase **traffic-light** intersection
(Halifax / Armdale-Roundabout style). Each car is an object that accelerates
toward a target speed and brakes with an exponential drag term when it gets
close to another car or to a stop line. Cars enter at the four arms via a
Poisson process and are removed when they reach the far end of their exit
road (open boundary / grand-canonical setup, per the project hints).

## Repo layout

```
PHYC2050_TrafficSim/
├── trafficsim/              importable simulation package
│   ├── vehicle.py           Vehicle dataclass + geometry helpers
│   ├── roundabout.py        polar-coordinate roundabout sim
│   ├── traffic_light.py     two-phase light sim with left-turn lane
│   ├── _common.py           shared spawn / exit / summary code
│   ├── analysis.py          repeated-run helper (mean +/- stderr)
│   └── plotting.py          drawing + animation helpers
├── scripts/                 numbered runnable analyses
│   ├── 01_two_car_braking.py
│   ├── 02_pedestrian_light.py
│   ├── 03_demo_animations.py
│   ├── 04_roundabout_volume_sweep.py
│   ├── 05_asymmetric_traffic_contour.py
│   ├── 06_roundabout_vs_lights.py
│   ├── 07_cycle_length_sweep.py
│   ├── 08_random_destinations.py
│   ├── 09_radius_sensitivity.py
│   └── run_all.py
├── figures/                 saved plots and .mp4 movies (script output)
├── requirements.txt
└── README.md
```

## Install and run

```bash
git clone <this repo>
cd PHYC2050_TrafficSim
python -m pip install -r requirements.txt

# one analysis at a time
python scripts/01_two_car_braking.py
python scripts/04_roundabout_volume_sweep.py

# everything, in order
python scripts/run_all.py            # full resolution
python scripts/run_all.py --quick    # fast smoke-test (~1-2 min)
```

Saving the demo animations as `.mp4` requires `ffmpeg` on your `PATH`
(`brew install ffmpeg` on macOS, `apt install ffmpeg` on Debian/Ubuntu).
The other figures need only `numpy` and `matplotlib`.

## What each script answers

| Script | Project question(s) | Output |
|--------|---------------------|--------|
| `01_two_car_braking.py` | Hint #3 -- braking sanity check | `fig1_two_car_braking.png` |
| `02_pedestrian_light.py` | Hint #4 -- single-road pedestrian light | `fig2_pedestrian_light.png` |
| `03_demo_animations.py` | Hint #10 -- visualizing both intersections | `fig3_example_states.png`, `movie_*.mp4` |
| `04_roundabout_volume_sweep.py` | Analyses #1, #2 -- passing time vs volume | `fig4_roundabout_volume_sweep.png` |
| `05_asymmetric_traffic_contour.py` | Analyses #3, #4 -- asymmetric H/V traffic and bias | `fig5...contour.png`, `fig6...directional_bias.png` |
| `06_roundabout_vs_lights.py` | Analyses #5, #6 -- which intersection wins, when | `fig7...vs_lights.png`, `fig8...difference.png` |
| `07_cycle_length_sweep.py` | Analysis #5 follow-up -- best traffic-light cycle | `fig9_cycle_length_sweep.png` |
| `08_random_destinations.py` | Analyses #7, #8 -- random destinations | `fig10_random_destinations.png` |
| `09_radius_sensitivity.py` | Analysis #9 -- effect of roundabout radius | `fig11_radius_sensitivity.png` |

## Modelling choices (short)

* **Car following.** Each car carries a target speed `vmax` and an exponential
  brake `a_brake = exp(brake_d / gap) * v` from the project hint. This brakes
  hard when `gap` is small and basically vanishes at long range, so cars
  cruise normally on open road and platoon cleanly behind a leader.
* **Roundabout.** Polar coordinates inside the circle; each entering car has
  to satisfy a time-gap criterion against every car already on the ring
  (yields to traffic from the left). Once on the ring it follows arc-length
  spacing and exits the moment its angle sweeps past the target arm.
* **Traffic light.** Two-phase, no yellow (per spec). Each arm carries a
  through lane and a left-turn lane of length equal to the roundabout
  radius, so left-turners don't block straight-through traffic. A small
  discharge headway between successive departures captures startup loss.
* **Open boundary.** Cars are spawned via a Poisson process per arm and
  deleted once they pass the far end of their exit road. Throughput is
  measured as completed cars per second after a warm-up period.
* **Statistics.** Every operating point in the sweeps is run with multiple
  random seeds and the plots show mean +/- standard error.

## Authors

Final project for **PHYC2050 / MATH2052** (Dalhousie University, 2026).
