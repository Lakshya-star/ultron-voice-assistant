"""Ultron HUD geometry — pure 3D math helpers, no Tkinter (unit-testable anywhere)."""
import math
import random

CAM_DIST = 560.0


def rot_y(p, a):
    """Rotate point (x,y,z) around the Y axis by angle a (radians)."""
    x, y, z = p
    c, s = math.cos(a), math.sin(a)
    return (x * c + z * s, y, -x * s + z * c)


def rot_x(p, a):
    """Rotate point (x,y,z) around the X axis by angle a (radians)."""
    x, y, z = p
    c, s = math.cos(a), math.sin(a)
    return (x, y * c - z * s, y * s + z * c)


def project(p, cam_dist=CAM_DIST):
    """Perspective-project a 3D point onto the screen.

    Returns (x, y, depth) where depth > 1 means closer to the camera.
    """
    x, y, z = p
    f = cam_dist / max(cam_dist - z, 1e-6)
    return (x * f, y * f, f)


def lerp_color(c1, c2, t):
    """Blend two '#rrggbb' hex colors; t=0 gives c1, t=1 gives c2."""
    t = max(0.0, min(1.0, t))
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02x%02x%02x" % tuple(int(x + (y - x) * t) for x, y in zip(a, b))


def ring_segment_list(radius, tilt, angle, n=56):
    """A tilted ring rotating around its own axis, perspective-projected.

    Returns a list of segments: [((x1, y1, d1), (x2, y2, d2)), ...]
    where d is the perspective depth factor (bigger = nearer).
    """
    segs = []
    for i in range(n):
        t1 = 2 * math.pi * i / n
        t2 = 2 * math.pi * (i + 1) / n
        p1 = (radius * math.cos(t1), 0.0, radius * math.sin(t1))
        p2 = (radius * math.cos(t2), 0.0, radius * math.sin(t2))
        p1 = rot_x(rot_y(p1, angle), tilt)
        p2 = rot_x(rot_y(p2, angle), tilt)
        segs.append((project(p1), project(p2)))
    return segs


def make_particles(n=14, seed=7):
    """Deterministic set of orbiting particles around the core."""
    rng = random.Random(seed)
    return [{
        "theta": rng.uniform(0, 2 * math.pi),
        "r": rng.uniform(96, 136),
        "speed": rng.uniform(0.6, 1.4),
        "height": rng.uniform(6, 26),
        "wob": rng.uniform(1.0, 3.0),
        "phase": rng.uniform(0, 2 * math.pi),
    } for _ in range(n)]


def particle_positions(particles, angle):
    """Projected positions of all particles at time `angle`."""
    out = []
    for p in particles:
        t = p["theta"] + angle * p["speed"]
        point = (p["r"] * math.cos(t),
                 math.sin(t * p["wob"] + p["phase"]) * p["height"],
                 p["r"] * math.sin(t))
        out.append(project(point))
    return out
