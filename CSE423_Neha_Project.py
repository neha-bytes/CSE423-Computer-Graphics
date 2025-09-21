# Endless Surf 3D


import time, math, random
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18, GLUT_BITMAP_HELVETICA_12
import ctypes

# ---------------------- State constants ----------------------
MENU, HOW_TO, PLAYING, GAME_OVER = 0, 1, 2, 3

# ---------------------- 2D helpers (overlay HUD/UI) ----------------------
def begin_2d(w, h):
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    gluOrtho2D(0, w, 0, h)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST)

def end_2d():
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_text(x, y, s, r=1, g=1, b=1, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(r, g, b)
    glRasterPos2f(x, y)
    for ch in s:
        glutBitmapCharacter(font, ord(ch))

def text_width(s, font=GLUT_BITMAP_HELVETICA_18):
    buf = s.encode('utf-8')
    c_buf = (ctypes.c_ubyte * len(buf))(*buf)
    return glutBitmapLength(font, c_buf)

# ---------------------- Player model (position, tilt, draw) ----------------------
class Player:
    def __init__(self):
        self.x, self.y, self.z = 0.0, 0.0, -200.0
        self.vx = 0.0
        self.tilt = 0.0

    def update(self, dt, speed_forward, drowning=False, drown_progress=0.0,
               wind_dx=0.0, lane_min_x=-240.0, lane_max_x=240.0):
        self.x += self.vx * dt + wind_dx * dt
        self.x = max(lane_min_x, min(lane_max_x, self.x))
        self.tilt = (self.vx + wind_dx*4.0) * 0.12
        if not drowning:
            self.z += speed_forward * dt


    def draw_human_upright(self):
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)

        # legs
        glColor3f(0.0, 0.0, 1.0)
        glPushMatrix()
        glTranslatef(-8, 0, 0); gluCylinder(gluNewQuadric(), 4, 4, 36, 10, 10)
        glTranslatef(16, 0, 0);  gluCylinder(gluNewQuadric(), 4, 4, 36, 10, 10)
        glPopMatrix()

        # torso
        glColor3f(0.33, 0.66, 0.33)
        glPushMatrix(); glTranslatef(0, 0, 36 + 12); glutSolidCube(24); glPopMatrix()

        # head
        glColor3f(1.0, 0.85, 0.7)
        glPushMatrix(); glTranslatef(0, 0, 36 + 12 + 18); glutSolidSphere(8, 16, 16); glPopMatrix()

        # arms
        glColor3f(1.0, 0.85, 0.7)
        glPushMatrix(); glTranslatef(-18, 0, 36 + 9); gluCylinder(gluNewQuadric(), 3, 3, 18, 8, 8); glPopMatrix()
        glPushMatrix(); glTranslatef( 18, 0, 36 + 9); gluCylinder(gluNewQuadric(), 3, 3, 18, 8, 8); glPopMatrix()

        glPopMatrix()

    def draw(self, blink_timer=0.0, blink_interval=0.15, drowning=False,
             drown_progress=0.0, show_human=True):
        if blink_timer > 0 and not drowning:
            phase = int((blink_timer / blink_interval)) % 2
            if phase == 0:
                return

        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.tilt, 0, 0, 1)

        # surfboard (simple cube)
        glPushMatrix()
        glColor3f(0.9, 0.25, 0.4)
        glTranslatef(0, 0.4, 0)
        glScalef(0.7, 0.12, 2.5)
        glutSolidCube(28)
        glPopMatrix()

        # rider
        if show_human:
            sink = drown_progress if drowning else 0.0
            glPushMatrix()
            glTranslatef(0, 5.0 - sink, 0)
            glScalef(0.85, 0.85, 0.85)
            self.draw_human_upright()
            glPopMatrix()

        glPopMatrix()

# ---------------------- World actors: Obstacle / Coins / Star ----------------------
class Obstacle:
    SHARK, LOG = 0, 1

    def __init__(self, x, z, kind):
        self.x, self.y, self.z = x, 0.0, z
        self.kind = kind
        self.wobble = random.uniform(0, 2*math.pi)

    def draw(self, t, dim=False):
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        if dim:
            glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if self.kind == Obstacle.SHARK:
            (glColor4f(0.35, 0.35, 0.4, 0.35) if dim else glColor3f(0.35, 0.35, 0.4))
            glScalef(1.8, 0.9, 1.0)
            glutSolidSphere(16, 12, 12)
            fin = 12 + 4*math.sin(t*3.0 + self.wobble)
            (glColor4f(0.3, 0.3, 0.35, 0.35) if dim else glColor3f(0.3, 0.3, 0.35))
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 0, 0);  glVertex3f(-18, fin, 6); glVertex3f(18, fin, 6)
            glVertex3f(0, -2, 0); glVertex3f(-16, 4, -6); glVertex3f(-16, -4, 6)
            glVertex3f(0, -2, 0); glVertex3f(16, 4, -6);  glVertex3f(16, -4, 6)
            glEnd()
            if not dim:
                glColor3f(1, 0, 0)
                glPushMatrix(); glTranslatef(10, 2, 10);  glutSolidSphere(2.3, 8, 8);  glPopMatrix()
                glPushMatrix(); glTranslatef(10,-2, 10);  glutSolidSphere(2.3, 8, 8);  glPopMatrix()
        else:
            (glColor4f(0.55, 0.38, 0.2, 0.35) if dim else glColor3f(0.55, 0.38, 0.2))
            glScalef(1.6, 1.0, 2.4)
            glutSolidCube(18)

        if dim: glDisable(GL_BLEND)
        glPopMatrix()

    def hits(self, pl):
        dx, dz = pl.x - self.x, pl.z - self.z
        return (dx*dx + dz*dz) < (28*28)  # circular approx collision

class Coin:
    def __init__(self, x, z):
        self.x, self.y, self.z = x, 10.0, z
        self.spin = random.uniform(0, 360)
        self.bob = random.uniform(0, 2*math.pi)

    def draw(self, dt):
        self.spin = (self.spin + 90*dt) % 360
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.spin, 0, 1, 0)
        glColor3f(1.0, 0.84, 0.0)
        glutSolidSphere(7.5, 12, 12)
        glPopMatrix()

    def picked(self, pl):
        dx = pl.x - self.x
        dz = pl.z - self.z
        return (dx*dx + dz*dz) < (22*22)

class PurpleCoin(Coin):
    def draw(self, dt):
        self.spin = (self.spin + 120*dt) % 360
        self.bob += 1.8*dt
        y = self.y + 2.4*math.sin(self.bob)
        glPushMatrix()
        glTranslatef(self.x, y, self.z)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.8, 0.4, 1.0, 0.18); glutSolidSphere(15, 10, 10)
        glDisable(GL_BLEND)
        glRotatef(self.spin, 0, 1, 0)
        glColor3f(0.6, 0.2, 0.85); glutSolidSphere(8.0, 12, 12)
        glPopMatrix()

class BlackCoin(Coin):
    def draw(self, dt):
        self.spin = (self.spin + 100*dt) % 360
        self.bob += 1.5*dt
        y = self.y + 1.6*math.sin(self.bob)
        glPushMatrix()
        glTranslatef(self.x, y, self.z)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.1, 0.1, 0.1, 0.22); glutSolidSphere(18, 12, 12)
        glDisable(GL_BLEND)
        glRotatef(self.spin, 0, 1, 0)
        glColor3f(0.0, 0.0, 0.0); glutSolidSphere(10.5, 14, 14)
        glPopMatrix()

class Star:
    def __init__(self, x, z):
        self.x, self.y, self.z = x, 14.0, z
        self.spin = random.uniform(0, 360)
        self.bob = random.uniform(0, 2*math.pi)

    def draw(self, dt):
        self.spin = (self.spin + 160*dt) % 360
        glPushMatrix()
        glTranslatef(self.x, self.y, self.z)
        glRotatef(self.spin, 0, 1, 0)
        glColor3f(1.0, 0.92, 0.2)
        for a in (0, 90):
            glPushMatrix(); glRotatef(a, 0, 1, 0)
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 0, 0); glVertex3f(0, 6, 14);  glVertex3f(0, -6, 14)
            glVertex3f(0, 0, 0); glVertex3f(0, 6, -14); glVertex3f(0, -6, -14)
            glEnd()
            glPopMatrix()
        glPopMatrix()

    def picked(self, pl):
        dx = pl.x - self.x
        dz = pl.z - self.z
        return (dx*dx + dz*dz) < (24*24)

# ---------------------- Game core (state, spawn, update, draw) ----------------------
class Game:
    def __init__(self):
        # Window + aspect (used by camera)
        self.w, self.h = 1200, 800
        self.aspect = self.w / float(self.h)

        # main state machine
        self.state = MENU
        self.paused = False

        # motion/speeds (base forward speed; cheats modify effective)
        self.speed = 100.0
        self.base_speed = 100.0
        self.max_speed = 500.0
        self.speed_step = 20.0

        # progression (gain base_speed as coins pass thresholds)
        self.coin_speed_increase_interval = 50
        self.coins_for_next_speed = self.coin_speed_increase_interval

        # player and scoring
        self.player = Player()
        self.start_z = self.player.z
        self.lives = 5
        self.coins = 0
        self.distance_m = 0
        self.score = 0   # score = distance + coins

        # world lists
        self.obstacles = []
        self.coins_list = []
        self.powerups = []

        # spawn pacing (seconds)
        self.last_obs = 0.0
        self.last_coin = 0.0
        self.spawn_gap_obs = 1.4
        self.spawn_gap_coin = 0.9

        # effects and blink
        self.night = False
        self.blink_timer = 0.0
        self.blink_duration = 1.0
        self.blink_interval = 0.15

        # drowning animation setup
        self.drowning = False
        self.drown_progress = 0.0
        self.drown_speed = 30.0

        # lane/buoy guides
        self.buoy_gap = 240.0
        self.lane_min_x = -240.0
        self.lane_max_x = 240.0

        # cheats/power
        self.cheat_active = False       # L
        self.cheat_t_end = 0.0
        self.cheat_k_active = False     # K
        self.cheat_k_end = 0.0
        self.star_active = False
        self.star_t_end = 0.0

        # weather 0=Rain, 1=Windy, 2=Clear cycling /100m
        self.weather_state = 0
        self.last_weather_mark = 0
        self.wind_strength = 0.0
        self.wind_dir = 1.0

        # rare spawns pacing
        self.last_purple = 0.0; self.spawn_gap_purple = 5.0
        self.last_black  = 0.0; self.spawn_gap_black  = 5.0
        self.last_star   = 0.0; self.spawn_gap_star   = 5.0

        # camera modes (3rd, 1st, shoulder)
        self.camera_mode = 0

        # background sprite seeds
        random.seed(42)
        self.stars = [(random.randint(0, self.w), random.randint(int(self.h*0.55), self.h)) for _ in range(140)]
        self.cloud_seeds = [(random.uniform(0, self.w), random.uniform(self.h*0.6, self.h*0.85), random.uniform(60, 120)) for _ in range(7)]
        self.bird_seeds  = [(random.uniform(0, self.w), random.uniform(self.h*0.65, self.h*0.9),  random.uniform(50, 90))  for _ in range(5)]

        # ui button rects computed lazily while drawing
        self.btn_howto = (0,0,0,0)
        self.btn_back  = (0,0,0,0)

    # ---------- helpers ----------
    def lane_rand_x(self):
        return random.uniform(self.lane_min_x, self.lane_max_x)

    def clamp_lane(self, x):
        return max(self.lane_min_x, min(self.lane_max_x, x))

    # ---------- weather ----------
    def set_weather_if_needed(self):
        # Cycle weather every 100 meters of progress
        if self.distance_m - self.last_weather_mark >= 500:
            self.last_weather_mark += 500
            self.weather_state = (self.weather_state + 1) % 3
            if self.weather_state == 0:           # Rain
                self.wind_strength = 0.0
            elif self.weather_state == 1:         # Windy
                self.wind_strength = 1.2
                self.wind_dir = random.choice([-1.0, 1.0])
            else:                                 # Clear
                self.wind_strength = 0.0

    # ---------- cheats/power ----------
    def activate_cheat(self, seconds=20.0):
        if self.cheat_k_active or self.star_active: return
        self.cheat_active = True
        self.cheat_t_end = time.time() + seconds

    def activate_cheat_k(self, seconds=25.0):
        if self.cheat_active or self.star_active: return
        self.cheat_k_active = True
        self.cheat_k_end = time.time() + seconds
        # K-cheat: obstacles convert into regular coins (keeps them in-lane)
        for o in list(self.obstacles):
            ox = self.clamp_lane(o.x)
            self.coins_list.append(Coin(ox, o.z))
            self.obstacles.remove(o)

    def activate_star(self, seconds=20.0):
        if self.cheat_active or self.cheat_k_active: return
        self.star_active = True
        self.star_t_end = time.time() + seconds

    # ---------- spawns ----------
    def spawn_ahead(self):
        zf = self.player.z + 600 + random.uniform(0, 400)

        # K active -> coin-rich path, fewer obstacles
        if self.cheat_k_active:
            if time.time() - self.last_coin > self.spawn_gap_coin*0.8:
                x = self.lane_rand_x()
                self.coins_list.append(PurpleCoin(x, zf + 120) if random.random() < 0.08 else Coin(x, zf + 120))
                self.last_coin = time.time()
        else:
            if time.time() - self.last_obs > self.spawn_gap_obs:
                kind = Obstacle.SHARK if random.random() < 0.5 else Obstacle.LOG
                x = random.uniform(-220, 220)  # near lane (wind may push a bit)
                self.obstacles.append(Obstacle(x, zf, kind))
                self.last_obs = time.time()

        if time.time() - self.last_coin > self.spawn_gap_coin:
            self.coins_list.append(Coin(self.lane_rand_x(), zf + 140))
            self.last_coin = time.time()

        if time.time() - self.last_purple > self.spawn_gap_purple:
            if random.random() < 0.25:
                self.coins_list.append(PurpleCoin(self.lane_rand_x(), zf + 200))
            self.last_purple = time.time()

        if time.time() - self.last_black > self.spawn_gap_black:
            if random.random() < 0.18:
                self.coins_list.append(BlackCoin(self.lane_rand_x(), zf + 260))
            self.last_black = time.time()

        if time.time() - self.last_star > self.spawn_gap_star:
            if random.random() < 0.22:
                self.powerups.append(Star(self.lane_rand_x(), zf + 300))
            self.last_star = time.time()

    # ---------- update (core game logic per frame) ----------
    def update(self, dt):
        now = time.time()
        if self.cheat_active and now >= self.cheat_t_end: self.cheat_active = False
        if self.cheat_k_active and now >= self.cheat_k_end: self.cheat_k_active = False
        if self.star_active and now >= self.star_t_end: self.star_active = False

        # Only update gameplay while playing and not paused
        if self.state != PLAYING and not self.drowning:
            return
        if self.paused and not self.drowning:
            return

        # Effective forward speed; star > K, enforced by activation guard anyway
        eff_speed = self.base_speed
        if self.star_active:
            eff_speed *= 5.0
        elif self.cheat_k_active:
            eff_speed *= 3.0

        # Windy weather: flip wind direction randomly (gentle)
        if self.weather_state == 1:
            if random.random() < 0.05:
                self.wind_dir = -self.wind_dir

        wind_dx = 30.0 * self.wind_strength * self.wind_dir

        if not self.drowning:
            # move player, spawn content
            self.player.update(dt, eff_speed, wind_dx=wind_dx,
                               lane_min_x=self.lane_min_x, lane_max_x=self.lane_max_x)
            self.spawn_ahead()

            # Weather pushes actors sideways (clamped to lane for collectibles)
            if self.weather_state == 1:
                for o in self.obstacles: o.x += wind_dx * 0.3 * dt
                for c in self.coins_list: c.x = self.clamp_lane(c.x + wind_dx * 0.25 * dt)
                for s in self.powerups:   s.x = self.clamp_lane(s.x + wind_dx * 0.2  * dt)

            # Pickups: coins
            for c in list(self.coins_list):
                if c.picked(self.player):
                    if isinstance(c, PurpleCoin): self.coins += 5
                    elif isinstance(c, BlackCoin): self.coins = max(0, self.coins - 10)
                    else: self.coins += 1
                    self.coins_list.remove(c)
                    # Speed progression
                    if self.coins >= self.coins_for_next_speed:
                        self.base_speed = min(self.max_speed, self.base_speed + self.speed_step)
                        self.coins_for_next_speed += self.coin_speed_increase_interval

            # Pickups: star
            for s in list(self.powerups):
                if s.picked(self.player):
                    self.activate_star(20.0)
                    self.powerups.remove(s)

            # Collisions with obstacles
            for o in list(self.obstacles):
                if o.hits(self.player):
                    if not (self.cheat_active or self.star_active):
                        self.lives -= 1
                    self.obstacles.remove(o)
                    self.blink_timer = self.blink_duration
                    if self.lives <= 0 and not (self.cheat_active or self.star_active):
                        self.drowning = True
                        self.drown_progress = 0.0
                        self.state = GAME_OVER
                        self.night = not self.night
                        break

            # Blink decay
            if self.blink_timer > 0:
                self.blink_timer = max(0.0, self.blink_timer - dt)

            # Distance and final score (distance + coins)
            self.distance_m = max(0, int((self.player.z - self.start_z) * 0.10))
            self.score = self.coins + self.distance_m

            # Cull items behind camera
            keep_z = self.player.z - 650
            self.obstacles = [o for o in self.obstacles if o.z > keep_z]
            self.coins_list = [c for c in self.coins_list if c.z > keep_z]
            self.powerups = [p for p in self.powerups if p.z > keep_z]

            # Weather step
            self.set_weather_if_needed()
        else:
            # Play drowning animation smoothly (no forward move)
            self.drown_progress += self.drown_speed * dt
            self.player.update(dt, 0, drowning=True, drown_progress=self.drown_progress,
                               lane_min_x=self.lane_min_x, lane_max_x=self.lane_max_x)

    # ---------- camera ----------
    def set_camera(self):
        # Standard perspective camera and three preset viewpoints
        glMatrixMode(GL_PROJECTION); glLoadIdentity()
        gluPerspective(60, self.aspect, 1.0, 5000.0)
        glMatrixMode(GL_MODELVIEW); glLoadIdentity()
        px, py, pz = self.player.x, self.player.y, self.player.z
        if self.camera_mode == 0:
            gluLookAt(px, py+180, pz-340,  px, py, pz,  0,1,0)
        elif self.camera_mode == 1:
            gluLookAt(px, py+52,  pz+6,    px, py+18, pz+180,  0,1,0)
        else:
            gluLookAt(px, py+110, pz-120,  px, py+60, pz+60,   0,1,0)

    # ---------- water and environment ----------
    def wave_height(self, x, z, t):
        base = 1.8*math.sin(0.035*x + 1.1*t) + 0.8*math.sin(0.018*z + 0.9*t)
        wind_term = self.wind_strength * (0.6*math.sin(0.015*z + 2.2*t) + 0.4*math.sin(0.055*x + 1.7*t))
        return base + wind_term

    def draw_water(self, t):
        for k in range(26):
            z0 = self.player.z - 900 + 70*k
            xL, xR = -340, 340
            y00 = self.wave_height(xL, z0, t);       y10 = self.wave_height(xR, z0, t)
            y11 = self.wave_height(xR, z0 + 68, t);  y01 = self.wave_height(xL, z0 + 68, t)
            glColor4f(0.0, 0.35 + 0.15*self.wind_strength, 0.7, 0.9)
            glBegin(GL_QUADS)
            glVertex3f(xL, y00, z0)
            glVertex3f(xR, y10, z0)
            glVertex3f(xR, y11, z0 + 68)
            glVertex3f(xL, y01, z0 + 68)
            glEnd()

        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1.0, 1.0, 1.0, 0.10 + 0.10*self.wind_strength)
        for k in range(0, 26, 2):
            zc = self.player.z - 900 + 70*k + 8*math.sin(0.8*t + k)
            y = self.wave_height(0, zc, t) + 0.35
            glBegin(GL_QUADS)
            glVertex3f(-340, y, zc)
            glVertex3f( 340, y, zc)
            glVertex3f( 340, y, zc + 2)
            glVertex3f(-340, y, zc + 2)
            glEnd()
        glDisable(GL_BLEND)

    def draw_island(self, x, z, height=60, radius=80):
        glPushMatrix()
        glTranslatef(x, 0, z)
        glColor3f(0.92, 0.85, 0.55); glutSolidSphere(radius*0.65, 18, 18)
        glRotatef(-90, 1, 0, 0)
        glColor3f(0.56, 0.42, 0.24); glutSolidCone(radius*0.45, height, 16, 4)
        glPopMatrix()
        self.draw_palm(x + 12, z, height + 12)

    def draw_palm(self, x, z, h):
        glPushMatrix()
        glTranslatef(x, 0, z)
        glColor3f(0.53, 0.32, 0.12); glRotatef(-90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 3.5, 2.5, h, 8, 2)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(x, h*0.98, z)
        glColor3f(0.1, 0.6, 0.2)
        for a in range(0, 360, 45):
            glPushMatrix(); glRotatef(a, 0, 1, 0)
            glBegin(GL_TRIANGLES)
            glVertex3f(0, 0, 0); glVertex3f(0, 2, 36); glVertex3f(0, -2, 28)
            glEnd(); glPopMatrix()
        glPopMatrix()

    def draw_buoy(self, x, z, t):
        y = self.wave_height(x, z, t) + 0.5*math.sin(2.5*t + (x+z)*0.01)
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(1.0, 0.2, 0.2); glutSolidSphere(8, 12, 12)
        glRotatef(-90, 1, 0, 0)
        glColor3f(0.8, 0.8, 0.85); gluCylinder(gluNewQuadric(), 1.2, 1.2, 24, 8, 1)
        glTranslatef(0, 0, 24)
        glow = 0.5 + 0.5*math.sin(3.0*t + (x+z)*0.01)
        glColor3f(1.0, 0.9*glow, 0.2*glow); glutSolidSphere(2.3, 10, 10)
        glPopMatrix()

    def draw_environment_3d(self, t):
        block = 800.0
        baseI = math.floor(self.player.z / block) * block
        for i in range(-2, 6):
            z = baseI + i*block + 500
            self.draw_island(-520, z, height=70, radius=80)
            self.draw_island( 520, z + 260, height=65, radius=75)

        view_back = 400.0; view_ahead = 2200.0
        baseB = math.floor((self.player.z - view_back) / self.buoy_gap) * self.buoy_gap
        z = baseB
        while z < self.player.z + view_ahead:
            self.draw_buoy(-260, z + 120, t)
            self.draw_buoy( 260, z + 210, t)
            z += self.buoy_gap

    # ---------- sky (menu + overlays) ----------
    def draw_cloud_blob_2d(self, cx, cy, w):
        glColor4f(1,1,1,0.25 if not self.night else 0.18)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(cx, cy)
        for a in range(0, 361, 12):
            ang = math.radians(a)
            rx = w*0.6 + 12*math.sin(ang*3.0)
            ry = w*0.35 + 8*math.cos(ang*2.0)
            glVertex2f(cx + rx*math.cos(ang), cy + ry*math.sin(ang))
        glEnd()
        for off in (-w * 0.3, w * 0.35):
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(cx + off, cy + 5)
            for a in range(0, 361, 12):
                ang = math.radians(a)
                rx = w * 0.35; ry = w * 0.22
                glVertex2f(cx + off + rx * math.cos(ang), cy + 5 + ry * math.sin(ang))
            glEnd()

    def draw_rain_2d(self, t):
        begin_2d(self.w, self.h)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(0.85, 0.9, 1.0, 0.45); glLineWidth(1.6)
        random.seed(int(t*60))
        glBegin(GL_LINES)
        for _ in range(220):
            x = random.randint(0, self.w); y = random.randint(0, self.h)
            glVertex2f(x, y); glVertex2f(x+6, y-18)
        glEnd()
        glDisable(GL_BLEND)
        end_2d()

    def draw_wind_2d(self, t):
        begin_2d(self.w, self.h)
        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glColor4f(1,1,1,0.12); glLineWidth(2)
        glBegin(GL_LINES)
        for k in range(18):
            y = self.h*0.2 + k*(self.h*0.7/18.0)
            phase = (t*120 + k*37) % (self.w+120)
            x0 = (phase * (1 if self.wind_dir>0 else -1)) % (self.w+120) - 60
            glVertex2f(x0-40, y); glVertex2f(x0+40, y)
        glEnd()
        glDisable(GL_BLEND)
        end_2d()

    def draw_sky_2d(self, t):
        begin_2d(self.w, self.h)
        if self.weather_state == 0:
            ctop = (0.10, 0.18, 0.28) if not self.night else (0.04, 0.07, 0.12)
            cbottom = (0.08, 0.12, 0.20) if not self.night else (0.03, 0.05, 0.09)
        elif self.weather_state == 1:
            ctop = (0.32, 0.33, 0.35) if not self.night else (0.14, 0.15, 0.16)
            cbottom = (0.28, 0.29, 0.30) if not self.night else (0.10, 0.11, 0.12)
        else:
            ctop = (0.35, 0.55, 0.95) if not self.night else (0.02, 0.03, 0.07)
            cbottom = (0.80, 0.90, 1.0) if not self.night else (0.10, 0.15, 0.25)

        glBegin(GL_QUADS)
        glColor3f(*ctop);    glVertex2f(0, self.h);   glVertex2f(self.w, self.h)
        glColor3f(*cbottom); glVertex2f(self.w, 0);    glVertex2f(0, 0)
        glEnd()

        glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        # sun/moon disc
        cx = self.w*0.82; cy = self.h*0.82; rad = 36
        (glColor4f(0.9,0.95,1.0,0.95) if self.night else glColor4f(1.0,0.95,0.6,0.95))
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(cx, cy)
        for a in range(0, 361, 8):
            ang = math.radians(a)
            glVertex2f(cx + rad*math.cos(ang), cy + rad*math.sin(ang))
        glEnd()

        # star field at night
        if self.night:
            glPointSize(2)
            glBegin(GL_POINTS)
            glColor4f(1,1,1,0.9)
            for (sx, sy) in self.stars:
                glVertex2f(sx, sy)
            glEnd()

        # drifting clouds
        for (sx, sy, w) in self.cloud_seeds:
            x = (sx + (t*20.0)) % (self.w + 200) - 100
            self.draw_cloud_blob_2d(x, sy, w)

        # flock-like birds
        glLineWidth(2)
        glColor4f(0.05, 0.05, 0.05, 0.7 if not self.night else 0.4)
        glBegin(GL_LINES)
        for (bx, by, spd) in self.bird_seeds:
            xx = (bx + (t*spd*1.2)) % (self.w + 120) - 60
            size = 14
            glVertex2f(xx - size, by); glVertex2f(xx, by + size*0.5)
            glVertex2f(xx, by + size*0.5); glVertex2f(xx + size, by)
        glEnd()

        # MENU panel + button
        if self.state == MENU:
            panel_w, panel_h = self.w*0.7, self.h*0.55
            x0 = (self.w - panel_w)/2; y0 = (self.h - panel_h)/2
            glColor4f(0.0, 0.0, 0.0, 0.7)
            glBegin(GL_QUADS)
            glVertex2f(x0, y0); glVertex2f(x0+panel_w, y0)
            glVertex2f(x0+panel_w, y0+panel_h); glVertex2f(x0, y0+panel_h)
            glEnd()

            title = "Welcome to Enless Surf 3D"
            sub   = "Press enter/space to play"
            draw_text(self.w/2 - text_width(title)/2, y0 + panel_h - 60, title, 1,1,1)
            draw_text(self.w/2 - text_width(sub)/2,   y0 + panel_h - 100, sub, 1,1,0.7)

            btn_w, btn_h = 160, 44
            bx = self.w/2 - btn_w/2
            by = y0 + panel_h/2 + 10
            glColor3f(0.3, 0.5, 0.8)
            glBegin(GL_QUADS)
            glVertex2f(bx, by); glVertex2f(bx+btn_w, by)
            glVertex2f(bx+btn_w, by-btn_h); glVertex2f(bx, by-btn_h)
            glEnd()
            draw_text(bx + 14, by - 30, "HOW TO PLAY", 1,1,1)
            self.btn_howto = (bx, by-btn_h, btn_w, btn_h)

        end_2d()

    # ---------- HUD ----------
    def draw_hud(self):
        begin_2d(self.w, self.h)
        margin = 20

        # score top-left
        draw_text(margin, self.h - 30, f"Score: {self.score}")

        # coins top-middle (fixed y to avoid overlap with other HUD)
        coins_str = f"Coins: {self.coins}"
        draw_text(self.w/2 - text_width(coins_str)/2, self.h - 680, coins_str)

        # lives top-right
        lives_str = f"Lives: {self.lives}"
        draw_text(self.w - text_width(lives_str) - margin, self.h - 30, lives_str)

        # distance center
        dist_str = f"Distance: {self.distance_m} m"
        draw_text(self.w/2 - text_width(dist_str)/2, self.h - 580, dist_str)

        # hint and weather line
        hint = "click l/k to cheat"
        draw_text(self.w/2 - text_width(hint, GLUT_BITMAP_HELVETICA_12)/2, self.h - 780, hint, font=GLUT_BITMAP_HELVETICA_12)
        wtxt = "Rain" if self.weather_state==0 else ("Windy" if self.weather_state==1 else "Clear")
        wlabel = f"Weather: {wtxt}"
        draw_text(self.w/2 - text_width(wlabel, GLUT_BITMAP_HELVETICA_12)/2, self.h - 50, wlabel, font=GLUT_BITMAP_HELVETICA_12)

        # status boxes (cheats/star timers)
        if self.cheat_active:
            remain = max(0.0, self.cheat_t_end - time.time())
            glColor4f(0,0,0,0.35)
            glBegin(GL_QUADS); glVertex2f(10, self.h - 110); glVertex2f(360, self.h - 110); glVertex2f(360, self.h - 140); glVertex2f(10, self.h - 140); glEnd()
            draw_text(20, self.h - 130, f"CHEAT L ACTIVE: {remain:4.1f}s", 1,1,0.2, font=GLUT_BITMAP_HELVETICA_12)

        if self.cheat_k_active:
            remainK = max(0.0, self.cheat_k_end - time.time())
            glColor4f(0,0,0,0.35)
            glBegin(GL_QUADS); glVertex2f(380, self.h - 110); glVertex2f(860, self.h - 110); glVertex2f(860, self.h - 140); glVertex2f(380, self.h - 140); glEnd()
            draw_text(390, self.h - 130, f"CHEAT K ACTIVE: {remainK:4.1f}s (Obstacle->Coins, Speed x3)", 0.8,1.0,0.3, font=GLUT_BITMAP_HELVETICA_12)

        if self.star_active:
            remainS = max(0.0, self.star_t_end - time.time())
            glColor4f(0,0,0,0.35)
            glBegin(GL_QUADS); glVertex2f(10, self.h - 160); glVertex2f(420, self.h - 160); glVertex2f(420, self.h - 190); glVertex2f(10, self.h - 190); glEnd()
            draw_text(20, self.h - 180, f"STAR BOOST: {remainS:4.1f}s (Speed x5 + Harmless Obstacles)", 1.0,0.95,0.2, font=GLUT_BITMAP_HELVETICA_12)

        # pause banner
        if self.paused and self.state == PLAYING:
            pmsg = "PAUSED - Press P to Resume"
            draw_text(self.w/2 - text_width(pmsg)/2, self.h/2 + 40, pmsg, 1,1,0.3)

        end_2d()

    def draw_how_to(self):
        begin_2d(self.w, self.h)
        panel_w, panel_h = self.w * 0.75, self.h * 0.62
        x0 = (self.w - panel_w)/2; y0 = (self.h - panel_h)/2
        glColor4f(0,0,0,0.82)
        glBegin(GL_QUADS)
        glVertex2f(x0, y0); glVertex2f(x0+panel_w, y0)
        glVertex2f(x0+panel_w, y0+panel_h); glVertex2f(x0, y0+panel_h)
        glEnd()

        y = y0 + panel_h - 50
        lh = 24
        draw_text(x0+20, y, "How to Play", 1,1,0.9); y -= lh
        draw_text(x0+20, y, "- A/D to move left/right; N toggles night; C or 1/2/3 switches camera", 1,1,1, GLUT_BITMAP_HELVETICA_12); y -= lh
        draw_text(x0+20, y, "- L cheat: invincible, obstacles dim for 20s", 1,1,1, GLUT_BITMAP_HELVETICA_12); y -= lh
        draw_text(x0+20, y, "- K cheat: turn all obstacles to coins and speed x3 for 25s", 1,1,1, GLUT_BITMAP_HELVETICA_12); y -= lh
        draw_text(x0+20, y, "- Star power-up: speed x5 and obstacles harmless for 20s", 1,1,1, GLUT_BITMAP_HELVETICA_12); y -= lh
        draw_text(x0+20, y, "- Yellow coin +1, Purple coin +5 (rare), Black coin -10 (penalty, bigger)", 1,1,1, GLUT_BITMAP_HELVETICA_12); y -= lh
        draw_text(x0+20, y, "- Weather cycles /100m: Rain, Windy (random push L/R), Clear", 1,1,1, GLUT_BITMAP_HELVETICA_12); y -= lh
        draw_text(x0+20, y, "- Lose all 5 lives to end game; Press R to restart; ESC to quit; P to pause/resume", 1,1,1, GLUT_BITMAP_HELVETICA_12); y -= lh*2

        # back button
        btn_w, btn_h = 120, 40
        bx = x0 + 20
        by = y0 + 20 + btn_h
        glColor3f(0.75, 0.25, 0.25)
        glBegin(GL_QUADS)
        glVertex2f(bx, by); glVertex2f(bx+btn_w, by)
        glVertex2f(bx+btn_w, by-btn_h); glVertex2f(bx, by-btn_h)
        glEnd()
        draw_text(bx + 20, by - 28, "BACK", 1,1,1)

        self.btn_back = (bx, by-btn_h, btn_w, btn_h)

        # enter/space starts from HOW_TO too
        start_hint = "Press ENTER/SPACE to Start"
        draw_text(self.w/2 - text_width(start_hint)/2, y0 + 28, start_hint, 1,1,0.7)

        end_2d()

    def draw_game_over(self):
        begin_2d(self.w, self.h)
        draw_text(self.w/2 - text_width("GAME OVER")/2, self.h/2 + 80, "GAME OVER", 1,0.3,0.3)
        draw_text(self.w/2 - text_width(f"Distance: {self.distance_m} m")/2, self.h/2 + 30, f"Distance: {self.distance_m} m", 1,1,1)
        draw_text(self.w/2 - text_width(f"Coins: {self.coins}")/2, self.h/2 + 0, f"Coins: {self.coins}", 1,1,1)
        draw_text(self.w/2 - text_width(f"Score: {self.score}")/2, self.h/2 - 30, f"Score: {self.score}", 1,1,1)
        draw_text(self.w/2 - text_width("Press R to Restart or ESC to Quit")/2, self.h/2 - 90, "Press R to Restart or ESC to Quit", 0.9,0.9,0.9)
        end_2d()

    # ---------- main draw ----------
    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        t = glutGet(GLUT_ELAPSED_TIME)/1000.0
        self.draw_sky_2d(t)

        # Early returns for menu/how-to so we don’t render 3D unnecessarily
        if self.state == MENU:
            glutSwapBuffers(); return
        if self.state == HOW_TO:
            self.draw_how_to(); glutSwapBuffers(); return

        glEnable(GL_DEPTH_TEST)
        self.set_camera()
        self.draw_water(t)
        self.draw_environment_3d(t)

        # world actors
        for o in self.obstacles: o.draw(t, dim=(self.cheat_active or self.star_active))
        for c in self.coins_list: c.draw(1/60.0)
        for p in self.powerups:   p.draw(1/60.0)

        # player (hide human mesh in first-person)
        first_person = (self.camera_mode == 1)
        if self.state == PLAYING or self.drowning:
            self.player.draw(self.blink_timer, self.blink_interval, self.drowning, self.drown_progress, show_human=not first_person)

        # weather overlays
        if self.weather_state == 0: self.draw_rain_2d(t)
        elif self.weather_state == 1: self.draw_wind_2d(t)

        # HUD or game over
        if self.state == PLAYING: self.draw_hud()
        elif self.state == GAME_OVER: self.draw_game_over()

        glutSwapBuffers()

    # ---------- mouse UI ----------
    def mouse_click(self, button, state, mx, my):
        if state != GLUT_DOWN or button != GLUT_LEFT_BUTTON:
            return
        px = mx
        py = self.h - my

        if self.state == MENU:
            bx, by, bw, bh = self.btn_howto
            if bx <= px <= bx+bw and by <= py <= by+bh:
                self.state = HOW_TO
                return

        if self.state == HOW_TO:
            bx, by, bw, bh = self.btn_back
            if bx <= px <= bx+bw and by <= py <= by+bh:
                self.state = MENU
                return

# ---------------------- GLUT wiring (display/idle/input) ----------------------
game = Game()

def display():
    game.draw()

def idle():
    dt = 1/60.0
    game.update(dt)
    glutPostRedisplay()

def keyboard(k, x, y):
    k = k.decode().lower()

    # MENU
    if game.state == MENU:
        if k in ('\r', '\n', ' '): game.state = PLAYING
        elif k == '\x1b': glutLeaveMainLoop()
        return

    # HOW_TO
    if game.state == HOW_TO:
        if k in ('\r', '\n', ' '): game.state = PLAYING
        elif k == '\x1b': game.state = MENU
        return

    # PLAYING or drowning animation
    if game.state == PLAYING or game.drowning:
        if k == '\x1b': glutLeaveMainLoop()
        elif k == 'a': game.player.vx = 100.0
        elif k == 'd': game.player.vx = -100.0
        elif k == 'n': game.night = not game.night
        elif k == 'l': game.activate_cheat(20.0)
        elif k == 'k': game.activate_cheat_k(25.0)
        elif k == 'c': game.camera_mode = (game.camera_mode + 1) % 3
        elif k == '1': game.camera_mode = 0
        elif k == '2': game.camera_mode = 1
        elif k == '3': game.camera_mode = 2
        elif k == 'p': game.paused = not game.paused
        elif k == 'r': restart()

    elif game.state == GAME_OVER:
        if k == '\x1b': glutLeaveMainLoop()
        elif k == 'r': restart()

def keyup(k, x, y):
    k = k.decode().lower()
    if k in ('a', 'd'):
        game.player.vx = 0.0

def mouse(button, state, mx, my):
    game.mouse_click(button, state, mx, my)

def restart():
    global game
    game = Game()
    game.state = PLAYING

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(game.w, game.h)
    glutInitWindowPosition(80, 60)
    glutCreateWindow(b"Endless Surf 3D")
    glEnable(GL_DEPTH_TEST)

    glutDisplayFunc(display)
    glutIdleFunc(idle)
    glutKeyboardFunc(keyboard)
    glutMouseFunc(mouse)
    try:
        glutKeyboardUpFunc(keyup)
    except:
        pass

    glutMainLoop()

if __name__ == "__main__":
    main()