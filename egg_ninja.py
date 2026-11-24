import math
import random
import time
import pygame
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# ----------------- Audio Setup -----------------
pygame.mixer.init()

try:
    pygame.mixer.music.load("bgm.mp3")
    pygame.mixer.music.set_volume(0.45)
    pygame.mixer.music.play(-1)
    print("Background music started!")
except Exception as e:
    print(f"Error loading BGM: {e}")

try:
    scream_sound = pygame.mixer.Sound("scream.wav")
    scream_sound.set_volume(0.35)
except Exception as e:
    print(f"Error loading scream sound: {e}")
    scream_sound = None

try:
    gameover_sound = pygame.mixer.Sound("gameover.wav")
    gameover_sound.set_volume(0.8)
except Exception as e:
    print(f"Game over sound error: {e}")
    gameover_sound = None


WIDTH = 1000
HEIGHT = 700

GRAVITY = 0.6
SPAWN_INTERVAL = 0.7
TRAIL_LENGTH = 12

EGG_TYPES = [
    "egg_red",
    "egg_blue",
    "egg_green",
    "egg_yellow",
    "egg_purple"
]

OBJECT_TYPES = EGG_TYPES + ["bomb", "bomb"]

EGG_COLORS = {
    "egg_red": (55, 55, 220),
    "egg_blue": (220, 100, 45),
    "egg_green": (65, 175, 75),
    "egg_yellow": (0, 215, 245),
    "egg_purple": (175, 70, 180)
}

# Diverse character presets: (skin_color, hair_color, shirt_color, hair_style, name)
CHARACTER_PRESETS = [
    # African: warm dark skin, short dark curly hair, vibrant cyan/orange shirt
    {
        "ethnicity": "african",
        "skin": (35, 55, 85),
        "skin_shadow": (20, 35, 55),
        "hair": (15, 15, 20),
        "hair_style": "short_afro",
        "shirt": (0, 140, 240)
    },
    # East Asian: fair skin tone, straight dark sleek hair
    {
        "ethnicity": "asian",
        "skin": (180, 215, 250),
        "skin_shadow": (145, 175, 210),
        "hair": (20, 20, 25),
        "hair_style": "straight_bangs",
        "shirt": (210, 60, 50)
    },
    # European (Blonde): light skin, golden blonde hair
    {
        "ethnicity": "european_blonde",
        "skin": (195, 225, 255),
        "skin_shadow": (160, 185, 220),
        "hair": (70, 190, 235),
        "hair_style": "messy_spiky",
        "shirt": (60, 175, 95)
    },
    # European / Latino (Brunette): rosy/peach skin, wavy brown hair
    {
        "ethnicity": "european_brown",
        "skin": (170, 205, 245),
        "skin_shadow": (130, 165, 205),
        "hair": (30, 65, 110),
        "hair_style": "wavy",
        "shirt": (160, 60, 160)
    },
    # Middle Eastern / South Asian: olive/warm tan skin, thick jet black hair
    {
        "ethnicity": "middle_eastern",
        "skin": (110, 160, 210),
        "skin_shadow": (80, 120, 165),
        "hair": (15, 15, 18),
        "hair_style": "pompadour",
        "shirt": (40, 210, 220)
    }
]

detector = HandDetector(
    maxHands=1,
    detectionCon=0.7,
    minTrackCon=0.7
)


def egg_points(x, y, radius, angle=0.0, scale=1.0):
    points = []
    width = radius * 0.82 * scale
    height = radius * 1.08 * scale

    cos_angle = math.cos(angle)
    sin_angle = math.sin(angle)

    for i in range(32):
        theta = (2.0 * math.pi * i) / 32.0
        vertical_ratio = (math.sin(theta) + 1.0) / 2.0
        width_factor = 0.72 + 0.28 * vertical_ratio

        local_x = math.cos(theta) * width * width_factor
        local_y = math.sin(theta) * height

        rotated_x = local_x * cos_angle - local_y * sin_angle
        rotated_y = local_x * sin_angle + local_y * cos_angle

        points.append([int(x + rotated_x), int(y + rotated_y)])

    return np.array(points, dtype=np.int32)


def lighter_color(color, amount=45):
    return tuple(min(255, channel + amount) for channel in color)

class Target:
    def __init__(self, speed_multiplier=1.0):
        self.reset(speed_multiplier)

    def reset(self, speed_multiplier=1.0):
        self.x = random.randint(150, WIDTH - 150)
        self.y = HEIGHT - 10

        # Scale launch velocities with speed_multiplier
        base_vx = random.uniform(-4, 4)
        base_vy = random.uniform(-23, -17)

        self.vx = base_vx * speed_multiplier
        self.vy = base_vy * speed_multiplier

        # Keep other existing properties intact (radius, type, sliced, etc.)

class FlyingObject:
    def __init__(self, kind, speed_multiplier=1.0):
        self.kind = kind
        self.speed_multiplier = speed_multiplier
        self.radius = random.randint(48, 64)
        self.x = random.randint(80, WIDTH - 80)
        self.y = HEIGHT + self.radius

        # Scale launch velocities with speed multiplier
        self.vx = random.uniform(-5.5, 5.5) * speed_multiplier
        self.vy = random.uniform(-28.0, -24.0) * speed_multiplier

        self.angle = random.uniform(-0.5, 0.5)
        self.spin = random.uniform(-0.07, 0.07)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += GRAVITY * self.speed_multiplier
        self.angle += self.spin

    def draw(self, frame):
        draw_object(
            frame,
            self.kind,
            int(self.x),
            int(self.y),
            self.radius,
            self.angle
        )


class EggHalf:
    def __init__(self, egg, side):
        self.kind = egg.kind
        self.x = egg.x + side * 14
        self.y = egg.y
        self.radius = egg.radius
        self.side = side
        self.angle = egg.angle

        self.vx = egg.vx * 0.5 + side * random.uniform(4.0, 7.5)
        self.vy = random.uniform(8.0, 14.0)
        self.gravity = 1.3
        self.spin = side * random.uniform(0.1, 0.2)
        self.life = 85

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.spin
        self.life -= 1

    def draw(self, frame):
        draw_half_egg(
            frame,
            self.kind,
            int(self.x),
            int(self.y),
            self.radius,
            self.side,
            self.angle
        )


class ScreamingCharacter:
    def __init__(self, egg):
        self.x = egg.x
        self.y = egg.y
        self.size = max(46, int(egg.radius * 0.95))
        self.preset = random.choice(CHARACTER_PRESETS)

        self.vx = egg.vx * 0.25
        self.vy = -4.5
        self.gravity = 0.75
        self.timer = 28
        self.wiggle = 0.0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.timer -= 1
        self.wiggle += 0.45

    def draw(self, frame):
        scale = self.size / 56.0
        draw_detailed_character(
            frame,
            int(self.x),
            int(self.y),
            scale,
            self.preset,
            self.timer,
            self.wiggle
        )

    def split_into_pieces(self):
        size = self.size
        p = self.preset

        return [
            CharacterPiece(
                "head",
                self.x,
                self.y - int(size * 0.55),
                random.uniform(-5.0, 5.0),
                random.uniform(-9.5, -4.5),
                int(size * 0.32),
                p
            ),
            CharacterPiece(
                "body",
                self.x,
                self.y - int(size * 0.05),
                random.uniform(-4.0, 4.0),
                random.uniform(-5.0, 0.0),
                int(size * 0.35),
                p
            ),
            CharacterPiece(
                "arm",
                self.x - int(size * 0.32),
                self.y - int(size * 0.1),
                random.uniform(-8.0, -3.0),
                random.uniform(-7.5, -1.5),
                int(size * 0.26),
                p
            ),
            CharacterPiece(
                "arm",
                self.x + int(size * 0.32),
                self.y - int(size * 0.1),
                random.uniform(3.0, 8.0),
                random.uniform(-7.5, -1.5),
                int(size * 0.26),
                p
            ),
            CharacterPiece(
                "leg",
                self.x - int(size * 0.15),
                self.y + int(size * 0.4),
                random.uniform(-5.0, 0.0),
                random.uniform(-2.0, 3.5),
                int(size * 0.28),
                p
            ),
            CharacterPiece(
                "leg",
                self.x + int(size * 0.15),
                self.y + int(size * 0.4),
                random.uniform(0.0, 5.0),
                random.uniform(-2.0, 3.5),
                int(size * 0.28),
                p
            )
        ]


class CharacterPiece:
    def __init__(self, kind, x, y, vx, vy, size, preset):
        self.kind = kind
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.preset = preset
        self.gravity = 1.25
        self.angle = random.uniform(-0.5, 0.5)
        self.spin = random.uniform(-0.16, 0.16)
        self.life = 95

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.angle += self.spin
        self.life -= 1

    def draw(self, frame):
        draw_character_piece(
            frame,
            self.kind,
            int(self.x),
            int(self.y),
            self.size,
            self.angle,
            self.preset
        )


def draw_object(frame, kind, x, y, radius, angle):
    if kind.startswith("egg_"):
        draw_egg(frame, kind, x, y, radius, angle)
    elif kind == "bomb":
        draw_bomb(frame, x, y, radius)


def draw_egg(frame, kind, x, y, radius, angle):
    color = EGG_COLORS[kind]
    outer_points = egg_points(x, y, radius, angle)
    inner_points = egg_points(
        x - int(radius * 0.04),
        y - int(radius * 0.05),
        int(radius * 0.91),
        angle
    )

    cv2.fillPoly(frame, [outer_points], color)
    cv2.fillPoly(frame, [inner_points], lighter_color(color, 25))
    cv2.polylines(frame, [outer_points], True, (245, 245, 245), 2, cv2.LINE_AA)

    highlight_x = int(x - radius * 0.27)
    highlight_y = int(y - radius * 0.38)
    cv2.ellipse(
        frame,
        (highlight_x, highlight_y),
        (max(4, radius // 8), max(7, radius // 5)),
        -25,
        0,
        360,
        (255, 255, 255),
        -1,
        cv2.LINE_AA
    )


def draw_half_egg(frame, kind, x, y, radius, side, angle):
    color = EGG_COLORS[kind]
    points = egg_points(x, y, radius, angle)

    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.fillPoly(mask, [points], 255)

    half_mask = np.zeros_like(mask)
    if side < 0:
        half_mask[:, :x] = mask[:, :x]
    else:
        half_mask[:, x:] = mask[:, x:]

    frame[half_mask > 0] = color

    cv2.line(
        frame,
        (x, y - radius),
        (x, y + radius),
        (250, 250, 250),
        3,
        cv2.LINE_AA
    )

    edge_points = points.copy()
    if side < 0:
        edge_points[:, 0] = np.minimum(edge_points[:, 0], x)
    else:
        edge_points[:, 0] = np.maximum(edge_points[:, 0], x)

    cv2.polylines(frame, [edge_points], False, (245, 245, 245), 2, cv2.LINE_AA)


def draw_hair(frame, cx, cy, radius, style, hair_color):
    if style == "short_afro":
        for angle_deg in range(160, 381, 28):
            rad = math.radians(angle_deg)
            px = int(cx + (radius + 3) * math.cos(rad))
            py = int(cy + (radius + 2) * math.sin(rad))
            cv2.circle(frame, (px, py), int(radius * 0.36), hair_color, -1, cv2.LINE_AA)
            cv2.circle(frame, (px, py), int(radius * 0.36), (10, 10, 15), 1, cv2.LINE_AA)

    elif style == "straight_bangs":
        pts = np.array([
            [cx - int(radius * 1.15), cy],
            [cx - int(radius * 1.1), cy - int(radius * 1.1)],
            [cx, cy - int(radius * 1.3)],
            [cx + int(radius * 1.1), cy - int(radius * 1.1)],
            [cx + int(radius * 1.15), cy],
            [cx + int(radius * 0.8), cy - int(radius * 0.35)],
            [cx, cy - int(radius * 0.45)],
            [cx - int(radius * 0.8), cy - int(radius * 0.35)]
        ], np.int32)
        cv2.fillPoly(frame, [pts], hair_color)
        cv2.polylines(frame, [pts], True, (15, 15, 20), 1, cv2.LINE_AA)

    elif style == "messy_spiky":
        spikes = [
            (cx - int(radius * 1.05), cy - int(radius * 0.2)),
            (cx - int(radius * 0.95), cy - int(radius * 1.1)),
            (cx - int(radius * 0.4), cy - int(radius * 1.45)),
            (cx + int(radius * 0.1), cy - int(radius * 1.35)),
            (cx + int(radius * 0.65), cy - int(radius * 1.4)),
            (cx + int(radius * 1.05), cy - int(radius * 0.95)),
            (cx + int(radius * 1.05), cy - int(radius * 0.2)),
            (cx + int(radius * 0.5), cy - int(radius * 0.5)),
            (cx - int(radius * 0.5), cy - int(radius * 0.5))
        ]
        pts = np.array(spikes, np.int32)
        cv2.fillPoly(frame, [pts], hair_color)
        cv2.polylines(frame, [pts], True, (25, 25, 30), 1, cv2.LINE_AA)

    elif style == "wavy":
        cv2.ellipse(frame, (cx, cy - int(radius * 0.6)),
                    (int(radius * 1.18), int(radius * 0.85)), 0, 160, 380, hair_color, -1, cv2.LINE_AA)
        cv2.circle(frame, (cx - int(radius * 1.0), cy - int(radius * 0.1)), int(radius * 0.35), hair_color, -1, cv2.LINE_AA)
        cv2.circle(frame, (cx + int(radius * 1.0), cy - int(radius * 0.1)), int(radius * 0.35), hair_color, -1, cv2.LINE_AA)

    elif style == "pompadour":
        cv2.ellipse(frame, (cx, cy - int(radius * 0.8)),
                    (int(radius * 1.1), int(radius * 0.85)), -15, 0, 360, hair_color, -1, cv2.LINE_AA)


def draw_detailed_character(frame, x, y, scale, preset, timer, wiggle):
    skin = preset["skin"]
    hair = preset["hair"]
    shirt = preset["shirt"]
    style = preset["hair_style"]
    black = (20, 20, 25)
    white = (250, 250, 250)

    wiggle_x = int(math.sin(wiggle) * 3)

    head_r = max(13, int(18 * scale))
    body_w = max(13, int(18 * scale))
    body_h = max(20, int(29 * scale))

    head_x = x + wiggle_x
    head_y = y - int(34 * scale)
    body_x = x
    body_y = y

    # Torso
    cv2.ellipse(frame, (body_x, body_y), (body_w, body_h), 0, 0, 360, shirt, -1, cv2.LINE_AA)
    cv2.ellipse(frame, (body_x, body_y), (body_w, body_h), 0, 0, 360, black, 2, cv2.LINE_AA)

    # Collar detail
    cv2.circle(frame, (body_x, body_y - int(body_h * 0.8)), max(2, int(4 * scale)), skin, -1, cv2.LINE_AA)

    # Arms
    hand_y = head_y + int(3 * scale)
    shoulder_y = body_y - int(10 * scale)
    arm_thick = max(3, int(5 * scale))

    cv2.line(frame, (body_x - body_w + 3, shoulder_y), (head_x - head_r - int(4 * scale), hand_y), skin, arm_thick, cv2.LINE_AA)
    cv2.line(frame, (body_x - body_w + 3, shoulder_y), (head_x - head_r - int(4 * scale), hand_y), black, 1, cv2.LINE_AA)
    cv2.circle(frame, (head_x - head_r, hand_y), max(3, int(5 * scale)), skin, -1, cv2.LINE_AA)

    cv2.line(frame, (body_x + body_w - 3, shoulder_y), (head_x + head_r + int(4 * scale), hand_y), skin, arm_thick, cv2.LINE_AA)
    cv2.line(frame, (body_x + body_w - 3, shoulder_y), (head_x + head_r + int(4 * scale), hand_y), black, 1, cv2.LINE_AA)
    cv2.circle(frame, (head_x + head_r, hand_y), max(3, int(5 * scale)), skin, -1, cv2.LINE_AA)

    # Legs
    leg_y = body_y + body_h - 2
    leg_offset = int(math.sin(wiggle * 1.5) * 4)
    cv2.line(frame, (body_x - int(7 * scale), leg_y), (body_x - int(15 * scale) + leg_offset, leg_y + int(24 * scale)), (35, 45, 60), arm_thick, cv2.LINE_AA)
    cv2.line(frame, (body_x + int(7 * scale), leg_y), (body_x + int(15 * scale) - leg_offset, leg_y + int(24 * scale)), (35, 45, 60), arm_thick, cv2.LINE_AA)

    # Head and Hair
    draw_hair(frame, head_x, head_y, head_r, style, hair)
    cv2.circle(frame, (head_x, head_y), head_r, skin, -1, cv2.LINE_AA)
    cv2.circle(frame, (head_x, head_y), head_r, black, 2, cv2.LINE_AA)

    # Eyes
    eye_offset_x = int(6 * scale)
    eye_offset_y = int(3 * scale)
    eye_radius = max(3, int(5 * scale))

    cv2.circle(frame, (head_x - eye_offset_x, head_y - eye_offset_y), eye_radius, white, -1, cv2.LINE_AA)
    cv2.circle(frame, (head_x + eye_offset_x, head_y - eye_offset_y), eye_radius, white, -1, cv2.LINE_AA)
    cv2.circle(frame, (head_x - eye_offset_x, head_y - eye_offset_y), eye_radius, black, 1, cv2.LINE_AA)
    cv2.circle(frame, (head_x + eye_offset_x, head_y - eye_offset_y), eye_radius, black, 1, cv2.LINE_AA)

    pupil_r = max(1, int(2 * scale))
    cv2.circle(frame, (head_x - eye_offset_x, head_y - eye_offset_y), pupil_r, black, -1, cv2.LINE_AA)
    cv2.circle(frame, (head_x + eye_offset_x, head_y - eye_offset_y), pupil_r, black, -1, cv2.LINE_AA)

    # Eyebrows
    brow_y = head_y - eye_offset_y - int(4 * scale)
    cv2.line(frame, (head_x - eye_offset_x - 3, brow_y + 2), (head_x - 2, brow_y - 2), black, 2, cv2.LINE_AA)
    cv2.line(frame, (head_x + 2, brow_y - 2), (head_x + eye_offset_x + 3, brow_y + 2), black, 2, cv2.LINE_AA)

    # Mouth
    mouth_w = max(4, int(6 * scale))
    mouth_h = max(6, int(10 * scale))
    mouth_center = (head_x, head_y + int(8 * scale))

    cv2.ellipse(frame, mouth_center, (mouth_w, mouth_h), 0, 0, 360, (25, 25, 30), -1, cv2.LINE_AA)
    cv2.ellipse(frame, mouth_center, (mouth_w, mouth_h), 0, 0, 360, black, 1, cv2.LINE_AA)

    tongue_center = (head_x, head_y + int(13 * scale))
    cv2.ellipse(frame, tongue_center, (max(2, int(4 * scale)), max(2, int(4 * scale))), 0, 0, 360, (140, 110, 240), -1, cv2.LINE_AA)

    cv2.rectangle(frame,
                  (head_x - mouth_w + 2, mouth_center[1] - mouth_h + 1),
                  (head_x + mouth_w - 2, mouth_center[1] - mouth_h + max(3, int(4 * scale))),
                  white, -1)


def draw_character_piece(frame, kind, x, y, size, angle, preset):
    skin = preset["skin"]
    hair = preset["hair"]
    shirt = preset["shirt"]
    black = (20, 20, 25)

    if kind == "head":
        head_r = max(8, size)
        draw_hair(frame, x, y, head_r, preset["hair_style"], hair)
        cv2.circle(frame, (x, y), head_r, skin, -1, cv2.LINE_AA)
        cv2.circle(frame, (x, y), head_r, black, 2, cv2.LINE_AA)

        cv2.circle(frame, (x - 3, y - 2), max(2, head_r // 4), (250, 250, 250), -1, cv2.LINE_AA)
        cv2.circle(frame, (x - 3, y - 2), max(1, head_r // 7), black, -1, cv2.LINE_AA)
        cv2.ellipse(frame, (x, y + 4), (max(2, head_r // 4), max(3, head_r // 3)), 0, 0, 360, (20, 20, 20), -1, cv2.LINE_AA)

    elif kind == "body":
        cv2.ellipse(frame, (x, y), (max(6, size // 2), max(9, size)), int(angle * 45), 0, 360, shirt, -1, cv2.LINE_AA)
        cv2.ellipse(frame, (x, y), (max(6, size // 2), max(9, size)), int(angle * 45), 0, 360, black, 2, cv2.LINE_AA)

    elif kind == "arm":
        length = max(12, int(size * 1.6))
        end_x = int(x + math.cos(angle) * length)
        end_y = int(y + math.sin(angle) * length)
        cv2.line(frame, (x, y), (end_x, end_y), skin, max(3, size // 4), cv2.LINE_AA)
        cv2.line(frame, (x, y), (end_x, end_y), black, 1, cv2.LINE_AA)
        cv2.circle(frame, (end_x, end_y), max(2, size // 5), skin, -1, cv2.LINE_AA)

    elif kind == "leg":
        length = max(14, int(size * 1.7))
        end_x = int(x + math.cos(angle + math.pi / 2) * length)
        end_y = int(y + math.sin(angle + math.pi / 2) * length)
        cv2.line(frame, (x, y), (end_x, end_y), (35, 45, 60), max(3, size // 4), cv2.LINE_AA)
        cv2.line(frame, (x, y), (end_x, end_y), black, 1, cv2.LINE_AA)


def draw_bomb(frame, x, y, radius):
    cv2.circle(frame, (x, y), radius, (25, 25, 30), -1, cv2.LINE_AA)
    cv2.circle(frame, (x, y), radius, (10, 10, 12), 2, cv2.LINE_AA)
    cv2.circle(frame, (x - 10, y - 12), 7, (90, 90, 100), -1, cv2.LINE_AA)

    cv2.line(frame, (x + 10, y - radius + 5), (x + 22, y - radius - 13), (175, 175, 180), 5, cv2.LINE_AA)
    cv2.circle(frame, (x + 24, y - radius - 16), 7, (0, 120, 255), -1, cv2.LINE_AA)


def distance_point_to_segment(point, start, end):
    px, py = point
    ax, ay = start
    bx, by = end

    dx = bx - ax
    dy = by - ay

    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)

    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))

    closest_x = ax + t * dx
    closest_y = ay + t * dy

    return math.hypot(px - closest_x, py - closest_y)


def was_cut(obj, previous_point, current_point):
    if previous_point is None or current_point is None:
        return False

    distance = distance_point_to_segment(
        (obj.x, obj.y),
        previous_point,
        current_point
    )

    return distance < obj.radius + 18


def main():
    start_time = time.time()
    speed_multiplier = 1.0

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

    objects = []
    halves = []
    characters = []
    character_pieces = []
    trail = []

    last_spawn = time.time()
    game_over = False
    game_over_played = False
    score = 0

    while True:
        success, camera_frame = cap.read()
        if not success:
            break

        camera_frame = cv2.flip(camera_frame, 1)
        camera_frame = cv2.resize(camera_frame, (WIDTH, HEIGHT))

        frame = camera_frame.copy()
        now = time.time()

        hands, _ = detector.findHands(
            camera_frame,
            draw=False,
            flipType=False
        )

        current_point = None

        if hands:
            hand = hands[0]
            fingers = detector.fingersUp(hand)
            is_fist = sum(fingers) == 0

            if not is_fist:
                landmarks = hand["lmList"]
                index_tip = landmarks[8]
                current_point = (int(index_tip[0]), int(index_tip[1]))
                trail.append(current_point)

                if len(trail) > TRAIL_LENGTH:
                    trail.pop(0)
            else:
                trail.clear()
        else:
            trail.clear()

        # Spawning objects
        if not game_over and now - last_spawn >= SPAWN_INTERVAL:
            elapsed = time.time() - start_time
            # Increase speed by 8% every 5 seconds (capped at 2.2x so it stays playable)
            level = int(elapsed // 5)
            speed_multiplier = min(2.2, 1.0 + (level * 0.08))

            objects.append(FlyingObject(random.choice(OBJECT_TYPES)))
            last_spawn = now

        if not game_over:
            for obj in objects:
                obj.update()

        remaining_objects = []

        if not game_over:
            for obj in objects:
                cut = was_cut(
                    obj,
                    trail[-2] if len(trail) >= 2 else None,
                    trail[-1] if trail else None
                )

                if cut:
                    if obj.kind == "bomb":
                        if not game_over:
                            game_over = True
                            try:
                                pygame.mixer.music.stop()
                            except Exception:
                                pass
                            if gameover_sound and not game_over_played:
                                gameover_sound.play()
                                game_over_played = True
                    else:
                        halves.append(EggHalf(obj, -1))
                        halves.append(EggHalf(obj, 1))
                        characters.append(ScreamingCharacter(obj))
                        if scream_sound:
                            scream_sound.play()
                        score += 1
                else:
                    remaining_objects.append(obj)

            objects = remaining_objects

        # Update and render egg halves
        for half in halves:
            half.update()
            half.draw(frame)

        halves = [h for h in halves if h.life > 0 and h.y < HEIGHT + 120]

        # Update and render screaming characters
        active_characters = []
        for character in characters:
            character.update()
            if character.timer <= 0:
                character_pieces.extend(character.split_into_pieces())
            else:
                character.draw(frame)
                active_characters.append(character)

        characters = active_characters

        # Update and render exploding body pieces
        for piece in character_pieces:
            piece.update()
            piece.draw(frame)

        character_pieces = [p for p in character_pieces if p.life > 0 and p.y < HEIGHT + 150]

        # Draw eggs / bombs
        for obj in objects:
            obj.draw(frame)

        # Draw knife blade trail
        if len(trail) >= 2:
            for i in range(1, len(trail)):
                thickness = max(1, int(8 * i / len(trail)))
                cv2.line(frame, trail[i - 1], trail[i], (255, 255, 255), thickness, cv2.LINE_AA)

        # Draw index fingertip pointer
        if current_point:
            cv2.circle(frame, current_point, 12, (255, 220, 80), -1, cv2.LINE_AA)
            cv2.circle(frame, current_point, 18, (255, 255, 255), 2, cv2.LINE_AA)

        # UI Text
        cv2.putText(
            frame,
            f"SCORE: {score}",
            (25, 45),
            cv2.FONT_HERSHEY_DUPLEX,
            0.95,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            frame,
            "Slice eggs - avoid bombs! (Fist disables blade)",
            (25, 78),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (220, 230, 245),
            1,
            cv2.LINE_AA
        )

        # Game Over Screen
        if game_over:
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (WIDTH, HEIGHT), (0, 0, 0), -1)
            frame = cv2.addWeighted(frame, 0.35, overlay, 0.65, 0)

            cv2.putText(
                frame,
                "GAME OVER",
                (WIDTH // 2 - 190, HEIGHT // 2 - 20),
                cv2.FONT_HERSHEY_DUPLEX,
                1.7,
                (0, 80, 255),
                4,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                f"Final score: {score}",
                (WIDTH // 2 - 110, HEIGHT // 2 + 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.85,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                "Press R to restart or Q to quit",
                (WIDTH // 2 - 170, HEIGHT // 2 + 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.62,
                (220, 220, 220),
                1,
                cv2.LINE_AA
            )

        cv2.imshow("Egg Ninja - Hand Slice", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        if key == ord("r") and game_over:
            objects.clear()
            halves.clear()
            characters.clear()
            character_pieces.clear()
            trail.clear()
            score = 0
            game_over = False
            game_over_played = False
            last_spawn = time.time()
            try:
                pygame.mixer.music.play(-1)
            except Exception:
                pass

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
