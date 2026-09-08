import sys
import os
import json
import time
import math
import random
import colorsys
import numpy as np
import pygame

try:
    AUDIO_AVAILABLE = True
except ImportError:
    AUDIO_AVAILABLE = False

# --------------------------------------------------------------------------- #
# CONSTANTS
# --------------------------------------------------------------------------- #
WIDTH, HEIGHT, FPS = 1000, 700, 60
BLACK, WHITE = (5, 5, 12), (240, 240, 250)

FOCAL = 480.0
NEAR = 4.0
WORLD_UP = np.array([0.0, 1.0, 0.0])

CHASE_DIST = 46.0          # how far behind the ship the camera sits
CHASE_HEIGHT = 16.0        # how far above the ship the camera sits
CHASE_LOOKAHEAD = 60.0     # how far ahead of the ship the camera looks
CAM_POS_SMOOTH = 0.08      # camera position easing (higher = snappier)
CAM_DIR_SMOOTH = 0.05      # camera facing-direction easing
MIN_STEER_SPEED = 0.12     # below this speed, keep last known facing (avoid jitter)

ESCAPE_RADIUS = 1050.0     # distance from a system's sun that triggers a
                            # zone transition into deep space (this is what
                            # a "slingshot" is actually for -- building up
                            # enough speed to cross it before gravity can
                            # pull you back)
BEACON_DIST = 2400.0       # how far ahead the next system's beacon sits
BEACON_CAPTURE = 160.0     # how close you need to get to warp in
DEEPSPACE_DESPAWN = 1300.0 # ship-relative distance at which deep-space
                            # debris is cleaned up

SHIP_SIZE = 9
SHIP_HITBOX = 9.0
THRUST = 0.15
MAX_SPEED = 6.5
STAR_SHELL_RADIUS = 2200.0  # stars are rendered by direction only, always
                             # at this distance from the CURRENT camera
                             # position each frame -- a proper skybox that
                             # can never be "left behind" no matter how far
                             # the ship travels across zones

MAX_RANGE = 250000.0       # far safety clamp only (guards against runaway
                            # float drift) -- NOT a gameplay boundary; the
                            # real boundary is ESCAPE_RADIUS below, which
                            # triggers a zone change. Kept huge and measured
                            # from world origin only as a last-resort guard,
                            # since normal play can legitimately end up
                            # thousands of units from the origin after a
                            # few zone transitions.

G = 1.0
MIN_GRAV_DIST = 40.0
SUN_MASS = 2200.0
SUN_RADIUS = 60.0

SCORE_MULTIPLIER = 1

SCORES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solar_drift_scores.json")
MAX_SAVED_SCORES = 8
MAX_HISTORY = 10


def load_data():
    """
    Read saved progress from disk: top scores, recent run history, and
    total cumulative playtime. Returns a fresh empty structure if the
    file is missing, empty, or corrupted -- never raises. Also
    transparently upgrades the old file format (a bare list of ints)
    from an earlier version of this game.
    """
    empty = {"scores": [], "history": [], "total_playtime": 0.0}
    try:
        with open(SCORES_FILE, "r") as f:
            data = json.load(f)
        if isinstance(data, list):  # old format
            scores = sorted([int(x) for x in data if isinstance(x, (int, float))], reverse=True)
            return {"scores": scores[:MAX_SAVED_SCORES], "history": [], "total_playtime": 0.0}
        if isinstance(data, dict):
            scores = sorted([int(x) for x in data.get("scores", []) if isinstance(x, (int, float))],
                             reverse=True)[:MAX_SAVED_SCORES]
            history = data.get("history", [])
            if not isinstance(history, list):
                history = []
            total = data.get("total_playtime", 0.0)
            if not isinstance(total, (int, float)):
                total = 0.0
            return {"scores": scores, "history": history[:MAX_HISTORY], "total_playtime": float(total)}
    except Exception:
        pass
    return empty


def save_data(data):
    try:
        with open(SCORES_FILE, "w") as f:
            json.dump({
                "scores": sorted(data["scores"], reverse=True)[:MAX_SAVED_SCORES],
                "history": data["history"][:MAX_HISTORY],
                "total_playtime": data["total_playtime"],
            }, f)
    except Exception:
        pass  # non-fatal -- the game should still run without disk access


def record_run(score, duration):
    """Log a completed run: updates the leaderboard, prepends to recent
    history, adds to total playtime, persists it, and returns the
    updated data dict."""
    data = load_data()
    data["scores"] = sorted(data["scores"] + [int(score)], reverse=True)[:MAX_SAVED_SCORES]
    data["history"].insert(0, {
        "score": int(score),
        "duration": round(float(duration), 1),
        "time": time.strftime("%b %d, %H:%M"),
    })
    data["history"] = data["history"][:MAX_HISTORY]
    data["total_playtime"] = data.get("total_playtime", 0.0) + duration
    save_data(data)
    return data


def format_duration(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h}h {m}m"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


# =========================================================================== #
# VECTOR HELPERS
# =========================================================================== #
def normalize(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v.copy()


def lerp(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def hue(t, s=0.85, v=1.0):
    r, g, b = colorsys.hsv_to_rgb(t % 1.0, s, v)
    return int(r * 255), int(g * 255), int(b * 255)


# =========================================================================== #
# ALGORITHM 1: DDA LINE ALGORITHM (2D, applied to already-projected points)
# =========================================================================== #
def dda_points(x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    steps = int(max(abs(dx), abs(dy))) or 1
    xi, yi = dx / steps, dy / steps
    return [(x1 + xi * i, y1 + yi * i) for i in range(steps + 1)]


# =========================================================================== #
# ALGORITHM 1b: BRESENHAM'S LINE ALGORITHM (distinct integer/decision-
# variable approach, as opposed to DDA's equal floating-point increments)
# =========================================================================== #
def bresenham_line_points(x1, y1, x2, y2):
    x1, y1, x2, y2 = int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))
    pts = []
    dx, dy = abs(x2 - x1), abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    x, y = x1, y1
    while True:
        pts.append((x, y))
        if x == x2 and y == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x += sx
        if e2 < dx:
            err += dx
            y += sy
    return pts


def bresenham_line(surf, x1, y1, x2, y2, color, width=1):
    """Used for the ship's own hull edges/fin/thruster flame -- short,
    close-up structural lines where Bresenham's classic algorithm is a
    natural (and cheap, since these segments are short) fit."""
    half = max(0, width // 2)
    for (px, py) in bresenham_line_points(x1, y1, x2, y2):
        if width <= 1:
            if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                surf.set_at((px, py), color)
        else:
            rx, ry = max(0, px - half), max(0, py - half)
            rw = min(WIDTH, px + half + 1) - rx
            rh = min(HEIGHT, py + half + 1) - ry
            if rw > 0 and rh > 0:
                surf.fill(color, (rx, ry, rw, rh))


# =========================================================================== #
# ALGORITHM 2: BRESENHAM'S CIRCLE ALGORITHM
# =========================================================================== #
def circle_points(xc, yc, r):
    pts, x, y, d = [], 0, r, 3 - 2 * r
    while x <= y:
        pts += [(xc+x,yc+y), (xc-x,yc+y), (xc+x,yc-y), (xc-x,yc-y),
                (xc+y,yc+x), (xc-y,yc+x), (xc+y,yc-x), (xc-y,yc-x)]
        d = d + 4*x + 6 if d < 0 else d + 4*(x-y) + 10
        if d >= 0:
            y -= 1
        x += 1
    return pts


def fill_circle(surf, xc, yc, r, color):
    """
    Filled circle via the SAME Bresenham/midpoint decision loop as
    circle_points, but converted to a proper scanline fill: for each step
    of the midpoint algorithm we fill whole horizontal spans between the
    mirrored boundary x-coordinates, instead of stacking many thin outline
    rings and plotting them one pixel at a time. This still walks only
    O(r) steps of the circle algorithm (same as the outline version) but
    each step fills a full row in one fast call -- both much faster and,
    as a side effect, a cleanly solid disk instead of the faint
    ring-texture the old stacked-outlines approach produced.
    """
    xc, yc, r = int(xc), int(yc), max(1, int(round(r)))
    if r > 400:  # sanity guard against pathological sizes
        r = 400

    def hspan(x1, x2, y):
        if y < 0 or y >= HEIGHT:
            return
        if x1 > x2:
            x1, x2 = x2, x1
        x1 = max(0, x1)
        x2 = min(WIDTH - 1, x2)
        if x1 > x2:
            return
        surf.fill(color, (x1, y, x2 - x1 + 1, 1))

    x, y, d = 0, r, 3 - 2*r
    while x <= y:
        hspan(xc - y, xc + y, yc - x)
        hspan(xc - y, xc + y, yc + x)
        hspan(xc - x, xc + x, yc - y)
        hspan(xc - x, xc + x, yc + y)
        d = d + 4*x + 6 if d < 0 else d + 4*(x-y) + 10
        if d >= 0:
            y -= 1
        x += 1


# =========================================================================== #
# ALGORITHM 3: SCAN-LINE POLYGON FILL
# =========================================================================== #
def fill_polygon(surf, points, color):
    """
    ALGORITHM: SCAN-LINE POLYGON FILL. For each horizontal scanline that
    crosses the polygon, find where the polygon's edges intersect that
    row, sort those crossing points left-to-right, and fill the spans
    between each pair. Used for the ship's hull panels (after they've
    been culled and clipped) and the Deep Space beacon's diamond marker.
    """
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y_top = max(0, int(math.floor(min(ys))))
    y_bot = min(HEIGHT - 1, int(math.ceil(max(ys))))
    n = len(points)
    for y in range(y_top, y_bot + 1):
        xs = []
        for i in range(n):
            x1, y1 = points[i]
            x2, y2 = points[(i+1) % n]
            if y1 == y2:
                continue
            if min(y1, y2) <= y < max(y1, y2):
                t = (y - y1) / (y2 - y1)
                xs.append(x1 + t * (x2 - x1))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            xa, xb = int(round(xs[i])), int(round(xs[i+1]))
            xa = max(0, xa)
            xb = min(WIDTH - 1, xb)
            if xa <= xb:
                surf.fill(color, (xa, y, xb - xa + 1, 1))


# =========================================================================== #
# ALGORITHM 4: FLOOD FILL
# =========================================================================== #
def flood_fill_blob(seed, grid_size=40, fill_probability=0.6):
    """
    ALGORITHM: FLOOD FILL. Classic stack-based 4-connected flood fill:
    start from a seed cell, and keep spreading to unvisited neighbors as
    long as they satisfy a 'fill condition' -- normally 'same color as
    the seed' for a paint-bucket tool, here a distance-fading random
    probability instead, which is what turns a single seed point into an
    organic, irregular blob shape rather than a hard-edged circle. Used
    to generate the nebula cloud patches drawn in the Deep Space
    backdrop. Runs once per patch (cached), never per-frame.
    """
    cx, cy = grid_size // 2, grid_size // 2
    rng = random.Random(seed)
    visited = set()
    stack = [(cx, cy)]
    filled = []
    while stack:
        x, y = stack.pop()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        if not (0 <= x < grid_size and 0 <= y < grid_size):
            continue
        dist = math.hypot(x - cx, y - cy) / (grid_size / 2)
        if dist > 1.0:
            continue
        # Keep exploring through this cell regardless of whether it gets
        # painted -- otherwise a single failed probability roll near the
        # seed can prematurely kill the entire fill before it ever spreads.
        stack.extend([(x+1, y), (x-1, y), (x, y+1), (x, y-1)])
        if rng.random() <= fill_probability * (1 - dist * 0.5):
            filled.append((x, y))
    return filled


def generate_nebula_patches(seed_base, count=3):
    """
    Build a few decorative nebula-cloud patches for the Deep Space
    backdrop, each one an irregular blob produced by flood_fill_blob.
    This runs once whenever a Deep Space zone is entered (not per
    frame) and the result is cached in game state.
    """
    rng = random.Random(seed_base)
    patches = []
    for i in range(count):
        cx = rng.uniform(180, WIDTH - 180)
        cy = rng.uniform(90, HEIGHT - 220)
        cell = rng.uniform(4.5, 7.5)
        patch_hue = rng.random()
        cells = flood_fill_blob(seed=seed_base * 97 + i, grid_size=26, fill_probability=0.5)
        patches.append({"cx": cx, "cy": cy, "cell": cell, "hue": patch_hue, "cells": cells})
    return patches


def build_nebula_surface(patches):
    """
    Renders the nebula patches ONCE onto a cached per-pixel-alpha surface.
    The patches never change after being generated, so redrawing ~1000
    small circles every single frame (as an earlier version of this
    function did) would waste ~12ms/frame for a static decoration --
    exactly the kind of per-frame cost that caused the lag fixed
    earlier in this project. Instead we pay that cost once, when the
    Deep Space zone is entered, and every frame after that is just a
    single cheap blit of the finished image.
    """
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for patch in patches:
        col = lerp((8, 8, 16), hue(patch["hue"], s=0.5, v=0.5), 0.5)
        half = 17 * patch["cell"]
        for (gx, gy) in patch["cells"]:
            px = patch["cx"] + (gx*patch["cell"] - half)
            py = patch["cy"] + (gy*patch["cell"] - half)
            fill_circle(surf, px, py, patch["cell"]*0.7, col)
    return surf


def ring_circle(surf, xc, yc, r, color):
    r = max(1, int(round(r)))
    if r > 400:
        return
    for px, py in circle_points(xc, yc, r):
        if 0 <= px < WIDTH and 0 <= py < HEIGHT:
            surf.set_at((int(px), int(py)), color)


def glow_line(surf, x1, y1, x2, y2, color, thick):
    pts = dda_points(x1, y1, x2, y2)
    for px, py in pts[::max(1, len(pts)//180)]:
        fill_circle(surf, px, py, thick, color)


# =========================================================================== #
# ALGORITHM 5: COHEN-SUTHERLAND CLIPPING (2D, post-projection screen bounds)
# =========================================================================== #
def cs_clip(x1, y1, x2, y2, xmin, xmax, ymin, ymax):
    def code(x, y):
        c = 0
        c |= 1 if x < xmin else 2 if x > xmax else 0
        c |= 8 if y < ymin else 4 if y > ymax else 0
        return c
    c1, c2 = code(x1, y1), code(x2, y2)
    while True:
        if c1 == 0 and c2 == 0:
            return x1, y1, x2, y2
        if c1 & c2:
            return None
        co = c1 or c2
        if co & 4:
            x, y = x1 + (x2-x1)*(ymax-y1)/(y2-y1), ymax
        elif co & 8:
            x, y = x1 + (x2-x1)*(ymin-y1)/(y2-y1), ymin
        elif co & 2:
            x, y = xmax, y1 + (y2-y1)*(xmax-x1)/(x2-x1)
        else:
            x, y = xmin, y1 + (y2-y1)*(xmin-x1)/(x2-x1)
        if co == c1:
            x1, y1, c1 = x, y, code(x, y)
        else:
            x2, y2, c2 = x, y, code(x, y)


# =========================================================================== #
# ALGORITHM 6: LIANG-BARSKY CLIPPING -- generalized to 3D
# =========================================================================== #
def liang_barsky_2d(x1, y1, x2, y2, xmin, xmax, ymin, ymax):
    dx, dy = x2 - x1, y2 - y1
    p = [-dx, dx, -dy, dy]
    q = [x1-xmin, xmax-x1, y1-ymin, ymax-y1]
    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None
            continue
        t = qi / pi
        if pi < 0:
            if t > u2:
                return None
            u1 = max(u1, t)
        else:
            if t < u1:
                return None
            u2 = min(u2, t)
    return None if u1 > u2 else (x1+u1*dx, y1+u1*dy, x1+u2*dx, y1+u2*dy)


def liang_barsky_3d(p1, p2, box_min, box_max):
    """
    Same parametric clipping idea as the classic 2D Liang-Barsky, just with
    two extra boundary planes for the Z axis. Used here as genuine 3D
    hit-detection: clip a solar flare's full 3D line against the ship's
    axis-aligned bounding box. A non-None result means the beam's line
    actually passes through the box -> the ship got hit.
    """
    d = p2 - p1
    p = [-d[0], d[0], -d[1], d[1], -d[2], d[2]]
    q = [p1[0]-box_min[0], box_max[0]-p1[0],
         p1[1]-box_min[1], box_max[1]-p1[1],
         p1[2]-box_min[2], box_max[2]-p1[2]]
    u1, u2 = 0.0, 1.0
    for pi, qi in zip(p, q):
        if pi == 0:
            if qi < 0:
                return None
            continue
        t = qi / pi
        if pi < 0:
            if t > u2:
                return None
            u1 = max(u1, t)
        else:
            if t < u1:
                return None
            u2 = min(u2, t)
    return None if u1 > u2 else (p1 + u1*d, p1 + u2*d)


# =========================================================================== #
# ALGORITHM 7: SUTHERLAND-HODGMAN POLYGON CLIPPING
# =========================================================================== #
def sutherland_hodgman_clip(polygon, xmin, xmax, ymin, ymax):
    """
    Clips a 2D polygon (list of (x,y) points) against an axis-aligned
    rectangle. Unlike Cohen-Sutherland / Liang-Barsky (which clip LINES),
    this clips a filled AREA -- it walks the polygon around each of the
    four boundary half-planes in turn, keeping points that are inside and
    inserting a new vertex wherever an edge crosses the boundary. Used
    here to clip the ship's hull panels to the screen before filling them.
    """
    def clip_edge(poly, inside, intersect):
        if not poly:
            return []
        result = []
        prev = poly[-1]
        prev_in = inside(prev)
        for curr in poly:
            curr_in = inside(curr)
            if curr_in:
                if not prev_in:
                    result.append(intersect(prev, curr))
                result.append(curr)
            elif prev_in:
                result.append(intersect(prev, curr))
            prev, prev_in = curr, curr_in
        return result

    def make_intersect(axis, bound):
        def intersect(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            if axis == "x":
                t = (bound - x1) / (x2 - x1) if x2 != x1 else 0
                return (bound, y1 + t * (y2 - y1))
            t = (bound - y1) / (y2 - y1) if y2 != y1 else 0
            return (x1 + t * (x2 - x1), bound)
        return intersect

    poly = polygon
    poly = clip_edge(poly, lambda p: p[0] >= xmin, make_intersect("x", xmin))
    poly = clip_edge(poly, lambda p: p[0] <= xmax, make_intersect("x", xmax))
    poly = clip_edge(poly, lambda p: p[1] >= ymin, make_intersect("y", ymin))
    poly = clip_edge(poly, lambda p: p[1] <= ymax, make_intersect("y", ymax))
    return poly


def clip_near_plane(v1, v2, near=NEAR):
    """Clip a view-space line segment against the camera's near plane
    (z = near) so we never divide by a tiny/negative z during projection."""
    z1, z2 = v1[2], v2[2]
    if z1 >= near and z2 >= near:
        return v1, v2
    if z1 < near and z2 < near:
        return None
    t = (near - z1) / (z2 - z1)
    cross = v1 + t * (v2 - v1)
    return (cross, v2) if z1 < near else (v1, cross)


def project_segment(cam, p1_world, p2_world):
    """World-space line segment -> clipped, screen-space endpoints (or
    None if entirely off-screen / behind the camera). Combines near-plane
    clipping with the Cohen-Sutherland screen-rectangle clip."""
    clipped = clip_near_plane(cam.to_view(p1_world), cam.to_view(p2_world))
    if clipped is None:
        return None
    sx1, sy1, _ = cam.project(clipped[0])
    sx2, sy2, _ = cam.project(clipped[1])
    return cs_clip(sx1, sy1, sx2, sy2, 0, WIDTH, 0, HEIGHT)


# =========================================================================== #
# CAMERA / PROJECTION PIPELINE
# =========================================================================== #
def safe_right(forward, up_ref=WORLD_UP):
    """Cross product for the camera's right vector, with a fallback when
    forward is (near) parallel to the up reference -- e.g. the ship flying
    straight up -- which would otherwise produce a degenerate zero vector."""
    r = np.cross(forward, up_ref)
    if np.linalg.norm(r) < 1e-4:
        r = np.cross(forward, np.array([0.0, 0.0, 1.0]))
    return normalize(r)


class ChaseCamera:
    """Follows behind and slightly above the ship, looking in the direction
    of travel. Both position and facing are smoothed (exponential easing)
    so the view doesn't jitter when the ship drifts slowly or reverses."""

    def __init__(self, ship_pos):
        self.look_dir = np.array([0.0, 0.0, 1.0])
        self.pos = ship_pos - self.look_dir * CHASE_DIST + WORLD_UP * CHASE_HEIGHT
        self._recompute(ship_pos)

    def _recompute(self, ship_pos):
        target = ship_pos + self.look_dir * CHASE_LOOKAHEAD
        self.forward = normalize(target - self.pos)
        self.right = safe_right(self.forward)
        self.up = np.cross(self.right, self.forward)

    def update(self, ship_pos, ship_vel):
        speed = np.linalg.norm(ship_vel)
        if speed > MIN_STEER_SPEED:
            desired = normalize(ship_vel)
            self.look_dir = normalize(self.look_dir + (desired - self.look_dir) * CAM_DIR_SMOOTH)

        desired_pos = ship_pos - self.look_dir * CHASE_DIST + WORLD_UP * CHASE_HEIGHT
        self.pos = self.pos + (desired_pos - self.pos) * CAM_POS_SMOOTH
        self._recompute(ship_pos)

    def to_view(self, world_p):
        rel = world_p - self.pos
        return np.array([np.dot(rel, self.right), np.dot(rel, self.up), np.dot(rel, self.forward)])

    def project(self, view_p):
        x, y, z = view_p
        z = max(z, 0.001)
        sx = WIDTH / 2 + (x / z) * FOCAL
        sy = HEIGHT / 2 - (y / z) * FOCAL
        return sx, sy, FOCAL / z

    def light_screen_dir(self, world_pos):
        """Direction toward the sun (origin), as a 2D screen-space unit
        vector, used to decide which side of a sphere gets the highlight."""
        light_dir = normalize(-world_pos)
        vx = np.dot(light_dir, self.right)
        vy = -np.dot(light_dir, self.up)
        d = math.hypot(vx, vy)
        return (vx/d, vy/d) if d > 1e-6 else (0.0, 0.0)


# =========================================================================== #
# PROCEDURAL AUDIO (unchanged approach: numpy synthesis, no external files)
# =========================================================================== #
class Audio:
    def __init__(self):
        self.ok = False
        if not AUDIO_AVAILABLE:
            return
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.sr = 44100
            self.ambient = self._to_sound(self._build_ambient())
            self.chip = self._to_sound(self._build_chiptune())
            self.zap = self._to_sound(self._build_zap())
            self.boom = self._to_sound(self._build_boom())
            self.ambient_ch = pygame.mixer.Channel(0)
            self.chip_ch = pygame.mixer.Channel(1)
            self.fx_ch = pygame.mixer.Channel(2)
            self.ambient_ch.play(self.ambient, loops=-1)
            self.ambient_ch.set_volume(0.5)
            self.chip_ch.play(self.chip, loops=-1)
            self.chip_ch.set_volume(0.0)
            self.ok = True
        except Exception:
            self.ok = False

    def _to_sound(self, mono):
        arr = np.clip(mono, -1, 1)
        arr16 = (arr * 32767).astype(np.int16)
        stereo = np.column_stack([arr16, arr16])
        return pygame.sndarray.make_sound(np.ascontiguousarray(stereo))

    def _tone(self, freq, dur, wave="sine", amp=0.25, fade=0.01):
        sr = self.sr
        t = np.linspace(0, dur, int(sr*dur), endpoint=False)
        w = np.sin(2*np.pi*freq*t) if wave == "sine" else np.sign(np.sin(2*np.pi*freq*t))
        env = np.ones_like(t)
        fn = max(1, int(sr*fade))
        env[:fn] = np.linspace(0, 1, fn)
        env[-fn:] = np.linspace(1, 0, fn)
        return amp * w * env

    def _build_ambient(self):
        sr, dur = self.sr, 8.0
        t = np.linspace(0, dur, int(sr*dur), endpoint=False)
        freqs = [55, 82.5, 110]
        wave = sum(np.sin(2*np.pi*f*t + i*0.7) for i, f in enumerate(freqs))
        lfo = 0.6 + 0.4*np.sin(2*np.pi*0.08*t)
        return (wave/len(freqs)) * lfo * 0.35

    def _build_chiptune(self):
        notes = [220.0, 261.6, 293.7, 329.6, 392.0, 329.6, 293.7, 261.6]
        return np.concatenate([self._tone(f, 0.15, "square", 0.14, 0.008) for f in notes])

    def _build_zap(self):
        sr, dur = self.sr, 0.2
        t = np.linspace(0, dur, int(sr*dur), endpoint=False)
        sweep = np.linspace(950, 200, len(t))
        wave = np.sin(2*np.pi*np.cumsum(sweep)/sr)
        env = np.exp(-np.linspace(0, 6, len(t)))
        return wave * env * 0.3

    def _build_boom(self):
        sr, dur = self.sr, 0.6
        n = int(sr*dur)
        noise = np.random.uniform(-1, 1, n)
        env = np.exp(-np.linspace(0, 7, n))
        return noise * env * 0.55

    def set_intensity(self, t):
        if self.ok:
            self.chip_ch.set_volume(max(0.0, min(0.85, t)))

    def play_zap(self):
        if self.ok:
            self.fx_ch.play(self.zap)

    def play_boom(self):
        if self.ok:
            self.fx_ch.play(self.boom)


# =========================================================================== #
# GAME OBJECTS (all positions are numpy 3-vectors: world space)
# =========================================================================== #
class Star:
    def __init__(self):
        self.dir = normalize(np.random.uniform(-1, 1, 3))
        self.phase = random.uniform(0, math.tau)
        self.speed = random.uniform(0.5, 1.5)
        self.base_r = random.uniform(1.1, 2.0)


class Planet:
    def __init__(self, orbit_r, orbit_speed, radius, mass, color, start_angle):
        self.orbit_r = orbit_r
        self.orbit_speed = orbit_speed
        self.radius = radius
        self.mass = mass
        self.color = color
        self.angle = start_angle

    def update(self):
        self.angle += self.orbit_speed

    def pos(self):
        return np.array([math.cos(self.angle)*self.orbit_r, 0.0, math.sin(self.angle)*self.orbit_r])


def make_planets(zone_index=0):
    """Same orbital layout every system (keeps gravity feel consistent),
    but each zone gets a distinct color palette and a bit of extra variety
    the deeper you travel."""
    base = [(220, 0.021, 12, 220, 0.08), (380, 0.015, 17, 500, 0.30),
            (560, 0.010, 20, 820, 0.55), (760, 0.007, 15, 600, 0.75)]
    hue_shift = (zone_index * 0.31) % 1.0
    rnd = random.Random(zone_index * 97 + 13)
    planets = []
    for orbit_r, orbit_speed, radius, mass, base_hue in base:
        color = hue((base_hue + hue_shift) % 1.0, s=0.55, v=0.9)
        planets.append(Planet(orbit_r, orbit_speed, radius, mass, color, rnd.uniform(0, math.tau)))
    if zone_index >= 2:
        color = hue((0.9 + hue_shift) % 1.0, s=0.6, v=0.95)
        planets.append(Planet(940, 0.005, 18, 715, color, rnd.uniform(0, math.tau)))
    return planets


ORBIT_RING_PTS = 72


SHIP_FACING_SMOOTH = 0.10   # how quickly the ship's visual orientation
                             # eases toward its current velocity direction

# =========================================================================== #
# ALGORITHM 8: BACK-FACE CULLING (Visible Surface Detection)
# =========================================================================== #
# The ship's hull is a small tetrahedron (4 triangular panels). We precompute
# each panel's LOCAL-space outward normal once here at import time -- since
# the ship only ever rotates rigidly (never deforms), these local normals
# stay valid forever; only their world-space ORIENTATION needs updating each
# frame (by rotating them along with the ship's forward/right/up basis,
# exactly like the vertices, but without translation since a normal is a
# direction, not a position).
_s = SHIP_SIZE
SHIP_LOCAL_PTS = {
    "nose":  np.array([_s*1.7, 0.0, 0.0]),
    "lwing": np.array([-_s*0.9,  _s*0.85, -_s*0.2]),
    "rwing": np.array([-_s*0.9, -_s*0.85, -_s*0.2]),
    "ttop":  np.array([-_s*1.1, 0.0,  _s*0.5]),
}
SHIP_TAIL_FIN_LOCAL = np.array([-_s*0.7, 0.0, _s*1.0])
SHIP_FACES = [("nose", "lwing", "rwing"), ("nose", "rwing", "ttop"),
              ("nose", "ttop", "lwing"), ("lwing", "ttop", "rwing")]
SHIP_FACE_COLORS = [(120, 200, 245), (150, 220, 255), (150, 220, 255), (90, 160, 210)]

_centroid = sum(SHIP_LOCAL_PTS.values()) / len(SHIP_LOCAL_PTS)
SHIP_FACE_NORMALS = {}
for _face in SHIP_FACES:
    _p0, _p1, _p2 = (SHIP_LOCAL_PTS[_face[0]], SHIP_LOCAL_PTS[_face[1]], SHIP_LOCAL_PTS[_face[2]])
    _n = np.cross(_p1 - _p0, _p2 - _p0)
    _face_center = (_p0 + _p1 + _p2) / 3
    if np.dot(_n, _face_center - _centroid) < 0:
        _n = -_n
    SHIP_FACE_NORMALS[_face] = normalize(_n)


class Ship:
    def __init__(self):
        start_dir = normalize(np.array([1.0, 0.0, -1.0]))
        r0 = 500.0
        self.pos = start_dir * r0
        v_circ = math.sqrt(G * SUN_MASS / r0)  # true circular velocity -> stable resting orbit
        self.vel = safe_right(start_dir) * v_circ
        self.facing = normalize(self.vel)
        self.thrusting = False

    def apply_gravity(self, sources):
        acc = np.zeros(3)
        for (spos, mass) in sources:
            d = spos - self.pos
            dist = max(MIN_GRAV_DIST, np.linalg.norm(d))
            a = G * mass / (dist * dist)
            acc += a * d / dist
        self.vel += acc

    def update(self, move_dir):
        self.thrusting = np.linalg.norm(move_dir) > 1e-6
        if self.thrusting:
            self.vel += normalize(move_dir) * THRUST

        speed = np.linalg.norm(self.vel)
        if speed > MAX_SPEED:
            self.vel = self.vel / speed * MAX_SPEED

        self.pos += self.vel

        if speed > MIN_STEER_SPEED:
            desired = self.vel / max(speed, 1e-6)
            self.facing = normalize(self.facing + (desired - self.facing) * SHIP_FACING_SMOOTH)

        r = np.linalg.norm(self.pos)
        if r > MAX_RANGE:
            self.pos = self.pos / r * MAX_RANGE

    def hitbox(self):
        return self.pos - SHIP_HITBOX, self.pos + SHIP_HITBOX


class Asteroid:
    def __init__(self, center, diff):
        spawn_dir = normalize(np.random.uniform(-1, 1, 3))
        self.pos = center + spawn_dir * random.uniform(1000, 1150)
        target = center + normalize(np.random.uniform(-1, 1, 3)) * random.uniform(0, 260)
        direction = normalize(target - self.pos)
        speed = random.uniform(1.6, 2.4) + diff * 0.10
        self.vel = direction * speed
        self.radius = random.uniform(14, 26)
        self.hue = random.random()
        self.craters = [(random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4),
                         random.uniform(0.2, 0.35)) for _ in range(3)]
        self.center = center
        self.dead = False

    def update(self, gravity_sources):
        for (spos, mass) in gravity_sources:
            d = spos - self.pos
            dist = max(MIN_GRAV_DIST, np.linalg.norm(d))
            a = (G * 0.3) * mass / (dist * dist)
            self.vel += a * d / dist
        self.pos += self.vel
        if np.linalg.norm(self.pos - self.center) > 1550:
            self.dead = True

    def hits(self, ship):
        return np.linalg.norm(self.pos - ship.pos) < self.radius + SHIP_HITBOX


class DeepSpaceDebris:
    """Sparse drifting rock field for the transit zone between star systems.
    Unlike Asteroid, it spawns and despawns relative to the SHIP's current
    position (there's no central sun to measure from out here). It shares
    the same .pos/.radius/.craters shape as Asteroid so both can be drawn
    by the same rendering code."""
    def __init__(self, ship_pos, travel_dir):
        ahead_bias = travel_dir * random.uniform(120, 800)
        offset = normalize(np.random.uniform(-1, 1, 3)) * random.uniform(350, 1000)
        self.pos = ship_pos + ahead_bias + offset
        self.vel = normalize(np.random.uniform(-1, 1, 3)) * random.uniform(0.8, 2.0)
        self.radius = random.uniform(12, 24)
        self.craters = [(random.uniform(-0.4, 0.4), random.uniform(-0.4, 0.4),
                         random.uniform(0.2, 0.35)) for _ in range(3)]
        self.dead = False

    def update(self, ship_pos):
        self.pos += self.vel
        if np.linalg.norm(self.pos - ship_pos) > DEEPSPACE_DESPAWN:
            self.dead = True

    def hits(self, ship):
        return np.linalg.norm(self.pos - ship.pos) < self.radius + SHIP_HITBOX


class DeepSpaceLaser:
    """A rogue laser beam flashing across deep space near the ship's flight
    path. Same warn -> active -> hit-detection mechanics as a SolarFlare
    (including the same 3D Liang-Barsky check) -- just spawned relative to
    the ship instead of a sun, so it shares SolarFlare's rendering code
    in the main loop without any special-casing."""
    def __init__(self, ship_pos, travel_dir, diff):
        center = (ship_pos + travel_dir * random.uniform(150, 650) +
                  normalize(np.random.uniform(-1, 1, 3)) * random.uniform(80, 300))
        direction = normalize(np.random.uniform(-1, 1, 3))
        length = 900.0
        self.p1 = center - direction * length / 2
        self.p2 = center + direction * length / 2
        self.warn = max(16, 46 - diff*3)
        self.active = 12
        self.t, self.state, self.dead = 0, "warn", False
        self.fired_sound = False

    def update(self):
        self.t += 1
        if self.state == "warn" and self.t >= self.warn:
            self.state, self.t = "active", 0
        elif self.state == "active" and self.t >= self.active:
            self.dead = True

    def just_fired(self):
        if self.state == "active" and not self.fired_sound:
            self.fired_sound = True
            return True
        return False

    def hits(self, ship):
        if self.state != "active":
            return False
        bmin, bmax = ship.hitbox()
        return liang_barsky_3d(self.p1, self.p2, bmin, bmax) is not None


class SolarFlare:
    """A beam erupting from the Sun's surface outward in a random 3D direction."""
    def __init__(self, center, diff):
        direction = normalize(np.random.uniform(-1, 1, 3))
        self.p1 = center + direction * SUN_RADIUS
        self.p2 = center + direction * 1750.0
        self.warn = max(18, 50 - diff*3)
        self.active = 12
        self.t, self.state, self.dead = 0, "warn", False
        self.fired_sound = False

    def update(self):
        self.t += 1
        if self.state == "warn" and self.t >= self.warn:
            self.state, self.t = "active", 0
        elif self.state == "active" and self.t >= self.active:
            self.dead = True

    def just_fired(self):
        if self.state == "active" and not self.fired_sound:
            self.fired_sound = True
            return True
        return False

    def hits(self, ship):
        if self.state != "active":
            return False
        bmin, bmax = ship.hitbox()
        return liang_barsky_3d(self.p1, self.p2, bmin, bmax) is not None


class Particle:
    def __init__(self, pos):
        d = normalize(np.random.uniform(-1, 1, 3))
        self.pos = pos.copy()
        self.vel = d * random.uniform(1.5, 5.0)
        self.life = random.uniform(20, 45)
        self.age = 0
        self.color = hue(random.random())

    def update(self):
        self.pos += self.vel
        self.vel *= 0.95
        self.age += 1

    def dead(self):
        return self.age >= self.life


class MenuCamera:
    """A slow, purely decorative auto-orbiting camera for the title screen
    (separate from ChaseCamera used in actual gameplay -- deliberately
    isolated so menu visuals can never affect play camera behavior)."""
    def __init__(self):
        self.az0 = 0.6

    def basis(self, t):
        az = self.az0 + t * 0.05
        elev = 0.34
        dist = 980.0
        pos = np.array([math.cos(elev)*math.cos(az), math.sin(elev),
                         math.cos(elev)*math.sin(az)]) * dist
        forward = normalize(-pos)
        right = safe_right(forward)
        up = np.cross(right, forward)
        return pos, forward, right, up

    def to_view(self, world_p, pos, right, up, forward):
        rel = world_p - pos
        return np.array([np.dot(rel, right), np.dot(rel, up), np.dot(rel, forward)])

    def project(self, view_p):
        x, y, z = view_p
        z = max(z, 0.001)
        return WIDTH/2 + (x/z)*FOCAL, HEIGHT/2 - (y/z)*FOCAL, FOCAL/z


# =========================================================================== #
# MAIN GAME
# =========================================================================== #
def main():
    pygame.init()
    audio = Audio()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Solar Drift 3D")
    clock = pygame.time.Clock()
    font_big = pygame.font.SysFont("consolas", 46, bold=True)
    font_mid = pygame.font.SysFont("consolas", 24)
    font_small = pygame.font.SysFont("consolas", 16)

    stars = [Star() for _ in range(260)]
    menu_cam = MenuCamera()
    menu_planets = make_planets(0)
    save_data_state = load_data()
    leaderboard = save_data_state["scores"]
    history = save_data_state["history"]
    total_playtime = save_data_state["total_playtime"]
    menu_tab = "scores"    # "scores" or "history"

    def new_game(hs):
        ship = Ship()
        return {"ship": ship, "zone": "system", "zone_index": 0,
                "system_center": np.zeros(3), "beacon": None, "nebula": [],
                "nebula_surface": None,
                "planets": make_planets(0), "asteroids": [], "flares": [],
                "particles": [], "frame": 0, "spawn": 0, "alive": True,
                "high": hs, "cam": ChaseCamera(ship.pos),
                "msg": "System 1", "msg_timer": 90,
                "score_saved": False}

    app_state = "menu"     # "menu" or "playing"
    menu_t = 0
    game = None
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif app_state == "menu":
                    if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                        app_state = "playing"
                        game = new_game(leaderboard[0] if leaderboard else 0)
                    elif e.key == pygame.K_TAB:
                        menu_tab = "history" if menu_tab == "scores" else "scores"
                elif app_state == "playing":
                    if e.key == pygame.K_r and not game["alive"]:
                        game = new_game(game["high"])
                    elif e.key == pygame.K_m and not game["alive"]:
                        d = load_data()
                        leaderboard, history, total_playtime = d["scores"], d["history"], d["total_playtime"]
                        app_state = "menu"

        if app_state == "menu":
            menu_t += 1
            for p in menu_planets:
                p.update()

            screen.fill(BLACK)
            t_sec = menu_t / FPS
            pos, forward, right, up = menu_cam.basis(t_sec)

            for s in stars:
                v = menu_cam.to_view(pos + s.dir * STAR_SHELL_RADIUS, pos, right, up, forward)
                if v[2] < NEAR:
                    continue
                sx, sy, _ = menu_cam.project(v)
                if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
                    b = 0.5 + 0.5 * math.sin(t_sec*s.speed + s.phase)
                    fill_circle(screen, sx, sy, s.base_r, lerp((10, 10, 20), WHITE, b))

            drawables = []
            v = menu_cam.to_view(np.zeros(3), pos, right, up, forward)
            if v[2] > NEAR:
                drawables.append((v[2], "sun", None, v))
            for p in menu_planets:
                v = menu_cam.to_view(p.pos(), pos, right, up, forward)
                if v[2] > NEAR:
                    drawables.append((v[2], "planet", p, v))
            drawables.sort(key=lambda d: d[0], reverse=True)

            for depth, kind, obj, v in drawables:
                sx, sy, scale = menu_cam.project(v)
                if kind == "sun":
                    pulse = 1.0 + 0.08*math.sin(t_sec*2.2)
                    for i, rr in enumerate([SUN_RADIUS*1.6, SUN_RADIUS*1.3, SUN_RADIUS]):
                        col = [(255, 140, 40), (255, 190, 80), (255, 240, 180)][i]
                        fill_circle(screen, sx, sy, rr*pulse*scale, col)
                else:
                    r = obj.radius * scale
                    fill_circle(screen, sx, sy, r, obj.color)

            # Dark backing panel so the tab content stays readable regardless
            # of the decorative sun/planets/stars animating behind it.
            panel_surf = pygame.Surface((420, 300), pygame.SRCALPHA)
            panel_surf.fill((6, 9, 16, 225))
            screen.blit(panel_surf, (WIDTH//2 - 210, 160))

            title_hue = hue((menu_t * 0.002) % 1.0, s=0.5, v=1.0)
            title = font_big.render("SOLAR DRIFT 3D", True, title_hue)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))
            subtitle = font_small.render(
                "An Algorithm-Powered Space Odyssey", True, (170, 200, 230))
            screen.blit(subtitle, (WIDTH//2 - subtitle.get_width()//2, 122))

            # ---- tab headers ----
            tab_scores_col = WHITE if menu_tab == "scores" else (110, 115, 125)
            tab_history_col = WHITE if menu_tab == "history" else (110, 115, 125)
            tab_scores = font_mid.render("TOP SCORES", True, tab_scores_col)
            tab_history = font_mid.render("HISTORY", True, tab_history_col)
            gap = 40
            total_w = tab_scores.get_width() + tab_history.get_width() + gap
            tx = WIDTH//2 - total_w//2
            ty = 182
            screen.blit(tab_scores, (tx, ty))
            screen.blit(tab_history, (tx + tab_scores.get_width() + gap, ty))
            active_x, active_w = (tx, tab_scores.get_width()) if menu_tab == "scores" \
                else (tx + tab_scores.get_width() + gap, tab_history.get_width())
            pygame.draw.line(screen, (120, 200, 255), (active_x, ty+30), (active_x+active_w, ty+30), 2)
            tab_hint = font_small.render("(TAB to switch)", True, (110, 115, 125))
            screen.blit(tab_hint, (WIDTH//2 - tab_hint.get_width()//2, ty + 38))

            panel_top = 262
            if menu_tab == "scores":
                if leaderboard:
                    for i, sc in enumerate(leaderboard[:8]):
                        line = font_small.render(f"{i+1}.  {sc}", True, (220, 225, 235))
                        screen.blit(line, (WIDTH//2 - line.get_width()//2, panel_top + i*24))
                else:
                    none_yet = font_small.render("No runs yet -- be the first!", True, (150, 150, 160))
                    screen.blit(none_yet, (WIDTH//2 - none_yet.get_width()//2, panel_top))
            else:
                total_line = font_small.render(
                    f"Total time played: {format_duration(total_playtime)}", True, (170, 210, 235))
                screen.blit(total_line, (WIDTH//2 - total_line.get_width()//2, panel_top))
                if history:
                    for i, run in enumerate(history[:7]):
                        line_txt = f"Score {run['score']}  --  {run['duration']}s  --  {run['time']}"
                        line = font_small.render(line_txt, True, (210, 215, 225))
                        screen.blit(line, (WIDTH//2 - line.get_width()//2, panel_top + 30 + i*24))
                else:
                    none_yet = font_small.render("No runs recorded yet.", True, (150, 150, 160))
                    screen.blit(none_yet, (WIDTH//2 - none_yet.get_width()//2, panel_top + 30))

            pulse_t = 0.5 + 0.5*math.sin(menu_t * 0.12)
            prompt = font_mid.render("Press SPACE to Launch", True,
                                      lerp((80, 90, 100), (255, 255, 255), pulse_t))
            screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, HEIGHT - 110))
            controls = font_small.render(
                "WASD/Arrows move -- Space up -- Ctrl down -- ESC quit", True, (150, 160, 175))
            screen.blit(controls, (WIDTH//2 - controls.get_width()//2, HEIGHT - 70))

            pygame.display.flip()
            clock.tick(FPS)
            continue

        cam = game["cam"]
        ship = game["ship"]
        cam.update(ship.pos, ship.vel)

        keys = pygame.key.get_pressed()
        if game["alive"]:
            fwd_xz = normalize(np.array([cam.forward[0], 0.0, cam.forward[2]]))
            right_xz = normalize(np.cross(fwd_xz, WORLD_UP))
            move = np.zeros(3)
            if keys[pygame.K_w] or keys[pygame.K_UP]: move += fwd_xz
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: move -= fwd_xz
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move += right_xz
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: move -= right_xz
            if keys[pygame.K_SPACE]: move += WORLD_UP
            if keys[pygame.K_LCTRL] or keys[pygame.K_c]: move -= WORLD_UP

            game["frame"] += 1
            diff = game["frame"] / FPS
            center = game["system_center"]

            gravity_sources = []
            if game["zone"] == "system":
                for p in game["planets"]:
                    p.update()
                gravity_sources = [(center, SUN_MASS)] + \
                                   [(center + p.pos(), p.mass) for p in game["planets"]]

            ship.apply_gravity(gravity_sources)
            ship.update(move)

            travel_dir = normalize(ship.vel) if np.linalg.norm(ship.vel) > 0.05 else fwd_xz

            # ---- spawn hazards ----
            game["spawn"] += 1
            if game["zone"] == "system":
                interval = max(16, int(55 - diff*1.4))
                if game["spawn"] >= interval:
                    game["spawn"] = 0
                    if random.random() < 0.62:
                        game["asteroids"].append(Asteroid(center, diff))
                    else:
                        game["flares"].append(SolarFlare(center, diff))
                for a in game["asteroids"]:
                    a.update(gravity_sources)
            else:  # deep space: dense debris field + rogue lasers
                interval = max(12, int(34 - diff*0.6))
                if game["spawn"] >= interval:
                    game["spawn"] = 0
                    if random.random() < 0.7:
                        game["asteroids"].append(DeepSpaceDebris(ship.pos, travel_dir))
                        if random.random() < 0.4:  # sometimes spawn a second one together
                            game["asteroids"].append(DeepSpaceDebris(ship.pos, travel_dir))
                    else:
                        game["flares"].append(DeepSpaceLaser(ship.pos, travel_dir, diff))
                for a in game["asteroids"]:
                    a.update(ship.pos)

            for f in game["flares"]:
                f.update()
                if f.just_fired():
                    audio.play_zap()

            audio.set_intensity(diff / 30)

            # ---- zone transitions ----
            if game["zone"] == "system" and np.linalg.norm(ship.pos - center) > ESCAPE_RADIUS:
                game["zone"] = "deepspace"
                game["beacon"] = ship.pos + travel_dir * BEACON_DIST
                game["planets"] = []
                game["asteroids"] = []
                game["flares"] = []
                game["nebula"] = generate_nebula_patches(game["frame"])
                game["nebula_surface"] = build_nebula_surface(game["nebula"])
                game["msg"] = "Entering Deep Space..."
                game["msg_timer"] = 120
            elif game["zone"] == "deepspace" and np.linalg.norm(ship.pos - game["beacon"]) < BEACON_CAPTURE:
                game["zone"] = "system"
                game["zone_index"] += 1
                game["system_center"] = game["beacon"]
                game["planets"] = make_planets(game["zone_index"])
                game["asteroids"] = []
                game["msg"] = f"System {game['zone_index']+1} Discovered!"
                game["msg_timer"] = 120
                # Orbital insertion: arriving at high inward speed pointed
                # straight at the new sun would otherwise risk an instant,
                # unavoidable collision. Re-place the ship at a safe orbital
                # radius along the same approach direction and convert its
                # momentum into a tangential (orbit-starting) velocity,
                # rather than snapping speed to zero or teleporting blind.
                center = game["system_center"]
                approach = ship.pos - center
                approach = normalize(approach) if np.linalg.norm(approach) > 1.0 else np.array([0.0, 0.0, -1.0])
                ship.pos = center + approach * 500.0
                ship.vel = safe_right(approach) * math.sqrt(G * SUN_MASS / 500.0)

            center = game["system_center"]  # may have just changed

            # ---- collisions ----
            hit = False
            if game["zone"] == "system":
                if np.linalg.norm(ship.pos - center) < SUN_RADIUS + SHIP_HITBOX:
                    hit = True
                for p in game["planets"]:
                    if np.linalg.norm(ship.pos - (center + p.pos())) < p.radius + SHIP_HITBOX:
                        hit = True
            for a in game["asteroids"]:
                if a.hits(ship):
                    hit = True
            for f in game["flares"]:
                if f.hits(ship):
                    hit = True

            game["asteroids"] = [a for a in game["asteroids"] if not a.dead]
            game["flares"] = [f for f in game["flares"] if not f.dead]

            if hit:
                game["alive"] = False
                audio.play_boom()
                for _ in range(50):
                    game["particles"].append(Particle(ship.pos))
                final_score = int(diff * SCORE_MULTIPLIER)
                game["high"] = max(game["high"], final_score)
                if not game["score_saved"]:
                    game["score_saved"] = True
                    d = record_run(final_score, diff)
                    leaderboard, history, total_playtime = d["scores"], d["history"], d["total_playtime"]

        if game["msg_timer"] > 0:
            game["msg_timer"] -= 1

        for p in game["particles"]:
            p.update()
        game["particles"] = [p for p in game["particles"] if not p.dead()]

        # ---------------- RENDER (3D pipeline) ----------------
        screen.fill(BLACK)
        t_sec = game["frame"] / FPS
        center = game["system_center"]

        # Deep Space nebula backdrop (flat screen-space decoration, built
        # from Flood Fill blobs) -- pre-rendered once at zone entry and
        # cached, so this is just a cheap blit, not a redraw.
        if game["zone"] == "deepspace" and game.get("nebula_surface") is not None:
            screen.blit(game["nebula_surface"], (0, 0))

        # Stars (fixed far points, twinkle brightness)
        for s in stars:
            v = cam.to_view(cam.pos + s.dir * STAR_SHELL_RADIUS)
            if v[2] < NEAR:
                continue
            sx, sy, _ = cam.project(v)
            if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
                b = 0.5 + 0.5 * math.sin(t_sec*s.speed + s.phase)
                col = lerp((10, 10, 20), WHITE, b)
                fill_circle(screen, sx, sy, s.base_r, col)

        # Orbit rings (only in a star system)
        if game["zone"] == "system":
            for p in game["planets"]:
                prev = None
                for i in range(ORBIT_RING_PTS + 1):
                    a = (i / ORBIT_RING_PTS) * math.tau
                    wp = center + np.array([math.cos(a)*p.orbit_r, 0.0, math.sin(a)*p.orbit_r])
                    v = cam.to_view(wp)
                    if v[2] < NEAR:
                        prev = None
                        continue
                    sx, sy, _ = cam.project(v)
                    if prev is not None:
                        c = cs_clip(prev[0], prev[1], sx, sy, 0, WIDTH, 0, HEIGHT)
                        if c:
                            pygame.draw.line(screen, (35, 35, 55), c[0:2], c[2:4], 1)
                    prev = (sx, sy)

        # Solar flares
        for f in game["flares"]:
            v1, v2 = cam.to_view(f.p1), cam.to_view(f.p2)
            clipped = clip_near_plane(v1, v2)
            if clipped is None:
                continue
            cv1, cv2 = clipped
            sx1, sy1, _ = cam.project(cv1)
            sx2, sy2, _ = cam.project(cv2)
            c = cs_clip(sx1, sy1, sx2, sy2, 0, WIDTH, 0, HEIGHT)
            if not c:
                continue
            if f.state == "warn":
                pulse = 0.5 + 0.5*math.sin(f.t*0.4)
                glow_line(screen, *c, lerp((90, 30, 0), (255, 140, 30), pulse), 1+pulse*1.3)
            else:
                glow_line(screen, *c, (255, 220, 120), 3.5)

        # ---- Painter's Algorithm: collect every sphere-like object, sort by
        # ---- depth (farthest first), then draw so nearer things occlude ----
        drawables = []
        if game["zone"] == "system":
            v = cam.to_view(center)
            if v[2] > NEAR:
                drawables.append((v[2], "sun", None, v))
            for p in game["planets"]:
                v = cam.to_view(center + p.pos())
                if v[2] > NEAR:
                    drawables.append((v[2], "planet", p, v))
        else:
            v = cam.to_view(game["beacon"])
            if v[2] > NEAR:
                drawables.append((v[2], "beacon", None, v))
        for a in game["asteroids"]:
            v = cam.to_view(a.pos)
            if v[2] > NEAR:
                drawables.append((v[2], "asteroid", a, v))
        if game["alive"]:
            v = cam.to_view(ship.pos)
            if v[2] > NEAR:
                drawables.append((v[2], "ship", ship, v))
        for pt in game["particles"]:
            v = cam.to_view(pt.pos)
            if v[2] > NEAR:
                drawables.append((v[2], "particle", pt, v))

        drawables.sort(key=lambda d: d[0], reverse=True)

        for depth, kind, obj, v in drawables:
            sx, sy, scale = cam.project(v)
            if not (-50 <= sx < WIDTH+50 and -50 <= sy < HEIGHT+50):
                continue

            if kind == "sun":
                pulse = 1.0 + 0.08*math.sin(t_sec*2.2)
                for i, rr in enumerate([SUN_RADIUS*1.6, SUN_RADIUS*1.3, SUN_RADIUS]):
                    col = [(255, 140, 40), (255, 190, 80), (255, 240, 180)][i]
                    fill_circle(screen, sx, sy, rr*pulse*scale, col)

            elif kind == "beacon":
                pulse = 1.0 + 0.15*math.sin(t_sec*3.0)
                # Outer soft glow stays a circle (Bresenham); the beacon's
                # core marker is a diamond, filled via Scan-Line Polygon
                # Fill after being clipped with Sutherland-Hodgman -- a
                # second, distinct showcase of both algorithms beyond the
                # ship's hull panels.
                glow_r = 28 * 1.7 * pulse * scale
                fill_circle(screen, sx, sy, glow_r, (120, 200, 255))
                d = 28 * pulse * scale
                diamond = [(sx, sy-d), (sx+d, sy), (sx, sy+d), (sx-d, sy)]
                clipped = sutherland_hodgman_clip(diamond, 0, WIDTH, 0, HEIGHT)
                if len(clipped) >= 3:
                    fill_polygon(screen, clipped, (230, 245, 255))

            elif kind == "planet":
                r = obj.radius * scale
                fill_circle(screen, sx, sy, r, obj.color)
                # light source is the current system's sun, at `center`
                light_dir = normalize(center - (center + obj.pos()))
                vx, vy = np.dot(light_dir, cam.right), -np.dot(light_dir, cam.up)
                dn = math.hypot(vx, vy) or 1.0
                lx, ly = vx/dn, vy/dn
                shadow_off = 0.4 * r
                fill_circle(screen, sx - lx*shadow_off, sy - ly*shadow_off,
                            r*0.7, lerp(obj.color, BLACK, 0.55))
                fill_circle(screen, sx + lx*shadow_off*0.5, sy + ly*shadow_off*0.5,
                            r*0.35, lerp(obj.color, WHITE, 0.35))

            elif kind == "asteroid":
                r = obj.radius * scale
                fill_circle(screen, sx, sy, r, (150, 130, 110))
                for (cx, cy, cr) in obj.craters:
                    fill_circle(screen, sx+cx*r, sy+cy*r, max(1, cr*r), (100, 85, 70))

            elif kind == "ship":
                # Soft tracking halo (fixed screen-space size -- see note
                # in earlier profiling: the chase camera keeps the ship at
                # roughly constant distance, so this doesn't need to scale
                # with perspective).
                halo_r = 20 + 3*math.sin(t_sec*4.0)
                for rr, col in [(halo_r, (30, 70, 90)), (halo_r*0.6, (50, 110, 140))]:
                    ring_circle(screen, sx, sy, rr, col)

                # Rotate the ship's precomputed LOCAL hull points/normals
                # into world space using its facing basis (translation for
                # points, rotation-only for normals).
                fwd = obj.facing
                right_v = safe_right(fwd)
                up_v = np.cross(right_v, fwd)
                world_pts = {k: obj.pos + lp[0]*fwd + lp[1]*right_v + lp[2]*up_v
                             for k, lp in SHIP_LOCAL_PTS.items()}

                # ALGORITHM 6 (Back-Face Culling): only the panels whose
                # outward normal faces toward the camera get drawn at all.
                for face, base_col in zip(SHIP_FACES, SHIP_FACE_COLORS):
                    n_local = SHIP_FACE_NORMALS[face]
                    n_world = n_local[0]*fwd + n_local[1]*right_v + n_local[2]*up_v
                    face_center = sum(world_pts[k] for k in face) / 3
                    view_vec = cam.pos - face_center
                    if np.dot(n_world, view_vec) <= 0:
                        continue  # back-facing -- skip entirely, cheap cull

                    views = [cam.to_view(world_pts[k]) for k in face]
                    if any(v[2] < NEAR for v in views):
                        continue  # simple near-plane guard for this small panel
                    screen_pts = [cam.project(v)[:2] for v in views]

                    # ALGORITHM 5 (Sutherland-Hodgman): clip the filled
                    # panel to the screen before rasterizing it.
                    clipped = sutherland_hodgman_clip(screen_pts, 0, WIDTH, 0, HEIGHT)
                    if len(clipped) >= 3:
                        # simple flat shading: brighten faces more square-on to the camera
                        shade = 0.6 + 0.4 * min(1.0, np.dot(n_world, normalize(view_vec)))
                        fill_polygon(screen, clipped, lerp(BLACK, base_col, shade))

                # Tail fin + thruster flame: short accent lines, drawn with
                # ALGORITHM 1b (Bresenham's Line Algorithm).
                seg = project_segment(cam, world_pts["ttop"],
                                       obj.pos + SHIP_TAIL_FIN_LOCAL[0]*fwd +
                                       SHIP_TAIL_FIN_LOCAL[1]*right_v +
                                       SHIP_TAIL_FIN_LOCAL[2]*up_v)
                if seg:
                    bresenham_line(screen, *seg, (200, 235, 255), 2)

                fill_circle(screen, sx, sy, 7, WHITE)

                if obj.thrusting:
                    flick = random.uniform(0.7, 1.3)
                    flame_tip = obj.pos - fwd * (SHIP_SIZE*1.6*flick)
                    seg = project_segment(cam, world_pts["ttop"], flame_tip)
                    if seg:
                        bresenham_line(screen, *seg,
                                  lerp((255, 200, 40), (255, 90, 20), random.random()), 3)

            elif kind == "particle":
                t = 1 - obj.age/obj.life
                r = max(1, min(10, 4*t*scale))
                fill_circle(screen, sx, sy, r, lerp(BLACK, obj.color, t))

        # ---------------- HUD ----------------
        score = int(game["frame"] / FPS * SCORE_MULTIPLIER)
        screen.blit(font_mid.render(f"Score: {score}", True, WHITE), (16, 12))
        screen.blit(font_small.render(f"Best: {game['high']}", True, WHITE), (16, 42))

        if game["zone"] == "system":
            zone_label = f"System {game['zone_index']+1}"
        else:
            dist = np.linalg.norm(ship.pos - game["beacon"])
            zone_label = f"Deep Space -- beacon {int(dist)}m"
        screen.blit(font_small.render(zone_label, True, (170, 200, 230)), (16, 66))

        if game["msg_timer"] > 0:
            alpha_t = min(1.0, game["msg_timer"]/30) if game["msg_timer"] < 30 else 1.0
            msg_surf = font_mid.render(game["msg"], True, lerp(BLACK, (180, 230, 255), alpha_t))
            screen.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, 90))

        if not game["alive"]:
            over = font_big.render("SHIP LOST", True, (255, 90, 60))
            hint = font_mid.render("R to restart -- M for menu", True, WHITE)
            screen.blit(over, (WIDTH//2 - over.get_width()//2, HEIGHT//2 - 60))
            screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()