import pygame
import random
import time
import threading

# === Init ===
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elipson Core Manager")
clock = pygame.time.Clock()
font = pygame.font.SysFont("consolas", 20)

# === Game State ===
rooms = ["core", "control", "silos", "bunker", "helipad", "radio"]

player = {
    "location": "control",
    "moving": False,
    "move_target": None,
    "move_timer": 0,
    "event": None,
    "event_timer": 0,
    "alive": True
}

core = {
    "temp": 50000,
    "stability": 100,
    "power": 5000,
    "openings": 3,
    "heating": True,
    "cooling": False,
    "antimatter": True
}
def set_openings(val):
    if 0 <= val <= 6:
        core["openings"] = val
# === Music ===
current_music = None
event_music_files = {
    "FREEZEDOWN": "/path/to/Frozen.mp3",
    "MELTDOWN": "/path/to/Overheated.mp3",
    "OVERLOAD": "/path/to/Invasions.mp3",
    "COLLAPSE": "/path/to/Unstable.mp3",
    "ALIEN_INVASION": "/path/to/Extraterrestrial.mp3",
    "HELP_RECEIVED": "/path/to/Radiations.mp3"
}

def play_music(event):
    global current_music
    file = event_music_files.get(event)
    if file and current_music != file:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play(-1)
        current_music = file
def move_to(room):
    if not player["moving"]:
        player["moving"] = True
        player["move_target"] = room
        player["move_timer"] = 10
def stop_music():
    global current_music
    pygame.mixer.music.stop()
    current_music = None

# === Events ===
def trigger_event(event, timer):
    if not player["event"]:
        player["event"] = event
        player["event_timer"] = timer
        print(f"⚠️ EVENT: {event}")
        play_music(event)

def process_event():
    if player["event"]:
        player["event_timer"] -= 1
        if player["event_timer"] <= 0:
            print(f"You failed to survive the {player['event']}.")
            player["alive"] = False

# === Core Simulation ===
def update_core():
    if core["cooling"]:
        core["temp"] -= 1500
    if core["heating"]:
        core["temp"] += 1000
    if core["antimatter"]:
        core["stability"] += 2
    else:
        core["stability"] -= 1

    core["stability"] = max(0, min(core["stability"], 100))
    core["power"] += core["openings"] * 300 - 500
    core["power"] = max(core["power"], 0)

    if core["temp"] < 0:
        trigger_event("FREEZEDOWN", 300)
    elif core["temp"] >= 100000:
        trigger_event("MELTDOWN", 300)
    elif core["stability"] <= 0:
        trigger_event("COLLAPSE", 300)
    elif core["power"] <= 0:
        trigger_event("OVERLOAD", 300)

# === Movement ===
def resolve_movement():
    if player["moving"]:
        player["move_timer"] -= 1
        if player["move_timer"] <= 0:
            player["location"] = player["move_target"]
            player["moving"] = False
            player["move_target"] = None
            print(f"Arrived at {player['location']}")

            if player["event"] == "COLLAPSE" and player["location"] == "silos":
                print("🚀 Rocket launch! You win!")
                player["alive"] = False
            elif player["event"] == "OVERLOAD" and player["location"] == "helipad":
                print("🚁 Copter launch! You win!")
                player["alive"] = False
            elif player["event"] in ["FREEZEDOWN", "MELTDOWN"] and player["location"] == "bunker":
                print("🛡️ Bunker sealed. You survived!")
                player["alive"] = False
            elif player["event"] == "ALIEN_INVASION" and player["location"] == "bunker":
                print("🛡️ You sealed yourself in the bunker and survived the alien invasion!")
                player["alive"] = False
            elif player["event"] == "HELP_RECEIVED" and player["location"] == "helipad":
                print("🚁 Rescue arrived! You were saved!")
                player["alive"] = False


# === Game Ticking Thread ===
def game_tick_loop():
    while player["alive"]:
        update_core()
        resolve_movement()
        process_event()
        time.sleep(1)

threading.Thread(target=game_tick_loop, daemon=True).start()

# === UI Buttons ===
buttons = []

def draw_text(text, x, y, color=(255, 255, 255)):
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

def make_button(label, x, y, action):
    w, h = 200, 30
    rect = pygame.Rect(x, y, w, h)
    buttons.append((rect, action, label))
    pygame.draw.rect(screen, (100, 100, 100), rect)
    draw_text(label, x + 10, y + 5)

def draw_ui():
    screen.fill((0, 0, 0))
    draw_text(f"Location: {player['location'].upper()}", 20, 20)
    draw_text(f"Temp: {core['temp']}K", 20, 50)
    draw_text(f"Stability: {core['stability']}%", 20, 80)
    draw_text(f"Power: {core['power']}W", 20, 110)
    draw_text(f"Heating: {'ON' if core['heating'] else 'OFF'}", 20, 140)
    draw_text(f"Cooling: {'ON' if core['cooling'] else 'OFF'}", 20, 170)
    draw_text(f"Antimatter: {'ON' if core['antimatter'] else 'OFF'}", 20, 200)
    draw_text(f"Openings: {core['openings']}", 20, 230)
    if player["moving"]:
        draw_text(f"Moving to {player['move_target']}... ETA: {player['move_timer']}s", 20, 260)
    if player["event"]:
        draw_text(f"⚠️ EVENT: {player['event']} | {player['event_timer']}s", 20, 290, (255, 100, 100))

    # Buttons
    buttons.clear()
    make_button("Toggle Heating", 550, 50, lambda: toggle("heating"))
    make_button("Toggle Cooling", 550, 90, lambda: toggle("cooling"))
    make_button("Toggle Antimatter", 550, 130, lambda: toggle("antimatter"))

    y = 180
    for room in rooms:
        if room != player["location"]:
            make_button(f"Go to {room}", 550, y, lambda r=room: move_to(r))
            y += 40

    make_button("Set Openings +1", 550, y + 20, lambda: set_openings(core["openings"] + 1))
    make_button("Set Openings -1", 550, y + 60, lambda: set_openings(core["openings"] - 1))
    if player["location"] == "radio":
        make_button("Activate Radio", 550, y + 100, activate_radio)
def reset_core():
    core["temp"] = 50000
    core["stability"] = 100
    core["power"] = 5000
    core["heating"] = True
    core["cooling"] = False
    core["antimatter"] = True
    core["openings"] = 3
    print("✅ Core fully stabilized by help.")

def toggle(key):
    core[key] = not core[key]
def activate_radio():
    if player["location"] == "radio" and not player["event"]:
        if random.random() < 0.5:
            trigger_event("ALIEN_INVASION", 300)
        else:
            reset_core()
    if 0 <= val <= 6:
        core["openings"] = val

# === Main Loop ===
running = True
while running and player["alive"]:
    draw_ui()
    pygame.display.flip()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for rect, action, label in buttons:
                if rect.collidepoint(pos):
                    action()
    clock.tick(30)

pygame.quit()
