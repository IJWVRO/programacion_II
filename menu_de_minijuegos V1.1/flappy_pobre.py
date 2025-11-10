#====== Flappy Pobre con envío de email (solo EMAIL_USER y EMAIL_PASS) ======
import pygame
import random
import sys
import os
import math
import json
import smtplib
from email.message import EmailMessage
from itertools import cycle
from pygame.locals import *  # Importación necesaria para las constantes como QUIT, KEYDOWN, etc.

# === CONFIGURA AQUI TU CUENTA (solo estas dos variables) ===
EMAIL_USER = "fairbotnotifier@gmail.com"     # <- tu correo Gmail
EMAIL_PASS = "pvrcyhncquzcibyv"           # <- clave de aplicación (app password)
# =======================================================================

# Configuración del juego
FPS = 30
SCREENWIDTH = 576
SCREENHEIGHT = 768
PIPEGAPSIZE = 150
BASEY = SCREENHEIGHT * 0.79

# Configuración de pantalla
FULLSCREEN = False

# Diccionarios
IMAGES, SOUNDS, HITMASKS = {}, {}, {}

# Colores
COLORS = {
    'day_sky': (135, 206, 235),
    'night_sky': (25, 25, 112),
    'ground': (222, 184, 135),
    'pipe_green': (0, 128, 0),
    'pipe_red': (220, 20, 60),
    'red_box': (220, 20, 60),
    'blue_box': (30, 144, 255),
    'yellow_box': (255, 215, 0),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'text': (255, 255, 255),
    'button': (100, 100, 200),
    'clear_button': (200, 50, 50),
    'user_button': (50, 150, 50),
}

# Jugadores y elementos
PLAYERS_LIST = (
    ('redbox-upflap', 'redbox-midflap', 'redbox-downflap'),
    ('bluebox-upflap', 'bluebox-midflap', 'bluebox-downflap'),
    ('yellowbox-upflap', 'yellowbox-midflap', 'yellowbox-downflap'),
)

BACKGROUNDS_LIST = ('background-day', 'background-night',)
PIPES_LIST = ('pipe-green', 'pipe-red',)

SCORES_FILE = "flappy_pobre_scores.json"
CURRENT_SCORE_FILE = "flappy_pobre_current_score.json"
USER_DATA_FILE = "flappy_pobre_user_data.json"

try:
    xrange
except NameError:
    xrange = range

# ------------------ Manejo de datos de usuario ------------------
def save_user_data(name, email):
    try:
        with open(USER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({'name': name, 'email': email}, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def load_user_data():
    try:
        if os.path.exists(USER_DATA_FILE):
            with open(USER_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('name', ''), data.get('email', '')
        return '', ''
    except:
        return '', ''

# ------------------ Manejo de puntajes ------------------
def load_high_scores():
    try:
        if os.path.exists(SCORES_FILE):
            with open(SCORES_FILE, 'r', encoding='utf-8') as f:
                scores = json.load(f)
                if scores and isinstance(scores[0], int):
                    return [{'name': 'Jugador', 'score': score} for score in scores]
                return scores
        return []
    except:
        return []

def save_high_scores(scores):
    try:
        with open(SCORES_FILE, 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def clear_high_scores():
    try:
        if os.path.exists(SCORES_FILE):
            os.remove(SCORES_FILE)
        save_current_score(0, "")
        return True
    except:
        return False

def load_current_score():
    try:
        if os.path.exists(CURRENT_SCORE_FILE):
            with open(CURRENT_SCORE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('score', 0), data.get('name', '')
        return 0, ''
    except:
        return 0, ''

def save_current_score(score, name):
    try:
        with open(CURRENT_SCORE_FILE, 'w', encoding='utf-8') as f:
            json.dump({'score': score, 'name': name}, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False

def update_high_scores(new_score, name):
    scores = load_high_scores()
    found = False
    for i, score_data in enumerate(scores):
        if isinstance(score_data, dict) and score_data.get('name') == name:
            if new_score > score_data.get('score', 0):
                scores[i]['score'] = new_score
            found = True
            break
    if not found:
        scores.append({'name': name, 'score': new_score})
    scores.sort(key=lambda x: x['score'], reverse=True)
    scores = scores[:10]
    save_high_scores(scores)
    return scores

# ------------------ Input en pantalla (nombre / email) ------------------
def prompt_text_box(title, hint="", max_len=64):
    """
    Muestra una caja de texto en pantalla y devuelve el texto introducido por el usuario (ENTER).
    Si el usuario cierra o pulsa ESC devuelve None.
    """
    input_active = True
    text = ""
    # Caja
    input_box = pygame.Rect(SCREENWIDTH//2 - 200, SCREENHEIGHT//2, 400, 48)
    # Fondo semitransparente
    bg = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))
    bg.fill((0,0,0))
    bg.set_alpha(180)
    font_title = pygame.font.SysFont('Arial', 28, bold=True)
    font_hint = pygame.font.SysFont('Arial', 18)
    font_text = pygame.font.SysFont('Arial', 24)
    clock = pygame.time.Clock()

    while input_active:
        for event in pygame.event.get():
            if event.type == QUIT:
                return None
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return None
                elif event.key == K_RETURN:
                    if text.strip() == "":
                        # ignorar enter si campo vacío
                        pass
                    else:
                        return text.strip()
                elif event.key == K_BACKSPACE:
                    text = text[:-1]
                else:
                    if len(text) < max_len and event.unicode.isprintable():
                        text += event.unicode

        # Dibujado
        SCREEN.blit(bg, (0,0))
        # Panel
        panel_w, panel_h = 520, 220
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel, (10,10,10,230), (0,0,panel_w,panel_h), border_radius=8)
        pygame.draw.rect(panel, COLORS['white'], (0,0,panel_w,panel_h), 2, border_radius=8)
        panel_x = (SCREENWIDTH - panel_w)//2
        panel_y = (SCREENHEIGHT - panel_h)//2
        SCREEN.blit(panel, (panel_x, panel_y))

        # Title
        title_surf = font_title.render(title, True, COLORS['white'])
        SCREEN.blit(title_surf, (SCREENWIDTH//2 - title_surf.get_width()//2, panel_y + 20))

        # Hint
        if hint:
            hint_surf = font_hint.render(hint, True, (200,200,200))
            SCREEN.blit(hint_surf, (SCREENWIDTH//2 - hint_surf.get_width()//2, panel_y + 60))

        # Input box
        pygame.draw.rect(SCREEN, COLORS['white'], input_box, 2, border_radius=6)
        txt_surf = font_text.render(text, True, COLORS['white'])
        SCREEN.blit(txt_surf, (input_box.x + 8, input_box.y + 8))

        # Instrucciones
        inst = font_hint.render("ENTER = aceptar  |  ESC = cancelar", True, (180,180,180))
        SCREEN.blit(inst, (SCREENWIDTH//2 - inst.get_width()//2, panel_y + panel_h - 40))

        pygame.display.update()
        clock.tick(FPS)

def get_name_and_email(score, default_name="Jugador"):
    """
    Pide al jugador primero su nombre y luego su correo.
    Devuelve (name, email) o (None, None) si el usuario cancela.
    """
    # Pedir nombre
    name = prompt_text_box("Ingresa tu nombre", hint="Tu nombre aparecerá en la tabla de puntajes", max_len=20)
    if name is None:
        return None, None
    # Pedir email
    email = prompt_text_box("Ingresa tu correo electrónico", hint="Recibirás una notificación con tu puntaje", max_len=64)
    if email is None:
        return None, None
    return name, email

def get_user_info():
    """
    Pide al jugador su nombre y correo electrónico.
    Devuelve (name, email) o (None, None) si el usuario cancela.
    """
    # Pedir nombre
    name = prompt_text_box("Ingresa tu nombre", hint="Tu nombre aparecerá en el juego", max_len=20)
    if name is None:
        return None, None
    # Pedir email
    email = prompt_text_box("Ingresa tu correo electrónico", hint="Recibirás una notificación con tu puntaje", max_len=64)
    if email is None:
        return None, None
    return name, email

# ------------------ Envío de correo (Gmail SMTP) ------------------
def send_score_email(to_email, player_name, score):
    """
    Envia un correo simple usando SMTP de Gmail.
    Usa las variables EMAIL_USER y EMAIL_PASS definidas arriba.
    Devuelve (True, "") si tuvo exito o (False, mensaje_error).
    """
    if not EMAIL_USER or not EMAIL_PASS:
        return False, "Credenciales de email no configuradas."

    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = f"Nuevo puntaje en Flappy Bird Pobre: {score}"
    body = f"Hola {player_name},\n\n¡Buen trabajo! Acabas de hacer {score} tuberías en Flappy Bird Pobre.\n\nSaludos,\nFlappy Bird Pobre"
    msg.set_content(body)

    try:
        # conectar con Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=10)
        server.ehlo()
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        return True, ""
    except Exception as e:
        return False, str(e)

# ------------------ Generación de imágenes / sonidos (sin cambios esenciales) ------------------
def generate_images():
    # (idéntica a tu implementación original)
    day_bg = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))
    day_bg.fill(COLORS['day_sky'])
    for _ in range(10):
        x = random.randint(0, SCREENWIDTH)
        y = random.randint(50, SCREENHEIGHT // 2)
        radius = random.randint(20, 40)
        pygame.draw.circle(day_bg, COLORS['white'], (x, y), radius)
        pygame.draw.circle(day_bg, COLORS['white'], (x + radius, y), radius)
        pygame.draw.circle(day_bg, COLORS['white'], (x - radius, y), radius)
    IMAGES['background-day'] = day_bg

    night_bg = pygame.Surface((SCREENWIDTH, SCREENHEIGHT))
    night_bg.fill(COLORS['night_sky'])
    for _ in range(100):
        x = random.randint(0, SCREENWIDTH)
        y = random.randint(0, SCREENHEIGHT // 2)
        pygame.draw.circle(night_bg, COLORS['white'], (x, y), 1)
    IMAGES['background-night'] = night_bg

    base_height = SCREENHEIGHT - BASEY
    base = pygame.Surface((SCREENWIDTH * 2, base_height))
    base.fill(COLORS['ground'])
    for x in range(0, SCREENWIDTH * 2, 20):
        pygame.draw.line(base, (200, 164, 115), (x, 0), (x, base_height), 2)
    IMAGES['base'] = base

    pipe_width = 104
    pipe_height = 640

    pipe_green = pygame.Surface((pipe_width, pipe_height), pygame.SRCALPHA)
    pygame.draw.rect(pipe_green, COLORS['pipe_green'], (0, 0, pipe_width, pipe_height))
    pygame.draw.rect(pipe_green, (0, 100, 0), (0, 0, pipe_width, pipe_height), 3)
    pygame.draw.rect(pipe_green, (0, 100, 0), (0, 0, pipe_width, 60))
    pygame.draw.rect(pipe_green, (0, 100, 0), (0, 0, pipe_width, 60), 3)
    IMAGES['pipe-green'] = pipe_green

    pipe_red = pygame.Surface((pipe_width, pipe_height), pygame.SRCALPHA)
    pygame.draw.rect(pipe_red, COLORS['pipe_red'], (0, 0, pipe_width, pipe_height))
    pygame.draw.rect(pipe_red, (139, 0, 0), (0, 0, pipe_width, pipe_height), 3)
    pygame.draw.rect(pipe_red, (139, 0, 0), (0, 0, pipe_width, 60))
    pygame.draw.rect(pipe_red, (139, 0, 0), (0, 0, pipe_width, 60), 3)
    IMAGES['pipe-red'] = pipe_red

    # redbox
    redbox_size = 40
    for flap, offset in [('upflap', -6), ('midflap', 0), ('downflap', 6)]:
        redbox = pygame.Surface((redbox_size, redbox_size), pygame.SRCALPHA)
        pygame.draw.rect(redbox, COLORS['red_box'], (0, 0, redbox_size, redbox_size))
        pygame.draw.rect(redbox, (139, 0, 0), (0, 0, redbox_size, redbox_size), 2)
        wing_y = redbox_size // 2 + offset
        pygame.draw.ellipse(redbox, (180, 0, 0), (redbox_size-12, wing_y-6, 18, 12))
        IMAGES[f'redbox-{flap}'] = redbox

    bluebox_size = 68
    for flap, offset in [('upflap', -10), ('midflap', 0), ('downflap', 10)]:
        bluebox = pygame.Surface((bluebox_size, bluebox_size), pygame.SRCALPHA)
        pygame.draw.rect(bluebox, COLORS['blue_box'], (0, 0, bluebox_size, bluebox_size))
        pygame.draw.rect(bluebox, (0, 0, 139), (0, 0, bluebox_size, bluebox_size), 2)
        wing_y = bluebox_size // 2 + offset
        pygame.draw.ellipse(bluebox, (0, 0, 180), (bluebox_size-20, wing_y-10, 30, 20))
        IMAGES[f'bluebox-{flap}'] = bluebox

    yellowbox_size = 68
    for flap, offset in [('upflap', -10), ('midflap', 0), ('downflap', 10)]:
        yellowbox = pygame.Surface((yellowbox_size, yellowbox_size), pygame.SRCALPHA)
        pygame.draw.rect(yellowbox, COLORS['yellow_box'], (0, 0, yellowbox_size, yellowbox_size))
        pygame.draw.rect(yellowbox, (184, 134, 0), (0, 0, yellowbox_size, yellowbox_size), 2)
        wing_y = yellowbox_size // 2 + offset
        pygame.draw.ellipse(yellowbox, (218, 165, 32), (yellowbox_size-20, wing_y-10, 30, 20))
        IMAGES[f'yellowbox-{flap}'] = yellowbox

    font = pygame.font.SysFont('Arial', 60, bold=True)
    for i in range(10):
        num_surface = font.render(str(i), True, COLORS['white'])
        IMAGES[str(i)] = num_surface

    message = pygame.Surface((368, 534), pygame.SRCALPHA)
    pygame.draw.rect(message, (0, 0, 0, 128), (0, 0, 368, 534))
    pygame.draw.rect(message, COLORS['white'], (0, 0, 368, 534), 2)
    title_font = pygame.font.SysFont('Arial', 60, bold=True)
    title_text = title_font.render("Flappy Pobre", True, COLORS['text'])
    title_rect = title_text.get_rect(center=(184, 100))
    message.blit(title_text, title_rect)
    inst_font = pygame.font.SysFont('Arial', 30)
    inst_text = inst_font.render("Presiona ESPACIO", True, COLORS['text'])
    inst_rect = inst_text.get_rect(center=(184, 300))
    message.blit(inst_text, inst_rect)
    inst_text2 = inst_font.render("para empezar", True, COLORS['text'])
    inst_rect2 = inst_text2.get_rect(center=(184, 340))
    message.blit(inst_text2, inst_rect2)
    IMAGES['message'] = message

    gameover = pygame.Surface((376, 120), pygame.SRCALPHA)
    pygame.draw.rect(gameover, (0, 0, 0, 128), (0, 0, 376, 120))
    pygame.draw.rect(gameover, COLORS['white'], (0, 0, 376, 120), 2)
    go_font = pygame.font.SysFont('Arial', 80, bold=True)
    go_text = go_font.render("Game Over", True, COLORS['text'])
    go_rect = go_text.get_rect(center=(188, 60))
    gameover.blit(go_text, go_rect)
    IMAGES['gameover'] = gameover

    button_width, button_height = 150, 50
    button = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    pygame.draw.rect(button, COLORS['button'], (0, 0, button_width, button_height))
    pygame.draw.rect(button, COLORS['white'], (0, 0, button_width, button_height), 2)
    button_font = pygame.font.SysFont('Arial', 30, bold=True)
    button_text = button_font.render("Tabla", True, COLORS['white'])
    button_text_rect = button_text.get_rect(center=(button_width//2, button_height//2))
    button.blit(button_text, button_text_rect)
    IMAGES['button'] = button

    # Botón de usuario
    user_button = pygame.Surface((button_width, button_height), pygame.SRCALPHA)
    pygame.draw.rect(user_button, COLORS['user_button'], (0, 0, button_width, button_height))
    pygame.draw.rect(user_button, COLORS['white'], (0, 0, button_width, button_height), 2)
    user_button_text = button_font.render("Usuario", True, COLORS['white'])
    user_button_text_rect = user_button_text.get_rect(center=(button_width//2, button_height//2))
    user_button.blit(user_button_text, user_button_text_rect)
    IMAGES['user_button'] = user_button

    clear_button_width, clear_button_height = 100, 35
    clear_button = pygame.Surface((clear_button_width, clear_button_height), pygame.SRCALPHA)
    pygame.draw.rect(clear_button, COLORS['clear_button'], (0, 0, clear_button_width, clear_button_height))
    pygame.draw.rect(clear_button, COLORS['white'], (0, 0, clear_button_width, clear_button_height), 2)
    clear_button_font = pygame.font.SysFont('Arial', 20, bold=True)
    clear_button_text = clear_button_font.render("Borrar", True, COLORS['white'])
    clear_button_text_rect = clear_button_text.get_rect(center=(clear_button_width//2, clear_button_height//2))
    clear_button.blit(clear_button_text, clear_button_text_rect)
    IMAGES['clear_button'] = clear_button

    scores_bg = pygame.Surface((400, 500), pygame.SRCALPHA)
    pygame.draw.rect(scores_bg, (0, 0, 0, 200), (0, 0, 400, 500))
    pygame.draw.rect(scores_bg, COLORS['white'], (0, 0, 400, 500), 3)
    title_font = pygame.font.SysFont('Arial', 28, bold=True)
    title_text = title_font.render("Tabla de Puntuaciones", True, COLORS['white'])
    title_rect = title_text.get_rect(center=(200, 40))
    scores_bg.blit(title_text, title_rect)
    IMAGES['scores_bg'] = scores_bg

def generate_sounds():
    try:
        SOUNDS['wing'] = pygame.mixer.Sound(buffer=create_sine_wave(440, 100))
        SOUNDS['point'] = pygame.mixer.Sound(buffer=create_sine_wave(880, 150))
        SOUNDS['hit'] = pygame.mixer.Sound(buffer=create_noise(200))
        SOUNDS['die'] = pygame.mixer.Sound(buffer=create_noise(500))
    except:
        print("No se pudieron generar los sonidos. El juego continuará sin sonido.")

def create_sine_wave(frequency, duration):
    sample_rate = 22050
    samples = int(sample_rate * duration / 1000)
    waves = [int(32767.0 * math.sin(2.0 * math.pi * frequency * i / sample_rate)) for i in range(samples)]
    sound_data = bytearray()
    for sample in waves:
        sound_data.extend([sample & 0xFF, (sample >> 8) & 0xFF])
    return bytes(sound_data)

def create_noise(duration):
    sample_rate = 22050
    samples = int(sample_rate * duration / 1000)
    noise = [random.randint(-32767, 32767) for _ in range(samples)]
    sound_data = bytearray()
    for sample in noise:
        sound_data.extend([sample & 0xFF, (sample >> 8) & 0xFF])
    return bytes(sound_data)

# ------------------ Main & flujo del juego (mayormente igual) ------------------
def main():
    global SCREEN, FPSCLOCK
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    if FULLSCREEN:
        SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.SCALED | pygame.FULLSCREEN)
    else:
        SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT), pygame.SCALED)
    pygame.display.set_caption('Flappy Pobre')

    generate_images()
    generate_sounds()

    # Cargar datos de usuario guardados si existen
    player_name, player_email = load_user_data()
    if not player_name:
        player_name = "Jugador"

    while True:
        randBg = random.randint(0, len(BACKGROUNDS_LIST) - 1)
        IMAGES['background'] = IMAGES[BACKGROUNDS_LIST[randBg]]
        randPlayer = random.randint(0, len(PLAYERS_LIST) - 1)
        IMAGES['player'] = (
            IMAGES[PLAYERS_LIST[randPlayer][0]],
            IMAGES[PLAYERS_LIST[randPlayer][1]],
            IMAGES[PLAYERS_LIST[randPlayer][2]],
        )
        pipeindex = random.randint(0, len(PIPES_LIST) - 1)
        pipe_key = PIPES_LIST[pipeindex]
        IMAGES['pipe'] = (
            pygame.transform.flip(IMAGES[pipe_key], False, True),
            IMAGES[pipe_key],
        )
        HITMASKS['pipe'] = (getHitmask(IMAGES['pipe'][0]), getHitmask(IMAGES['pipe'][1]))
        HITMASKS['player'] = (
            getReducedHitmask(IMAGES['player'][0]),
            getReducedHitmask(IMAGES['player'][1]),
            getReducedHitmask(IMAGES['player'][2]),
        )

        movementInfo = showWelcomeAnimation(player_name, player_email)
        player_name, player_email = movementInfo['player_name'], movementInfo['player_email']
        crashInfo = mainGame(movementInfo, player_name)
        # showGameOverScreen ahora pedirá nombre y email y enviará correo
        showGameOverScreen(crashInfo, player_name, player_email)

def showWelcomeAnimation(player_name="Jugador", player_email=""):
    playerIndex = 0
    playerIndexGen = cycle([0, 1, 2, 1])
    loopIter = 0
    playerx = int(SCREENWIDTH * 0.2)
    playery = int((SCREENHEIGHT - IMAGES['player'][0].get_height()) / 2)
    messagex = int((SCREENWIDTH - IMAGES['message'].get_width()) / 2)
    messagey = int(SCREENHEIGHT * 0.12)
    buttonx = int((SCREENWIDTH - IMAGES['button'].get_width()) / 2)
    buttony = int(SCREENHEIGHT * 0.7)
    user_buttonx = int((SCREENWIDTH - IMAGES['user_button'].get_width()) / 2)
    user_buttony = int(SCREENHEIGHT * 0.6)
    basex = 0
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()
    playerShmVals = {'val': 0, 'dir': 1}
    
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit(); sys.exit()
            if (event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP)) or event.type == MOUSEBUTTONDOWN:
                if event.type == MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    button_rect = pygame.Rect(buttonx, buttony, IMAGES['button'].get_width(), IMAGES['button'].get_height())
                    user_button_rect = pygame.Rect(user_buttonx, user_buttony, IMAGES['user_button'].get_width(), IMAGES['user_button'].get_height())
                    
                    if button_rect.collidepoint(mouse_pos):
                        showScoresTable()
                        continue
                    elif user_button_rect.collidepoint(mouse_pos):
                        # Pedir información del usuario
                        name, email = get_user_info()
                        if name is not None and email is not None:
                            player_name = name
                            player_email = email
                            save_user_data(player_name, player_email)
                        continue
                
                if 'wing' in SOUNDS:
                    SOUNDS['wing'].play()
                return {
                    'playery': playery + playerShmVals['val'], 
                    'basex': basex, 
                    'playerIndexGen': playerIndexGen,
                    'player_name': player_name,
                    'player_email': player_email
                }
        
        if (loopIter + 1) % 5 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 4) % baseShift)
        playerShm(playerShmVals)
        
        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(IMAGES['player'][playerIndex], (playerx, playery + playerShmVals['val']))
        SCREEN.blit(IMAGES['message'], (messagex, messagey))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        SCREEN.blit(IMAGES['button'], (buttonx, buttony))
        SCREEN.blit(IMAGES['user_button'], (user_buttonx, user_buttony))
        
        # --- MODIFICACIÓN: Mostrar información del usuario o "vacío" ---
        font = pygame.font.SysFont(None, 28) # Usamos una fuente un poco más pequeña
        if player_name != "Jugador" and player_email:
            # Si el email es muy largo, lo acortamos para que quepa en pantalla
            display_email = player_email
            if len(display_email) > 25:
                display_email = display_email[:22] + "..."
            user_info_text = font.render(f"Usuario: {player_name} | {display_email}", True, (255, 255, 255))
        else:
            # Si no hay usuario, mostramos "vacío"
            user_info_text = font.render("Usuario: vacío", True, (180, 180, 180))

        user_info_rect = user_info_text.get_rect(center=(SCREENWIDTH/2, 30))
        SCREEN.blit(user_info_text, user_info_rect)
        # --- FIN DE LA MODIFICACIÓN ---

        text = font.render("Presiona ESPACIO o haz clic para jugar", True, (255, 255, 255))
        text_rect = text.get_rect(center=(SCREENWIDTH/2, SCREENHEIGHT - 80))
        SCREEN.blit(text, text_rect)
        text_quit = font.render("Presiona ESC para salir", True, (255, 255, 255))
        text_quit_rect = text_quit.get_rect(center=(SCREENWIDTH/2, SCREENHEIGHT - 50))
        SCREEN.blit(text_quit, text_quit_rect)
        
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def showScoresTable():
    scores_x = (SCREENWIDTH - IMAGES['scores_bg'].get_width()) // 2
    scores_y = (SCREENHEIGHT - IMAGES['scores_bg'].get_height()) // 2
    clear_button_x = scores_x + 150
    clear_button_y = scores_y + 410
    close_area = pygame.Rect(scores_x - 10, scores_y - 10, IMAGES['scores_bg'].get_width() + 20, IMAGES['scores_bg'].get_height() + 20)
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and event.key == K_ESCAPE:
                return
            if event.type == MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                clear_button_rect = pygame.Rect(clear_button_x, clear_button_y, IMAGES['clear_button'].get_width(), IMAGES['clear_button'].get_height())
                if clear_button_rect.collidepoint(mouse_pos):
                    clear_high_scores()
                if not close_area.collidepoint(mouse_pos):
                    return
        scores_surface = IMAGES['scores_bg'].copy()
        scores = load_high_scores()
        font = pygame.font.SysFont('Arial', 14)
        y_offset = 100
        if not scores:
            no_scores_text = font.render("No hay puntuaciones guardadas", True, COLORS['white'])
            no_scores_rect = no_scores_text.get_rect(center=(200, 250))
            scores_surface.blit(no_scores_text, no_scores_rect)
        else:
            headers = ["Pos", "Nombre", "Tuberías"]
            header_x_positions = [80, 150, 280]
            for i, header in enumerate(headers):
                header_text = font.render(header, True, (255, 255, 0))
                header_rect = header_text.get_rect(center=(header_x_positions[i], y_offset))
                scores_surface.blit(header_text, header_rect)
            y_offset += 25
            for i, score_data in enumerate(scores[:10]):
                pos_text = font.render(f"{i+1}", True, COLORS['white'])
                pos_rect = pos_text.get_rect(center=(header_x_positions[0], y_offset))
                scores_surface.blit(pos_text, pos_rect)
                name = score_data['name']
                if len(name) > 12:
                    name = name[:12] + "..."
                name_text = font.render(name, True, COLORS['white'])
                name_rect = name_text.get_rect(center=(header_x_positions[1], y_offset))
                scores_surface.blit(name_text, name_rect)
                score_text = font.render(str(score_data['score']), True, COLORS['white'])
                score_rect = score_text.get_rect(center=(header_x_positions[2], y_offset))
                scores_surface.blit(score_text, score_rect)
                y_offset += 25
        current_score, current_name = load_current_score()
        if current_score > 0:
            current_text = font.render(f"Progreso actual de {current_name}: {current_score} tuberías", True, (255, 255, 0))
            current_rect = current_text.get_rect(center=(200, y_offset + 20))
            scores_surface.blit(current_text, current_rect)
        close_font = pygame.font.SysFont('Arial', 14)
        close_text = close_font.render("Haz clic fuera para cerrar", True, COLORS['white'])
        close_rect = close_text.get_rect(center=(200, 460))
        scores_surface.blit(close_text, close_rect)
        SCREEN.blit(IMAGES['background'], (0, 0))
        SCREEN.blit(scores_surface, (scores_x, scores_y))
        SCREEN.blit(IMAGES['clear_button'], (clear_button_x, clear_button_y))
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def mainGame(movementInfo, player_name):
    score, _ = load_current_score()
    playerIndex = loopIter = 0
    playerIndexGen = movementInfo['playerIndexGen']
    playerx, playery = int(SCREENWIDTH * 0.2), movementInfo['playery']
    basex = movementInfo['basex']
    baseShift = IMAGES['base'].get_width() - IMAGES['background'].get_width()
    newPipe1 = getRandomPipe()
    newPipe2 = getRandomPipe()
    upperPipes = [{'x': SCREENWIDTH + 200, 'y': newPipe1[0]['y']}, {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[0]['y']},]
    lowerPipes = [{'x': SCREENWIDTH + 200, 'y': newPipe1[1]['y']}, {'x': SCREENWIDTH + 200 + (SCREENWIDTH / 2), 'y': newPipe2[1]['y']},]
    pipeVelX = -4
    playerVelY = -9
    playerMaxVelY = 10
    playerMinVelY = -8
    playerAccY = 1
    playerRot = 45
    playerVelRot = 3
    playerRotThr = 20
    playerFlapAcc = -9
    playerFlapped = False
    save_counter = 0
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                save_current_score(score, player_name)
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP) or event.type == MOUSEBUTTONDOWN:
                if playery > -2 * IMAGES['player'][0].get_height():
                    playerVelY = playerFlapAcc
                    playerFlapped = True
                    if 'wing' in SOUNDS:
                        SOUNDS['wing'].play()
        crashTest = checkCrash({'x': playerx, 'y': playery, 'index': playerIndex}, upperPipes, lowerPipes)
        if crashTest[0]:
            save_current_score(0, player_name)
            return {'y': playery, 'groundCrash': crashTest[1], 'basex': basex, 'upperPipes': upperPipes, 'lowerPipes': lowerPipes, 'score': score, 'playerVelY': playerVelY, 'playerRot': playerRot}
        playerMidPos = playerx + IMAGES['player'][0].get_width() / 2
        for pipe in upperPipes:
            pipeMidPos = pipe['x'] + IMAGES['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                score += 1
                save_current_score(score, player_name)
                if 'point' in SOUNDS:
                    SOUNDS['point'].play()
        save_counter += 1
        if save_counter >= 60:
            save_current_score(score, player_name)
            save_counter = 0
        if (loopIter + 1) % 3 == 0:
            playerIndex = next(playerIndexGen)
        loopIter = (loopIter + 1) % 30
        basex = -((-basex + 100) % baseShift)
        if playerRot > -90:
            playerRot -= playerVelRot
        if playerVelY < playerMaxVelY and not playerFlapped:
            playerVelY += playerAccY
        if playerFlapped:
            playerFlapped = False
            playerRot = 45
        playerHeight = IMAGES['player'][playerIndex].get_height()
        playery += min(playerVelY, BASEY - playery - playerHeight)
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipe['x'] += pipeVelX
            lPipe['x'] += pipeVelX
        if len(upperPipes) > 0 and 0 < upperPipes[0]['x'] < 5:
            newPipe = getRandomPipe()
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])
        if len(upperPipes) > 0 and upperPipes[0]['x'] < -IMAGES['pipe'][0].get_width():
            upperPipes.pop(0)
            lowerPipes.pop(0)
        SCREEN.blit(IMAGES['background'], (0, 0))
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)
        font = pygame.font.SysFont(None, 24)
        name_text = font.render(f"Jugador: {player_name}", True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(SCREENWIDTH/2, 30))
        SCREEN.blit(name_text, name_rect)
        visibleRot = playerRotThr
        if playerRot <= playerRotThr:
            visibleRot = playerRot
        playerSurface = pygame.transform.rotate(IMAGES['player'][playerIndex], visibleRot)
        SCREEN.blit(playerSurface, (playerx, playery))
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def showGameOverScreen(crashInfo, player_name, player_email=""):
    """
    Ahora: cuando muere el jugador se le pide nombre+email, se actualiza la tabla y se intenta enviar email.
    Mostramos un mensaje de estado del envío en pantalla.
    """
    score = crashInfo['score']
    playerx = SCREENWIDTH * 0.2
    playery = crashInfo['y']
    playerHeight = IMAGES['player'][0].get_height()
    playerVelY = crashInfo['playerVelY']
    playerAccY = 2
    playerRot = crashInfo['playerRot']
    playerVelRot = 7
    basex = crashInfo['basex']
    upperPipes, lowerPipes = crashInfo['upperPipes'], crashInfo['lowerPipes']

    # Reproducir sonidos
    if 'hit' in SOUNDS:
        SOUNDS['hit'].play()
    if not crashInfo['groundCrash'] and 'die' in SOUNDS:
        SOUNDS['die'].play()

    # Si ya tenemos un email, no pedimos de nuevo
    if player_email:
        name = player_name
        email = player_email
        update_high_scores(score, name)
        ok, err = send_score_email(email, name, score)
        send_ok = ok
        send_err = err
    else:
        # Pedimos nombre y correo
        name, email = get_name_and_email(score, default_name=player_name)
        send_ok = None
        send_err = ""
        used_name = player_name
        if name is None:
            # usuario cancelo -> usar nombre inicial y no enviar correo
            used_name = player_name if player_name else "Jugador"
        else:
            used_name = name
            # Actualizar tabla con el nombre obtenido
            update_high_scores(score, used_name)
            # Intentar envio de correo (solo si email valido mínimo)
            if email and "@" in email and "." in email:
                ok, err = send_score_email(email, used_name, score)
                send_ok = ok
                send_err = err
            else:
                send_ok = False
                send_err = "Correo inválido."

        # Si el jugador no ingreso nombre (o cancelo), igualmente actualizamos la tabla con player_name
        if name is None:
            update_high_scores(score, used_name)

    # Mostrar pantalla final con estado del envío
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit(); sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP) or event.type == MOUSEBUTTONDOWN:
                if playery + playerHeight >= BASEY - 1:
                    return

        if playery + playerHeight < BASEY - 1:
            playery += min(playerVelY, BASEY - playery - playerHeight)
        if playerVelY < 15:
            playerVelY += playerAccY
        if not crashInfo['groundCrash']:
            if playerRot > -90:
                playerRot -= playerVelRot

        SCREEN.blit(IMAGES['background'], (0, 0))
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            SCREEN.blit(IMAGES['pipe'][0], (uPipe['x'], uPipe['y']))
            SCREEN.blit(IMAGES['pipe'][1], (lPipe['x'], lPipe['y']))
        SCREEN.blit(IMAGES['base'], (basex, BASEY))
        showScore(score)
        playerSurface = pygame.transform.rotate(IMAGES['player'][1], playerRot)
        SCREEN.blit(playerSurface, (playerx, playery))
        SCREEN.blit(IMAGES['gameover'], (100, 360))

        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Tuberías superadas: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREENWIDTH/2, 300))
        SCREEN.blit(score_text, score_rect)

        # Mensaje sobre el envío de email
        small = pygame.font.SysFont(None, 24)
        if player_email:
            if send_ok:
                info_text = small.render(f"Correo enviado a {player_email}.", True, (0, 220, 0))
            else:
                info_text = small.render(f"No se pudo enviar correo: {send_err}", True, (220, 70, 70))
            SCREEN.blit(info_text, (SCREENWIDTH//2 - info_text.get_width()//2, 340))
        else:
            if name is None:
                info_text = small.render("No ingresaste nombre/correo. Puntaje guardado localmente.", True, (255, 200, 0))
                SCREEN.blit(info_text, (SCREENWIDTH//2 - info_text.get_width()//2, 340))
            else:
                if send_ok is None:
                    info_text = small.render("Intentando enviar correo...", True, (200, 200, 200))
                elif send_ok:
                    info_text = small.render(f"Correo enviado a {email}.", True, (0, 220, 0))
                else:
                    info_text = small.render(f"No se pudo enviar correo: {send_err}", True, (220, 70, 70))
                SCREEN.blit(info_text, (SCREENWIDTH//2 - info_text.get_width()//2, 340))

        font2 = pygame.font.SysFont(None, 28)
        instr = font2.render("Presiona ESPACIO o clic para jugar de nuevo (ESC salir)", True, (255,255,255))
        SCREEN.blit(instr, (SCREENWIDTH//2 - instr.get_width()//2, SCREENHEIGHT - 80))

        pygame.display.update()
        clock.tick(FPS)

def playerShm(playerShm):
    if abs(playerShm['val']) == 8:
        playerShm['dir'] *= -1
    if playerShm['dir'] == 1:
        playerShm['val'] += 1
    else:
        playerShm['val'] -= 1

def getRandomPipe():
    gapY = random.randrange(0, int(BASEY * 0.6 - PIPEGAPSIZE))
    gapY += int(BASEY * 0.2)
    pipeHeight = IMAGES['pipe'][0].get_height()
    pipeX = SCREENWIDTH + 10
    return [{'x': pipeX, 'y': gapY - pipeHeight}, {'x': pipeX, 'y': gapY + PIPEGAPSIZE},]

def showScore(score):
    scoreDigits = [int(x) for x in list(str(score))]
    totalWidth = 0
    for digit in scoreDigits:
        totalWidth += IMAGES[str(digit)].get_width()
    Xoffset = (SCREENWIDTH - totalWidth) / 2
    for digit in scoreDigits:
        SCREEN.blit(IMAGES[str(digit)], (Xoffset, SCREENHEIGHT * 0.1))
        Xoffset += IMAGES[str(digit)].get_width()

def checkCrash(player, upperPipes, lowerPipes):
    pi = player['index']
    player['w'] = IMAGES['player'][0].get_width()
    player['h'] = IMAGES['player'][0].get_height()
    if player['y'] + player['h'] >= BASEY - 1:
        return [True, True]
    else:
        if 'redbox' in PLAYERS_LIST[pi][0]:
            collision_size = 25
        else:
            collision_size = 40
        collision_offset = (player['w'] - collision_size) / 2
        playerRect = pygame.Rect(player['x'] + collision_offset, player['y'] + collision_offset, collision_size, collision_size)
        pipeW = IMAGES['pipe'][0].get_width()
        pipeH = IMAGES['pipe'][0].get_height()
        for uPipe, lPipe in zip(upperPipes, lowerPipes):
            uPipeRect = pygame.Rect(uPipe['x'], uPipe['y'], pipeW, pipeH)
            lPipeRect = pygame.Rect(lPipe['x'], lPipe['y'], pipeW, pipeH)
            pHitMask = HITMASKS['player'][pi]
            uHitmask = HITMASKS['pipe'][0]
            lHitmask = HITMASKS['pipe'][1]
            uCollide = pixelCollision(playerRect, uPipeRect, pHitMask, uHitmask)
            lCollide = pixelCollision(playerRect, lPipeRect, pHitMask, lHitmask)
            if uCollide or lCollide:
                return [True, False]
    return [False, False]

def pixelCollision(rect1, rect2, hitmask1, hitmask2):
    rect = rect1.clip(rect2)
    if rect.width == 0 or rect.height == 0:
        return False
    x1, y1 = rect.x - rect1.x, rect.y - rect1.y
    x2, y2 = rect.x - rect2.x, rect.y - rect2.y
    for x in xrange(rect.width):
        for y in xrange(rect.height):
            if hitmask1[x1 + x][y1 + y] and hitmask2[x2 + x][y2 + y]:
                return True
    return False

def getHitmask(image):
    mask = []
    for x in xrange(image.get_width()):
        mask.append([])
        for y in xrange(image.get_height()):
            mask[x].append(bool(image.get_at((x, y))[3]))
    return mask

def getReducedHitmask(image):
    width, height = image.get_width(), image.get_height()
    # No podemos inspeccionar el "nombre" del sprite; usamos tamaños para decidir
    if image.get_width() <= 40:
        collision_size = 25
    else:
        collision_size = 40
    offset_x = (width - collision_size) // 2
    offset_y = (height - collision_size) // 2
    mask = []
    for x in xrange(width):
        mask.append([])
        for y in xrange(height):
            if offset_x <= x < offset_x + collision_size and offset_y <= y < offset_y + collision_size:
                mask[x].append(bool(image.get_at((x, y))[3]))
            else:
                mask[x].append(False)
    return mask

if __name__ == "__main__":
    main()
