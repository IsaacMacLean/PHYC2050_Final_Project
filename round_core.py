import math
import random
from dataclasses import dataclass

from sim_core import Vehicle, Lane, integrate


@dataclass
class RingCar:
    theta: float
    omega: float
    traveled: float
    needed: float
    omega_target: float
    relax: float
    sigma: float
    born: float
    direction: str


class Ring:
    def __init__(self, radius=20.0, ring_speed=9.0, sigma=15.0, relax=2.0):
        self.radius = radius
        self.ring_speed = ring_speed
        self.sigma = sigma
        self.relax = relax
        self.cars = []

    @property
    def omega_target(self):
        return self.ring_speed / self.radius

    def yield_blocked(self, entry_theta, threshold=math.pi / 3):
        for c in self.cars:
            ccw = (entry_theta - c.theta) % (2 * math.pi)
            if 0 < ccw < threshold:
                return True
        return False

    def admit(self, entry_theta, exit_theta, born, init_speed, direction):
        needed = (exit_theta - entry_theta) % (2 * math.pi)
        if needed < 1e-6:
            needed = 2 * math.pi
        self.cars.append(RingCar(
            theta=entry_theta,
            omega=max(init_speed / self.radius, 0.5),
            traveled=0.0,
            needed=needed,
            omega_target=self.omega_target,
            relax=self.relax,
            sigma=self.sigma,
            born=born,
            direction=direction,
        ))

    def advance(self, dt):
        n = len(self.cars)
        for i in range(n):
            c = self.cars[i]
            min_gap_rad = 2 * math.pi
            for j in range(n):
                if j == i:
                    continue
                ccw = (self.cars[j].theta - c.theta) % (2 * math.pi)
                if 1e-6 < ccw < min_gap_rad:
                    min_gap_rad = ccw
            if min_gap_rad < 2 * math.pi - 1e-6:
                arc_gap = self.radius * min_gap_rad
                gap = arc_gap if arc_gap > 0.5 else 0.5
                v_lin = c.omega * self.radius
                ang_brake = -((c.sigma / gap) ** 12) * v_lin / self.radius
            else:
                ang_brake = 0.0
            drive = (c.omega_target - c.omega) / c.relax
            c.omega = max(0.0, c.omega + (drive + ang_brake) * dt)
            d = c.omega * dt
            c.theta = (c.theta + d) % (2 * math.pi)
            c.traveled += d

    def harvest(self):
        kept = []
        out = []
        for c in self.cars:
            if c.traveled >= c.needed:
                out.append(c)
            else:
                kept.append(c)
        self.cars = kept
        return out

    def positions_xy(self):
        xs, ys = [], []
        for c in self.cars:
            xs.append(self.radius * math.cos(c.theta))
            ys.append(self.radius * math.sin(c.theta))
        return xs, ys


class RoundaboutSim:
    def __init__(self, radius=20.0, arm_len=200.0, ring_speed=9.0,
                 yield_threshold=math.pi / 3, sigma=15.0, relax=2.0):
        self.radius = radius
        self.arm_len = arm_len
        self.yield_threshold = yield_threshold
        self.ring = Ring(radius=radius, ring_speed=ring_speed, sigma=sigma, relax=relax)
        self.approach_h = Lane(entry_s=0.0, exit_s=arm_len)
        self.approach_v = Lane(entry_s=0.0, exit_s=arm_len)
        self.exit_h = Lane(entry_s=0.0, exit_s=arm_len)
        self.exit_v = Lane(entry_s=0.0, exit_s=arm_len)
        self.theta_in = {'h': math.pi, 'v': 3 * math.pi / 2}
        self.theta_out = {'h': 0.0, 'v': math.pi / 2}
        self.entry_dir_unit = {
            'h': (1.0, 0.0),
            'v': (0.0, 1.0),
        }
        self.exit_dir_unit = {
            'h': (1.0, 0.0),
            'v': (0.0, 1.0),
        }
        self.times_h = []
        self.times_v = []

    def _advance_approach(self, lane, direction):
        entry_theta = self.theta_in[direction]
        exit_theta = self.theta_out[direction]
        for idx, veh in enumerate(lane.queue):
            blocker = lane.queue[idx - 1].s if idx > 0 else None
            if self.ring.yield_blocked(entry_theta, self.yield_threshold):
                stop = lane.exit_s
                if veh.s < stop and (blocker is None or stop < blocker):
                    blocker = stop
            integrate(veh, dt=self._dt, blocker_s=blocker)

        while lane.queue and lane.queue[0].s >= lane.exit_s:
            if self.ring.yield_blocked(entry_theta, self.yield_threshold):
                break
            v = lane.queue.pop(0)
            self.ring.admit(entry_theta, exit_theta,
                            born=v.born, init_speed=max(v.vel, 1.0),
                            direction=direction)

    def step(self, t, dt, rate_h, rate_v):
        self._dt = dt
        self.approach_h.try_spawn(t, dt, rate_h)
        self.approach_v.try_spawn(t, dt, rate_v)

        self._advance_approach(self.approach_h, 'h')
        self._advance_approach(self.approach_v, 'v')

        self.ring.advance(dt)

        for ringcar in self.ring.harvest():
            target = self.exit_h if ringcar.direction == 'h' else self.exit_v
            target.queue.append(Vehicle(
                s=0.0,
                vel=ringcar.omega * self.radius,
                born=ringcar.born,
            ))

        self.exit_h.step(t, dt)
        self.exit_v.step(t, dt)

        while self.exit_h.passing_times:
            self.times_h.append(self.exit_h.passing_times.pop())
        while self.exit_v.passing_times:
            self.times_v.append(self.exit_v.passing_times.pop())

    def positions_xy(self):
        out = {'h_in': [], 'v_in': [], 'h_out': [], 'v_out': [], 'ring_x': [], 'ring_y': []}
        for v in self.approach_h.queue:
            out['h_in'].append((-(self.radius + (self.arm_len - v.s)), 0.0))
        for v in self.approach_v.queue:
            out['v_in'].append((0.0, -(self.radius + (self.arm_len - v.s))))
        for v in self.exit_h.queue:
            out['h_out'].append((self.radius + v.s, 0.0))
        for v in self.exit_v.queue:
            out['v_out'].append((0.0, self.radius + v.s))
        rx, ry = self.ring.positions_xy()
        out['ring_x'] = rx
        out['ring_y'] = ry
        return out


def run_roundabout(rate_h, rate_v, T=300.0, dt=0.05, seed=0,
                   radius=20.0, arm_len=200.0, ring_speed=9.0,
                   yield_threshold=math.pi / 3):
    random.seed(seed)
    sim = RoundaboutSim(radius=radius, arm_len=arm_len,
                        ring_speed=ring_speed, yield_threshold=yield_threshold)
    n_steps = int(T / dt)
    for i in range(n_steps):
        t = i * dt
        sim.step(t, dt, rate_h, rate_v)
    return sim.times_h, sim.times_v, T
