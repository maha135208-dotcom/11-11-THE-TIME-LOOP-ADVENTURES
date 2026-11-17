import pygame
import random
import math
import sys

pygame.init()

# ==========================================
# 11:11 - THE TIME LOOP | VERSION 2.0
# ==========================================

WIDTH, HEIGHT = 1000, 600
FPS = 60
WORLD = 2400

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("11:11 - THE TIME LOOP V2.0")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 22, bold=True)
BIG = pygame.font.SysFont("arial", 65, bold=True)
SMALL = pygame.font.SysFont("arial", 16)
TITLE = pygame.font.SysFont("arial", 38, bold=True)

WHITE = (245, 245, 255)
CYAN = (65, 225, 255)
PURPLE = (145, 90, 255)
PINK = (255, 80, 160)
DARK = (9, 12, 30)
GOLD = (255, 205, 75)

# ==========================================
# LEVEL DATA
# ==========================================

LEVELS = [
    {
        "name": "THE FORGOTTEN CITY",
        "color": (12, 15, 40),
        "platforms": [
            (0, 500, WORLD, 100),
            (330, 415, 190, 22),
            (650, 350, 190, 22),
            (990, 420, 220, 22),
            (1350, 350, 200, 22),
            (1700, 415, 220, 22)
        ],
        "shards": [390, 710, 1060, 1410, 1790],
        "enemies": [550, 900, 1250, 1600, 1950]
    },
    {
        "name": "THE BROKEN TIMELINE",
        "color": (22, 10, 48),
        "platforms": [
            (0, 500, WORLD, 100),
            (250, 410, 180, 22),
            (550, 330, 190, 22),
            (850, 400, 200, 22),
            (1150, 310, 200, 22),
            (1480, 390, 190, 22),
            (1800, 320, 200, 22)
        ],
        "shards": [300, 600, 920, 1210, 1540, 1870],
        "enemies": [480, 780, 1100, 1430, 1750, 2050]
    },
    {
        "name": "THE DARK DIMENSION",
        "color": (8, 20, 38),
        "platforms": [
            (0, 500, WORLD, 100),
            (300, 400, 180, 22),
            (600, 320, 180, 22),
            (900, 400, 180, 22),
            (1200, 300, 180, 22),
            (1500, 380, 180, 22),
            (1800, 300, 180, 22)
        ],
        "shards": [350, 650, 950, 1250, 1550, 1850],
        "enemies": [500, 800, 1100, 1400, 1700, 2050]
    },
    {
        "name": "THE TIME GUARDIAN",
        "color": (35, 8, 35),
        "platforms": [
            (0, 500, WORLD, 100),
            (350, 400, 180, 22),
            (700, 330, 180, 22),
            (1050, 400, 180, 22),
            (1400, 330, 180, 22),
            (1750, 400, 180, 22)
        ],
        "shards": [400, 750, 1100, 1450, 1800],
        "enemies": [600, 950, 1300, 1650]
    }
]

# ==========================================
# GAME VARIABLES
# ==========================================

game_state = "menu"

level = 0
health = 5
score = 0

player = pygame.Rect(80, 400, 36, 55)

vx = 0
vy = 0
speed = 5
gravity = 0.65
jump_power = -13

facing = 1
jumps_left = 2
on_ground = False

dash_timer = 0
dash_cooldown = 0

attack_timer = 0
attack_cooldown = 0

damage_cooldown = 0
rewind_cooldown = 0

loop_time = 75
loop_limit = 75

history = []

camera_x = 0

collected = 0
shards = []
platforms = []
enemies = []

checkpoint_x = 80
checkpoint_active = False

portal = pygame.Rect(2220, 390, 65, 110)

boss = {
    "x": 1900,
    "y": 410,
    "health": 12,
    "max_health": 12,
    "direction": -1,
    "alive": True
}

message = ""
message_timer = 0

# ==========================================
# BACKGROUND
# ==========================================

random.seed(11)

stars = [
    (random.randint(0, WORLD),
     random.randint(20, 360),
     random.randint(1, 3))
    for _ in range(150)
]

buildings = [
    (x, random.randint(240, 360),
     random.randint(75, 125))
    for x in range(0, WORLD, 130)
]


def text(msg, font, color, x, y, center=False):
    image = font.render(str(msg), True, color)
    rect = image.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(image, rect)


def draw_background():
    bg = LEVELS[level]["color"]
    screen.fill(bg)

    # Stars
    for x, y, size in stars:
        sx = int((x - camera_x * 0.25) % WIDTH)
        pygame.draw.circle(
            screen, (110, 130, 190),
            (sx, y), size
        )

    # Moon
    pygame.draw.circle(
        screen, (100, 120, 190),
        (820, 110), 45
    )
    pygame.draw.circle(
        screen, bg, (840, 95), 40
    )

    # City
    for x, h, w in buildings:
        sx = int(x - camera_x * 0.5)

        if -150 < sx < WIDTH + 150:
            pygame.draw.rect(
                screen, (25, 30, 65),
                (sx, h, w, HEIGHT - h)
            )

            for wy in range(h + 20, HEIGHT - 50, 35):
                for wx in range(sx + 12, sx + w - 8, 25):
                    pygame.draw.rect(
                        screen, (50, 85, 135),
                        (wx, wy, 7, 10)
                    )

    # Ground
    pygame.draw.rect(
        screen, (20, 26, 53),
        (0, 500, WIDTH, 100)
    )

    pygame.draw.line(
        screen, CYAN,
        (0, 500), (WIDTH, 500), 2
    )


# ==========================================
# LEVEL INITIALIZATION
# ==========================================

def load_level(number):
    global level, platforms, shards, enemies
    global collected, checkpoint_x, checkpoint_active
    global boss, portal, player, vx, vy
    global jumps_left, history, loop_time

    level = number

    data = LEVELS[level]

    platforms = [
        pygame.Rect(*p) for p in data["platforms"]
    ]

    shards = [
        pygame.Rect(x, 370 if i % 2 == 0 else 305, 20, 25)
        for i, x in enumerate(data["shards"])
    ]

    collected = 0

    enemies = []

    for x in data["enemies"]:
        enemies.append({
            "x": float(x),
            "y": 460,
            "start": x - 80,
            "end": x + 80,
            "direction": 1,
            "alive": True
        })

    checkpoint_x = 80
    checkpoint_active = False

    player.x = 80
    player.y = 400

    vx = 0
    vy = 0

    jumps_left = 2
    history = []

    loop_time = loop_limit

    portal = pygame.Rect(2220, 390, 65, 110)

    boss = {
        "x": 1900,
        "y": 410,
        "health": 12,
        "max_health": 12,
        "direction": -1,
        "alive": level == 3
    }


def start_game():
    global health, score, game_state

    health = 5
    score = 0

    load_level(0)

    game_state = "playing"


# ==========================================
# PLAYER DRAWING
# ==========================================

def draw_player():
    px = int(player.x - camera_x)
    py = player.y

    # Shadow
    pygame.draw.ellipse(
        screen, (5, 8, 20),
        (px - 4, py + 49, 44, 10)
    )

    # Dash trail
    if dash_timer > 0:
        for i in range(4):
            pygame.draw.circle(
                screen, (60, 120, 220),
                (px - facing * i * 15 + 18, py + 28),
                10 - i * 2
            )

    # Body
    pygame.draw.rect(
        screen, (55, 100, 210),
        (px + 5, py + 19, 27, 29),
        border_radius=8
    )

    # Head
    pygame.draw.circle(
        screen, (235, 210, 190),
        (px + 18, py + 12), 12
    )

    # Hair
    pygame.draw.arc(
        screen, (30, 25, 45),
        (px + 5, py, 26, 22),
        0, math.pi, 4
    )

    # Eye
    eye_x = px + (24 if facing == 1 else 11)

    pygame.draw.circle(
        screen, DARK, (eye_x, py + 12), 2
    )

    # Legs
    pygame.draw.line(
        screen, WHITE,
        (px + 12, py + 46),
        (px + 9, py + 54), 4
    )

    pygame.draw.line(
        screen, WHITE,
        (px + 26, py + 46),
        (px + 29, py + 54), 4
    )

    # Attack effect
    if attack_timer > 0:
        ax = px + (45 if facing == 1 else -10)

        pygame.draw.circle(
            screen, CYAN,
            (ax, py + 28), 35, 4
        )


# ==========================================
# WORLD DRAWING
# ==========================================

def draw_world():

    # Platforms
    for p in platforms:
        r = pygame.Rect(
            p.x - camera_x, p.y,
            p.width, p.height
        )

        if r.right > 0 and r.left < WIDTH:
            pygame.draw.rect(
                screen, (35, 50, 90),
                r, border_radius=6
            )

            pygame.draw.line(
                screen, CYAN,
                r.topleft, r.topright, 3
            )

    # Checkpoint
    cx = checkpoint_x - camera_x

    pygame.draw.rect(
        screen, PURPLE,
        (cx, 420, 8, 80)
    )

    pygame.draw.circle(
        screen, GOLD if checkpoint_active else CYAN,
        (cx + 4, 415), 12
    )

    # Shards
    for shard in shards:
        r = pygame.Rect(
            shard.x - camera_x,
            shard.y, shard.width, shard.height
        )

        pygame.draw.polygon(
            screen, CYAN,
            [
                (r.centerx, r.top),
                (r.right, r.centery),
                (r.centerx, r.bottom),
                (r.left, r.centery)
            ]
        )

    # Enemies
    for enemy in enemies:
        if enemy["alive"]:
            ex = int(enemy["x"] - camera_x)
            ey = enemy["y"]

            pygame.draw.ellipse(
                screen, PINK,
                (ex, ey, 40, 40)
            )

            pygame.draw.circle(
                screen, WHITE, (ex + 12, ey + 14), 4
            )

            pygame.draw.circle(
                screen, WHITE, (ex + 28, ey + 14), 4
            )

    # Boss
    if boss["alive"]:
        bx = int(boss["x"] - camera_x)
        by = boss["y"]

        pygame.draw.circle(
            screen, PURPLE,
            (bx + 30, by + 35), 40
        )

        pygame.draw.circle(
            screen, PINK,
            (bx + 17, by + 25), 7
        )

        pygame.draw.circle(
            screen, PINK,
            (bx + 43, by + 25), 7
        )

        # Boss health bar
        pygame.draw.rect(
            screen, (60, 20, 45),
            (WIDTH // 2 - 150, 115, 300, 16)
        )

        pygame.draw.rect(
            screen, PINK,
            (
                WIDTH // 2 - 150,
                115,
                int(300 * boss["health"] /
                    boss["max_health"]),
                16
            )
        )

        text(
            "TIME GUARDIAN",
            SMALL, WHITE,
            WIDTH // 2, 90, True
        )

    # Portal
    pr = pygame.Rect(
        portal.x - camera_x,
        portal.y,
        portal.width,
        portal.height
    )

    unlocked = (
        len(shards) == 0 and
        (level != 3 or not boss["alive"])
    )

    portal_color = CYAN if unlocked else PURPLE

    pygame.draw.ellipse(
        screen, portal_color, pr, 5
    )

    pygame.draw.ellipse(
        screen, (80, 90, 150),
        pr.inflate(-20, -10), 2
    )

    text(
        "EXIT" if unlocked else "LOCKED",
        SMALL, WHITE,
        pr.centerx, pr.bottom + 8, True
    )

    draw_player()


# ==========================================
# HUD
# ==========================================

def draw_hud():
    text("HEALTH", SMALL, WHITE, 25, 18)

    for i in range(health):
        pygame.draw.circle(
            screen, PINK,
            (115 + i * 25, 29), 9
        )

    text(
        LEVELS[level]["name"],
        FONT, CYAN, WIDTH // 2, 25, True
    )

    text(
        f"SHARDS: {collected}/{collected + len(shards)}",
        FONT, CYAN, 760, 20
    )

    text(
        f"SCORE: {score}",
        SMALL, WHITE, 760, 55
    )

    text("TIME LOOP", SMALL, WHITE, 25, 65)

    pygame.draw.rect(
        screen, (45, 50, 85),
        (25, 90, 190, 12)
    )

    pygame.draw.rect(
        screen,
        CYAN if loop_time > 15 else PINK,
        (
            25, 90,
            int(190 * max(0, loop_time / loop_limit)),
            12
        )
    )

    text(
        f"{max(0, int(loop_time))}s",
        SMALL, WHITE, 225, 85
    )

    text(
        "A/D MOVE  SPACE JUMP  SHIFT DASH  J ATTACK",
        SMALL, WHITE, 25, 555
    )

    text(
        "R REWIND   P PAUSE",
        SMALL, CYAN, 750, 555
    )


# ==========================================
# MENUS
# ==========================================

def draw_menu():
    draw_background()

    pygame.draw.circle(
        screen, CYAN, (500, 160), 70, 3
    )

    pygame.draw.circle(
        screen, PURPLE, (500, 160), 58, 2
    )

    pygame.draw.line(
        screen, WHITE,
        (500, 160), (500, 110), 3
    )

    pygame.draw.line(
        screen, WHITE,
        (500, 160), (535, 180), 3
    )

    text("11:11", BIG, WHITE, 500, 270, True)

    text(
        "THE TIME LOOP",
        TITLE, CYAN, 500, 330, True
    )

    text(
        "EVERY SECOND CHANGES YOUR DESTINY",
        SMALL, WHITE, 500, 380, True
    )

    text(
        "PRESS ENTER TO START",
        FONT, GOLD, 500, 455, True
    )

    text(
        "VERSION 2.0 | FOUR DIMENSIONS",
        SMALL, PURPLE, 500, 520, True
    )


def draw_pause():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(190)
    overlay.fill(DARK)

    screen.blit(overlay, (0, 0))

    text("PAUSED", BIG, CYAN, 500, 230, True)

    text(
        "P / ESC TO RESUME",
        FONT, WHITE, 500, 330, True
    )

    text(
        "ENTER TO RESTART",
        SMALL, PURPLE, 500, 390, True
    )


def draw_end(title, subtitle):
    screen.fill(DARK)

    text(title, BIG, CYAN, 500, 200, True)
    text(subtitle, FONT, WHITE, 500, 285, True)

    text(
        f"FINAL SCORE: {score}",
        FONT, GOLD, 500, 350, True
    )

    text(
        "PRESS ENTER TO PLAY AGAIN",
        FONT, PURPLE, 500, 445, True
    )


# ==========================================
# TIME LOOP RESET
# ==========================================

def reset_loop():
    global vx, vy, loop_time, history
    global message, message_timer, jumps_left

    player.x = checkpoint_x
    player.y = 400

    vx = 0
    vy = 0

    jumps_left = 2
    loop_time = loop_limit

    history.clear()

    for enemy in enemies:
        enemy["alive"] = True

    message = "TIME RESET! YOUR MEMORIES REMAIN..."
    message_timer = 180


# ==========================================
# MAIN LOOP
# ==========================================

while True:

    dt = min(clock.tick(FPS) / 1000, 0.04)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:

            if game_state == "menu":
                if event.key == pygame.K_RETURN:
                    start_game()

            elif game_state in ("gameover", "win"):
                if event.key == pygame.K_RETURN:
                    start_game()

            elif game_state == "playing":

                if event.key in (
                    pygame.K_SPACE,
                    pygame.K_w,
                    pygame.K_UP
                ):
                    if jumps_left > 0:
                        vy = jump_power
                        jumps_left -= 1
                        on_ground = False

                if event.key in (
                    pygame.K_LSHIFT,
                    pygame.K_RSHIFT
                ):
                    if dash_cooldown <= 0:
                        dash_timer = 0.18
                        dash_cooldown = 1.0

                if event.key == pygame.K_j:
                    if attack_cooldown <= 0:

                        attack_timer = 0.2
                        attack_cooldown = 0.4

                        # Attack enemies
                        for enemy in enemies:
                            if enemy["alive"]:

                                distance = (
                                    enemy["x"] - player.centerx
                                )

                                if (
                                    abs(distance) < 100
                                    and distance * facing >= -15
                                ):
                                    enemy["alive"] = False
                                    score += 100

                        # Attack boss
                        if boss["alive"]:

                            distance = (
                                boss["x"] - player.centerx
                            )

                            if (
                                abs(distance) < 125
                                and distance * facing >= -20
                            ):
                                boss["health"] -= 1
                                score += 50

                                if boss["health"] <= 0:
                                    boss["alive"] = False
                                    score += 1000

                                    message = "TIME GUARDIAN DEFEATED!"
                                    message_timer = 180

                if event.key == pygame.K_ESCAPE:
                    game_state = "paused"

            elif game_state == "paused":

                if event.key in (
                    pygame.K_ESCAPE,
                    pygame.K_p
                ):
                    game_state = "playing"

                if event.key == pygame.K_RETURN:
                    start_game()

    # ======================================
    # PLAYING
    # ======================================

    if game_state == "playing":

        keys = pygame.key.get_pressed()

        loop_time -= dt

        attack_cooldown = max(0, attack_cooldown - dt)
        attack_timer = max(0, attack_timer - dt)
        dash_cooldown = max(0, dash_cooldown - dt)
        damage_cooldown = max(0, damage_cooldown - dt)
        rewind_cooldown = max(0, rewind_cooldown - dt)

        if message_timer > 0:
            message_timer -= 1

        # Save history
        history.append((
            player.x, player.y, vx, vy
        ))

        if len(history) > 240:
            history.pop(0)

        # Movement
        vx = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            vx = -speed
            facing = -1

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            vx = speed
            facing = 1

        # Dash
        if dash_timer > 0:
            vx = facing * 13
            dash_timer -= dt

        # Rewind
        rewinding = False

        if (
            keys[pygame.K_r]
            and rewind_cooldown <= 0
            and len(history) > 1
        ):
            for _ in range(min(5, len(history))):
                old = history.pop()

                player.x = old[0]
                player.y = old[1]
                vx = old[2]
                vy = old[3]

            rewind_cooldown = 0.08
            rewinding = True

        if not rewinding:

            # Horizontal movement
            player.x += int(vx)

            player.x = max(
                0,
                min(WORLD - player.width, player.x)
            )

            # Vertical movement
            if dash_timer <= 0:
                vy += gravity

            vy = min(vy, 14)

            old_bottom = player.bottom

            player.y += int(vy)

            on_ground = False

            # Platform collision
            for p in platforms:

                if player.colliderect(p):

                    if vy >= 0 and old_bottom <= p.top + 8:

                        player.bottom = p.top
                        vy = 0
                        on_ground = True
                        jumps_left = 2

                    elif vy < 0:

                        player.top = p.bottom
                        vy = 0

        # Checkpoint activation
        if player.x >= 1100 and not checkpoint_active:

            checkpoint_x = 1100
            checkpoint_active = True

            message = "CHECKPOINT ACTIVATED!"
            message_timer = 150

        # Fall protection
        if player.y > HEIGHT + 100:

            health -= 1

            player.x = checkpoint_x
            player.y = 350

            vx = 0
            vy = 0

            damage_cooldown = 1.0

        # Enemy movement
        for enemy in enemies:

            if enemy["alive"]:

                enemy["x"] += (
                    enemy["direction"] * 1.6
                )

                if enemy["x"] <= enemy["start"]:
                    enemy["direction"] = 1

                if enemy["x"] >= enemy["end"]:
                    enemy["direction"] = -1

                enemy_rect = pygame.Rect(
                    int(enemy["x"]),
                    enemy["y"],
                    40, 40
                )

                if (
                    player.colliderect(enemy_rect)
                    and damage_cooldown <= 0
                ):

                    health -= 1
                    damage_cooldown = 1.2

                    vx = -facing * 5
                    vy = -5

        # Boss movement
        if boss["alive"]:

            boss["x"] += boss["direction"] * 1.3

            if boss["x"] < 1750:
                boss["direction"] = 1

            if boss["x"] > 2100:
                boss["direction"] = -1

            boss_rect = pygame.Rect(
                int(boss["x"]), boss["y"],
                60, 70
            )

            if (
                player.colliderect(boss_rect)
                and damage_cooldown <= 0
            ):

                health -= 1
                damage_cooldown = 1.2

                vx = -facing * 6
                vy = -6

        # Collect shards
        for shard in shards[:]:

            if player.colliderect(shard):

                shards.remove(shard)
                collected += 1
                score += 50

                message = "TIME SHARD COLLECTED!"
                message_timer = 80

        # Exit portal
        unlocked = (
            len(shards) == 0
            and (level != 3 or not boss["alive"])
        )

        if player.colliderect(portal) and unlocked:

            if level < 3:

                load_level(level + 1)

                message = "NEW DIMENSION UNLOCKED!"
                message_timer = 180

            else:
                game_state = "win"

        # Time loop
        if loop_time <= 0:
            reset_loop()

        # Camera
        camera_x = max(
            0,
            min(
                WORLD - WIDTH,
                player.centerx - WIDTH // 2
            )
        )

        # Game over
        if health <= 0:
            game_state = "gameover"

        # Drawing
        draw_background()
        draw_world()
        draw_hud()

        if message_timer > 0:
            text(
                message, FONT, CYAN,
                WIDTH // 2, 150, True
            )

        if damage_cooldown > 0:
            pygame.draw.rect(
                screen, PINK,
                (0, 0, WIDTH, HEIGHT), 3
            )

        if dash_cooldown > 0:
            text(
                "DASH RECHARGING",
                SMALL, PURPLE, 25, 120
            )

    # ======================================
    # OTHER STATES
    # ======================================

    elif game_state == "menu":
        draw_menu()

    elif game_state == "paused":

        draw_background()
        draw_world()
        draw_hud()
        draw_pause()

    elif game_state == "gameover":

        draw_end(
            "GAME OVER",
            "THE LOOP HAS CONSUMED YOU..."
        )

    elif game_state == "win":

        draw_end(
            "YOU ESCAPED!",
            "YOU BROKE THE TIME LOOP!"
        )

        text(
            "THE END",
            TITLE, GOLD, 500, 510, True
        )

    pygame.display.flip()