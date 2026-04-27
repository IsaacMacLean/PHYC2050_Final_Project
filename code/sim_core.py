import random
from dataclasses import dataclass, field


@dataclass
class Vehicle:
    s: float
    vel: float = 0.0
    v_target: float = 11.0
    relax: float = 2.0
    sigma: float = 7.0
    born: float = 0.0


def lj_brake(sigma, gap, vel):
    g = gap if gap > 0.5 else 0.5
    return -((sigma / g) ** 12) * vel


def integrate(veh, dt, blocker_s, min_gap=20.0):
    drive = (veh.v_target - veh.vel) / veh.relax
    if blocker_s is None:
        brake = 0.0
        gap = float("inf")
    else:
        gap = blocker_s - veh.s
        brake = lj_brake(veh.sigma, gap, veh.vel)
    veh.vel = max(0.0, veh.vel + (drive + brake) * dt)
    if gap < min_gap:
        veh.vel = 0.0
    veh.s += veh.vel * dt


@dataclass
class Signal:
    loc: float
    period: float = 10.0
    offset: float = 0.0

    def red(self, t):
        return ((t + self.offset) % self.period) < (self.period / 2)


class StopBlocker:
    def __init__(self, loc):
        self.loc = loc

    def red(self, t):
        return True


class OpenBlocker:
    def __init__(self, loc):
        self.loc = loc

    def red(self, t):
        return False


class Lane:
    def __init__(self, signal=None, entry_s=-95.0, exit_s=65.0, min_gap=10.0):
        self.signal = signal
        self.entry_s = entry_s
        self.exit_s = exit_s
        self.min_gap = min_gap
        self.queue = []
        self.passing_times = []

    def step(self, t, dt):
        for idx, veh in enumerate(self.queue):
            blocker = self.queue[idx - 1].s if idx > 0 else None
            if self.signal is not None and self.signal.red(t) and veh.s < self.signal.loc:
                if blocker is None or self.signal.loc < blocker:
                    blocker = self.signal.loc
            integrate(veh, dt, blocker)
        while self.queue and self.queue[0].s > self.exit_s:
            v = self.queue.pop(0)
            self.passing_times.append(t - v.born)

    def try_spawn(self, t, dt, rate):
        if random.random() >= rate * dt:
            return False
        if self.queue and self.queue[-1].s < self.entry_s + self.min_gap:
            return False
        self.queue.append(Vehicle(s=self.entry_s, vel=10.0, born=t))
        return True

    @property
    def positions(self):
        return [v.s for v in self.queue]


def run_lights(rate_h, rate_v, T=300.0, dt=0.05, period=20.0,
               entry_s=-95.0, exit_s=65.0, seed=0):
    random.seed(seed)
    sig_h = Signal(loc=0.0, period=period, offset=0.0)
    sig_v = Signal(loc=0.0, period=period, offset=period / 2)
    lane_h = Lane(signal=sig_h, entry_s=entry_s, exit_s=exit_s)
    lane_v = Lane(signal=sig_v, entry_s=entry_s, exit_s=exit_s)
    n_steps = int(T / dt)
    for i in range(n_steps):
        t = i * dt
        lane_h.try_spawn(t, dt, rate_h)
        lane_v.try_spawn(t, dt, rate_v)
        lane_h.step(t, dt)
        lane_v.step(t, dt)
    return lane_h.passing_times, lane_v.passing_times, T
