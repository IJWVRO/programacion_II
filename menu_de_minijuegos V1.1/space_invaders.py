# space_invaders_final_fixed.py
import pygame
import random
import sys
import os
import time
import json
import smtplib
from email.message import EmailMessage
from datetime import datetime

# ------------------ CONFIG (solo estas 2 variables para SMTP/Gmail) ------------------
# Reemplaza con tu email y la contraseña de aplicación (app password).
EMAIL_ADDRESS = "fairbotnotifier@gmail.com"    # <- pon aquí tu correo (o "" si no usarás mails)
EMAIL_PASSWORD = "pvrcyhncquzcibyv"   # <- pon aquí tu clave de aplicación (o "")

# ------------------ Inicialización / Config ------------------
pygame.init()
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except Exception as e:
    print("Advertencia: no se pudo inicializar el mixer:", e)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders - Mejorado")
clock = pygame.time.Clock()
FPS = 60

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 220, 0)
RED = (220, 60, 60)
YELLOW = (230, 230, 80)
BLUE = (100, 150, 255)
GRAY = (60, 60, 60)
GOLD = (220, 190, 40)
HIGHLIGHT = (160, 220, 120)
INPUT_BG = (245, 245, 245)
INPUT_BORDER = (200, 200, 200)

# Fuentes
font_small = pygame.font.SysFont("consolas", 16)
font_med = pygame.font.SysFont("consolas", 24)
font_big = pygame.font.SysFont("consolas", 44)

# Música (nombres de archivo locales - opcional)
menu = "menu.mp3"
juego = "game.mp3"

menu_volume = 0.3
game_volume = 0.6

SCORES_JSON = "scores.json"

# --- Variables globales para el perfil del jugador ---
PLAYER_NAME = ""    # inicializado como string vacío
PLAYER_EMAIL = ""   # inicializado como string vacío
IS_GUEST = False    # bandera para indicar modo invitado

# ------------------ Funciones para JSON de puntajes ------------------
def load_scores_json():
    """Lee scores.json y devuelve lista ordenada de dicts con keys: name, score, email, date"""
    if not os.path.exists(SCORES_JSON):
        return []
    try:
        with open(SCORES_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                out = []
                for it in data:
                    if isinstance(it, dict) and "name" in it and "score" in it:
                        try:
                            out.append({
                                "name": str(it.get("name", "") or ""),
                                "score": int(it.get("score", 0)),
                                "email": str(it.get("email", "") or ""),
                                "date": str(it.get("date", "") or "")
                            })
                        except Exception:
                            continue
                out.sort(key=lambda x: x["score"], reverse=True)
                return out
    except Exception as e:
        print("No se pudo leer scores.json:", e)
    return []

def save_score_json(name, pts, email=""):
    """
    Guarda/actualiza el score del jugador (solo el mejor).
    Retorna (was_new_record: bool, previous_best:int, new_rank:int).
    """
    name = str(name).strip() or "Invitado"
    email = str(email).strip()
    pts = int(pts)

    scores = load_scores_json()
    previous_best = 0
    found = False

    # Buscar y actualizar (comparación por nombre sin distinguir mayúsculas)
    for s in scores:
        if s["name"].lower() == name.lower():
            found = True
            previous_best = s.get("score", 0)
            if pts > s["score"]:
                s["score"] = pts
                s["date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if email:
                    s["email"] = email
                was_new_record = True
                print(f"[scores] Actualizado récord {name}: {previous_best} -> {pts}")
            else:
                was_new_record = False
            break

    if not found:
        new_item = {
            "name": name,
            "score": pts,
            "email": email,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        scores.append(new_item)
        was_new_record = True
        print(f"[scores] Nuevo jugador agregado: {name} ({pts})")

    # Ordenar y guardar
    scores.sort(key=lambda x: x["score"], reverse=True)
    try:
        with open(SCORES_JSON, "w", encoding="utf-8") as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error guardando scores.json:", e)

    # Calcular nuevo rank
    new_rank = None
    for i, s in enumerate(scores):
        if s["name"].lower() == name.lower():
            new_rank = i + 1
            break

    return was_new_record, previous_best, new_rank or (len(scores) if scores else 0)

# ------------------ Envío de correo (Gmail: smtp.gmail.com:587, STARTTLS) ------------------
def enviar_correo_gmail(destinatario, nombre, puntaje, puesto=None, fecha=None):
    """Envía correo normal con info del puntaje. Devuelve True/False."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("[mail] Credenciales no configuradas: no se enviará correo.")
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = f"Resultado en Space Invaders: {puntaje} pts"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = destinatario

        lines = [
            f"Hola {nombre},",
            "",
            f"Tu puntaje en Space Invaders fue de {puntaje} puntos."
        ]
        if puesto:
            lines.append(f"Posición en ranking local: #{puesto}")
        if fecha:
            lines.append(f"Fecha: {fecha}")
        lines.append("")
        lines.append("¡Sigue intentando superar tu marca!")
        body = "\n".join(lines)
        msg.set_content(body)

        server = "smtp.gmail.com"
        port = 587
        with smtplib.SMTP(server, port, timeout=10) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            s.send_message(msg)
        print(f"[mail] Correo de puntaje enviado a {destinatario}")
        return True
    except Exception as e:
        print("Error al enviar correo (SMTP):", e)
        return False

def enviar_correo_nuevo_record(destinatario, nombre, puntaje, puesto=None, fecha=None):
    """Envía correo especial por nuevo récord personal."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("[mail] Credenciales no configuradas: no se enviará correo.")
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = f"¡NUEVO RÉCORD PERSONAL en Space Invaders! ({puntaje} pts)"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = destinatario

        lines = [
            f"¡FELICIDADES, {nombre}!",
            "",
            f"Has establecido un nuevo récord personal con {puntaje} puntos."
        ]
        if puesto:
            lines.append(f"Posición actual en ranking local: #{puesto}")
        if fecha:
            lines.append(f"Fecha: {fecha}")
        lines.append("")
        lines.append("¡Excelente trabajo!")
        body = "\n".join(lines)
        msg.set_content(body)

        server = "smtp.gmail.com"
        port = 587
        with smtplib.SMTP(server, port, timeout=10) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            s.send_message(msg)
        print(f"[mail] Correo de NUEVO RÉCORD enviado a {destinatario}")
        return True
    except Exception as e:
        print("Error al enviar correo de nuevo récord (SMTP):", e)
        return False

def enviar_correo_top1(destinatario, nombre, puntaje, fecha=None):
    """Correo especial cuando el jugador llega a #1 global (local leaderboard)."""
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("[mail] Credenciales no configuradas: no se enviará correo.")
        return False
    try:
        msg = EmailMessage()
        msg["Subject"] = f"¡ERES #1 en Space Invaders! ({puntaje} pts)"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = destinatario

        lines = [
            f"¡IMPRESIONANTE, {nombre}!",
            "",
            f"Has alcanzado la posición #1 en el ranking local con {puntaje} puntos."
        ]
        if fecha:
            lines.append(f"Fecha: {fecha}")
        lines.append("")
        lines.append("¡Felicitaciones por ser el mejor localmente!")
        body = "\n".join(lines)
        msg.set_content(body)

        server = "smtp.gmail.com"
        port = 587
        with smtplib.SMTP(server, port, timeout=10) as s:
            s.ehlo()
            s.starttls()
            s.ehlo()
            s.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            s.send_message(msg)
        print(f"[mail] Correo TOP #1 enviado a {destinatario}")
        return True
    except Exception as e:
        print("Error al enviar correo TOP1 (SMTP):", e)
        return False

# ------------------ Reproducción de música ------------------
def play_music_with_fade(file, volume=0.6, loop=True, fade_ms=800):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    if os.path.exists(path):
        try:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.fadeout(fade_ms)
                pygame.time.delay(fade_ms)
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0, fade_ms=fade_ms)
        except Exception as e:
            print("Error al reproducir música:", e)
    else:
        # no es crítico, solo aviso
        pass

def play_music_instant(file, volume=0.6, loop=True):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file)
    if os.path.exists(path):
        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1 if loop else 0)
        except Exception as e:
            print("Error al reproducir música (instant):", e)

def stop_music(fade_ms=0):
    try:
        if pygame.mixer.music.get_busy() and fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
    except Exception:
        pass

# ------------------ Fondo de estrellas ------------------
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(70)]

def update_stars():
    for s in stars:
        s[1] += 1
        if s[1] > HEIGHT:
            s[0] = random.randint(0, WIDTH)
            s[1] = 0

def draw_background():
    screen.fill(BLACK)
    for s in stars:
        pygame.draw.circle(screen, WHITE, (s[0], s[1]), 1)

# ------------------ Utilidades de texto y UI ------------------
def draw_text_center(text, font_obj, color, x, y):
    surf = font_obj.render(text, True, color)
    rect = surf.get_rect(center=(x, y))
    screen.blit(surf, rect)
    return rect

def draw_text_left(text, font_obj, color, x, y):
    surf = font_obj.render(text, True, color)
    rect = surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)
    return rect

def draw_button(rect, text, base_color, hover_color=None, text_color=BLACK):
    mx, my = pygame.mouse.get_pos()
    color = base_color
    if rect.collidepoint(mx, my) and hover_color:
        color = hover_color
    pygame.draw.rect(screen, color, rect, border_radius=8)
    draw_text_center(text, font_med, text_color, rect.centerx, rect.centery)

# ------------------ Enemigos ------------------
def create_enemies(rows=4, cols=8):
    enemies = []
    for r in range(rows):
        for c in range(cols):
            x = 80 + c * 70
            y = 60 + r * 60
            enemies.append(pygame.Rect(x, y, 40, 40))
    return enemies

# ------------------ Loading y fade ------------------
def loading_screen(seconds=0.8):
    t0 = time.time()
    while time.time() - t0 < seconds:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        update_stars()
        draw_background()
        draw_text_center("CARGANDO...", font_big, WHITE, WIDTH//2, HEIGHT//2 - 20)
        frac = (time.time() - t0) / seconds
        if frac > 1: frac = 1
        bw = 400; bh = 14
        bx = WIDTH//2 - bw//2; by = HEIGHT//2 + 20
        pygame.draw.rect(screen, GRAY, (bx, by, bw, bh), border_radius=6)
        pygame.draw.rect(screen, GREEN, (bx, by, int(bw * frac), bh), border_radius=6)
        pygame.display.flip()

def fade_out_screen(duration_ms=300):
    fade = pygame.Surface((WIDTH, HEIGHT))
    fade.fill(BLACK)
    steps = 15
    delay = max(1, duration_ms // steps)
    for i in range(steps+1):
        alpha = int((i/steps) * 255)
        fade.set_alpha(alpha)
        update_stars()
        draw_background()
        screen.blit(fade, (0, 0))
        pygame.display.flip()
        pygame.time.delay(delay)

# ------------------ Ajuste de volumen ------------------
def adjust_volumes():
    global menu_volume, game_volume
    selected = 0  # 0=menu, 1=game
    play_music_instant(menu, menu_volume)
    adjusting = True
    while adjusting:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_TAB:
                    selected = 1 - selected
                    if selected == 0:
                        play_music_instant(menu, menu_volume)
                    else:
                        play_music_instant(juego, game_volume)
                elif ev.key == pygame.K_LEFT:
                    if selected == 0:
                        menu_volume = max(0.0, round(menu_volume - 0.05, 2))
                        pygame.mixer.music.set_volume(menu_volume)
                    else:
                        game_volume = max(0.0, round(game_volume - 0.05, 2))
                        pygame.mixer.music.set_volume(game_volume)
                elif ev.key == pygame.K_RIGHT:
                    if selected == 0:
                        menu_volume = min(1.0, round(menu_volume + 0.05, 2))
                        pygame.mixer.music.set_volume(menu_volume)
                    else:
                        game_volume = min(1.0, round(game_volume + 0.05, 2))
                        pygame.mixer.music.set_volume(game_volume)
                elif ev.key == pygame.K_ESCAPE:
                    play_music_with_fade(menu, menu_volume, fade_ms=400)
                    adjusting = False

        update_stars()
        draw_background()
        draw_text_center("AJUSTAR VOLUMEN", font_big, YELLOW, WIDTH//2, HEIGHT//6)
        draw_text_center("TAB = cambiar MENÚ/JUEGO | ← / → = ajustar | ESC = volver", font_small, BLUE, WIDTH//2, HEIGHT//6 + 40)
        draw_text_center(f"{'MENÚ' if selected == 0 else 'JUEGO'}: {int((menu_volume if selected==0 else game_volume)*100)}%", font_med, WHITE, WIDTH//2, HEIGHT//2)
        pygame.display.flip()

# ------------------ Triángulos para paginación ------------------
def draw_triangle_button(centerx, centery, size, direction="right", base_color=WHITE):
    """Dibuja triángulo (right/left) y devuelve rect para colisiones."""
    half = size // 2
    if direction == "right":
        points = [(centerx-half, centery-half), (centerx-half, centery+half), (centerx+half, centery)]
    else:
        points = [(centerx+half, centery-half), (centerx+half, centery+half), (centerx-half, centery)]
    pygame.draw.polygon(screen, base_color, points)
    minx = min(p[0] for p in points); maxx = max(p[0] for p in points)
    miny = min(p[1] for p in points); maxy = max(p[1] for p in points)
    return pygame.Rect(minx, miny, maxx - minx, maxy - miny)

def show_scores_screen():
    """Muestra puntajes con paginación y triángulos prev/next. Resalta PLAYER_NAME."""
    play_music_with_fade(menu, menu_volume, fade_ms=200)
    scores = load_scores_json()
    per_page = 10
    page = 0
    total_pages = max(1, (len(scores) + per_page - 1) // per_page)
    showing = True
    while showing:
        clock.tick(FPS)
        click = False
        mx, my = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                click = True
                mx, my = ev.pos
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    showing = False
                elif ev.key == pygame.K_LEFT:
                    page = max(0, page - 1)
                elif ev.key == pygame.K_RIGHT:
                    page = min(total_pages - 1, page + 1)

        update_stars()
        draw_background()
        draw_text_center("TABLA DE PUNTAJES", font_big, YELLOW, WIDTH//2, 70)
        draw_text_center("Nombre — Puntos    (email abajo)    (fecha)", font_small, BLUE, WIDTH//2, 102)

        start_idx = page * per_page
        for i, it in enumerate(scores[start_idx:start_idx + per_page]):
            index = start_idx + i
            line = f"{index+1:02d}. {it['name']} — {it['score']}"
            # Resaltar si es el jugador actual
            color = WHITE
            if PLAYER_NAME and it['name'].lower() == PLAYER_NAME.lower():
                color = HIGHLIGHT
            # Si es top1 y primera página, usar gold para el #1
            if index == 0 and page == 0:
                color = GOLD
            draw_text_center(line, font_med, color, WIDTH//2 - 60, 140 + i*42)
            # Email y fecha en fuente chica, a la derecha
            if it.get("email"):
                draw_text_left(f"{it.get('email')}", font_small, GRAY, WIDTH//2 - 60, 140 + i*42 + 22)
            if it.get("date"):
                draw_text_left(f"{it.get('date')}", font_small, BLUE, WIDTH//2 + 150, 140 + i*42 + 22)

        left_tri = draw_triangle_button(80, HEIGHT//2, 36, direction="left", base_color=WHITE if page>0 else GRAY)
        right_tri = draw_triangle_button(WIDTH-80, HEIGHT//2, 36, direction="right", base_color=WHITE if page < total_pages-1 else GRAY)

        draw_text_center(f"Página {page+1}/{total_pages}", font_small, BLUE, WIDTH//2, HEIGHT-40)
        draw_text_center("ESC = volver | ← → teclas | click triángulos", font_small, BLUE, WIDTH//2, HEIGHT-20)

        pygame.display.flip()

        if click:
            if left_tri.collidepoint(mx, my) and page > 0:
                page -= 1
            elif right_tri.collidepoint(mx, my) and page < total_pages - 1:
                page += 1
            else:
                # click fuera de triángulos -> salir
                showing = False

# --- Pantalla de registro de perfil (dos campos + botones Guardar y Jugar como invitado) ---
def register_player_screen():
    global PLAYER_NAME, PLAYER_EMAIL, IS_GUEST
    name = PLAYER_NAME or ""
    email = PLAYER_EMAIL or ""
    active_field = "name"  # or "email" or None
    input_box_name = pygame.Rect(WIDTH//2 - 260, HEIGHT//2 - 60, 520, 44)
    input_box_email = pygame.Rect(WIDTH//2 - 260, HEIGHT//2 + 0, 520, 44)
    save_button = pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 70, 150, 44)
    guest_button = pygame.Rect(WIDTH//2 + 10, HEIGHT//2 + 70, 150, 44)

    registering = True
    while registering:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        click = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                click = True
                if input_box_name.collidepoint(ev.pos):
                    active_field = "name"
                elif input_box_email.collidepoint(ev.pos):
                    active_field = "email"
                else:
                    active_field = None
                if save_button.collidepoint(ev.pos):
                    # Guardar perfil
                    if name.strip() == "":
                        # no se permite nombre vacío
                        print("[perfil] Nombre vacío: no se guardará.")
                    else:
                        PLAYER_NAME = name.strip()
                        PLAYER_EMAIL = email.strip()
                        IS_GUEST = False
                        print(f"[perfil] Guardado: {PLAYER_NAME}, {PLAYER_EMAIL}")
                        registering = False
                if guest_button.collidepoint(ev.pos):
                    # Jugar como invitado: no guardamos email, seteamos Invitado
                    PLAYER_NAME = "Invitado"
                    PLAYER_EMAIL = ""
                    IS_GUEST = True
                    print("[perfil] Jugando como Invitado")
                    registering = False

            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_TAB:
                    active_field = "email" if active_field == "name" else "name"
                elif ev.key == pygame.K_RETURN:
                    # si en campo nombre y no vacío, pasa a email; si en email guarda
                    if active_field == "name":
                        if name.strip() != "":
                            active_field = "email"
                    elif active_field == "email":
                        if name.strip() != "":
                            PLAYER_NAME = name.strip()
                            PLAYER_EMAIL = email.strip()
                            IS_GUEST = False
                            registering = False
                elif ev.key == pygame.K_BACKSPACE:
                    if active_field == "name":
                        name = name[:-1]
                    elif active_field == "email":
                        email = email[:-1]
                else:
                    ch = ev.unicode
                    if ch and ch.isprintable():
                        if active_field == "name" and len(name) < 30:
                            name += ch
                        elif active_field == "email" and len(email) < 100:
                            email += ch

        update_stars()
        draw_background()
        draw_text_center("REGISTRO DE JUGADOR", font_big, YELLOW, WIDTH//2, HEIGHT//4)
        draw_text_left("Nombre (obligatorio):", font_small, WHITE, input_box_name.x, input_box_name.y - 22)
        pygame.draw.rect(screen, INPUT_BG, input_box_name, border_radius=6)
        pygame.draw.rect(screen, INPUT_BORDER, input_box_name, 2, border_radius=6)
        name_surf = font_med.render(name, True, (0,0,0) if name else (120,120,120))
        screen.blit(name_surf, (input_box_name.x + 10, input_box_name.y + 8))

        draw_text_left("Correo electrónico (opcional, para notificaciones):", font_small, WHITE, input_box_email.x, input_box_email.y - 22)
        pygame.draw.rect(screen, INPUT_BG, input_box_email, border_radius=6)
        pygame.draw.rect(screen, INPUT_BORDER, input_box_email, 2, border_radius=6)
        email_surf = font_med.render(email, True, (0,0,0) if email else (120,120,120))
        screen.blit(email_surf, (input_box_email.x + 10, input_box_email.y + 8))

        # Indicador de campo activo
        if active_field == "name":
            pygame.draw.rect(screen, (120,200,255), input_box_name, 3, border_radius=6)
        elif active_field == "email":
            pygame.draw.rect(screen, (120,200,255), input_box_email, 3, border_radius=6)

        # Botones: Guardar y Jugar como invitado
        draw_button(save_button, "Guardar", GREEN, hover_color=(80,255,120), text_color=(0,0,0))
        draw_button(guest_button, "Jugar como invitado", GRAY, hover_color=(180,180,180), text_color=(0,0,0))

        draw_text_center("ENTER = confirmar | TAB = cambiar campo", font_small, BLUE, WIDTH//2, HEIGHT//2 + 130)
        pygame.display.flip()

# --- Banner temporal de nuevo récord ---
def show_new_record_banner(score, duration=1.5):
    t0 = time.time()
    while time.time() - t0 < duration:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
        update_stars()
        draw_background()
        rect = pygame.Rect(WIDTH//2 - 260, HEIGHT//2 - 70, 520, 120)
        pygame.draw.rect(screen, BLACK, rect, border_radius=12)
        pygame.draw.rect(screen, GOLD, rect, 4, border_radius=12)
        draw_text_center("🎉 ¡NUEVO RÉCORD PERSONAL! 🎉", font_big, GOLD, WIDTH//2, HEIGHT//2 - 18)
        draw_text_center(f"Puntos: {score}", font_med, WHITE, WIDTH//2, HEIGHT//2 + 30)
        pygame.display.flip()

# --- Lógica para manejar correos después del juego ---
def handle_post_game_emails_after_save(name, email, score, was_new_record, previous_best, new_rank):
    """
    Decide cuándo enviar correos:
    - Si no hay email -> no se envía nada.
    - Si was_new_record True -> enviar correo de nuevo récord (incluye puesto).
    - Si new_rank == 1 -> enviar correo TOP1 (adicional).
    """
    if not email:
        print("[mail] No hay correo configurado para el jugador. No se enviarán notificaciones.")
        return

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if was_new_record:
        enviar_correo_nuevo_record(email, name, score, puesto=new_rank, fecha=fecha)

    if new_rank == 1:
        enviar_correo_top1(email, name, score, fecha=fecha)

# ------------------ Game Over simple (sin pedir datos) ------------------
def game_over_screen_simple(score):
    stop_music()
    buttons = [
        {"label": "Jugar de nuevo", "rect": pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 60, 320, 52), "color": GREEN},
        {"label": "Volver al menú", "rect": pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 128, 320, 52), "color": BLUE},
    ]

    showing = True
    while showing:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                for b in buttons:
                    if b["rect"].collidepoint(ev.pos):
                        if b["label"] == "Jugar de nuevo":
                            play_music_with_fade(juego, game_volume, fade_ms=300)
                            return "retry"
                        else:
                            play_music_with_fade(menu, menu_volume, fade_ms=300)
                            return "menu"

        update_stars()
        draw_background()
        draw_text_center("GAME OVER", font_big, RED, WIDTH//2, HEIGHT//2 - 120)
        draw_text_center(f"Puntuación final: {score}", font_med, WHITE, WIDTH//2, HEIGHT//2 - 60)
        
        if PLAYER_NAME:
            draw_text_center(f"Jugador: {PLAYER_NAME}", font_small, GRAY, WIDTH//2, HEIGHT//2 - 20)

        for b in buttons:
            color = b["color"]
            if b["rect"].collidepoint(mx, my):
                color = (min(color[0]+40,255), min(color[1]+40,255), min(color[2]+40,255))
            pygame.draw.rect(screen, color, b["rect"], border_radius=8)
            draw_text_center(b["label"], font_med, BLACK, b["rect"].centerx, b["rect"].centery)

        pygame.display.flip()

# ------------------ Juego principal (Space Invaders básico) ------------------
def main_game():
    fade_out_screen(180)
    loading_screen()
    play_music_with_fade(juego, game_volume, fade_ms=300)

    player = pygame.Rect(WIDTH//2 - 25, HEIGHT - 60, 50, 20)
    bullets = []
    enemy_bullets = []
    enemies = create_enemies()
    direction = 1
    score = 0
    enemy_speed = 2
    player_lives = 3
    running = True

    while running:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.left > 0:
            player.x -= 7
        if keys[pygame.K_RIGHT] and player.right < WIDTH:
            player.x += 7
        if keys[pygame.K_SPACE] and len(bullets) < 6:
            bullets.append(pygame.Rect(player.centerx - 2, player.top, 4, 10))

        move_down = False
        for en in enemies:
            en.x += enemy_speed * direction
            if en.right >= WIDTH - 10 or en.left <= 10:
                move_down = True
        if move_down:
            direction *= -1
            for en in enemies:
                en.y += 20

        if enemies and random.randint(1, 40) == 1:
            shooter = random.choice(enemies)
            enemy_bullets.append(pygame.Rect(shooter.centerx - 2, shooter.bottom, 4, 10))

        for b in bullets[:]:
            b.y -= 8
            if b.bottom < 0:
                try:
                    bullets.remove(b)
                except ValueError:
                    pass
                continue
            hit_enemy = None
            for e in enemies:
                if b.colliderect(e):
                    hit_enemy = e
                    break
            if hit_enemy:
                try:
                    enemies.remove(hit_enemy)
                except ValueError:
                    pass
                try:
                    bullets.remove(b)
                except ValueError:
                    pass
                score += 10
                continue

        for eb in enemy_bullets[:]:
            eb.y += 6
            if eb.top > HEIGHT:
                try:
                    enemy_bullets.remove(eb)
                except ValueError:
                    pass
                continue
            if eb.colliderect(player):
                try:
                    enemy_bullets.remove(eb)
                except ValueError:
                    pass
                player_lives -= 1
                player.x = WIDTH//2 - player.width//2
                if player_lives <= 0:
                    running = False
                    break

        for e in enemies:
            if e.bottom >= player.top:
                player_lives = 0
                running = False
                break

        if not enemies:
            enemies = create_enemies()

        update_stars()
        draw_background()
        pygame.draw.rect(screen, GREEN, player)
        for b in bullets:
            pygame.draw.rect(screen, WHITE, b)
        for eb in enemy_bullets:
            pygame.draw.rect(screen, BLUE, eb)
        for e in enemies:
            pygame.draw.rect(screen, RED, e)

        draw_text_left(f"Puntos: {score}", font_small, WHITE, 10, 10)
        life_text = f"Vida: {player_lives}"
        draw_text_left(life_text, font_small, WHITE, WIDTH - 160, 10)
        max_lives = 3
        bar_w = 100
        bar_h = 12
        bx = WIDTH - 160
        by = 30
        pygame.draw.rect(screen, RED, (bx, by, bar_w, bar_h))
        if player_lives > 0:
            fill_w = int((player_lives / max_lives) * bar_w)
            pygame.draw.rect(screen, GREEN, (bx, by, fill_w, bar_h))

        pygame.display.flip()

    # --- Al terminar la partida: guardar, notificar y mostrar Game Over ---
    stop_music(fade_ms=300)

    # Asegurar PLAYER_NAME definido
    global PLAYER_NAME, PLAYER_EMAIL, IS_GUEST
    if not PLAYER_NAME:
        PLAYER_NAME = "Invitado"
        PLAYER_EMAIL = ""
        IS_GUEST = True

    if PLAYER_NAME:
        # Guardar/actualizar el puntaje (solo si es el mejor) y obtener resultado
        was_new_record, previous_best, new_rank = save_score_json(PLAYER_NAME, score, PLAYER_EMAIL)

        # Si hubo nuevo record, mostrar banner antes del Game Over (invitado también ve banner)
        if was_new_record:
            show_new_record_banner(score, duration=1.5)

        # Manejar envío de correos inteligentes (si no es invitado y tiene email)
        if not IS_GUEST and PLAYER_EMAIL:
            handle_post_game_emails_after_save(PLAYER_NAME, PLAYER_EMAIL, score, was_new_record, previous_best, new_rank)

    # Mostrar la pantalla de Game Over
    result = game_over_screen_simple(score)
    
    if result == "retry":
        main_game()
    else:
        return

# ------------------ Menu principal ------------------
def main_menu():
    # declarar globales porque esta función puede escribir PLAYER_NAME/EMAIL/IS_GUEST
    global PLAYER_NAME, PLAYER_EMAIL, IS_GUEST
    play_music_with_fade(menu, menu_volume, fade_ms=200)
    loading_screen()

    buttons = [
        ("JUGAR", HEIGHT//2 - 110, GREEN),
        ("PERFIL", HEIGHT//2 - 40, YELLOW),
        ("PUNTUACIONES", HEIGHT//2 + 30, BLUE),
        ("AJUSTAR VOLUMEN", HEIGHT//2 + 100, (100, 100, 255)),
        ("SALIR", HEIGHT//2 + 170, RED),
    ]

    running = True
    while running:
        clock.tick(FPS)
        mx, my = pygame.mouse.get_pos()
        click = False
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                stop_music()
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                click = True

        update_stars()
        draw_background()
        draw_text_center("SPACE INVADERS", font_big, GREEN, WIDTH//2, HEIGHT//4)
        
        # Mostrar perfil actual si existe
        if PLAYER_NAME:
            draw_text_center(f"Jugador: {PLAYER_NAME}", font_small, GRAY, WIDTH//2, HEIGHT//4 + 50)

        for text, y, base_color in buttons:
            rect = pygame.Rect(WIDTH//2 - 140, y - 22, 280, 48)
            color = base_color
            if rect.collidepoint(mx, my):
                color = (min(base_color[0] + 40, 255), min(base_color[1] + 40, 255), min(base_color[2] + 40, 255))
            pygame.draw.rect(screen, color, rect, border_radius=8)
            draw_text_center(text, font_med, BLACK, rect.centerx, rect.centery)

        pygame.display.flip()

        if click:
            for text, y, base_color in buttons:
                rect = pygame.Rect(WIDTH//2 - 140, y - 22, 280, 48)
                if rect.collidepoint(mx, my):
                    if text == "JUGAR":
                        if not PLAYER_NAME:
                            # Abrir registro; si el jugador cancela se pone como Invitado
                            register_player_screen()
                            if not PLAYER_NAME:
                                PLAYER_NAME = "Invitado"
                                PLAYER_EMAIL = ""
                                IS_GUEST = True
                        main_game()
                        play_music_with_fade(menu, menu_volume, fade_ms=200)
                    elif text == "PERFIL":
                        register_player_screen()
                    elif text == "PUNTUACIONES":
                        show_scores_screen()
                        play_music_with_fade(menu, menu_volume, fade_ms=200)
                    elif text == "AJUSTAR VOLUMEN":
                        adjust_volumes()
                        play_music_with_fade(menu, menu_volume, fade_ms=200)
                    elif text == "SALIR":
                        stop_music()
                        pygame.quit()
                        sys.exit()

# ------------------ Inicio ------------------
if __name__ == "__main__":
    main_menu()
